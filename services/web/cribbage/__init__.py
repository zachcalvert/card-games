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
            game_dict = {
                "name": game_name,
                "state": "INIT",
                "players": {nickname: {'nickname': nickname, 'points': 0}},
            }
            cache.set(game_name, json.dumps(game_dict))
        else:
            game_dict = json.loads(game_from_cache)
            if nickname not in game_dict["players"]:
                game_dict["players"][nickname] = {'nickname': nickname, 'points': 0}
                cache.set(game_name, json.dumps(game_dict))

        if game_dict["state"] != 'INIT':
            pass
            # return redirect(url_for('index'))

        other_players = [game_dict["players"][player] for player in game_dict["players"].keys() if player != nickname]
        print('game = {}'.format(game_dict))
        print('this player: {}'.format(nickname))
        print('all players: {}'.format(game_dict['players'].keys()))
        print('other players: {}'.format(other_players))
        return render_template('game.html', game=game_dict, player=game_dict['players'][nickname],
                               other_players=other_players, async_mode=socketio.async_mode)

    return redirect(url_for('index'))


@socketio.on('join', namespace='/game')
def join(message):
    join_room(message['game'])
    emit('player_join', {'nickname': message['nickname'], 'gameName': message['game']}, room=message['game'])


@socketio.on('leave', namespace='/game')
def leave(message):
    leave_room(message['game'])
    game_from_cache = cache.get(message['game'])
    # cache.delete(player)
    emit('player_leave',
         {'nickname': message['nickname'], 'gameName': message['game']}, room=message['game'])


@socketio.on('send_message', namespace='/game')
def send_message(message):
    emit('new_chat_message', {'data': message['data'], 'nickname': message['nickname']}, room=message['game'])


@socketio.on('start_game', namespace='/game')
def start_game(message):
    game_dict = json.loads(cache.get(message['game']))
    players = list(game_dict['players'].keys())
    dealer = random.choice(players)
    game_dict.update({
        'state': 'DEALING',
        'dealer': dealer,
        'hands': {},
        'played_cards': {},
        'crib': [],
        'turn': dealer,
        'pegging': {
            'total': 0,
            'cards': []
        },
    })
    for player in players:
        game_dict['played_cards'][player] = []

    cache.set(message["game"], json.dumps(game_dict))
    emit('start_game', {'game': game_dict["name"], 'players': list(game_dict["players"].keys()), 'dealer': dealer},
         room=game_dict["name"])


@socketio.on('deal_hands', namespace='/game')
def deal_hands(message):
    game_dict = json.loads(cache.get(message['game']))
    deck = CARDS.copy()  # exclude the facedown card

    for player in game_dict["players"].keys():
        dealt_cards = [random.choice(list(deck.keys())) for card in range(HAND_SIZE)]
        game_dict['hands'][player] = dealt_cards
    print('hands: {}'.format(game_dict['hands']))

    game_dict['cut_card'] = random.choice(list(deck.keys()))
    cache.set(game_dict["name"], json.dumps(game_dict))
    emit('deal_hands', {'hands': game_dict['hands']}, room=game_dict["name"])


@socketio.on('discard', namespace='/game')
def discard(message):
    """
    Add the discarded card to the crib of the dealer
    :param message:
    :return:
    """
    game_dict = json.loads(cache.get(message['game']))
    card = message["discarded"]
    discarder = message['nickname']

    game_dict['hands'][discarder].remove(card)
    game_dict['crib'].append(card)

    # if everyone's down to 4 cards
    if all(len(game_dict['hands'][nickname]) == 4 for nickname, _ in game_dict['players'].items()):
        game_dict['state'] = 'CUTTING'
        players = list(game_dict['players'].keys())
        turn = game_dict['turn']
        try:
            cutter = players[players.index(turn)+1]
        except IndexError:
            cutter = players[0]

        game_dict['turn'] = cutter
        print('showing cut to {}'.format(cutter))
        emit('show_cut_deck_action', {'cutter': game_dict['turn']}, room=message['game'])

    cache.set(message['game'], json.dumps(game_dict))
    emit('post_discard', {'discarded': card, 'nickname': discarder}, room=message['game'])


@socketio.on('cut_deck', namespace='/game')
def cut_deck(message):
    game_dict = json.loads(cache.get(message['game']))
    game_dict['state'] = 'PLAYING'
    cache.set(message['game'], json.dumps(game_dict))

    print('cut_card is {}'.format(game_dict['cut_card']))
    emit('show_cut_card', {"cut_card": game_dict['cut_card'], 'turn': game_dict['turn']}, room=message['game'])


@socketio.on('play_card', namespace='/game')
def play_card(message):
    game_dict = json.loads(cache.get(message['game']))
    player = message['nickname']
    card_played = message['card_played']

    # move played card into `played_cards` from player hand
    game_dict['played_cards'][player].append(card_played)
    game_dict['hands'][player].remove(card_played)

    # score hand
    scorer = PlayScorer(CARDS.get(card_played), game_dict['pegging']['cards'], game_dict['pegging']['total'])
    points_scored, new_total = scorer.calculate_points()

    # write output to cache
    game_dict['pegging']['cards'].append(card_played)
    game_dict['pegging']['total'] = new_total
    game_dict['players'][message['nickname']]['points'] += points_scored
    cache.set(message['game'], json.dumps(game_dict))

    # set next turn
    turn = game_dict['turn']
    players = list(game_dict['players'].keys())
    try:
        next_player = players[players.index(turn) + 1]
    except IndexError:
        next_player = players[0]

    # determine if next player can pass or play
    next_player_action = 'Pass'
    next_player_cards = [CARDS.get(card) for card in game_dict['hands'][next_player]]
    remainder = 31 - new_total
    if any(card['value'] <= remainder for card in next_player_cards):
        next_player_action = 'Play'

    print('play earned {} points, new_total is {}'.format(points_scored, new_total))
    emit('show_card_played', {
        'nickname': message['nickname'], 'card': card_played, 'points_scored': points_scored, 'new_total': new_total,
        'next_player': next_player, 'next_player_action': next_player_action}, room=message["game"])


@socketio.on('ready_to_score', namespace='/game')
def ready_to_score(message):
    game_dict = json.loads(cache.get(message['game']))
    hand_dict = game_dict['players'][message['nickname']]['hand']
    hand_dict['state'] = 'SCORING'
    game_dict['players'][message['nickname']]['hand'] = hand_dict
    cache.set(message['game'], json.dumps(game_dict))

    # if this game has no more Hands in a discarding state, dispatch the cut deck option
    for player_name, player_dict in game_dict["players"].items():
        if player_name['hand']['state'] == 'PEGGING':
            return

    emit('show_score_hands_action', room=game.name)



if __name__ == '__main__':
    socketio.run(app, debug=True)
