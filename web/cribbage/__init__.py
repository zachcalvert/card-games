#!/usr/bin/env python
import eventlet
eventlet.monkey_patch()

import json
import os
import random
import redis


from threading import Lock
from flask import Flask, render_template, session, request, Markup, redirect, url_for, jsonify
from flask_fontawesome import FontAwesome
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect

from cribbage import bev
from cribbage import cribby
from cribbage.utils import rotate_turn, play_or_pass, card_text_from_id

async_mode = None

app = Flask(__name__)

FontAwesome(app)
socketio = SocketIO(app, async_mode=async_mode)

thread = None
thread_lock = Lock()


@app.route('/', defaults={'reason': None}, methods=['GET', 'POST'])
@app.route('/<reason>', methods=['GET', 'POST'])
def index(reason):
    reason_mapping = {
        'already-exists': 'Oops! A game with that name is already underway. ',
        'full-game': "Uh oh! That game has 3 players and I can't support any more than that. "
    }
    message = None
    if reason:
        message = reason_mapping.get(reason, '') + 'Please try starting a game with a different name.'

    return render_template('index.html', message=message, async_mode=socketio.async_mode)


@app.route('/game', methods=['GET', 'POST'])
def game_detail():
    if request.method == 'POST':
        game_name = request.form['join_game_name']
        player = request.form.get('join_nickname')

        if not (game_name and player):
            return redirect(url_for('index'))

        game = bev.get_game(game_name)
        if not game:
            game = bev.setup_game(name=game_name, player=player)

        if game['state'] != 'INIT' and player not in game['players'].keys():
            return redirect(url_for('index', reason='already-exists'))

        if len(game['players']) >= 4:
            return redirect(url_for('index', reason='full-game'))

        if player not in game["players"]:
            game = bev.add_player(game_name, player)

        player_points = game['players'].pop(player)

        return render_template('game.html', game=game, player_name=player, player_points=player_points,
                               opponents=game['players'], async_mode=socketio.async_mode)

    return redirect(url_for('index'))


def award_points(game, player, amount, reason, just_won):
    if amount > 0:
        emit('new_message', {'type': 'score',  'data': '<b>+{} for {}</b>  ({})'.format(amount, player, reason)}, room=game)
        emit('award_points', {'player': player, 'amount': amount, 'reason': 'pegging'}, room=game)

    if just_won:
        emit('decorate_winner', {'player': player}, room=game)
        emit('new_message', {'type': 'chat', 'data': '{} wins!'.format(player), 'nickname': 'cribby'}, room=game)
        emit('send_turn', {'player': 'all', 'action': 'REMATCH'}, room=game)
        return True
    return False


def deal_extra_crib_card(game, card):
    emit('deal_extra_crib_card', {'card': card}, room=game)


def clear_pegging_area(game):
    emit('clear_pegging_area', room=game)


@socketio.on('join', namespace='/game')
def join(message):
    join_room(message['game'])
    emit('player_join', {'nickname': message['nickname'], 'points': 0, 'gameName': message['game']}, room=message['game'])


@socketio.on('leave', namespace='/game')
def leave(message):
    leave_room(message['game'])
    bev.remove_player(message['game'], message['nickname'])
    emit('player_leave', {'nickname': message['nickname'], 'gameName': message['game']}, room=message['game'])


@socketio.on('send_message', namespace='/game')
def send_message(message):

    if message['data'].startswith('/gif '):
        _, search_term = message['data'].split('/gif ')
        gif = cribby.find_gif(search_term) or 'Whoopsie!'
        emit('gif', {'nickname': message['nickname'], 'gif': gif}, room=message['game'])
        return
    elif message['data'].startswith('/') and ' ' in message['data']:
        type, request = message['data'].strip('/').split(' ')
        if type in {'blob', 'piggy', 'meow'}:
            found, known_animations = cribby.find_animation(type, request)
            if found:
                emit('animation', {'nickname': message['nickname'], 'type': type, 'instance': request}, room=message['game'])
            else:
                known = ', '.join(k for k in sorted(known_animations))
                msg = "Heyo! {}s I know about are: {}. <br /><b>*Only you can see this message*</b>".format(type, known)
                emit('new_message', {'type': 'chat', 'nickname': 'cribby', 'data': msg})
            return

    if message.get('private', '') == 'true':
        emit('new_message', {'type': 'chat', 'data': message['data'], 'nickname': message['nickname']})
    else:
        emit('new_message', {'type': 'chat', 'data': message['data'], 'nickname': message['nickname']}, room=message['game'])


