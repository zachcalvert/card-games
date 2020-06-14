import fakeredis

from .bev import Bev
from .cards import CARDS


class TestPegging:

    def test_can_play_if_has_ace_at_thirty(self):
        r = fakeredis.FakeStrictRedis()
        game_dict = {
            'crib': ['5c6bdd4fee', 'e26d0bead3', '04f17d1351', 'd1c9fde8ef'],
            'cut_card': '276f33cf69',
            'cutter': 'kathy',
            'dealer': 'tom',
            'deck': [],
            'first_to_score': 'kathy',
            'hand_size': 6,
            'hands': {'kathy': ['c88523b677'], 'tom': ['d00bb3f3b7', '56594b3880']},
            'name': 'r',
            'ok_with_next_round': [],
            'pegging': {
                'cards': ['30e1ddb610', 'fa0873dd7d', '1d5eb77128', 'd7ca85cf5e'],
                'last_played': 'tom',
                'passed': [],
                'run': [],
                'total': 30},
            'play_again': [],
            'played_cards': {'kathy': ['def8effef6', 'ce46b344a3', '6d95c18472'],
                             'tom': ['4de6b73ab8', 'ff2de622d8']},
            'players': {'kathy': {'nickname': 'kathy', 'points': 1},
                        'tom': {'nickname': 'tom', 'points': 0}},
            'scored_hands': [],
            'state': 'PLAYING',
            'turn': 'tom'}
        r.set('game', game_dict)

        card = 'a6a3e792b4'
        Bev.score_play('game', 'tom', card)
        assert



