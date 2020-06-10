from unittest import TestCase


from cribbage.cards import CARDS
from cribbage.scoring import Hand


class TestHandScoring(TestCase):

    def setUp(self):
        pass

    def test_four_of_a_kind(self):
        cards = ['a6a3e792b4', '30e1ddb610', 'fa0873dd7d', 'd7ca85cf5e']
        cut_card = '1d5eb77128'

        hand = Hand(cards, cut_card)
        self.assertEqual(str(hand), 'Fiveclubs, Fivespades, Fivehearts, Fivediamonds, Jackdiamonds')
        self.assertEqual(hand.calculate_points(), 20)
        self.assertEqual(len(hand.runs), 4)

    def test_four_runs(self):
        cards = ['def8effef6', '4dfe41e461', '4c8519af34', '597e4519ac']
        cut_card = 'ce46b344a3'

        hand = Hand(cards, cut_card)
        self.assertEqual(str(hand), 'Sevenhearts, Nineclubs, Eightclubs, Ninehearts, Eightspades')
        self.assertEqual(hand.calculate_points(), 20)
        self.assertEqual(len(hand.runs), 4)
