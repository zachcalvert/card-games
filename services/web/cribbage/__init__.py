#!/usr/bin/env python
import json
import random
import redis

from threading import Lock
from flask import Flask, render_template, session, request, Markup, redirect, url_for, jsonify
from flask_fontawesome import FontAwesome
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect

from cribbage.cards import CARDS
from cribbage.scoring import PlayScorer, Hand
from cribbage.utils import rotate_turn, play_or_pass, next_player_who_can_play_at_all, \
    next_player_who_can_take_action_this_round

async_mode = None

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)
fa = FontAwesome(app)
socketio = SocketIO(app, async_mode=async_mode)


thread = None
thread_lock = Lock()

POINTS_TO_WIN = 10


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
        return render_template('game.html', game=g, player=g['players'][nickname],
                               other_players=other_players, async_mode=socketio.async_mode)

    return redirect(url_for('index'))


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
        dealt_cards = [deck.pop() for card in range(g['hand_size'])]
        g['hands'][player] = dealt_cards

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

    done_discarding = False
    if len(g['hands'][discarder]) == 4:
        done_discarding = True

    emit('post_discard', {'discarded': card, 'nickname': discarder, 'done_discarding': done_discarding}, room=message['game'])

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
        emit('send_turn', {'player': cutter, 'action': 'CUT'}, room=message['game'])

    cache.set(message['game'], json.dumps(g))


@socketio.on('cut_deck', namespace='/game')
def cut_deck(message):
    g = json.loads(cache.get(message['game']))
    g['cut_card'] = g['deck'].pop()

    if g['cut_card'] in ['56594b3880', '95f92b2f0c', '1d5eb77128', '110e6e5b19']:
        player = g['dealer']
        g['players'][player]['points'] += 2
        msg = 'A Jack! 2 points for {}.'.format(g['dealer'])
        emit('new_chat_message', {'data': msg, 'nickname': 'cribbot'}, room=message['game'])
        emit('award_points', {'player': player, 'amount': 2, 'reason': 'Cutting a Jack'}, room=message['game'])

        if g['players'][player]['points'] >= POINTS_TO_WIN:
            g['winner'] = player
            emit('new_chat_message', {'data': '{} points! {} wins!'.format(POINTS_TO_WIN, player), 'nickname': 'cribbot'},
                 room=message['game'])
            emit('send_turn', {'player': 'all', 'action': 'PLAY AGAIN'}, room=message['game'])

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

        # make sure it's a valid card
        if CARDS.get(card_played)['value'] > 31 - g['pegging']['total']:
            emit('invalid_card', {'card': card_played})
            return

        # score play
        scorer = PlayScorer(card_played, g['pegging']['cards'], g['pegging']['run'], g['pegging']['total'])
        points_scored, new_total, run = scorer.calculate_points()

        # record play
        g['hands'][player].remove(card_played)
        g['played_cards'][player].append(card_played)
        g['pegging']['cards'].insert(0, card_played)
        g['pegging']['last_played'] = player
        g['pegging']['total'] = new_total

        if run:
            g['pegging']['run'] = run

        # show card getting played
        emit('show_card_played', {'nickname': message['nickname'], 'card': card_played, 'new_total': new_total}, room=message['game'])
        if points_scored > 0:
            msg = '{} scored {} from play'.format(player, points_scored)
            emit('new_chat_message', {'data': msg, 'nickname': 'cribbot'}, room=message['game'])

            g['players'][message['nickname']]['points'] += points_scored
            emit('award_points', {'player': player, 'amount': points_scored, 'reason': 'pegging'}, room=message['game'])

            if g['players'][player]['points'] >= POINTS_TO_WIN:
                g['winner'] = player
                emit('new_chat_message', {'data': '{} points! {} wins!'.format(POINTS_TO_WIN, player), 'nickname': 'cribbot'},
                     room=message['game'])
                emit('send_turn', {'player': 'all', 'action': 'PLAY AGAIN'}, room=message['game'])
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
        emit('send_turn', {'player': next_player, 'action': next_action}, room=message['game'])
    else:
        # award a point to current player for go (if they didn't already get em for 31) and reset
        if g['pegging']['total'] == 31:
            g['players'][message['nickname']]['points'] += 2
            msg = '{} scores 2 for 31'.format(g['pegging']['last_played'])
            emit('new_chat_message', {'data': msg, 'nickname': 'cribbot'}, room=message['game'])
            emit('award_points', {'player': g['pegging']['last_played'], 'amount': 2, 'reason': '31'}, room=message['game'])
        else:
            g['players'][message['nickname']]['points'] += 1
            msg = '{} gets 1 for go'.format(g['pegging']['last_played'])
            emit('new_chat_message', {'data': msg, 'nickname': 'cribbot'}, room=message['game'])
            emit('award_points', {'player': g['pegging']['last_played'], 'amount': 1, 'reason': 'go'}, room=message['game'])

        # clear the board
        emit('clear_pegging_area', room=message['game'])
        g['pegging'].update({
            'cards': [],
            'last_played': '',
            'passed': [],
            'run': [],
            'total': 0
        })
        next_player = next_player_who_can_play_at_all(g)
        if next_player:
            g['turn'] = next_player
            emit('send_turn', {'player': next_player, 'action': 'PLAY'}, room=message['game'])
        else:
            # nobody has any cards left
            g['turn'] = g['first_to_score']
            emit('send_turn', {'player': g['first_to_score'], 'action': 'SCORE'}, room=message['game'])

    # write next player to cache
    cache.set(message['game'], json.dumps(g))
    return


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
