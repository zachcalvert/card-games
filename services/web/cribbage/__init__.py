#!/usr/bin/env python
import random

from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context, Markup
from flask_fontawesome import FontAwesome
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from flask_sqlalchemy import SQLAlchemy

from .cards import CARDS

async_mode = None

app = Flask(__name__)
app.config.from_object("cribbage.config.Config")

db = SQLAlchemy(app)


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=False, nullable=False)
    players = db.relationship('Player', backref='games', lazy=True)

    def __init__(self, name):
        self.name = name


class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(128), unique=False, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)

    def __init__(self, nickname, game_id):
        self.nickname = nickname
        self.game_id = game_id


class Hand(db.Model):
    __tablename__ = 'hands'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    state = db.Column(db.String(20), unique=False, nullable=False, default='DISCARDING')


fa = FontAwesome(app)

socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('join', namespace='/game')
def join(message):
    join_room(message['game'])

    game = Game.query.filter_by(name=message['game']).first()
    if game is None:
        game = Game(name=message['game'])
        db.session.add(game)
        db.session.commit()

    player = Player.query.filter_by(nickname=message['nickname'], game_id=game.id).first()
    if player is None:
        player = Player(nickname=message['nickname'], game_id=game.id)
        db.session.add(player)
        db.session.commit()

    emit('player_join', {'nickname': player.nickname, 'gameName': game.name}, room=game.name)


@socketio.on('leave', namespace='/game')
def leave(message):
    leave_room(message['game'])

    game = Game.query.filter_by(name=message['game']).first()
    player = Player.query.filter_by(nickname=message['nickname'], game_id=game.id).first()
    if player is not None:
        db.session.delete(player)
        db.session.commit()

    emit('player_leave',
         {'nickname': message['nickname'], 'gameName': message['game']})


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
