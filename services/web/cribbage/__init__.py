#!/usr/bin/env python
import random

from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context, Markup
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from flask_sqlalchemy import SQLAlchemy

from .cards import CARDS

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config.from_object("cribbage.config.Config")
db = SQLAlchemy(app)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('join', namespace='/game')
def join(message):
    join_room(message['game'])
    emit('player_join',
         {'nickname': message['nickname'], 'gameName': message['game']})


@socketio.on('leave', namespace='/game')
def leave(message):
    leave_room(message['game'])
    emit('player_leave',
         {'nickname': message['nickname'], 'gameName': message['game']})


@socketio.on('player_action_announcement', namespace='/game')
def player_action_announcement(message):
    player = message['nickname']
    action = message['action']
    msg = '{} {}'.format(player, action)
    emit('player_action_announcement', {'data': msg}, room=message['game'])


@socketio.on('send_message', namespace='/game')
def send_message(message):
    emit('new_chat_message',
         {'data': message['data'], 'nickname': message['nickname']},
         room=message['game'])


@socketio.on('deal_card', namespace='/game')
def deal_card():
    session['receive_count'] = session.get('receive_count', 0) + 1
    card = random.choice(CARDS)
    value = Markup('<li><img class="playerCard" src="/static/img/{}" /></li>'.format(card['fields']['image']))
    emit('deal_card',
         {'data': value, 'count': session['receive_count']})


if __name__ == '__main__':
    socketio.run(app, debug=True)
