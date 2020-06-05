#!/usr/bin/env python
import random
import time

from threading import Lock
from flask import Flask, render_template, session, request, Markup, redirect, url_for, jsonify
from flask_fontawesome import FontAwesome
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
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
    state = db.Column(db.String(20), unique=False, nullable=False, default='INIT')

    def __init__(self, name, state='INIT'):
        self.name = name
        self.state = state


class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(128), unique=False, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    points = db.Column(db.Integer)

    def __init__(self, nickname, game_id):
        self.nickname = nickname
        self.game_id = game_id
        self.points = 0


class Hand(db.Model):
    __tablename__ = 'hands'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    state = db.Column(db.String(20), unique=False, nullable=False, default='DISCARDING')
    points = db.column(db.Integer)

    def __init__(self, player_id, game_id, state):
        self.player_id = player_id
        self.game_id = game_id
        self.state = state


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
        elif game.state == 'UNDERWAY' or game.state == 'FINISHED':
            pass
            # return redirect(url_for('index'))

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
    game = Game.query.filter_by(name=message['game']).first()
    player = Player.query.filter_by(nickname=message['nickname'], game_id=game.id).first()
    db.session.delete(player)
    db.session.commit()
    emit('player_leave',
         {'nickname': message['nickname'], 'gameName': message['game']}, room=message['game'])


@socketio.on('send_message', namespace='/game')
def send_message(message):
    emit('new_chat_message',
         {'data': message['data'], 'nickname': message['nickname']}, room=message['game'])


@socketio.on('start_game', namespace='/game')
def start_game(message):
    game = Game.query.filter_by(name=message['game']).first()
    game.state = 'UNDERWAY'
    db.session.add(game)
    db.session.commit()

    player_names = [player.nickname for player in game.players]

    emit('start_game', {'game': game.name, 'players': player_names}, room=game.name)


@socketio.on('deal_hands', namespace='/game')
def deal_hands(message):
    game = Game.query.filter_by(name=message['game']).first()

    deck = CARDS.copy()  # exclude the facedown card

    hands = {}
    for player in game.players:
        hand = Hand(player_id=player.id, game_id=game.id, state='DISCARDING')
        db.session.add(hand)
        db.session.commit()

        dealt_cards = [deck.pop(random.choice(list(deck.keys()))) for card in range(HAND_SIZE)]
        hands[player.nickname] = dealt_cards

    emit('deal_hands', {'hands': hands}, room=game.name)

    cut_card = random.choice(list(deck.keys()))
    emit('receive_cut_card', {'cut_card': cut_card}, room=game.name)


@socketio.on('discard', namespace='/game')
def discard(message):
    print('card_id is '.format(message["cardId"]))
    card_id = message['cardId']
    emit('post_discard', {'discarded': card_id, 'nickname': message['nickname']}, room=message['game'])


@socketio.on('ready_to_peg', namespace='/game')
def ready_to_peg(message):
    game = Game.query.filter_by(name=message['game']).first()
    player = Player.query.filter_by(nickname=message['nickname'], game_id=game.id).first()

    hand = Hand.query.filter_by(player_id=player.id, game_id=game.id, state='DISCARDING').first()
    hand.state = 'PEGGING'
    db.session.add(hand)
    db.session.commit()

    # if this game has no more Hands in a discarding state, dispatch the cut deck option
    if not Hand.query.filter_by(game_id=game.id, state='DISCARDING').first():
        emit('show_cut_deck_action', room=game.name)


@socketio.on('ready_to_score', namespace='/game')
def ready_to_score(message):
    game = Game.query.filter_by(name=message['game']).first()
    player = Player.query.filter_by(nickname=message['nickname'], game_id=game.id).first()

    hand = Hand.query.filter_by(player_id=player.id, game_id=game.id, state='PEGGING').first()
    hand.state = 'SCORING'
    db.session.add(hand)
    db.session.commit()

    # if this game has no more Hands in a pegging state, dispatch the score hands action
    if not Hand.query.filter_by(game_id=game.id, state='PEGGING').first():
        emit('show_score_hands_action', room=game.name)


@socketio.on('cut_deck', namespace='/game')
def cut_deck(message):
    game = Game.query.filter_by(name=message['game']).first()
    cut_card = CARDS[message["cut_card"]]
    emit('show_cut_card', {"cut_card": cut_card["image"]}, room=game.name)


@socketio.on('play_card', namespace='/game')
def play_card(message):
    print(" heard about a card to play: {}".format(message["cardId"]))
    card_played = CARDS[message["cardId"]]
    print('card is {}'.format(card_played))
    emit('show_card_played', {"card_id": message["cardId"], "card_image": card_played["image"]}, room=message["game"])


if __name__ == '__main__':
    socketio.run(app, debug=True)
