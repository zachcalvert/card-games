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

from app import frank, penny

async_mode = None

pinochle = Flask(__name__)

FontAwesome(pinochle)
socketio = SocketIO(pinochle, async_mode=async_mode)

thread = None
thread_lock = Lock()


@pinochle.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@pinochle.route('/game', methods=['GET', 'POST'])
def game_detail():
    if request.method == 'POST':
        game_name = request.form['join_game_name']
        player = request.form.get('join_nickname')

        if not (game_name and player):
            return redirect(url_for('index'))

        game = frank.get_game(game_name)
        if not game:
            game = frank.setup_game(name=game_name, player=player)

        if player not in game["players"]:
            game = frank.add_player(game_name, player)

        player_points = game['players'].pop(player)

        return render_template('game.html', game=game, player_name=player, player_points=player_points,
                               opponents=game['players'], async_mode=socketio.async_mode)

    return redirect(url_for('index'))


@socketio.on('join', namespace='/game')
def join(message):
    join_room(message['game'])
    emit('player_join', {'nickname': message['nickname'], 'points': 0, 'gameName': message['game']}, room=message['game'])


@socketio.on('leave', namespace='/game')
def leave(message):
    leave_room(message['game'])
    frank.remove_player(message['game'], message['nickname'])
    emit('player_leave', {'nickname': message['nickname'], 'gameName': message['game']}, room=message['game'])


@socketio.on('send_message', namespace='/game')
def send_message(message):

    if message['data'].startswith('/gif '):
        _, search_term = message['data'].split('/gif ')
        gif = penny.find_gif(search_term) or 'Whoopsie!'
        emit('gif', {'nickname': message['nickname'], 'gif': gif}, room=message['game'])
        return
    elif message['data'].startswith('/') and ' ' in message['data']:
        type, request = message['data'].strip('/').split(' ')
        if type in {'blob', 'piggy', 'meow'}:
            found, known_animations = penny.find_animation(type, request)
            if found:
                emit('animation', {'nickname': message['nickname'], 'type': type, 'instance': request}, room=message['game'])
            else:
                known = ', '.join(k for k in sorted(known_animations))
                msg = "Heyo! {}s I know about are: {}. <br /><b>*Only you can see this message*</b>".format(type, known)
                emit('new_message', {'type': 'chat', 'nickname': 'penny', 'data': msg})
            return

    if message.get('private', '') == 'true':
        emit('new_message', {'type': 'chat', 'data': message['data'], 'nickname': message['nickname']})
    else:
        emit('new_message', {'type': 'chat', 'data': message['data'], 'nickname': message['nickname']}, room=message['game'])


@socketio.on('start_game', namespace='/game')
def start_game(msg):
    dealer = frank.start_game(msg['game'])
    emit('new_message', {'type': 'chat', 'data': 'Here we go!', 'nickname': 'cribby'}, room=msg['game'])
    emit('start_game', {'dealer': dealer}, room=msg['game'])


@socketio.on('deal_hands', namespace='/game')
def deal_hands(msg):
    hands = frank.deal_hands(msg['game'])
    emit('deal_hands', {'hands': hands}, room=msg['game'])
    emit('send_turn', {'player': 'all', 'action': 'BID'}, room=msg['game'])


if __name__ == '__main__':
    socketio.run(pinochle, debug=True)
