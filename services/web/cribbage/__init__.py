#!/usr/bin/env python
import itertools
import json
import random
import redis

from threading import Lock
from flask import Flask, render_template, session, request, Markup, redirect, url_for, jsonify
from flask_fontawesome import FontAwesome
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect

from .cards import CARDS
from .scoring import PlayScorer, HandScorer

async_mode = None

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)
fa = FontAwesome(app)
socketio = SocketIO(app, async_mode=async_mode)


thread = None
thread_lock = Lock()

HAND_SIZE = 6


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        nickname = request.form.get('join_nickname')
        game_name = request.form['join_game_name']
        game_from_cache = cache.get(game_name)
        if not game_from_cache:
            g = {
                "name": game_name,
                "state": "INIT",
                "players": {nickname: {'nickname': nickname, 'points': 0}},
            }
            cache.set(game_name, json.dumps(g))
        else:
            g = json.loads(game_from_cache)
            if nickname not in g["players"]:
                g["players"][nickname] = {'nickname': nickname, 'points': 0}
                cache.set(game_name, json.dumps(g))

        if g["state"] != 'INIT':
            pass
            # return redirect(url_for('index'))

        other_players = [g["players"][player] for player in g["players"].keys() if player != nickname]
        print('game = {}'.format(g))
        print('this player: {}'.format(nickname))
        print('all players: {}'.format(g['players'].keys()))
        print('other players: {}'.format(other_players))
        return render_template('game.html', game=g, player=g['players'][nickname],
                               other_players=other_players, async_mode=socketio.async_mode)

    return redirect(url_for('index'))


def rotate_turn(current, players):
    """
    :param current:
    :param players:
    :return:
    """
    try:
        next_player = players[players.index(current) + 1]
    except IndexError:
        next_player = players[0]
    return next_player


def play_or_pass(cards, pegging_total):
    """
    :param player:
    :param cards:
    :param pegging_total:
    :return:
    """
    action = 'PASS'
    card_values = [CARDS.get(card)['value'] for card in cards]
    print('card values: {}'.format(card_values))
    remainder = 31 - pegging_total
    print('they must have a card with value less than or equal to {} to play'.format(remainder))
    if any(value <= remainder for value in card_values):
        print('since they have a card with value {}, they can play'.format(any(value <= remainder for value in card_values)))
        action = 'PLAY'
    return action


@socketio.on('join', namespace='/game')
def join(message):
    join_room(message['game'])
    emit('player_join', {'nickname': message['nickname'], 'points': 0, 'gameName': message['game']}, room=message['game'])


@socketio.on('leave', namespace='/game')
def leave(message):
    leave_room(message['game'])
    g = json.loads(cache.get(message['game']))
    g['players'].pop(message['nickname'])
    cache.set(message['game'], json.dumps(g))
    emit('player_leave', {'nickname': message['nickname'], 'gameName': message['game']}, room=message['game'])


@socketio.on('send_message', namespace='/game')
def send_message(message):
    emit('new_chat_message', {'data': message['data'], 'nickname': message['nickname']}, room=message['game'])


@socketio.on('start_game', namespace='/game')
def start_game(message):
    g = json.loads(cache.get(message['game']))
    players = list(g['players'].keys())
    dealer = random.choice(players)
    g.update({
        'state': 'DEAL',
        'dealer': dealer,
        'deck': [],
        'hands': {},
        'played_cards': {},
        'crib': [],
        'turn': dealer,
        'pegging': {
            'total': 0,
            'cards': [],
            'passed': []
        },
    })
    for player in players:
        g['played_cards'][player] = []

    cache.set(message['game'], json.dumps(g))
    emit('start_game', {'game': g["name"], 'players': list(g["players"].keys()), 'dealer': dealer},
         room=message['game'])


@socketio.on('deal_hands', namespace='/game')
def deal_hands(message):
    g = json.loads(cache.get(message['game']))
    deck = list(CARDS.keys())
    random.shuffle(deck)

    for player in g["players"].keys():
        dealt_cards = [deck.pop() for card in range(HAND_SIZE)]
        g['hands'][player] = dealt_cards
        print('dealt a hand, the deck now has {} cards'.format(len(deck)))

    print('hands: {}'.format(g['hands']))

    g['state'] = 'DISCARD'
    g['deck'] = deck
    cache.set(message['game'], json.dumps(g))
    emit('deal_hands', {'hands': g['hands'], 'dealer': g['dealer']}, room=g['name'])
    emit('update_action_button', {'action': 'DISCARD'}, room=g['name'])