@socketio.on('start_game', namespace='/game')
def start_game(msg):
    dealer, players = bev.start_game(msg['game'], msg['winningScore'], msg['jokers'])
    message = "First to {} wins! It's {}'s crib.".format(msg['winningScore'], dealer)
    if msg['jokers']:
        message += " We're playing with jokers."
    emit('new_message', {'type': 'chat', 'data': message, 'nickname': 'cribby'}, room=msg['game'])
    emit('start_game', {'dealer': dealer, 'players': players, 'winningScore': msg['winningScore']}, room=msg['game'])


@socketio.on('deal_hands', namespace='/game')
def deal_hands(msg):
    hands = bev.deal_hands(msg['game'])
    emit('deal_hands', {'hands': hands}, room=msg['game'])
    emit('send_turn', {'player': 'all', 'action': 'DISCARD'}, room=msg['game'])


@socketio.on('select_joker_for_hand', namespace='/game')
def select_joker_for_hand(msg):
    replacement, text = bev.set_joker(msg['game'], msg['joker'], msg['replacement'])
    emit('show_chosen_joker', {'player': msg['player'], 'joker': msg['joker'], 'replacement': replacement}, room=msg['game'])
    emit('new_message', {'type': 'chat', 'data': "{} got a joker! They've made it a {}.".format(msg['player'], text),
                              'nickname': 'cribby'}, room=msg['game'])


@socketio.on('select_joker_for_cut', namespace='/game')
def select_joker_for_cut(msg):
    replacement, text = bev.set_joker(msg['game'], msg['joker'], msg['replacement'])
    emit('show_cut_joker', {'player': msg['player'], 'replacement': replacement}, room=msg['game'])
    emit('new_message', {'type': 'chat', 'data': "The cut card is the {}.".format(text),
                              'nickname': 'cribby'}, room=msg['game'])


@socketio.on('discard', namespace='/game')
def discard(msg):
    """
    """
    player_done, all_done = bev.discard(msg['game'], msg['player'], msg["card"])
    emit('discard', {'card': msg['card'], 'nickname': msg['player'], 'done': player_done}, room=msg['game'])
    if all_done:
        cutter = bev.get_cutter(msg['game'])
        emit('send_turn', {'player': cutter, 'action': 'CUT'}, room=msg['game'])


@socketio.on('cut_deck', namespace='/game')
def cut_deck(msg):
    cut_card, turn, dealer = bev.cut_deck(msg['game'])
    emit('show_cut_card', {"cut_card": cut_card, 'turn': turn, 'dealer': dealer}, room=msg['game'])


@socketio.on('peg_round_action', namespace='/game')
def peg_round_action(msg):
    """
    Handles the playing of a card as well as passing on playing
    :param message:
    :return:
    """
    if 'card_played' in msg.keys():
        total = bev.get_pegging_total(msg['game'])
        if bev.get_card_value(msg['game'], msg['card_played']) > (31 - total):
            emit('invalid_card', {'card': msg['card_played']})
            return

        if msg['player'] != bev.get_current_turn(msg['game']):
            emit('invalid_card', {'card': msg['card_played']})
            return

        just_won, points_scored, points_source = bev.score_play(msg['game'], msg['player'], msg['card_played'])

        new_total = bev.record_play(msg['game'], msg['player'], msg['card_played'])
        card_text = card_text_from_id(msg['card_played'])
        message = '{} played {}. <b>({})</b>'.format(msg['player'], card_text, new_total)

        emit('new_message', {'type': 'action', 'data': message}, room=msg['game'])
        emit('show_card_played', {'nickname': msg['player'], 'card': msg['card_played']}, room=msg['game'])

        if points_scored > 0:
            reason = ', '.join(ps for ps in sorted(points_source))
            award_points(msg['game'], msg['player'], points_scored, reason, just_won)
        if just_won:
            return

    else:
        bev.record_pass(msg['game'], msg['player'])
        emit('new_message', {'type': 'action', 'data': '{} passed.'.format(msg['player'])}, room=msg['game'])

    next_player, go_point_wins = bev.next_player(msg['game'])
    if go_point_wins:
        return
    next_action = bev.get_player_action(msg['game'], next_player)
    if next_action == 'SCORE':
        emit('new_message', {'type': 'chat', 'data': "Time to score everyone's hand! {} goes first.".format(next_player), 'nickname': 'cribby'}, room=msg['game'])

    emit('send_turn', {'player': next_player, 'action': next_action}, room=msg['game'])


