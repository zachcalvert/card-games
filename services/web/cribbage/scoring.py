from itertools import chain, combinations
import more_itertools as mit
import random

from .cards import CARDS


class PlayScorer:
    def __init__(self, card, previously_played_cards, running_total):
        self.card = card
        self.previously_played_cards = previously_played_cards
        self.running_total = int(running_total)

    def calculate_points(self):
        print("calculating points..")
        points = 0

        new_total = self.running_total + self.card["value"]
        print("new total is: {}".format(new_total))
        if new_total == 15:
            points += 2
        elif new_total == 31:
            points += 2

        if self.previously_played_cards:

            for count, _ in enumerate(self.previously_played_cards):
                card = CARDS.get(self.previously_played_cards[count])
                if self.card["rank"] == card["rank"]:
                    if count == 0:
                        points += 2
                        print('found a pair')
                    elif count == 1:
                        print('found three of a kind')
                        points += 4
                    elif count == 2:
                        print('found four of a kind')
                        points += 6

        return points, new_total


class HandScorer:

    def __init__(self, cards={}, cut_card={}, is_crib=False):
        self.cards = cards
        self.cut_card = cut_card
        self.is_crib = True

        self.fifteens = {}
        self.pairs = None
        self.run = None
        self.flush_points = 0
        self.nobs = False

    def __str__(self):
        s = ''
        for card in self.cards.items():
            s += (str(card) + ", ")
        return s

    def _power_hand(self, values):
        """
        Given a hand of 5 cards (or 4 or 6..) this method creates every
        possible combination of the cards of that hand.
        Useful for counting 15's.
        ***modified from: docs.python.org/2/library/itertools.html***
        Returns a list of tuples of each possible card combination.
        """
        assert type(values) == list
        ch = chain.from_iterable(combinations(values, r) for r in range(len(values) + 1))
        return list(ch)

    def _sum_cards(self, cards):
        """
        This method takes a hand of any length and adds the values of each card.
        Useful for counting 15's.
        Returns an int of the sum of all the cards' values
        """
        hand_sum = 0
        for card in cards:
            hand_sum += card
        return hand_sum

    def _has_fifteens(self):
        """
        Takes a hand of 5 cards, counts all ways those cards can add up to 15.
        Returns the number of points from 15s.
        """
        counter = 2
        values = sorted([card["value"] for _, card in self.cards.items()] + [self.cut_card["value"]])
        all_combos = self._power_hand(values)
        for combo in all_combos:
            if self._sum_cards(combo) == 15:
                print('{} add up to 15'.format(combo))
                self.fifteens[counter] = combo
                counter += 2

        return self.fifteens != {}

    def _has_pairs(self):
        ranks = [card["rank"] for _, card in self.cards.items()] + [self.cut_card["rank"]]
        pairs = {rank: ranks.count(rank) for rank in ranks if ranks.count(rank) > 1}
        if pairs:
            self.pairs = pairs
            return True
        return False

    def _has_runs(self):
        ranks = [card["rank"] for _, card in self.cards.items()] + [self.cut_card["rank"]]
        groups = [list(group) for group in mit.consecutive_groups(ranks)]
        for group in groups:
            if len(group) > 2:
                self.run = group
                return True
        return False

    def _has_flush(self):

        def _cut_card_matches_hand():
            return self.cut_card["suit"] == next(iter(self.cards.values()))["suit"]

        if all(card["suit"] == next(iter(self.cards.values()))["suit"] for _, card in self.cards.items()()):
            if self.is_crib:
                if _cut_card_matches_hand():
                    self.flush_points = 5
                    return True
                return False

            if _cut_card_matches_hand():
                self.flush_points = 5
            else:
                self.flush_points = 4
            return True
        return False

    def _has_nobs(self):
        jacks = [card for k, card in self.cards.items() if card["name"] == 'Jack']
        if jacks:
            potential_nobs = [jack["suit"] for jack in jacks]
            if self.cut_card["suit"] in potential_nobs:
                self.nobs = True
                return True
        return False

    def calculate_points(self):
        points = 0

        if self._has_fifteens():
            print('found some fifteens')
            for fifteen in self.fifteens:
                points += 2

        if self._has_pairs():
            print('found some pairs')
            for pair in self.pairs:
                print('One pair is: {}'.format(pair))
                count = self.pairs.get(pair)
                if count == 4:
                    points += 12
                elif count == 3:
                    points += 6
                else:
                    points += 2

        if self._has_runs():
            print('found a run')
            points += len(self.run)

        if self._has_flush():
            print('found a flush')
            points += self.flush_points

        if self._has_nobs():
            print('Nobs!')
            points += 1

        return points
