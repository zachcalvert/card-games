from cribbage.cards import CARDS
from cribbage.utils import rotate_turn, rotate_reverse, play_or_pass


class TestRotateTurn:
    def test_rotate_turn_base_case(self):
        players = ['mom', 'dad', 'paul', 'leah']
        next = rotate_turn('mom', players)
        assert next == 'dad'

    def test_rotate_turn_loop_around(self):
        players = ['mom', 'dad', 'paul', 'leah']
        next = rotate_turn('leah', players)
        assert next == 'mom'


class TestRotateReverse:
    def test_rotate_turn(self):
        players = ['mom', 'dad', 'paul', 'leah']
        next = rotate_reverse('leah', players)
        assert next == 'paul'

    def test_rotate_turn_loop_around(self):
        players = ['mom', 'dad', 'paul', 'leah']
        next = rotate_reverse('mom', players)
        assert next == 'leah'


class TestPlayOrPass:
    def test_play_or_pass_base_case(self):
        cards = ['1']  # ace of diamonds
        assert play_or_pass(cards, 30) == 'PLAY'

        cards = ['2']  # two of diamonds
        assert play_or_pass(cards, 30) == 'PASS'

    def test_all_cards_can_play_when_total_is_twentyone(self):
        for id, card in CARDS.items():
            assert play_or_pass([card['value']], 21) == 'PLAY'

    def test_must_pass_when_multiple_cards(self):
        cards = ['4', '6', '9']  # four of hearts, six of clubs, nine of diamonds
        assert play_or_pass(cards, 28) == 'PASS'

    def test_must_play_when_multiple_cards(self):
        cards = ['4', '6', '9']  # four of hearts, six of clubs, nine of diamonds
        assert play_or_pass(cards, 27) == 'PLAY'
