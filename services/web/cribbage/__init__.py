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
        print('{}'.format(any(value <= remainder for value in card_values)))
        action = 'PLAY'
    return action


def next_player_who_can_take_action_this_round(game_dict):
    """
    Return the next player who still has cards and has not passed
    :return: nickname
    """
    if game_dict['pegging']['total'] >= 31:
        # we should never get above 31, but just in case
        return None

    player_order = list(game_dict['players'].keys())
    starting_point = player_order.index(game_dict['turn'])
    players_to_check_in_order = player_order[starting_point + 1:] + player_order[:starting_point + 1]
    for player in players_to_check_in_order:
        print('checking if {} can play this round..'.format(player))
        if player in game_dict['pegging']['passed']:  # if they've passed
            print('{} has already passed, skipping them'.format(player))
            continue
        if not game_dict['hands'][player]:  # or have no cards left
            print('{} has no cards left, skipping them'.format(player))
            continue

        # make sure that the next player isn't also the current player and they would have to pass
        if player == game_dict['pegging']['last_played']:
            print('weve circled back around to {}'.format(player))
            next_action = play_or_pass(game_dict['hands'][player], game_dict['pegging']['total'])
            if next_action == 'PASS':
                print('they cant play either, so we are returning None')
                return None

        print('{} hasnt passed and has at least one card'.format(player))
        return player

    print('everyone has already passed or has no cards left')
    return None


def next_player_who_can_play_at_all(game_dict):
    """
    Return the next player who still has cards
    :return:
    """
    player_order = list(game_dict['players'].keys())
    starting_point = player_order.index(game_dict['turn'])
    players_to_check_in_order = player_order[starting_point + 1:] + player_order[:starting_point + 1]
    for player in players_to_check_in_order:
        print('checking if {} can peg at all'.format(player))
        if not game_dict['hands'][player]:  # or have no cards left
            print('{} has no cards left, skipping them'.format(player))
            continue
        return player

    print('everyone is out of cards')
    return None


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
        'first_to_score': rotate_turn(dealer, players),
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
        'scored_hands': []
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
    emit('send_turn', {'player': 'all', 'action': 'DISCARD'}, room=g['name'])


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
        emit('send_turn', {'player': cutter, 'action': 'CUT'}, room=message['game'])

    cache.set(message['game'], json.dumps(g))
    emit('post_discard', {'discarded': card, 'nickname': discarder}, room=message['game'])


@socketio.on('cut_deck', namespace='/game')
def cut_deck(message):
    g = json.loads(cache.get(message['game']))
    g['cut_card'] = g['deck'].pop()
    g['state'] = 'PLAYING'
    cache.set(message['game'], json.dumps(g))
    emit('show_cut_card', {"cut_card": g['cut_card'], 'turn': g['turn']}, room=message['game'])


