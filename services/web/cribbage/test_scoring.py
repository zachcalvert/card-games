from .cards import CARDS
from .scoring import Hand


class TestHandScoring:
    """
    Test that various hand combinations are scored correctly
    """
    def test_no_points(self):
        cards = ['f6571e162f', '5c6bdd4fee', 'ace1293f8a', '110e6e5b19']
        cut_card = '32f7615119'
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'Ten of diamonds, Four of spades, Two of hearts, Jack of clubs, Seven of spades'
        assert hand.points == 0

    def test_fifteen_two(self):
        cards = ['f6571e162f', '30e1ddb610', 'ace1293f8a', '4dfe41e461']
        cut_card = '32f7615119'
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'Ten of diamonds, Five of spades, Two of hearts, Nine of clubs, Seven of spades'
        assert hand.fifteens == {2: (5, 10)}
        assert hand.points == 2

    def test_fifteen_four(self):
        cards = ['f6571e162f', '30e1ddb610', 'c88523b677', '4dfe41e461']
        cut_card = 'ace1293f8a'
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'Ten of diamonds, Five of spades, Six of hearts, Nine of clubs, Two of hearts'
        assert hand.fifteens == {2: (5, 10), 4: (6, 9)}
        assert hand.points == 4

    def test_fifteen_six(self):
        cards = ['f6571e162f', '30e1ddb610', 'c88523b677', 'ae2caea4bb']
        cut_card = '56594b3880'
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'Ten of diamonds, Five of spades, Six of hearts, King of clubs, Jack of hearts'
        assert hand.fifteens == {2: (5, 10), 4: (5, 10), 6: (5, 10)}
        assert hand.points == 6

    def test_fifteen_eight(self):
        cards = ['4f99bf15e5', '32f7615119', '4de6b73ab8', '4c8519af34']
        cut_card = '56594b3880'
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'Seven of diamonds, Seven of spades, Eight of hearts, Eight of clubs, Jack of hearts'
        assert hand.fifteens == {2: (7, 8), 4: (7, 8), 6: (7, 8), 8: (7, 8)}
        assert hand.pairs == {7: 2, 8: 2}
        assert hand.points == 12

    def test_one_pair(self):
        cards = ['f6571e162f', 'd3a2460e93', 'ace1293f8a', '4dfe41e461']
        cut_card = '32f7615119'
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'Ten of diamonds, Ten of spades, Two of hearts, Nine of clubs, Seven of spades'
        assert hand.pairs == {10: 2}
        assert hand.points == 2

    def test_two_pairs(self):
        cards = ['f6571e162f', 'd3a2460e93', 'ace1293f8a', 'd1c9fde8ef']
        cut_card = '32f7615119'
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'Ten of diamonds, Ten of spades, Two of hearts, Two of clubs, Seven of spades'
        assert hand.pairs == {10: 2, 2: 2}
        assert hand.points == 4

    def test_one_run(self):
        cards = ['def8effef6', '4dfe41e461', '4c8519af34', 'ace1293f8a']
        cut_card = '110e6e5b19'
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'Seven of hearts, Nine of clubs, Eight of clubs, Two of hearts, Jack of clubs'
        assert len(hand.runs) == 1
        assert hand.points == 5

    def test_double_run(self):
        cards = ['def8effef6', '4dfe41e461', '4c8519af34', '597e4519ac']
        cut_card = '110e6e5b19'
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'Seven of hearts, Nine of clubs, Eight of clubs, Nine of hearts, Jack of clubs'
        assert len(hand.runs) == 2
        assert hand.points == 10

    def test_double_run_of_four(self):
        cards = ['def8effef6', '4c8519af34', '597e4519ac', '4dfe41e461']
        cut_card = '276f33cf69'
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'Seven of hearts, Eight of clubs, Nine of hearts, Nine of clubs, Ten of clubs'
        assert len(hand.runs) == 2
        assert hand.points == 12

    def test_four_runs(self):
        cards = ['def8effef6', '4dfe41e461', '4c8519af34', '597e4519ac']
        cut_card = 'ce46b344a3'
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'Seven of hearts, Nine of clubs, Eight of clubs, Nine of hearts, Eight of spades'
        assert len(hand.runs) == 4
        assert hand.points == 20

    def test_hand_flush_without_cut_card(self):
        cards = ['c88623fa16', '04f17d1351', '5c6bdd4fee', 'd3a2460e93']
        cut_card = '60575e1068'
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'Six of spades, Three of spades, Four of spades, Ten of spades, King of diamonds'
        assert hand.flush_points == 4
        assert hand.points == 4

    def test_hand_flush_with_cut_card(self):
        cards = ['c88623fa16', '04f17d1351', '5c6bdd4fee', 'd3a2460e93']
        cut_card = '32f7615119'
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'Six of spades, Three of spades, Four of spades, Ten of spades, Seven of spades'
        assert hand.flush_points == 5
        assert hand.points == 5

    def test_crib_flush_without_cut_card(self):
        """
        A crib only has a flush if the cut card matches as well
        """
        cards = ['c88623fa16', '04f17d1351', '5c6bdd4fee', 'd3a2460e93']
        cut_card = '60575e1068'
        crib = Hand(cards, cut_card, is_crib=True)
        crib.calculate_points()
        assert str(crib) == 'Six of spades, Three of spades, Four of spades, Ten of spades, King of diamonds'
        assert crib.flush_points == 0
        assert crib.points == 0

    def test_crib_flush_with_cut_card(self):
        cards = ['c88623fa16', '04f17d1351', '5c6bdd4fee', 'd3a2460e93']
        cut_card = '32f7615119'
        crib = Hand(cards, cut_card, is_crib=True)
        crib.calculate_points()
        assert str(crib) == 'Six of spades, Three of spades, Four of spades, Ten of spades, Seven of spades'
        assert crib.flush_points == 5
        assert crib.points == 5

    def test_perfect_hand(self):
        cards = ['a6a3e792b4', '30e1ddb610', 'fa0873dd7d', '1d5eb77128']
        cut_card = 'd7ca85cf5e'
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'Five of clubs, Five of spades, Five of hearts, Jack of diamonds, Five of diamonds'
        assert hand.pairs == {5: 4}
        assert len(hand.fifteens.keys()) == 8
        assert hand._has_nobs()
        assert hand.points == 29


