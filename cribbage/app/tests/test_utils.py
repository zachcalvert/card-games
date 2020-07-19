from app.cards import CARDS
from app.utils import rotate_turn, rotate_reverse, play_or_pass, card_object_from_text, card_text_from_id


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


class TestGetCardObjectFromText:
    def test_three_of_spades(self):
        expected = {
            "04f17d1351": {
                "name": "three",
                "rank": 3,
                "value": 3,
                "suit": "spades"
              }
        }
        assert card_object_from_text('three of spades') == expected

    def test_jack_of_diamonds(self):
        expected = {
            "1d5eb77128": {
                "name": "jack",
                "rank": 11,
                "value": 10,
                "suit": "diamonds"
              }
          }
        assert card_object_from_text('jack of diamonds') == expected

    def test_ace_of_hearts(self):
        expected = {
            "bd4b01946d": {
                "name": "ace",
                "rank": 1,
                "value": 1,
                "suit": "hearts"
              }
          }
        assert card_object_from_text('ace of hearts') == expected


class TestGetCardTextFromId:
    def test_three_of_spades(self):
        expected = 'the three of spades'
        assert card_text_from_id('04f17d1351') == expected

    def test_jack_of_diamonds(self):
        expected = 'the jack of diamonds'
        assert card_text_from_id('1d5eb77128') == expected

    def test_ace_of_hearts(self):
        expected = 'the ace of hearts'
        assert card_text_from_id('bd4b01946d') == expected

    def test_jokers(self):
        expected = 'a joker'
        for joker in ['joker1', 'joker2']:
            assert card_text_from_id(joker) == expected
