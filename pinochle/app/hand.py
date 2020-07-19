import more_itertools as mit

from .cards import CARDS


class Hand:
    def __init__(self, cards):
        self.cards = cards
        self.marriage = None
        self.pinochle = None
        self.points = 0

    def __str__(self):
        s = ''
        for card in self.cards:
            s += (card['name'] + ' of ' + card['suit'] + ", ")
        s += "{} of {}".format(self.cut_card['name'], self.cut_card['suit'])
        return s

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

    def calculate_points(self):
        points = 0

        if self._has_runs():
            for run in self.runs:
                points += len(run)
                print('a run of {} for {} ({})'.format(len(run), points, run))

        self.points = points
        return points
