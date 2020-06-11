from itertools import chain, combinations
import more_itertools as mit

from cribbage.cards import CARDS


class PlayScorer:
    def __init__(self, card, previously_played_cards, run, total):
        self.card = CARDS.get(card)
        self.previously_played_cards = [CARDS.get(card_id) for card_id in previously_played_cards]
        self.run = run
        self.total = int(total)

    def calculate_points(self):
        """
        Runs and pairs/threes/fours are mutually exclusive in the ry
        :return:
        """
        print("calculating points..")
        points = 0

        new_total = self.total + self.card["value"]
        if new_total == 15:
            points += 2

        if self.previously_played_cards:
            print('previously played cards: {}'.format(self.previously_played_cards))

            # evaluate pairs, threes, and fours
            most_recent = self.previously_played_cards[0]
            if self.card['rank'] == most_recent['rank']:
                if len(self.previously_played_cards) > 1:
                    if self.card['rank'] == self.previously_played_cards[1]['rank']:
                        if len(self.previously_played_cards) > 2:
                            if self.card['rank'] == self.previously_played_cards[2]['rank']:
                                print('four of a kind!')
                                points += 12
                                return points, new_total, []
                        print('three of a kind!')
                        points += 6
                        return points, new_total, []
                print('a pair!')
                points += 2
                return points, new_total, []

            # Is there already a run going? If so, see if this one has added to it
            if self.run:
                pass

            # or, has this card itself made a run
            elif len(self.previously_played_cards) == 2:
                # just get the most recent 2 played
                ranks = sorted([card["rank"] for card in self.previously_played_cards[:2]] + [self.card["rank"]])
                groups = [list(group) for group in mit.consecutive_groups(ranks)]
                for group in groups:
                    if len(group) > 2:
                        self.run = group
                        points += len(group)
                        continue

        return points, new_total, self.run


class Hand:
    def __init__(self, cards, cut_card, is_crib=False):
        self.cards = [CARDS.get(card_id) for card_id in cards]
        self.cut_card = CARDS.get(cut_card)
        self.is_crib = is_crib

        self.fifteens = {}
        self.pairs = None
        self.runs = []
        self.flush_points = 0
        self.nobs = False

    def __str__(self):
        s = ''
        for card in self.cards:
            s += (card['name'] + card['suit'] + ", ")
        s += "{}{}".format(self.cut_card['name'], self.cut_card['suit'])
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
        values = sorted([card["value"] for card in self.cards] + [self.cut_card["value"]])
        all_combos = self._power_hand(values)
        for combo in all_combos:
            if self._sum_cards(combo) == 15:
                self.fifteens[counter] = combo
                counter += 2

        return self.fifteens != {}

    def _has_pairs(self):
        ranks = [card["rank"] for card in self.cards] + [self.cut_card["rank"]]
        pairs = {rank: ranks.count(rank) for rank in ranks if ranks.count(rank) > 1}
        if pairs:
            self.pairs = pairs
            return True
        return False

    def _has_runs(self):
        ranks = sorted([card["rank"] for card in self.cards] + [self.cut_card["rank"]])
        distinct_ranks = sorted(list(set(ranks)))

        # print('the ranks are: {}'.format(ranks))
        groups = [list(group) for group in mit.consecutive_groups(distinct_ranks)]
        # print('the groups are: {}'.format(groups))
        for group in groups:
            if len(group) > 2:
                multiples = False
                # print('this group has at least three cards: {}'.format(group))
                for card in group:
                    if ranks.count(card) > 1:
                        multiples = True
                        for i in range(0,ranks.count(card)):
                            self.runs.append(group)
                if not multiples:
                    self.runs.append(group)
                return True
        return False

    def _has_flush(self):

        def _cut_card_matches_hand():
            return self.cut_card["suit"] == next(iter(self.cards))["suit"]

        if all(card["suit"] == next(iter(self.cards))["suit"] for card in self.cards):
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
        jacks = [card for card in self.cards if card["name"] == 'Jack']
        if jacks:
            potential_nobs = [jack["suit"] for jack in jacks]
            if self.cut_card["suit"] in potential_nobs:
                self.nobs = True
                return True
        return False

    def calculate_points(self):
        points = 0

        if self._has_fifteens():
            for fifteen, cards in self.fifteens.items():
                print('Fifteen {} ({})'.format(fifteen, cards))
                points += 2

        if self._has_pairs():
            for pair in self.pairs:
                count = self.pairs.get(pair)
                if count == 4:
                    points += 12
                    print('four {}s for {}'.format(pair, points))
                elif count == 3:
                    points += 6
                    print('three {}s for {}'.format(pair, points))
                else:
                    points += 2
                    print('a pair of {}s for {}'.format(pair, points))

        if self._has_runs():
            for run in self.runs:
                points += len(run)
                print('a run of {} for {} ({})'.format(len(run), points, run))

        if self._has_flush():
            points += self.flush_points
            print('four {} for {}'.format(self.cards[0]['suit'], points))

        if self._has_nobs():
            points += 1
            if points > 1:
                print('And nobs for {}'.format(points))
            else:
                print('Nobs for one')
        return points
