import json
import logging
import random
import redis

from itertools import chain, combinations
import more_itertools as mit

from cribbage.cards import CARDS
from cribbage.utils import rotate_turn, play_or_pass

cache = redis.Redis(host='redis', port=6379)
logger = logging.getLogger(__name__)


class Bev:
    """
    Beverley manages the state of the game and all the cache interactions.
    """
    @staticmethod
    def get_game(name):
        try:
            return json.loads(cache.get(name))
        except TypeError:
            return None

    @staticmethod
    def setup_game(name, player):
        g = {
            "name": name,
            "state": "INIT",
            "players": {player: {'nickname': player, 'points': 0}},
        }
        cache.set(name, json.dumps(g))
        return g

    @staticmethod
    def add_player(game, player):
        g = json.loads(cache.get(game))

        if g["state"] != 'INIT':
            pass  # maybe return False or something

        g['players'][player] = {'nickname': player, 'points': 0}
        cache.set(game, json.dumps(g))
        return g

    @staticmethod
    def remove_player(game, player):
        g = json.loads(cache.get(game))
        g['players'].pop(player)
        cache.set(game, json.dumps(g))

    @staticmethod
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


    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def get_cutter(game):
        g = json.loads(cache.get(game))
        return g['cutter']

    @staticmethod
    def cut_deck(game):
        from cribbage.app import award_points
        g = json.loads(cache.get(game))
        g['cut_card'] = g['deck'].pop()
        g['state'] = 'PLAYING'

        if g['cut_card'] in ['56594b3880', '95f92b2f0c', '1d5eb77128', '110e6e5b19']:
            g['players'][g['dealer']]['points'] += 2
            award_points(game, g['dealer'], 2, g['players'][g['dealer']]['points'])

        cache.set(game, json.dumps(g))
        return g['cut_card'], g['turn']

    @staticmethod
    def get_pegging_total(game):
        g = json.loads(cache.get(game))
        return g['pegging']['total']

    @staticmethod
    def score_play(game, player, card):
        from cribbage.app import award_points, clear_pegging_area

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

        if (g['pegging']['total'] + card_played['value']) in [15, 31]:
            points += 2

        if points > 0:
            g['players'][player]['points'] += points
            award_points(game, player, points, g['players'][player]['points'])

        cache.set(game, json.dumps(g))

    @staticmethod
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

    @staticmethod
    def record_pass(game, player):
        g = json.loads(cache.get(game))
        g['pegging']['passed'].append(player)
        cache.set(game, json.dumps(g))

    @staticmethod
    def next_player_and_action(game):
        from cribbage.app import award_points, clear_pegging_area

        g = json.loads(cache.get(game))
        player_order = list(g['players'].keys())
        starting_point = player_order.index(g['turn'])
        players_to_check_in_order = player_order[starting_point + 1:] + player_order[:starting_point + 1]
        def _clear_pegging_data():
            g['pegging'].update({
                'cards': [],
                'last_played': '',
                'passed': [],
                'run': [],
                'total': 0
            })

        def _next_player_for_this_round():
            for player in players_to_check_in_order:
                if g['pegging']['total'] == 31:
                    return None

                print('checking {}'.format(player))
                if g['hands'][player] and player not in g['pegging']['passed'] and player != g['pegging']['last_played']:
                    return player

                card_values = [CARDS[card]['value'] for card in g['hands'][player]]
                if play_or_pass(card_values, g['pegging']['total']) == 'PLAY':
                    return player

            if g['pegging']['total'] != 31:  # player will get their two points for 31 during score_play()
                g['players'][g['pegging']['last_played']]['points'] += 1
                award_points(game, player, 1, g['players'][g['pegging']['last_played']]['points'])
            return None

        def _next_player_who_has_cards():
            clear_pegging_area(game)
            _clear_pegging_data()
            for player in players_to_check_in_order:
                if g['hands'][player]:  # has cards left
                    return player
            return None

        next_player = _next_player_for_this_round() or _next_player_who_has_cards()
        if next_player:
            card_values = [CARDS[card]['value'] for card in g['hands'][next_player]]
            next_action = play_or_pass(card_values, g['pegging']['total'])
        else:
            next_player = g['first_to_score']
            next_action = 'SCORE'

        g['turn'] = next_player
        cache.set(game, json.dumps(g))
        return next_player, next_action
