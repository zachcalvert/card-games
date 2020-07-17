"""
Frank manages the state of the game and all the cache interactions.
"""
import json
import logging
import os
import random
import redis
import time

from itertools import chain, combinations
import more_itertools as mit

from app.cards import CARDS
from app.hand import Hand

redis_host = os.environ.get('REDISHOST', 'localhost')
cache = redis.StrictRedis(host=redis_host, port=6379)

logger = logging.getLogger(__name__)


def get_game(name):
    try:
        return json.loads(cache.get(name))
    except TypeError:
        return None


def get_cutter(game):
    g = json.loads(cache.get(game))
    return g['cutter']


def get_dealer(game):
    g = json.loads(cache.get(game))
    return g['dealer']


def get_current_turn(game):
    g = json.loads(cache.get(game))
    return g['turn']


def get_card_value(game, card_id):
    g = json.loads(cache.get(game))
    card = g['cards'][card_id]
    return card['value']


def setup_game(name, player):
    g = {
        "name": name,
        "state": "INIT",
        "players": {player: 0}
    }
    cache.set(name, json.dumps(g))
    return g


def add_player(game, player):
    g = json.loads(cache.get(game))

    if g["state"] != 'INIT':
        pass  # maybe return False or something

    g['players'][player] = 0
    cache.set(game, json.dumps(g))
    return g


def remove_player(game, player):
    g = json.loads(cache.get(game))
    g['players'].pop(player)
    if len(g['players']) == 0:
        cache.delete(game)
    else:
        cache.set(game, json.dumps(g))


def start_game(game, teams={}):
    g = json.loads(cache.get(game))
    players = list(g['players'].keys())
    dealer = random.choice(players)
    g.update({
        'bid': {},
        'dealer': dealer,
        'deck': list(CARDS.keys()),
        'hands': {},
        'ok_with_next_round': [],
        'play': {
            'lead': [],
            'played': {},
            'passed': [],
            'tricks': [],
        },
        'play_again': [],
        'played_cards': {},
        'state': 'DEAL',
        'teams': teams,
        'turn': dealer,
    })
    for player in players:
        g['played_cards'][player] = []

    cache.set(game, json.dumps(g))
    return g['dealer']


def _sort_cards(cards):
    """
    spades, diamonds, clubs, hearts
    """
    card_keys_and_values = [{card: CARDS.get(card)} for card in cards]
    ascending_card_ids = []
    for suit in ['clubs', 'diamonds', 'spades', 'hearts']:
        ascending_suit_dicts = sorted((b for b in card_keys_and_values if next(iter(b.items()))[1]['suit'] == suit), key=lambda x: (x[list(x)[0]]['rank']))
        ascending_suit_ids = [list(card_dict.keys())[0] for card_dict in ascending_suit_dicts]
        ascending_card_ids.extend(ascending_suit_ids)
    return ascending_card_ids


def deal_hands(game):
    g = json.loads(cache.get(game))

    random.shuffle(g['deck'])

    for player in g["players"].keys():
        dealt_cards = [g['deck'].pop() for card in range(12)]
        g['hands'][player] = _sort_cards(dealt_cards)

    g['state'] = 'BID'
    cache.set(game, json.dumps(g))
    return g['hands']


def bid(game, player, points):
    pass