#!/usr/bin/env python
import json
import random
import redis

from threading import Lock
from flask import Flask, render_template, session, request, Markup, redirect, url_for, jsonify
from flask_fontawesome import FontAwesome
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect

from .cards import CARDS
from .scoring import HandScorer, PlayScorer

async_mode = None

app = Flask(__name__)
app.config.from_object("cribbage.config.Config")

cache = redis.Redis(host='redis', port=6379)

HAND_SIZE = 6


class Game:

    def __init__(self, name, players=[], state='INIT'):
        self.name = name
        self.players = players
        self.state = state


class Player:

    def __init__(self, nickname, game, points=0):
        self.nickname = nickname
        self.game = game
        self.points = points


class Hand:

    def __init__(self, player, game, state, cards={}, points=0):
        self.player = player
        self.game = game
        self.state = state
        self.cards = cards
        self.points = points


fa = FontAwesome(app)

socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


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
            game = {
                "name": game_name,
                "state": "INIT",
                "players": {nickname: {'nickname': nickname, 'points': 0}}
            }
            cache.set(game_name, json.dumps(game))
        else:
            game = json.loads(game_from_cache)
            if nickname not in game["players"]:
                game["players"][nickname] = {'nickname': nickname, 'points': 0}
                cache.set(game_name, json.dumps(game))

        if game["state"] in ['UNDERWAY','FINISHED']:
            pass
            # return redirect(url_for('index'))

        other_players = [game["players"][player] for player in game["players"].keys() if player != nickname]
        print('game = {}'.format(game))
        print('this player: {}'.format(nickname))
        print('all players: {}'.format(game['players'].keys()))
        print('other players: {}'.format(other_players))
        return render_template('game.html', game=game, player=game['players'][nickname],
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
    emit('new_chat_message',
         {'data': message['data'], 'nickname': message['nickname']}, room=message['game'])


@socketio.on('start_game', namespace='/game')
def start_game(message):
    game = json.loads(cache.get(message['game']))
    print('starting game {}'.format(game))
    game["state"] = 'UNDERWAY'
    cache.set(message["game"], json.dumps(game))

    player_names = [player for player in game["players"].keys()]

    print('starting {} with these players: {}'.format(game["name"], player_names))
    emit('start_game', {'game': game["name"], 'players': player_names}, room=game["name"])


@socketio.on('deal_hands', namespace='/game')
def deal_hands(message):
    game_dict = json.loads(cache.get(message['game']))

    deck = CARDS.copy()  # exclude the facedown card

    hands = {}
    for player in game_dict["players"].keys():
        dealt_cards = [random.choice(list(deck.keys())) for card in range(HAND_SIZE)]
        game_dict['hands'][player] = {
            'state': 'DISCARDING',
            'cards': dealt_cards
        }
        cache.set(game["name"], json.dumps(game_dict))
        hands[player] = dealt_cards

    print('hands: {}'.format(hands))
    emit('deal_hands', {'hands': hands}, room=game["name"])

    cut_card = random.choice(list(deck.keys()))
    game_dict['cut_card'] = cut_card


@socketio.on('discard', namespace='/game')
def discard(message):
    """
    Add the discarded card to the crib of the dealer
    :param message:
    :return:
    """
    dealer_name = message['dealer']
    game = json.loads(cache.get(message['game']))
    card = message["discarded"]
    dealer_dict = game['players'][message['nickname']]

    if 'crib' in dealer_dict.keys():
        dealer_dict['crib'].append(card)
    else:
        dealer_dict['crib'] = [card]

    game[dealer_name] = dealer_dict

    cache.set(game["name"], json.dumps(game))

    print('discarded is {}'.format(card))
    emit('post_discard', {'discarded': card, 'nickname': message['nickname']}, room=message['game'])


@socketio.on('cut_deck', namespace='/game')
def cut_deck(message):
    game = json.loads(cache.get(message['game']))
    cut_card = message["cut_card"]
    print('cut_card is {}'.format(cut_card))
    emit('show_cut_card', {"cut_card": cut_card}, room=game["name"])


@socketio.on('ready_to_peg', namespace='/game')
def ready_to_peg(message):
    game_dict = json.loads(cache.get(message['game']))
    hand_dict = game_dict['players'][message['nickname']]['hand']
    hand_dict['state'] = 'PEGGING'
    game_dict['players'][message['nickname']]['hand'] = hand_dict
    cache.set(message['game'], json.dumps(game_dict))

    # if this game has no more Hands in a discarding state, dispatch the cut deck option
    for player_name, player_dict in game_dict["players"].items():
        if player_name['hand']['state'] == 'DISCARDING':
            return

    emit('show_cut_deck_action', room=game.name)


@socketio.on('play_card', namespace='/game')
def play_card(message):
    total = message["running_total"] or 0
    card_played = message["card_played"]
    print('card_played is {}'.format(card_played))
    previously_played_cards = message["previously_played_cards"]
    print('previously_played_cards is {}'.format(previously_played_cards))

    scorer = PlayScorer(CARDS.get(card_played), previously_played_cards, total)
    points_scored, new_total = scorer.calculate_points()

    game_dict = json.loads(cache.get(message['game']))
    game_dict['players'][message['nickname']]['points'] += points_scored
    cache.set(message['game'], json.dumps(game_dict))

    player_points = game_dict['players'][message['nickname']]['points']

    print('play earned {} points, new_total is {}, and player has {} total points'.format(points_scored, new_total, player_points))
    emit('show_card_played', {"nickname": message["nickname"], "card": card_played, "points": points_scored,
                              "player_points": player_points, "new_total": new_total}, room=message["game"])


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
