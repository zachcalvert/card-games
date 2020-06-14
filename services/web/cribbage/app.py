#!/usr/bin/env python
import json
import random
import redis

from threading import Lock
from flask import Flask, render_template, session, request, Markup, redirect, url_for, jsonify
from flask_fontawesome import FontAwesome
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect

from cribbage.bev import Bev
from cribbage.cards import CARDS
from cribbage.scoring import Hand
from cribbage.utils import rotate_turn, play_or_pass

async_mode = None

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)
fa = FontAwesome(app)
socketio = SocketIO(app, async_mode=async_mode)

thread = None
thread_lock = Lock()

POINTS_TO_WIN = 121


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@app.route('/game', methods=['GET', 'POST'])
def game_detail():
    if request.method == 'POST':
        game_name = request.form['join_game_name']
        player = request.form.get('join_nickname')

        game = Bev.get_game(game_name)
        if not game:
            game = Bev.setup_game(name=game_name, player=player)

        if player not in game["players"]:
            game = Bev.add_player(game_name, player)

        other_players = [game["players"][p] for p in game["players"].keys() if p != player]
        return render_template('game.html', game=game, player=game['players'][player], other_players=other_players,
                               async_mode=socketio.async_mode)

    return redirect(url_for('index'))


def award_points(game, player, amount, total_points):
    emit('new_chat_message', {'data': '{} for {}'.format(amount, player), 'nickname': 'cribbot'}, room=game)
    emit('award_points', {'player': player, 'amount': amount, 'reason': 'pegging'}, room=game)

    if total_points > POINTS_TO_WIN:
        emit('new_chat_message', {'data': '{} wins!'.format(player), 'nickname': 'cribbot'}, room=game)


def clear_pegging_area(game):
    emit('clear_pegging_area', room=game)


@socketio.on('join', namespace='/game')
def join(message):
    join_room(message['game'])
    emit('player_join', {'nickname': message['nickname'], 'points': 0, 'gameName': message['game']}, room=message['game'])


@socketio.on('leave', namespace='/game')
def leave(message):
    leave_room(message['game'])
    Bev.remove_player(message['game'], message['nickname'])
    emit('player_leave', {'nickname': message['nickname'], 'gameName': message['game']}, room=message['game'])


@socketio.on('send_message', namespace='/game')
def send_message(message):
    emit('new_chat_message', {'data': message['data'], 'nickname': message['nickname']}, room=message['game'])


@socketio.on('start_game', namespace='/game')
def start_game(message):
    dealer = Bev.start_game(message['game'])
    emit('start_game', {'dealer': dealer}, room=message['game'])


@socketio.on('deal_hands', namespace='/game')
def deal_hands(msg):
    hands = Bev.deal_hands(msg['game'])
    emit('deal_hands', {'hands': hands}, room=msg['game'])
    emit('send_turn', {'player': 'all', 'action': 'DISCARD'}, room=msg['game'])


@socketio.on('discard', namespace='/game')
def discard(msg):
    """
    """
    player_done, all_done = Bev.discard(msg['game'], msg['player'], msg["card"])
    emit('discard', {'card': msg['card'], 'nickname': msg['player'], 'done': player_done}, room=msg['game'])
    if all_done:
        cutter = Bev.get_cutter(msg['game'])
        emit('send_turn', {'player': cutter, 'action': 'CUT'}, room=msg['game'])


@socketio.on('cut_deck', namespace='/game')
def cut_deck(msg):
    cut_card, turn = Bev.cut_deck(msg['game'])
    emit('show_cut_card', {"cut_card": cut_card, 'turn': turn}, room=msg['game'])


@socketio.on('peg_round_action', namespace='/game')
def peg_round_action(msg):
    """
    Handles the playing of a card as well as passing on playing
    :param message:
    :return:
    """
    if 'card_played' in msg.keys():
        total = Bev.get_pegging_total(msg['game'])
        if CARDS.get(msg['card_played'])['value'] > (31 - total):
            emit('invalid_card', {'card': msg['card_played']})
            return
        Bev.score_play(msg['game'], msg['player'], msg['card_played'])
        new_total = Bev.record_play(msg['game'], msg['player'], msg['card_played'])
        emit('show_card_played', {'nickname': msg['player'], 'card': msg['card_played'], 'new_total': new_total},
             room=msg['game'])
    else:
        Bev.record_pass(msg['game'], msg['nickname'])

    next_player, next_action = Bev.next_player_and_action(msg['game'])
    emit('send_turn', {'player': next_player, 'action': next_action}, room=msg['game'])


