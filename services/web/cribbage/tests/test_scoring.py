from unittest import TestCase

from cribbage.cards import CARDS
from cribbage.scoring import Hand


class TestHandScoring(TestCase):

    def setUp(self):
        pass

    def test_perfect_hand(self):
        cards = ['a6a3e792b4', '30e1ddb610', 'fa0873dd7d', '1d5eb77128']
        cut_card = 'd7ca85cf5e'

        hand = Hand(cards, cut_card)
        self.assertEqual(str(hand), 'Fiveclubs, Fivespades, Fivehearts, Fivediamonds, Jackdiamonds')
        self.assertEqual(len(hand.runs), 4)
        self.assertEqual(len(hand.fifteens.keys()), 8)
        self.assertTrue(hand._has_nobs())
        self.assertEqual(hand.calculate_points(), 29)

    def test_four_runs(self):
        cards = ['def8effef6', '4dfe41e461', '4c8519af34', '597e4519ac']
        cut_card = 'ce46b344a3'

        hand = Hand(cards, cut_card)
        self.assertEqual(str(hand), 'Sevenhearts, Nineclubs, Eightclubs, Ninehearts, Eightspades')
        self.assertEqual(hand.calculate_points(), 20)
        self.assertEqual(len(hand.runs), 4)