# class TestPlayScoring:
#     def test_fifteen_two(self):
#         card = '4c8519af34'
#         previously_played_cards = ['32f7615119']
#         play = PlayScorer(card, previously_played_cards, [], 7)
#         assert str(play) == 'on the table: Seven of spades, played: Eight of clubs'
#         points, new_total, run = play.calculate_points()
#         assert points == 2
#
#     def test_pair(self):
#         card = 'a6a3e792b4'
#         previously_played_cards = ['30e1ddb610', '1d5eb77128']
#         play = PlayScorer(card, previously_played_cards, [], 15)
#         assert str(play) == 'on the table: Five of spades, Jack of diamonds, played: Five of clubs'
#         points, new_total, run = play.calculate_points()
#         assert points == 2
#
#     def test_three_of_a_kind(self):
#         card = 'a6a3e792b4'
#         previously_played_cards = ['30e1ddb610', 'fa0873dd7d', '1d5eb77128']
#         play = PlayScorer(card, previously_played_cards, [], 15)
#         assert str(play) == 'on the table: Five of spades, Five of hearts, Jack of diamonds, played: Five of clubs'
#         points, new_total, run = play.calculate_points()
#         assert points == 6
#
#     def test_four_of_a_kind(self):
#         card = 'a6a3e792b4'
#         previously_played_cards = ['30e1ddb610', 'fa0873dd7d', 'd7ca85cf5e', '1d5eb77128']
#         play = PlayScorer(card, previously_played_cards, [], 15)
#         assert str(play) == 'on the table: Five of spades, Five of hearts, Five of diamonds, Jack of diamonds, played: Five of clubs'
#         points, new_total, run = play.calculate_points()
#         assert points == 12
#
#     def test_run_of_three(self):
#         card = '3698fe0420'
#         previously_played_cards = ['5c6bdd4fee', '85ba715700']
#         play = PlayScorer(card, previously_played_cards, [3,4], 7)
#         assert str(play) == 'on the table: Four of spades, Three of clubs, played: Two of diamonds'
#         points, new_total, run = play.calculate_points()
#         assert run == [2, 3, 4]
#         assert points == 3
#
#     def test_run_of_four(self):
#         card = 'd7ca85cf5e'
#         previously_played_cards = ['3698fe0420', '5c6bdd4fee', '85ba715700']
#         play = PlayScorer(card, previously_played_cards, [2, 3, 4], 9)
#         assert str(play) == 'on the table: Two of diamonds, Four of spades, Three of clubs, played: Five of diamonds'
#         points, new_total, run = play.calculate_points()
#         assert run == [2, 3, 4, 5]
#         assert points == 4
#
#     def test_run_of_five_and_fifteen_two(self):
#         card = 'bd4b01946d'
#         previously_played_cards = ['d7ca85cf5e', '3698fe0420', '5c6bdd4fee', '85ba715700']
#         play = PlayScorer(card, previously_played_cards, [2, 3, 4, 5], 14)
#         assert str(play) == 'on the table: Five of diamonds, Two of diamonds, Four of spades, Three of clubs, played: Ace of hearts'
#         points, new_total, run = play.calculate_points()
#         assert new_total == 15
#         assert run == [1, 2, 3, 4, 5]
#         assert points == 7
#
#     def test_fifteen_two_and_a_pair(self):
#         card = '64fe85d796'
#         previously_played_cards = ['85ba715700', 'de1c863a7f']
#         play = PlayScorer(card, previously_played_cards, [], 12)
#         assert str(play) == 'on the table: Three of clubs, Nine of spades, played: Three of diamonds'
#         points, new_total, run = play.calculate_points()
#         assert new_total == 15
#         assert points == 4
#
#     def test_fifteen_two_and_three_of_a_kind(self):
#         card = '64fe85d796'
#         previously_played_cards = ['85ba715700', '04f17d1351', 'c88623fa16']
#         play = PlayScorer(card, previously_played_cards, [], 12)
#         assert str(play) == 'on the table: Three of clubs, Three of spades, Six of spades, played: Three of diamonds'
#         points, new_total, run = play.calculate_points()
#         assert new_total == 15
#         assert points == 8