@socketio.on('score_hand', namespace='/game')
def score_hand(message):
    g = json.loads(cache.get(message['game']))
    player = message['nickname']
    player_cards = g['played_cards'][player]

    hand = Hand(player_cards, g['cut_card'])
    hand_points = hand.calculate_points()

    g['players'][player]['points'] += hand_points
    g['scored_hands'].append(player)
    cache.set(message['game'], json.dumps(g))

    msg = '{} scored {} with their hand!'.format(player, hand_points)
    emit('new_chat_message', {'data': msg, 'nickname': 'cribbot'}, room=message['game'])
    emit('award_points', {'player': player, 'amount': hand_points, 'reason': 'Points from hand'}, room=message['game'])

    if g['players'][player]['points'] >= POINTS_TO_WIN:
        g['winner'] = player
        emit('new_chat_message', {'data': '{} points! {} wins!'.format(POINTS_TO_WIN, player), 'nickname': 'cribbot'},
             room=message['game'])
        emit('send_turn', {'player': 'all', 'action': 'PLAY AGAIN'}, room=message['game'])
        return

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

    crib = Hand(g['crib'], g['cut_card'], is_crib=True)
    crib_points = crib.calculate_points()
    g['players'][player]['points'] += crib_points

    cache.set(message['game'], json.dumps(g))

    msg = '{} got {} from their crib!'.format(player, crib_points)
    emit('new_chat_message', {'data': msg, 'nickname': 'cribbot'}, room=message['game'])
    emit('award_points', {'player': player, 'amount': crib_points, 'reason': 'Points from crib'}, room=message['game'])

    if g['players'][player]['points'] >= POINTS_TO_WIN:
        g['winner'] = player
        emit('new_chat_message', {'data': '{} points! {} wins!'.format(POINTS_TO_WIN, player), 'nickname': 'cribbot'},
             room=message['game'])
        emit('send_turn', {'player': 'all', 'action': 'PLAY AGAIN'}, room=message['game'])
        return

    emit('send_turn', {'player': 'all', 'action': 'END ROUND'}, room=message['game'])


@socketio.on('end_round', namespace='/game')
def end_round(message):
    g = json.loads(cache.get(message['game']))
    player = message['nickname']
    g['ok_with_next_round'].append(player)
    cache.set(message['game'], json.dumps(g))

    if set(g['ok_with_next_round']) == set(g['players'].keys()):
        next_to_deal = rotate_turn(g['dealer'], list(g['players'].keys()))
        next_to_score_first = rotate_turn(next_to_deal, list(g['players'].keys()))

        g.update({
            'state': 'DEAL',
            'crib': [],
            'dealer': next_to_deal,
            'first_to_score': next_to_score_first,
            'hands': {},
            'ok_with_next_round': [],
            'played_cards': {},
            'scored_hands': [],
            'turn': next_to_deal,
        })
        for player in list(g['players'].keys()):
            g['played_cards'][player] = []
        cache.set(message['game'], json.dumps(g))
        emit('clear_table', {'next_dealer': next_to_deal}, room=message['game'])
        msg = "New round! It is now {}'s crib.".format(next_to_deal)
        emit('new_chat_message', {'data': msg, 'nickname': 'cribbot'}, room=message['game'])
        emit('send_turn', {'player': g['dealer'], 'action': 'DEAL'}, room=message['game'])


@socketio.on('play_again', namespace='/game')
def play_again(message):
    g = json.loads(cache.get(message['game']))
    g['play_again'].append(message['nickname'])
    cache.set(message['game'], json.dumps(g))

    if set(g['play_again']) == set(g['players'].keys()):
        players = list(g['players'].keys())
        dealer = random.choice(players)

        g = {
            'name': message['game'],
            'players': {},
            'state': 'DEAL',
            'dealer': dealer,
            'first_to_score': rotate_turn(dealer, players),
            'deck': [],
            'hand_size': 6 if len(players) == 2 else 5,
            'hands': {},
            'played_cards': {},
            'crib': [],
            'turn': dealer,
            'pegging': {
                'cards': [],
                'passed': [],
                'run': [],
                'total': 0
            },
            'scored_hands': [],
            'ok_with_next_round': [],
            'play_again': [],
        }
        for player in players:
            g['players'][player] = {'nickname': player, 'points': 0}
            g['hands'][player] = []
            g['played_cards'][player] = []

        cache.set(message['game'], json.dumps(g))
        emit('reset_table', room=message['game'])
        emit('start_game', {'game': g["name"], 'players': list(g["players"].keys()), 'dealer': dealer},
             room=message['game'])


if __name__ == '__main__':
    socketio.run(app, debug=True)