@socketio.on('peg_round_action', namespace='/game')
def peg_round_action(message):
    """
    Handles the playing of a card as well as passing on playing
    :param message:
    :return:
    """
    print('received a pef round action')
    g = json.loads(cache.get(message['game']))
    player = message['nickname']
    if 'card_played' in message.keys():
        # record card getting played
        card_played = message['card_played']
        g['played_cards'][player].append(card_played)
        g['hands'][player].remove(card_played)
        g['pegging']['cards'].append(card_played)
        g['pegging']['last_played'] = player
        print('{} played {}, and their hand is now {}'.format(player, card_played, g['hands'][player]))

        # score card play
        scorer = PlayScorer(CARDS.get(card_played), g['pegging']['cards'], g['pegging']['total'])
        points_scored, new_total = scorer.calculate_points()
        g['pegging']['total'] = new_total

        # show card getting played
        emit('show_card_played', {'nickname': message['nickname'], 'card': card_played, 'new_total': new_total}, room=message['game'])
        print('play earned {} points, new_total is {}'.format(points_scored, new_total))
        if points_scored > 0:
            g['players'][message['nickname']]['points'] += points_scored
            emit('award_points', {'player': player, 'amount': points_scored, 'reason': 'pegging'}, room=message['game'])
    else:
        # player passed
        g['pegging']['passed'].append(message['nickname'])

    # write to cache
    cache.set(message['game'], json.dumps(g))

    # determine what happens next
    next_player = next_player_who_can_take_action_this_round(g)
    if next_player:
        g['turn'] = next_player
        next_action = play_or_pass(g['hands'][next_player], g['pegging']['total'])
        print('It is time for {} to {}'.format(next_player, next_action))
        emit('send_turn', {'player': next_player, 'action': next_action}, room=message['game'])
    else:
        # award a point to current player for go (if they didn't already get em for 31) and reset
        if g['pegging']['total'] != 31:
            print('awarding a point to {} for go'.format(g['pegging']['last_played']))
            emit('award_points', {'player': g['pegging']['last_played'], 'amount': 1, 'reason': 'go'}, room=message['game'])
        print('about to tell the frontend to clean up the pegging area')
        emit('clear_pegging_area', room=message['game'])
        g['pegging'].update({
            'cards': [],
            'last_played': '',
            'passed': [],
            'total': 0
        })
        next_player = next_player_who_can_play_at_all(g)
        if next_player:
            g['turn'] = next_player
            print('It is time for {} to {}'.format(next_player, 'PLAY'))
            emit('send_turn', {'player': next_player, 'action': 'PLAY'}, room=message['game'])
        else:
            # nobody has any cards left
            g['turn'] = g['first_to_score']
            print('It is time for {} to {}'.format(next_player, 'SCORE'))
            emit('send_turn', {'player': g['first_to_score'], 'action': 'SCORE'}, room=message['game'])

    # write next player to cache
    cache.set(message['game'], json.dumps(g))
    return


@socketio.on('score_hand', namespace='/game')
def score_hand(message):
    g = json.loads(cache.get(message['game']))
    player = message['nickname']
    hand = g['played_cards'][player]

    scorer = HandScorer(hand, g['cut_card'])
    points = scorer.calculate_points()

    g['players'][player]['points'] += points
    g['scored_hands'].append(player)
    cache.set(message['game'], json.dumps(g))

    msg = '{} scored {} with their hand!'.format(player, points)
    emit('new_chat_message', {'data': msg, 'nickname': 'cribbot'}, room=message['game'])
    emit('award_points', {'player': player, 'amount': points, 'reason': 'Points from hand'}, room=message['game'])

    if set(g['scored_hands']) == set(g['players'].keys()):
        emit('send_turn', {'player': g['dealer'], 'action': 'SCORE CRIB'}, room=message['game'])
    else:
        next_to_score = rotate_turn(player, list(g['players'].keys()))
        emit('send_turn', {'player': next_to_score, 'action': 'SCORE'}, room=message['game'])


@socketio.on('score_crib', namespace='/game')
def score_crib(message):
    g = json.loads(cache.get(message['game']))
    player = message['nickname']

    emit('reveal_crib', room=message['game'])

    scorer = HandScorer(g['crib'], g['cut_card'], is_crib=True)
    points = scorer.calculate_points()

    g['players'][player]['points'] += points
    cache.set(message['game'], json.dumps(g))

    msg = '{} got {} from their crib!'.format(player, points)
    emit('new_chat_message', {'data': msg, 'nickname': 'cribbot'}, room=message['game'])
    emit('award_points', {'player': player, 'amount': points, 'reason': 'Points from crib'}, room=message['game'])

    emit('send_turn', {'player': g['dealer'], 'action': 'END ROUND'}, room=message['game'])


@socketio.on('end_round', namespace='/game')
def end_round(message):
    g = json.loads(cache.get(message['game']))

    emit('clear_table', room=message['game'])

    next_to_deal = rotate_turn(g['dealer'], list(g['players'].keys()))
    next_to_score_first = rotate_turn(next_to_deal, list(g['players'].keys()))

    g.update({
        'state': 'DEAL',
        'crib': [],
        'dealer': next_to_deal,
        'first_to_score': next_to_score_first,
        'hands': {},
        'played_cards': {},
        'scored_hands': [],
        'turn': next_to_deal,
    })
    cache.set(message['game'], json.dumps(g))
    emit('send_turn', {'player': g['dealer'], 'action': 'DEAL'}, room=message['game'])


if __name__ == '__main__':
    socketio.run(app, debug=True)