@socketio.on('score_hand', namespace='/game')
def score_hand(msg):
    points, next_to_score, just_won = bev.score_hand(msg['game'], msg['nickname'])
    emit('display_scored_hand', {'player': msg['nickname']}, room=msg['game'])

    if points == 0:
        emit('new_message', {'type': 'chat', 'data': "+0 for {} (from hand)".format(msg['nickname']), 'nickname': 'cribby'}, room=msg['game'])
        emit('new_message', {'type': 'chat', 'data': random.choice(cribby.ZERO_POINT_RESPONSES), 'nickname': 'cribby'}, room=msg['game'])
    elif points >= 11:
        emit('new_message', {'type': 'chat', 'data': random.choice(cribby.GREAT_HAND_RESPONSES), 'nickname': 'cribby'}, room=msg['game'])

    if just_won:
        return
    elif next_to_score:
        emit('new_message', {'type': 'chat', 'data': "Time to score {}'s hand..".format(next_to_score), 'nickname': 'cribby'}, room=msg['game'])
        emit('send_turn', {'player': next_to_score, 'action': 'SCORE'}, room=msg['game'])
    else:
        dealer = bev.get_dealer(msg['game'])
        emit('new_message', {'type': 'chat', 'data': "Time to score {}'s crib..".format(dealer), 'nickname': 'cribby'}, room=msg['game'])
        emit('send_turn', {'player': dealer, 'action': 'CRIB'}, room=msg['game'])


@socketio.on('score_crib', namespace='/game')
def score_crib(msg):
    dealer = bev.get_dealer(msg['game'])
    crib = bev.get_crib(msg['game'])
    emit('reveal_crib', {'dealer': dealer, 'crib': crib}, room=msg['game'])
    points, just_won = bev.score_crib(msg['game'], msg['nickname'])

    if points == 0:
        emit('new_message', {'type': 'score', 'data': "+0 for {} (from crib)".format(dealer), 'nickname': 'cribby'}, room=msg['game'])
        emit('new_message', {'type': 'chat', 'data': random.choice(cribby.ZERO_POINT_RESPONSES), 'nickname': 'cribby'}, room=msg['game'])
    elif points >= 9:
        emit('new_message', {'type': 'chat', 'data': random.choice(cribby.GREAT_HAND_RESPONSES), 'nickname': 'cribby'}, room=msg['game'])

    if just_won:
        return
    else:
        emit('send_turn', {'player': 'all', 'action': 'NEXT'}, room=msg['game'])


@socketio.on('end_round', namespace='/game')
def end_round(msg):
    all_have_ended = bev.end_round(msg['game'], msg['nickname'])
    if all_have_ended:
        dealer = bev.get_dealer(msg['game'])
        emit('clear_table', {'next_dealer': dealer}, room=msg['game'])
        message = "New round! It is now {}'s crib.".format(dealer)
        emit('new_message', {'type': 'chat', 'data': message, 'nickname': 'cribby'}, room=msg['game'])
        emit('send_turn', {'player': dealer, 'action': 'DEAL'}, room=msg['game'])


@socketio.on('play_again', namespace='/game')
def play_again(msg):
    all_want_to_play_again = bev.play_again(msg['game'], msg['nickname'])
    if all_want_to_play_again:
        winning_score, jokers = bev.reset_game_dict(msg['game'])
        emit('reset_table', room=msg['game'])
        dealer, players = bev.start_game(msg['game'], winning_score, jokers)
        emit('start_game', {'dealer': dealer, 'players': players, 'winningScore': winning_score}, room=msg['game'])
        message = "First to {} wins! It's {}'s crib to start.".format(winning_score, dealer)
        if jokers:
            message += " We're playing with jokers."
        emit('new_message', {'type': 'chat', 'data': message, 'nickname': 'cribby'}, room=msg['game'])


if __name__ == '__main__':
    socketio.run(app, debug=True)
