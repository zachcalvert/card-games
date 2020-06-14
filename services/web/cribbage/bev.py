"""
Beverley manages the state of the game and all the cache interactions.
"""

import json
import logging
import random
import redis

from itertools import chain, combinations
import more_itertools as mit

from cribbage.cards import CARDS
from cribbage.scoring import Hand
from cribbage.utils import rotate_turn, play_or_pass

cache = redis.Redis(host='redis', port=6379)
logger = logging.getLogger(__name__)


def get_game(name):
    try:
        return json.loads(cache.get(name))
    except TypeError:
        return None


def setup_game(name, player):
    g = {
        "name": name,
        "state": "INIT",
        "players": {player: {'nickname': player, 'points': 0}},
    }
    cache.set(name, json.dumps(g))
    return g


def add_player(game, player):
    g = json.loads(cache.get(game))

    if g["state"] != 'INIT':
        pass  # maybe return False or something

    g['players'][player] = {'nickname': player, 'points': 0}
    cache.set(game, json.dumps(g))
    return g


def remove_player(game, player):
    g = json.loads(cache.get(game))
    g['players'].pop(player)
    cache.set(game, json.dumps(g))


def start_game(game):
    g = json.loads(cache.get(game))
    players = list(g['players'].keys())
    dealer = random.choice(players)
    first_to_score = rotate_turn(dealer, players)
    g.update({
        'state': 'DEAL',
        'dealer': dealer,
        'cutter': first_to_score,
        'first_to_score': first_to_score,
        'deck': [],
        'hand_size': 6 if len(players) <= 2 else 5,
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

    cache.set(game, json.dumps(g))
    return g['dealer']


def deal_hands(game):
    g = json.loads(cache.get(game))
    deck = list(CARDS.keys())
    random.shuffle(deck)

    for player in g["players"].keys():
        dealt_cards = [deck.pop() for card in range(g['hand_size'])]
        g['hands'][player] = dealt_cards

    g['state'] = 'DISCARD'
    g['deck'] = deck
    cache.set(game, json.dumps(g))
    return g['hands']


def discard(game, player, card):
    g = json.loads(cache.get(game))

    g['hands'][player].remove(card)
    g['crib'].append(card)

    player_done = len(g['hands'][player]) == 4
    all_done = all(len(g['hands'][nickname]) == 4 for nickname, _ in g['players'].items())
    if all_done:
        g['state'] = 'CUT'

    cache.set(game, json.dumps(g))
    return player_done, all_done


def get_cutter(game):
    g = json.loads(cache.get(game))
    return g['cutter']


def get_dealer(game):
    g = json.loads(cache.get(game))
    return g['dealer']


def get_current_turn(game):
    g = json.loads(cache.get(game))
    return g['turn']


def cut_deck(game):
    from cribbage.app import award_points
    just_won = False

    g = json.loads(cache.get(game))
    g['cut_card'] = g['deck'].pop()
    g['state'] = 'PLAYING'

    if g['cut_card'] in ['56594b3880', '95f92b2f0c', '1d5eb77128', '110e6e5b19']:
        g['players'][g['dealer']]['points'] += 2
        just_won = award_points(game, g['dealer'], 2, g['players'][g['dealer']]['points'])

    cache.set(game, json.dumps(g))
    return g['cut_card'], g['turn'], just_won


def get_pegging_total(game):
    g = json.loads(cache.get(game))
    return g['pegging']['total']


def score_play(game, player, card):
    from cribbage.app import award_points, clear_pegging_area

    just_won = False
    g = json.loads(cache.get(game))
    card_played = CARDS[card]
    cards_on_table = [CARDS.get(card) for card in g['pegging']['cards']]
    points = 0

    def _is_run(ranks):
        groups = [list(group) for group in mit.consecutive_groups(ranks)]
        if any(len(group) == len(ranks) for group in groups):
            return True
        return False

    if cards_on_table:
        if g['pegging']['run']:   # Is there already a run going? If so, try to add to it
            ranks = sorted([rank for rank in g['pegging']['run']] + [card_played['rank']])
            run_is_continued = _is_run(ranks)
            g['pegging']['run'] = ranks if run_is_continued else []
            points += len(g['pegging']['run'])
        elif len(cards_on_table) >= 2:  # or maybe this card has started a new run
            ranks = sorted([card['rank'] for card in cards_on_table[:2]] + [card_played['rank']])
            g['pegging']['run'] = ranks if _is_run(ranks) else []
            points += len(g['pegging']['run'])

        ranks = [card['rank'] for card in cards_on_table]  # evaluate for pairs, threes, and fours
        for count, rank in enumerate(ranks, 1):
            if card_played['rank'] == rank:
                points += count*2
            else:
                break

    if (g['pegging']['total'] + card_played['value']) in [15, 31]:
        points += 2

    if points > 0:
        g['players'][player]['points'] += points
        just_won = award_points(game, player, points, g['players'][player]['points'])

    cache.set(game, json.dumps(g))
    return just_won


def record_play(game, player, card):
    g = json.loads(cache.get(game))
    value = CARDS[card]['value']
    g['hands'][player].remove(card)
    g['played_cards'][player].append(card)
    g['pegging']['cards'].insert(0, card)
    g['pegging']['last_played'] = player
    g['pegging']['total'] += value
    cache.set(game, json.dumps(g))
    return g['pegging']['total']


def record_pass(game, player):
    g = json.loads(cache.get(game))
    g['pegging']['passed'].append(player)
    cache.set(game, json.dumps(g))


def next_player_for_this_round(players_to_check_in_order, hands, passed_list):
    """
    Find the next player who still has cards and has not passed
    :param players_to_check_in_order:
    :param hands:
    :param passed_list:
    :return:
    """
    for player in players_to_check_in_order:
        if hands[player] and player not in passed_list:
            return player
    return None


def next_player_who_has_cards(players_to_check_in_order, hands):
    """
    Find the next player who still has cards
    """
    for player in players_to_check_in_order:
        if hands[player]:
            return player
    return None


def next_player(game):
    from cribbage.app import award_points, clear_pegging_area

    just_won = False
    g = json.loads(cache.get(game))
    player_order = list(g['players'].keys())
    starting_point = player_order.index(g['turn'])
    players_to_check_in_order = player_order[starting_point + 1:] + player_order[:starting_point + 1]

    if g['pegging']['total'] == 31:
        if g['hands'][g['pegging']['last_played']]:  # if the person who hit 31 still has cards, it's their turn
            next = g['pegging']['last_played']
        else:
            next = next_player_who_has_cards(players_to_check_in_order, g['hands'])
        g['pegging'].update({
            'cards': [],
            'last_played': '',
            'passed': [],
            'run': [],
            'total': 0
        })
    else:
        next = next_player_for_this_round(players_to_check_in_order, g['hands'], g['pegging']['passed'])
        # if no one can play this round, award the last to play one point and look for the next player with cards
        if not next:
            last_played = g['pegging']['last_played']
            g['players'][last_played]['points'] += 1
            just_won = award_points(game, last_played, 1, g['players'][last_played]['points'])
            if g['hands'][last_played]:
                next = last_played
            else:
                next = next_player_who_has_cards(players_to_check_in_order, g['hands'])
            g['pegging'].update({
                'cards': [],
                'last_played': '',
                'passed': [],
                'run': [],
                'total': 0
            })

    if not next:
        next = g['first_to_score']
        g['state'] = 'SCORE'

    g['turn'] = next
    cache.set(game, json.dumps(g))
    return next, just_won


def get_player_action(game, player):
    g = json.loads(cache.get(game))
    if g['state'] == 'SCORE':
        next_action = 'SCORE'
    else:
        if g['pegging']['total'] == 31:
            return 'PLAY'
        card_values = [CARDS[card]['value'] for card in g['hands'][player]]
        next_action = play_or_pass(card_values, g['pegging']['total'])

    cache.set(game, json.dumps(g))
    return next_action


def score_hand(game, player):
    from cribbage.app import award_points
    next_to_score = None

    g = json.loads(cache.get(game))
    player_cards = g['played_cards'][player]
    hand = Hand(player_cards, g['cut_card'])
    hand_points = hand.calculate_points()

    g['players'][player]['points'] += hand_points
    just_won = award_points(game, player, hand_points, g['players'][player]['points'])

    g['scored_hands'].append(player)
    cache.set(game, json.dumps(g))

    if set(g['scored_hands']) != set(g['players'].keys()):
        next_to_score = rotate_turn(player, list(g['players'].keys()))
    return next_to_score, just_won


def score_crib(game, player):
    from cribbage.app import award_points

    g = json.loads(cache.get(game))
    crib = Hand(g['crib'], g['cut_card'], is_crib=True)
    crib_points = crib.calculate_points()
    g['players'][player]['points'] += crib_points
    just_won = award_points(game, player, crib_points, g['players'][player]['points'])
    cache.set(game, json.dumps(g))
    return just_won


def end_round(game, player):
    g = json.loads(cache.get(game))
    g['ok_with_next_round'].append(player)
    cache.set(game, json.dumps(g))

    all_have_ended = False
    if set(g['ok_with_next_round']) == set(g['players'].keys()):
        all_have_ended = True
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
        cache.set(game, json.dumps(g))

    return all_have_ended


def play_again(game, player):
    g = json.loads(cache.get(game))
    g['play_again'].append(player)
    cache.set(game, json.dumps(g))

    if set(g['play_again']) == set(g['players'].keys()):
        return True
    return False


def reset_game_dict(game):
    g = json.loads(cache.get(game))
    players = list(g['players'].keys())
    game_dict = {
        'players': {},
        "name": game,
        "state": "INIT",
    }
    for player in players:
        game_dict['players'][player] = {'nickname': player, 'points': 0}

    cache.set(game, json.dumps(game_dict))

