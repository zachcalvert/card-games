import fakeredis
import json
import mock

from app import bev
from app.cards import CARDS


class TestStartGame:

    def test_start_with_two_players(self, two_player_game_unstarted):
        fake_redis = fakeredis.FakeRedis()
        fake_redis.set('cheers', json.dumps(two_player_game_unstarted))
        bev.cache = fake_redis
        bev.start_game('cheers')

        g = json.loads(fake_redis.get('cheers'))
        assert g['state'] == 'DEAL'
        assert g['hand_size'] == 6
        assert g['dealer'] != g['cutter']
        assert g['dealer'] != g['first_to_score']
        assert g['turn'] == g['dealer']
        assert g['winning_score'] == 121
        assert not g['jokers']

    def test_start_with_three_players(self, three_player_game_unstarted):
        fake_redis = fakeredis.FakeRedis()
        fake_redis.set('cheers', json.dumps(three_player_game_unstarted))
        bev.cache = fake_redis
        bev.start_game('cheers')

        g = json.loads(fake_redis.get('cheers'))
        assert g['state'] == 'DEAL'
        assert g['hand_size'] == 5
        assert g['dealer'] != g['cutter']
        assert g['dealer'] != g['first_to_score']
        assert g['cutter'] != g['first_to_score']
        assert g['turn'] == g['dealer']
        assert g['winning_score'] == 121
        assert not g['jokers']

    def test_start_with_jokers(self, two_player_game_unstarted):
        fake_redis = fakeredis.FakeRedis()
        fake_redis.set('cheers', json.dumps(two_player_game_unstarted))
        bev.cache = fake_redis
        bev.start_game('cheers', jokers=True)

        g = json.loads(fake_redis.get('cheers'))
        assert g['state'] == 'DEAL'
        assert g['hand_size'] == 6
        assert g['dealer'] != g['cutter']
        assert g['dealer'] != g['first_to_score']
        assert g['turn'] == g['dealer']
        assert g['winning_score'] == 121
        assert g['jokers']

    def test_start_shorter_game(self, two_player_game_unstarted):
        fake_redis = fakeredis.FakeRedis()
        fake_redis.set('cheers', json.dumps(two_player_game_unstarted))
        bev.cache = fake_redis
        bev.start_game('cheers', winning_score=60)

        g = json.loads(fake_redis.get('cheers'))
        assert g['state'] == 'DEAL'
        assert g['hand_size'] == 6
        assert g['dealer'] != g['cutter']
        assert g['dealer'] != g['first_to_score']
        assert g['turn'] == g['dealer']
        assert g['winning_score'] == 60
        assert not g['jokers']


class TestDeal:

    def test_deal_unique_cards(self, three_player_game_unstarted):
        fake_redis = fakeredis.FakeRedis()
        fake_redis.set('cheers', json.dumps(three_player_game_unstarted))
        bev.cache = fake_redis
        bev.start_game('cheers')
        bev.deal_hands('cheers')

        g = json.loads(fake_redis.get('cheers'))
        assert g['state'] == 'DISCARD'
        for player in three_player_game_unstarted['players'].keys():
            assert player in g['hands'].keys()
            assert len(g['hands'][player]) == g['hand_size']


class TestDiscard:

    def test_first_discard(self, two_player_game_unstarted):
        fake_redis = fakeredis.FakeRedis()
        fake_redis.set('cheers', json.dumps(two_player_game_unstarted))
        bev.cache = fake_redis
        bev.start_game('cheers')
        bev.deal_hands('cheers')

        g = json.loads(fake_redis.get('cheers'))
        player_done, all_done = bev.discard('cheers', 'sam', g['hands']['sam'][0])
        assert not player_done
        assert not all_done
        assert g['state'] == 'DISCARD'

    def test_first_to_be_done_discarding(self, two_player_game_unstarted):
        fake_redis = fakeredis.FakeRedis()
        fake_redis.set('cheers', json.dumps(two_player_game_unstarted))
        bev.cache = fake_redis
        bev.start_game('cheers')
        bev.deal_hands('cheers')

        g = json.loads(fake_redis.get('cheers'))
        _, _ = bev.discard('cheers', 'sam', g['hands']['sam'][0])
        player_done, all_done = bev.discard('cheers', 'sam', g['hands']['sam'][1])
        assert player_done
        assert not all_done
        assert g['state'] == 'DISCARD'

    def test_all_have_discarded(self, two_player_game_unstarted):
        fake_redis = fakeredis.FakeRedis()
        fake_redis.set('cheers', json.dumps(two_player_game_unstarted))
        bev.cache = fake_redis
        bev.start_game('cheers')
        bev.deal_hands('cheers')

        g = json.loads(fake_redis.get('cheers'))
        _, _ = bev.discard('cheers', 'sam', g['hands']['sam'][0])
        player_done, all_done = bev.discard('cheers', 'sam', g['hands']['sam'][1])
        assert player_done
        assert not all_done
        _, _ = bev.discard('cheers', 'diane', g['hands']['diane'][0])
        player_done, all_done = bev.discard('cheers', 'diane', g['hands']['diane'][1])
        assert player_done
        assert all_done
        g = json.loads(fake_redis.get('cheers'))
        assert g['state'] == 'CUT'