@socketio.on('discard', namespace='/game')
def discard(message):
    """
    Add the discarded card to the crib of the dealer
    :param message:
    :return:
    """
    g = json.loads(cache.get(message['game']))
    card = message["discarded"]
    discarder = message['nickname']

    g['hands'][discarder].remove(card)
    g['crib'].append(card)

    # if everyone's down to 4 cards
    if all(len(g['hands'][nickname]) == 4 for nickname, _ in g['players'].items()):
        g['state'] = 'CUT'
        players = list(g['players'].keys())
        turn = g['turn']
        try:
            cutter = players[players.index(turn)+1]
        except IndexError:
            cutter = players[0]

        g['turn'] = cutter
        print('showing cut to {}'.format(cutter))
        emit('enable_action_button', {'nickname': cutter, 'action': 'CUT'}, room=message['game'])

    cache.set(message['game'], json.dumps(g))
    emit('post_discard', {'discarded': card, 'nickname': discarder}, room=message['game'])


@socketio.on('cut_deck', namespace='/game')
def cut_deck(message):
    g = json.loads(cache.get(message['game']))
    g['cut_card'] = g['deck'].pop()
    g['state'] = 'PLAYING'
    cache.set(message['game'], json.dumps(g))
    emit('show_cut_card', {"cut_card": g['cut_card'], 'turn': g['turn']}, room=message['game'])


@socketio.on('play_card', namespace='/game')
def play_card(message):
    g = json.loads(cache.get(message['game']))
    player = message['nickname']
    card_played = message['card_played']

    # update game dict with record of card being played
    print('card_played: {}'.format(card_played))
    print('player: {}'.format(player))
    print('{}s hand: {}'.format(player, g['hands'][player]))
    g['played_cards'][player].append(card_played)
    g['hands'][player].remove(card_played)
    g['pegging']['cards'].append(card_played)

    # score hand
    scorer = PlayScorer(CARDS.get(card_played), g['pegging']['cards'], g['pegging']['total'])
    points_scored, new_total = scorer.calculate_points()
    g['pegging']['total'] = new_total

    print('play earned {} points, new_total is {}'.format(points_scored, new_total))
    if points_scored > 0:
        g['players'][message['nickname']]['points'] += points_scored
        emit('award_points', {'player': player, 'amount': points_scored, 'reason': 'pegging'}, room=message['game'])

    # if no one has any cards left to play, end the pegging round
    no_cards_left = all([not hand for player, hand in g['hands'].items()])
    if no_cards_left:
        g['state'] = 'SCORE'
        g['pegging'].update({
            'total': 0,
            'cards': [],
            'passed': []
        })
        cache.set(message['game'], json.dumps(g))
        # send the players cards back to their hands, in game_dict and on screen
        emit('enable_action_button', {'nickname': g['dealer'], 'action': 'SCORE'}, room=g['name'])

    # determine next_player
    next_player = rotate_turn(g['turn'], list(g['players'].keys()))
    if next_player in g['pegging']['passed']:
        print('we should be skipping {} since they already passed'.format(next_player))
    next_player_action = play_or_pass(g['hands'][next_player], g['pegging']['total'])
    print('next player is {} and they should {}'.format(next_player, next_player_action))

    # write the game state
    cache.set(message['game'], json.dumps(g))
    emit('show_card_played', {
         'nickname': message['nickname'], 'card': card_played, 'new_total': new_total,
         'next_player': next_player, 'next_player_action': next_player_action}, room=message["game"])

    # if they hit 31 on the nose, reset pegging round (they already received the 2 points)
    if new_total == 31:
        g['pegging'].update({
            'total': 0,
            'cards': [],
            'passed': []
        })
        emit('clear_pegging_area', room=message['game'])
        next_player_action = 'PLAY'

    g['turn'] = next_player
    cache.set(message['game'], json.dumps(g))
    emit('show_card_played', {
         'nickname': message['nickname'], 'card': card_played, 'new_total': new_total,
         'next_player': next_player, 'next_player_action': next_player_action}, room=message["game"])


@socketio.on('pass', namespace='/game')
def pass_on_play(message):
    g = json.loads(cache.get(message['game']))
    g['pegging']['passed'].append(message['nickname'])

    # check if everyone but the next player has passed at this point
    next_player = rotate_turn(g['turn'], list(g['players'].keys()))
    next_player_action = play_or_pass(g['hands'][next_player], g['pegging']['total'])
    if set(g['players'].keys()) - set(g['pegging']['passed']) == {next_player}:
        print('everyone but {} has passed'.format(next_player))
        # if the next player would also pass, that means they played the card that made everyone else pass,
        # so they get 1 point and they get to start the next round of pegging
        if next_player_action == 'PASS':
            print('{} cant play either, so we award them 1 point and reset the pegging round'.format(next_player))
            g['pegging'].update({
                'total': 0,
                'cards': [],
                'passed': []
            })
            emit('award_points', {'player': next_player, 'amount': 1, 'reason': '1 for go.'}, room=message['game'])
            emit('clear_pegging_area', room=message['game'])
            emit('enable_action_button', {'action': 'PLAY', 'nickname': next_player}, room=g['name'])

    else:
        emit('player_passed', {'player': message['nickname'], 'next_player': next_player,
                               'next_player_action': next_player_action}, room=message["game"])

    g['turn'] = next_player
    cache.set(message['game'], json.dumps(g))


if __name__ == '__main__':
    socketio.run(app, debug=True)
