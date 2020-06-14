from .cards import CARDS
from .utils import rotate_turn, play_or_pass


# class TestRotateTurn:
#     def test_rotate_turn_base_case(self):
#         players = ['mom', 'dad', 'paul', 'leah']
#         next = rotate_turn('mom', players)
#         assert next == 'dad'
#
#     def test_rotate_turn_loop_around(self):
#         players = ['mom', 'dad', 'paul', 'leah']
#         next = rotate_turn('leah', players)
#         assert next == 'mom'
#
#
# class TestPlayOrPass:
#     def test_play_or_pass_base_case(self):
#         cards = ['6d95c18472']  # ace of diamonds
#         assert play_or_pass(cards, 30) == 'PLAY'
#
#         cards = ['3698fe0420']  # two of diamonds
#         assert play_or_pass(cards, 30) == 'PASS'
#
#     def test_all_cards_can_play_when_total_is_twentyone(self):
#         for card in CARDS.keys():
#             assert play_or_pass([card], 21) == 'PLAY'
#
#     def test_must_pass_when_multiple_cards(self):
#         cards = ['83ef982410', 'ff2de622d8', '9eba093a9d']  # four of hearts, six of clubs, nine of diamonds
#         assert play_or_pass(cards, 28) == 'PASS'
#
#     def test_must_play_when_multiple_cards(self):
#         cards = ['83ef982410', 'ff2de622d8', '9eba093a9d']  # four of hearts, six of clubs, nine of diamonds
#         assert play_or_pass(cards, 27) == 'PLAY'