class TestCut:

    def test_cut(self, two_player_game_fully_dealt):
        fake_redis = fakeredis.FakeRedis()
        fake_redis.set('homemovies', json.dumps(two_player_game_fully_dealt))
        bev.cache = fake_redis

        bev.cut_deck('homemovies')

        g = json.loads(fake_redis.get('homemovies'))
        assert g['state'] == 'PLAY'
        assert g['cut_card']
        assert g['turn'] == g['first_to_score']
        for player in g['players'].keys():   # ensure the cut card isn't also in anyone's hand
            assert g['cut_card'] not in g['hands'][player]


class TestNextPlayer:

    def test_next_must_pass(self):
        """
        Kathy and Tom each have face cards, tom just played and the total is at 30

        Expected: It is now kathy's turn and she must pass
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'hands': {'kathy': ['5e1e7e60ab'], 'tom': ['95f92b2f0c']},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'tom',
                'passed': [],
                'run': [],
                'total': 30
            },
            'players': {
                'tom': 0,
                'kathy': 0
            },
            'state': 'PLAY',
            'turn': 'tom',
            'winning_score': 121,
        }
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['turn'] == 'kathy'
        assert g['pegging']['total'] == 30
        assert bev.get_player_action('test', g['turn']) == 'PASS'

    def test_next_must_play(self):
        """
        Kathy and Tom each have aces. Tom just played and the total is at 30

        Expected: It is now kathy's turn and she must play
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'hands': {'kathy': ['6d95c18472'], 'tom': ['ace1293f8a']},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'tom',
                'passed': [],
                'run': [],
                'total': 30},
            'players': {
                'tom': 0,
                'kathy': 0
            },
            'state': 'PLAY',
            'turn': 'tom',
            'winning_score': 121,
        }
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['turn'] == 'kathy'
        assert g['pegging']['total'] == 30
        assert bev.get_player_action('test', g['turn']) == 'PLAY'

    def test_everyone_has_passed_and_tom_cant_play_again_this_round(self):
        """
        Kathy and Tom each have face cards, kathy just passed and the total is at 30

        Expected: It is Tom's turn and he must pass.
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'hands': {'kathy': ['5e1e7e60ab'], 'tom': ['95f92b2f0c']},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'tom',
                'passed': ['kathy'],
                'run': [],
                'total': 30},
            'players': {
                'tom': 0,
                'kathy': 0
            },
            'scoring_stats':
                {'kathy': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }, 'tom': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }
            },
            'state': 'PLAY',
            'turn': 'kathy',
            'winning_score': 121,
        }
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['players']['tom'] == 0
        assert g['turn'] == 'tom'
        assert g['pegging']['total'] == 30
        assert bev.get_player_action('test', g['turn']) == 'PASS'

    @mock.patch('app.award_points', mock.MagicMock(return_value=True))
    def test_everyone_has_passed_and_tom_still_has_cards(self):
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'hands': {'kathy': ['5e1e7e60ab'], 'tom': ['95f92b2f0c']},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'tom',
                'passed': ['kathy', 'tom'],
                'run': [],
                'total': 30},
            'players': {
                'tom': 0,
                'kathy': 0
            },
            'scoring_stats':
                {'kathy': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }, 'tom': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }
            },
            'state': 'PLAY',
            'turn': 'kathy',
            'winning_score': 121,
        }
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['players']['tom'] == 1
        assert g['turn'] == 'kathy'
        assert g['pegging']['total'] == 0
        assert bev.get_player_action('test', g['turn']) == 'PLAY'

    def test_everyone_else_has_passed_and_tom_can_play_again_this_round(self):
        """
        Tom has an Ace, kathy just passed and the total is at 30

        Expected: It is now Tom's turn to play, he does not receive a point for go
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'hands': {'kathy': ['5e1e7e60ab'], 'tom': ['6d95c18472']},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'tom',
                'passed': ['kathy'],
                'run': [],
                'total': 30},
            'players': {
                'tom': 0,
                'kathy': 0
            },
            'state': 'PLAY',
            'turn': 'kathy',
            'winning_score': 121,
        }
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['players']['tom'] == 0
        assert g['turn'] == 'tom'
        assert g['pegging']['total'] == 30
        assert bev.get_player_action('test', g['turn']) == 'PLAY'

    def test_kathy_hit_thirtyone_still_has_cards(self):
        """
        Kathy just hit 31, and still has cards

        Expected: no new points for kathy, and its her turn with a fresh pegging area
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'hands': {'kathy': ['5e1e7e60ab'], 'tom': ['95f92b2f0c']},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'kathy',
                'passed': [],
                'run': [],
                'total': 31},
            'players': {
                'tom': 0,
                'kathy': 2
            },
            'turn': 'kathy',
            'winning_score': 121,
        }
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['players']['kathy'] == 2
        assert g['turn'] == 'tom'
        assert g['pegging']['total'] == 0

    def test_kathy_hit_thirtyone_has_no_cards_left_and_others_do(self):
        """
        Kathy just hit 31, and has no cards left. Tom has a card left

        Expected: no new points for kathy, and its now Tom's turn with a fresh pegging area
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'hands': {'kathy': [], 'tom': ['95f92b2f0c']},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'kathy',
                'passed': [],
                'run': [],
                'total': 31},
            'players': {
                'tom': 0,
                'kathy': 2
            },
            'turn': 'kathy',
            'winning_score': 121,
        }
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['players']['kathy'] == 2
        assert g['turn'] == 'tom'
        assert g['pegging']['total'] == 0

    def test_player_hit_thirtyone_and_no_one_has_cards_left(self):
        """
        Kathy just hit 31, and everyone is out of cards

        Expected: no new points for kathy, and it is now time to score hands
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'first_to_score': 'tom',
            'hands': {'kathy': [], 'tom': []},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'kathy',
                'passed': [],
                'run': [],
                'total': 31},
            'players': {
                'tom': 0,
                'kathy': 2
            },
            'turn': 'kathy',
            'winning_score': 121,
        }
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['players']['kathy'] == 2
        assert g['pegging']['total'] == 0
        assert g['state'] == 'SCORE'
        assert g['turn'] == 'tom'

    @mock.patch('app.award_points', mock.MagicMock(return_value=True))
    def test_no_one_has_cards_left(self):
        """
        Kathy just hit 24, and everyone is out of cards

        Expected: Kathy gets 1 point for go, and it is now time to score hands
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'first_to_score': 'tom',
            'hands': {'kathy': [], 'tom': []},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'kathy',
                'passed': [],
                'run': [],
                'total': 24},
            'players': {
                'tom': 0,
                'kathy': 2
            },
            'scoring_stats':
                {'kathy': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }, 'tom': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }
            },
            'turn': 'kathy',
            'winning_score': 121,
        }
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['players']['kathy'] == 3
        assert g['pegging']['total'] == 0
        assert g['state'] == 'SCORE'
        assert g['turn'] == 'tom'


