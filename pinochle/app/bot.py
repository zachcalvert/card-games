import random

BOT_NAMES = ['humphrey', 'belinda', 'josie', 'mingus', 'goran', 'soo-yung', 'kap']
TEAM_NAMES = ['the hey dudes', 'wandernickle', 'blunt boys', 'mixer dagger', 'ocean spray', 'holf rounder']


class Bot:

    def __init__(self, team, name=None, cards=[]):
        self.team = team
        self.name = name or random.choice(BOT_NAMES)
        self.cards = cards

    def bid(self):
        bids = [250, 250, 250, 250, 260, 260, 260, 270, 270, 280]
        return random.choice(bids)

    def play_card(self, suit):
        pass
