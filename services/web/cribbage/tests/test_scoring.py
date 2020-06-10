from unittest import TestCase

from games.models import Hand, Card, Round


class TestScoring(TestCase):

    def setUp(self):
        self.round = Round.objects.create()

    def deal_hand(self, cards):
        hand = Hand.objects.create(round=self.round)
        hand.cards.set(cards)
        return hand

    def deal_crib_hand(self, cards):
        crib_hand = Hand.objects.create(round=self.round, is_crib=True)
        crib_hand.cards.set(cards)
        return crib_hand

    def set_cut_card(self, card):
        self.round.cut_card = card
        self.round.save()

    def test_discard(self):
        cards = [self.ace_of_hearts, self.three_of_hearts, self.eight_of_hearts, self.king_of_spades]
        hand = self.deal_hand(cards)
        hand.discard(self.ace_of_hearts)
        self.assertListEqual(list(hand.cards.all()), [self.three_of_hearts, self.eight_of_hearts, self.king_of_spades])

    def test_no_points(self):
        # Nothin: Ace, Three, Eight, Queen, King
        hand = self.deal_hand([self.ace_of_hearts, self.three_of_hearts, self.eight_of_hearts, self.king_of_spades])
        self.set_cut_card(self.queen_of_hearts)
        self.assertEqual(hand.calculate_points(), 0)

        # Crib flush without cut card matching
        crib_hand = self.deal_crib_hand([self.ace_of_hearts, self.three_of_hearts, self.eight_of_hearts, self.king_of_hearts])
        self.set_cut_card(self.queen_of_spades)
        self.assertEqual(crib_hand.calculate_points(), 0)

    def test_one_point(self):
        # Nobs: Ace, Three, Eight, Jack, King
        hand = self.deal_hand([self.ace_of_hearts, self.three_of_hearts, self.eight_of_hearts, self.jack_of_spades])
        self.set_cut_card(self.queen_of_spades)
        self.assertTrue(hand._has_nobs())
        self.assertEqual(hand.calculate_points(), 1)

        # Crib Nobs: Ace, Three, Eight, Jack, King
        hand = self.deal_crib_hand([self.ace_of_hearts, self.three_of_hearts, self.eight_of_hearts, self.jack_of_spades])
        self.set_cut_card(self.queen_of_spades)
        self.assertTrue(hand._has_nobs())
        self.assertEqual(hand.calculate_points(), 1)

    def test_two_points(self):
        # Fifteen two: Ace, Six, Eight, Queen, King
        hand = self.deal_hand([self.ace_of_hearts, self.six_of_hearts, self.eight_of_hearts, self.king_of_spades])
        self.set_cut_card(self.queen_of_hearts)
        self.assertEqual(hand.calculate_points(), 2)

        # Fifteen two: Ace, Three, Five, Eight, King
        hand = self.deal_hand([self.ace_of_hearts, self.three_of_hearts, self.five_of_hearts, self.king_of_spades])
        self.set_cut_card(self.eight_of_hearts)
        self.assertEqual(hand.calculate_points(), 2)

        # One pair: Three, Three, Four, Ten, King
        hand = self.deal_hand([self.three_of_hearts, self.three_of_diamonds, self.ten_of_hearts, self.king_of_spades])
        self.set_cut_card(self.four_of_hearts)
        self.assertEqual(hand.calculate_points(), 2)

    def test_three_points(self):
        # Run of three: Three, Six, Jack, Queen, King
        hand = self.deal_hand([self.three_of_hearts, self.jack_of_spades, self.queen_of_spades, self.king_of_spades])
        self.set_cut_card(self.six_of_hearts)
        self.assertEqual(hand.calculate_points(), 3)

        # Fifteen Two and Nobs: Ace, Six, Eight, Queen, King
        hand = self.deal_hand([self.ace_of_hearts, self.six_of_hearts, self.eight_of_hearts, self.jack_of_spades])
        self.set_cut_card(self.queen_of_spades)
        self.assertEqual(hand.calculate_points(), 3)

    def test_four_points(self):
        # Hand flush without cut card
        hand = self.deal_hand([self.ace_of_hearts, self.three_of_hearts, self.eight_of_hearts, self.king_of_hearts])
        self.set_cut_card(self.queen_of_spades)
        self.assertEqual(hand.calculate_points(), 4)

        # Two pairs
        hand = self.deal_hand([self.ace_of_hearts, self.ace_of_spades, self.three_of_hearts, self.three_of_spades])
        self.set_cut_card(self.four_of_spades)
        self.assertEqual(hand.calculate_points(), 4)

        # Fifteen two and a pair
        hand = self.deal_hand([self.ace_of_hearts, self.three_of_hearts, self.five_of_hearts, self.king_of_spades])
        self.set_cut_card(self.three_of_spades)
        self.assertEqual(hand.calculate_points(), 4)

        # Fifteen Four
        hand = self.deal_hand([self.two_of_hearts, self.three_of_hearts, self.five_of_hearts, self.king_of_spades])
        self.set_cut_card(self.nine_of_spades)
        self.assertEqual(hand.calculate_points(), 4)

        # Run of three and nobs
        hand = self.deal_hand([self.ace_of_hearts, self.nine_of_hearts, self.ten_of_hearts, self.jack_of_spades])
        self.set_cut_card(self.king_of_spades)
        self.assertEqual(hand.calculate_points(), 4)

        # Run of four
        hand = self.deal_hand([self.eight_of_hearts, self.nine_of_hearts, self.ten_of_hearts, self.jack_of_spades])
        self.set_cut_card(self.king_of_hearts)
        self.assertEqual(hand.calculate_points(), 4)
        hand.refresh_from_db()
        self.assertEqual(hand.points, 4)

        # Run of four
        hand = self.deal_hand([self.queen_of_hearts, self.king_of_hearts, self.ten_of_hearts, self.jack_of_spades])
        self.set_cut_card(self.ace_of_hearts)
        self.assertEqual(hand.calculate_points(), 4)
        hand.refresh_from_db()
        self.assertEqual(hand.points, 4)

    def test_five_points(self):
        # Hand flush with cut card
        hand = self.deal_hand([self.ace_of_hearts, self.three_of_hearts, self.eight_of_hearts, self.king_of_hearts])
        self.set_cut_card(self.queen_of_hearts)
        self.assertEqual(hand.calculate_points(), 5)

        # Crib flush
        crib_hand = self.deal_crib_hand([self.ace_of_hearts, self.three_of_hearts, self.eight_of_hearts, self.king_of_hearts])
        self.set_cut_card(self.queen_of_hearts)
        self.assertEqual(crib_hand.calculate_points(), 5)

        # Run of four and nobs
        hand = self.deal_hand([self.eight_of_hearts, self.nine_of_hearts, self.ten_of_hearts, self.jack_of_spades])
        self.set_cut_card(self.king_of_spades)
        self.assertEqual(hand.calculate_points(), 5)

        # Fifteen two and a run of three
        hand = self.deal_hand([self.seven_of_hearts, self.eight_of_hearts, self.nine_of_hearts, self.jack_of_spades])
        self.set_cut_card(self.ace_of_diamonds)
        self.assertEqual(hand.calculate_points(), 5)

        # Fifteen four and nobs
        hand = self.deal_hand([self.four_of_hearts, self.eight_of_hearts, self.ten_of_hearts, self.jack_of_spades])
        self.set_cut_card(self.five_of_spades)
        self.assertEqual(hand.calculate_points(), 5)

        # Fifteen two, a pair and nobs
        hand = self.deal_hand([self.four_of_hearts, self.nine_of_spades, self.nine_of_hearts, self.jack_of_spades])
        self.set_cut_card(self.five_of_spades)
        self.assertEqual(hand.calculate_points(), 5)

        # Two pairs and nobs
        hand = self.deal_hand([self.four_of_hearts, self.nine_of_spades, self.nine_of_hearts, self.jack_of_spades])
        self.set_cut_card(self.four_of_spades)
        self.assertEqual(hand.calculate_points(), 5)

    def test_six_points(self):
        # Three of a kind
        hand = self.deal_hand([self.nine_of_clubs, self.nine_of_spades, self.nine_of_hearts, self.jack_of_hearts])
        self.set_cut_card(self.four_of_spades)
        self.assertEqual(hand.calculate_points(), 6)

        # Fifteen 4 and a pair: 6, 9, 9, 10, K
        hand = self.deal_hand([self.six_of_clubs, self.nine_of_spades, self.nine_of_hearts, self.ten_of_spades])
        self.set_cut_card(self.king_of_spades)
        self.assertEqual(hand.calculate_points(), 6)

    def test_seven_points(self):
        # Three of a kind and nobs
        hand = self.deal_hand([self.nine_of_clubs, self.nine_of_spades, self.nine_of_hearts, self.jack_of_spades])
        self.set_cut_card(self.four_of_spades)
        self.assertEqual(hand.calculate_points(), 7)

        # Fifteen 4, a pair, and nobs: 6, 9, 9, J, K
        hand = self.deal_hand([self.six_of_clubs, self.nine_of_spades, self.nine_of_hearts, self.jack_of_spades])
        self.set_cut_card(self.king_of_spades)
        self.assertEqual(hand.calculate_points(), 7)

    def test_eight_points(self):
        # Fifteen two and three of a kind
        hand = self.deal_hand([self.nine_of_clubs, self.nine_of_spades, self.nine_of_hearts, self.jack_of_spades])
        self.set_cut_card(self.five_of_hearts)
        self.assertEqual(hand.calculate_points(), 8)

    def test_twelve_points(self):
        # Two sevens, Two eights
        hand = self.deal_hand([self.seven_of_hearts, self.seven_of_clubs, self.eight_of_hearts, self.eight_of_clubs])
        self.set_cut_card(self.four_of_spades)
        self.assertEqual(hand.calculate_points(), 12)

        # Fifteen 6 and 3 of a kind
        hand = self.deal_hand([self.king_of_hearts, self.king_of_clubs, self.king_of_spades, self.eight_of_clubs])
        self.set_cut_card(self.five_of_spades)
        self.assertEqual(hand.calculate_points(), 12)

        # Four of a kind
        hand = self.deal_hand([self.eight_of_spades, self.eight_of_diamonds, self.eight_of_hearts, self.eight_of_clubs])
        self.set_cut_card(self.four_of_spades)
        self.assertEqual(hand.calculate_points(), 12)