class TestPlayScoring:

    @mock.patch('app.award_points', mock.MagicMock(return_value=False))
    def test_fifteen_two(self):
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'hands': {'kathy': ['6d95c18472', 'c6f4900f82'], 'tom': ['ace1293f8a']},
            'pegging': {
                'cards': ['4de6b73ab8'],  # eight of hearts
                'last_played': 'tom',
                'passed': [],
                'run': [],
                'total': 8},
            'players': {
                'tom': 0,
                'kathy': 0
            },
            'played_cards': {
                'kathy': [],
                'tom': []
            },
            'scoring_stats':
                {'tom': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }, 'kathy': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }
            },
            'state': 'PLAY',
            'turn': 'kathy',
            'winning_score': 121,
        }

        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        seven_of_clubs = 'c6f4900f82'
        just_won, points, points_source = bev.score_play('test', 'kathy', seven_of_clubs)
        assert not just_won
        bev.record_play('test', 'kathy', seven_of_clubs)
        g = json.loads(fake_redis.get('test'))
        assert g['players']['kathy'] == 2
        assert g['pegging']['total'] == 15
        assert set(g['pegging']['cards']) == set(['4de6b73ab8', 'c6f4900f82'])
        assert g['hands']['kathy'] == ['6d95c18472']

    @mock.patch('app.award_points', mock.MagicMock(return_value=False))
    def test_thirtyone(self):
        """
        Verify two points for 31
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'hands': {'kathy': ['6d95c18472', 'c6f4900f82'], 'tom': ['ace1293f8a']},
            'pegging': {
                'cards': ['4de6b73ab8', 'f6571e162f', 'c88523b677'],  # eight, ten, six
                'last_played': 'tom',
                'passed': [],
                'run': [],
                'total': 24},
            'players': {
                'tom': 0,
                'kathy': 0
            },
            'played_cards': {
                'kathy': ['f6571e162f'],
                'tom': ['4de6b73ab8', 'c88523b677']
            },
            'scoring_stats':
                {'tom': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }, 'kathy': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }
            },
            'state': 'PLAY',
            'turn': 'kathy',
            'winning_score': 121,
        }

        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        seven_of_clubs = 'c6f4900f82'
        just_won, points, points_source = bev.score_play('test', 'kathy', seven_of_clubs)
        assert not just_won
        bev.record_play('test', 'kathy', seven_of_clubs)
        g = json.loads(fake_redis.get('test'))
        assert set(g['pegging']['cards']) == set(['4de6b73ab8', 'f6571e162f', 'c88523b677', 'c6f4900f82'])
        assert g['hands']['kathy'] == ['6d95c18472']
        assert g['players']['kathy'] == 2
        assert g['pegging']['total'] == 31

    @mock.patch('app.award_points', mock.MagicMock(return_value=False))
    def test_pair(self):
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'hands': {'kathy': ['6d95c18472', 'c6f4900f82'], 'tom': ['ace1293f8a']},
            'pegging': {
                'cards': ['32f7615119'],  # seven of spades
                'last_played': 'tom',
                'passed': [],
                'run': [],
                'total': 7},
            'players': {
                'tom': 0,
                'kathy': 0
            },
            'played_cards': {
                'kathy': [],
                'tom': []
            },
            'scoring_stats':
                {'tom': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }, 'kathy': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }
            },
            'state': 'PLAY',
            'turn': 'kathy',
            'winning_score': 121,
        }

        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        seven_of_clubs = 'c6f4900f82'
        just_won, points, points_source = bev.score_play('test', 'kathy', seven_of_clubs)
        assert not just_won
        bev.record_play('test', 'kathy', seven_of_clubs)
        g = json.loads(fake_redis.get('test'))
        assert g['players']['kathy'] == 2
        assert g['pegging']['total'] == 14
        assert set(g['pegging']['cards']) == set(['32f7615119', 'c6f4900f82'])
        assert g['hands']['kathy'] == ['6d95c18472']

    @mock.patch('app.award_points', mock.MagicMock(return_value=False))
    def test_three_of_a_kind(self):
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'hands': {'kathy': ['6d95c18472', 'c6f4900f82'], 'tom': ['ace1293f8a']},
            'pegging': {
                'cards': ['32f7615119', '4f99bf15e5'],  # seven of spades, seven of diamonds
                'last_played': 'tom',
                'passed': [],
                'run': [],
                'total': 14},
            'players': {
                'tom': 2,
                'kathy': 0
            },
            'played_cards': {
                'kathy': ['32f7615119'],
                'tom': ['4f99bf15e5']
            },
            'scoring_stats':
                {'tom': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }, 'kathy': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }
            },
            'state': 'PLAY',
            'turn': 'kathy',
            'winning_score': 121,
        }

        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        seven_of_clubs = 'c6f4900f82'
        just_won, points, points_source = bev.score_play('test', 'kathy', seven_of_clubs)
        assert not just_won
        bev.record_play('test', 'kathy', seven_of_clubs)
        g = json.loads(fake_redis.get('test'))
        assert set(g['pegging']['cards']) == set(['32f7615119', '4f99bf15e5', 'c6f4900f82'])
        assert g['hands']['kathy'] == ['6d95c18472']
        assert g['pegging']['total'] == 21
        assert g['players']['kathy'] == 6

    @mock.patch('app.award_points', mock.MagicMock(return_value=False))
    def test_four_of_a_kind(self):
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'hands': {'kathy': ['6d95c18472', 'c6f4900f82'], 'tom': ['ace1293f8a']},
            'pegging': {
                'cards': ['32f7615119', '4f99bf15e5', 'def8effef6'],  # seven of spades, diamonds, hearts
                'last_played': 'tom',
                'passed': [],
                'run': [],
                'total': 21},
            'players': {
                'tom': 6,
                'kathy': 2
            },
            'played_cards': {
                'kathy': ['32f7615119'],
                'tom': ['4f99bf15e5', 'def8effef6']
            },
            'scoring_stats':
                {'tom': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }, 'kathy': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }
            },
            'state': 'PLAY',
            'turn': 'kathy',
            'winning_score': 121,
        }

        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        seven_of_clubs = 'c6f4900f82'
        just_won, points, points_source = bev.score_play('test', 'kathy', seven_of_clubs)
        assert not just_won
        bev.record_play('test', 'kathy', seven_of_clubs)
        g = json.loads(fake_redis.get('test'))
        assert set(g['pegging']['cards']) == set(['32f7615119', '4f99bf15e5', 'def8effef6', 'c6f4900f82'])  # all the sevens
        assert g['hands']['kathy'] == ['6d95c18472']
        assert g['pegging']['total'] == 28
        assert g['players']['kathy'] == 14

    @mock.patch('app.award_points', mock.MagicMock(return_value=False))
    def test_run_of_three(self):
        """
        test run of three scores three points
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'hands': {'kathy': ['6d95c18472', 'c6f4900f82'], 'tom': ['ace1293f8a']},
            'pegging': {
                'cards': ['4de6b73ab8', 'c88523b677'],  # eight, six
                'last_played': 'tom',
                'passed': [],
                'run': [],
                'total': 14},
            'players': {
                'tom': 0,
                'kathy': 0
            },
            'played_cards': {
                'kathy': ['32f7615119'],
                'tom': ['4f99bf15e5', 'def8effef6']
            },
            'scoring_stats':
                {'tom': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }, 'kathy': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }
            },
            'state': 'PLAY',
            'turn': 'kathy',
            'winning_score': 121,
        }

        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        seven_of_clubs = 'c6f4900f82'
        just_won, points, points_source = bev.score_play('test', 'kathy', seven_of_clubs)
        assert not just_won
        bev.record_play('test', 'kathy', seven_of_clubs)
        g = json.loads(fake_redis.get('test'))
        assert set(g['pegging']['cards']) == set(['4de6b73ab8', 'c88523b677', 'c6f4900f82'])  # all the sevens
        assert g['hands']['kathy'] == ['6d95c18472']
        assert g['pegging']['total'] == 21
        assert g['players']['kathy'] == 3

    def test_run_of_four(self):
        pass

    def test_run_of_five_and_fifteen_two(self):
        pass

    def test_fifteen_two_and_a_pair(self):
        pass

    def test_fifteen_two_and_three_of_a_kind(self):
        pass


