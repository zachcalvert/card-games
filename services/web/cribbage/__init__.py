#!/usr/bin/env python
import random
import time

from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context, Markup, redirect, url_for
from flask_fontawesome import FontAwesome
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from flask_sqlalchemy import SQLAlchemy

from .cards import CARDS

async_mode = None

app = Flask(__name__)
app.config.from_object("cribbage.config.Config")

db = SQLAlchemy(app)


HAND_SIZE = 6


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


@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        nickname = request.form.get('join_nickname')
        game_name = request.form['join_game_name']

        game = Game.query.filter_by(name=game_name).first()
        if game is None:
            game = Game(name=game_name)
            db.session.add(game)
            db.session.commit()

        player = Player.query.filter_by(nickname=nickname, game_id=game.id).first()
        if player is None:
            player = Player(nickname=nickname, game_id=game.id)
            db.session.add(player)
            db.session.commit()

        other_players = Player.query.filter(Player.game_id == game.id, Player.id != player.id)
        return render_template('game.html', game=game, player=player,
                               other_players=other_players, async_mode=socketio.async_mode)

    return redirect(url_for('index'))


@socketio.on('join', namespace='/game')
def join(message):
    join_room(message['game'])
    emit('player_join', {'nickname': message['nickname'], 'gameName': message['game']}, room=message['game'])


@socketio.on('leave', namespace='/game')
def leave(message):
    leave_room(message['game'])
    emit('player_leave',
         {'nickname': message['nickname'], 'gameName': message['game']}, room=message['game'])


@socketio.on('send_message', namespace='/game')
def send_message(message):
    emit('new_chat_message',
         {'data': message['data'], 'nickname': message['nickname']}, room=message['game'])


@socketio.on('deal_hands', namespace='/game')
def deal_hands(message):

    game = Game.query.filter_by(name=message['game']).first()

    hands = {}
    for player in game.players:
        hand = Hand(player_id=player.id, game_id=game.id)
        db.session.add(hand)
        db.session.commit()
        cards = [random.choice(CARDS)['fields'] for card in range(HAND_SIZE)]
        hands[player.nickname] = cards

    emit('deal_hands', {'hands': hands}, room=game.name)


if __name__ == '__main__':
    socketio.run(app, debug=True)
