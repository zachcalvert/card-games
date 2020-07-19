from app.cards import CARDS
from app.hand import Hand


class TestHand:
    """
    Test that various hand combinations are scored correctly
    """
    def test_no_points(self):
        card_ids = ['f6571e162f', '5c6bdd4fee', 'ace1293f8a', '110e6e5b19']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('32f7615119')
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'ten of diamonds, four of spades, two of hearts, jack of clubs, seven of spades'
        assert hand.points == 0

    def test_fifteen_two(self):
        card_ids = ['f6571e162f', '30e1ddb610', 'ace1293f8a', '4dfe41e461']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card =  CARDS.get('32f7615119')
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'ten of diamonds, five of spades, two of hearts, nine of clubs, seven of spades'
        assert hand.fifteens == {2: (5, 10)}
        assert hand.points == 2

    def test_fifteen_four(self):
        card_ids = ['f6571e162f', '30e1ddb610', 'c88523b677', '4dfe41e461']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('ace1293f8a')
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'ten of diamonds, five of spades, six of hearts, nine of clubs, two of hearts'
        assert hand.fifteens == {2: (5, 10), 4: (6, 9)}
        assert hand.points == 4

    def test_fifteen_six(self):
        card_ids = ['f6571e162f', '30e1ddb610', 'c88523b677', 'ae2caea4bb']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('56594b3880')
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'ten of diamonds, five of spades, six of hearts, king of clubs, jack of hearts'
        assert hand.fifteens == {2: (5, 10), 4: (5, 10), 6: (5, 10)}
        assert hand.points == 6

    def test_fifteen_eight(self):
        card_ids = ['4f99bf15e5', '32f7615119', '4de6b73ab8', '4c8519af34']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('56594b3880')
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'seven of diamonds, seven of spades, eight of hearts, eight of clubs, jack of hearts'
        assert hand.fifteens == {2: (7, 8), 4: (7, 8), 6: (7, 8), 8: (7, 8)}
        assert hand.pairs == {7: 2, 8: 2}
        assert hand.points == 12

    def test_one_pair(self):
        card_ids = ['f6571e162f', 'd3a2460e93', 'ace1293f8a', '4dfe41e461']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('32f7615119')
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'ten of diamonds, ten of spades, two of hearts, nine of clubs, seven of spades'
        assert hand.pairs == {10: 2}
        assert hand.points == 2

    def test_two_pairs(self):
        card_ids = ['f6571e162f', 'd3a2460e93', 'ace1293f8a', 'd1c9fde8ef']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('32f7615119')
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'ten of diamonds, ten of spades, two of hearts, two of clubs, seven of spades'
        assert hand.pairs == {10: 2, 2: 2}
        assert hand.points == 4

    def test_one_run(self):
        card_ids = ['def8effef6', '4dfe41e461', '4c8519af34', 'ace1293f8a']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('110e6e5b19')
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'seven of hearts, nine of clubs, eight of clubs, two of hearts, jack of clubs'
        assert len(hand.runs) == 1
        assert hand.points == 5

    def test_double_run(self):
        card_ids = ['def8effef6', '4dfe41e461', '4c8519af34', '597e4519ac']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('110e6e5b19')
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'seven of hearts, nine of clubs, eight of clubs, nine of hearts, jack of clubs'
        assert len(hand.runs) == 2
        assert hand.points == 10

    def test_double_run_of_four(self):
        card_ids = ['def8effef6', '4c8519af34', '597e4519ac', '4dfe41e461']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('276f33cf69')
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'seven of hearts, eight of clubs, nine of hearts, nine of clubs, ten of clubs'
        assert len(hand.runs) == 2
        assert hand.points == 12

    def test_four_runs(self):
        card_ids = ['def8effef6', '4dfe41e461', '4c8519af34', '597e4519ac']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('ce46b344a3')
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'seven of hearts, nine of clubs, eight of clubs, nine of hearts, eight of spades'
        assert len(hand.runs) == 4
        assert hand.points == 20

    def test_hand_flush_without_cut_card(self):
        card_ids = ['c88623fa16', '04f17d1351', '5c6bdd4fee', 'd3a2460e93']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('60575e1068')
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'six of spades, three of spades, four of spades, ten of spades, king of diamonds'
        assert hand.flush_points == 4
        assert hand.points == 4

    def test_hand_flush_with_cut_card(self):
        card_ids = ['c88623fa16', '04f17d1351', '5c6bdd4fee', 'd3a2460e93']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('32f7615119')
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'six of spades, three of spades, four of spades, ten of spades, seven of spades'
        assert hand.flush_points == 5
        assert hand.points == 5

    def test_crib_flush_without_cut_card(self):
        """
        A crib only has a flush if the cut card matches as well
        """
        card_ids = ['c88623fa16', '04f17d1351', '5c6bdd4fee', 'd3a2460e93']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('60575e1068')
        crib = Hand(cards, cut_card, is_crib=True)
        crib.calculate_points()
        assert str(crib) == 'six of spades, three of spades, four of spades, ten of spades, king of diamonds'
        assert crib.flush_points == 0
        assert crib.points == 0

    def test_crib_flush_with_cut_card(self):
        card_ids = ['c88623fa16', '04f17d1351', '5c6bdd4fee', 'd3a2460e93']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('32f7615119')
        crib = Hand(cards, cut_card, is_crib=True)
        crib.calculate_points()
        assert str(crib) == 'six of spades, three of spades, four of spades, ten of spades, seven of spades'
        assert crib.flush_points == 5
        assert crib.points == 5

    def test_perfect_hand(self):
        card_ids = ['a6a3e792b4', '30e1ddb610', 'fa0873dd7d', '1d5eb77128']
        cards = [CARDS.get(card_id) for card_id in card_ids]
        cut_card = CARDS.get('d7ca85cf5e')
        hand = Hand(cards, cut_card)
        hand.calculate_points()
        assert str(hand) == 'five of clubs, five of spades, five of hearts, jack of diamonds, five of diamonds'
        assert hand.pairs == {5: 4}
        assert len(hand.fifteens.keys()) == 8
        assert hand._has_nobs()
        assert hand.points == 29