class TestResetGameDict:

    def test_reset(self):
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'cards': CARDS,
            'crib': ['04a70825ff', '5c6bdd4fee', '9aa045dd99', 'bd4b01946d'],
            'cutter': 'brendon',
            'dealer': 'jason',
            'deck': ['d00bb3f3b7','64fe85d796','fc0f324620','276f33cf69','04f17d1351','f6571e162f','de1c863a7f',
                     'a482167f2a','ce46b344a3','ae2caea4bb','4dfe41e461','597e4519ac','c88623fa16','e26d0bead3',
                     'dd3749a1bc','83ef982410','4c8519af34','6d95c18472','b1fb3bec6f','c88523b677','32f7615119',
                     'd7ca85cf5e','30e1ddb610','85ba715700','a6a3e792b4','1d5eb77128','110e6e5b19','d1c9fde8ef',
                     '75e734d054','36493dcc05','e356ece3fc','95f92b2f0c','def8effef6','60575e1068','9eba093a9d',
                     'a20b6dac2c','f696d1f2d3','fa0873dd7d','ff2de622d8','3698fe0420'],
            'first_to_score': 'brendon',
            'hand_size': 6,
            'hands': {
                'brendon': [],
                'jason': []},
            'jokers': True,
            'name': 'homemovies',
            'ok_with_next_round': ['brendon', 'jason'],
            'pegging': {
                'cards': ['4de6b73ab8', 'e4fc8b9004', '5e1e7e60ab', 'ace1293f8a', 'd3a2460e93', '56594b3880',
                          '4f99bf15e5', 'c6f4900f82'],
                'passed': [], 'run': [], 'total': 0
            },
            'play_again': [],
            'played_cards': {'brendon': [],
                             'jason': []},
            'players': {'brendon': 12, 'jason': 11},
            'scored_hands': ['brendon', 'jason'],
            'state': 'SCORE',
            'turn': 'jason',
            'winning_score': 121}

        fake_redis.set('homemovies', json.dumps(game_dict))
        bev.cache = fake_redis

        bev.reset_game_dict('homemovies')

        expected = {
            "jokers": True,
            "name": 'homemovies',
            'players': {'brendon': 0, 'jason': 0},
            'scoring_stats':
                {'brendon': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }, 'jason': {
                    'a_play': 0,
                    'b_hand': 0,
                    'c_crib': 0
                }
            },
            "state": "INIT",
            "winning_score": 121,
        }

        g = json.loads(fake_redis.get('homemovies'))
        assert g == expected