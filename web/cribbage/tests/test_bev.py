import fakeredis
import json
import mock

from cribbage import bev
from cribbage.cards import CARDS


class TestStartGame:

    def test_start_with_two_players(self):
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'name': 'cheers',
            'state': 'INIT',
            'players': {'sam': {'nickname': 'sam', 'points': 0}, 'diane': {'nickname': 'diane', 'points': 0}}
        }
        fake_redis.set('cheers', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.start_game('cheers')
        g = json.loads(fake_redis.get('cheers'))
        assert g['state'] == 'DEAL'
        assert g['hand_size'] == 6
        assert g['dealer'] != g['cutter']
        assert g['dealer'] != g['first_to_score']
        assert g['turn'] == g['dealer']

    def test_start_with_three_players(self):
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'name': 'cheers',
            'state': 'INIT',
            'players': {
                'sam': {'nickname': 'sam', 'points': 0},
                'diane': {'nickname': 'diane', 'points': 0},
                'norm': {'nickname': 'norm', 'points': 0}}
        }
        fake_redis.set('cheers', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.start_game('cheers')
        g = json.loads(fake_redis.get('cheers'))
        assert g['state'] == 'DEAL'
        assert g['hand_size'] == 5
        assert g['dealer'] != g['cutter']
        assert g['dealer'] != g['first_to_score']
        assert g['cutter'] != g['first_to_score']
        assert g['turn'] == g['dealer']


class TestDeal:

    def test_deal_unique_cards(self):
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'name': 'cheers',
            'state': 'DEAL',
            'players': {
                'sam': {'nickname': 'sam', 'points': 0},
                'diane': {'nickname': 'diane', 'points': 0},
                'norm': {'nickname': 'norm', 'points': 0}}
        }
        fake_redis.set('cheers', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.start_game('cheers')
        bev.deal_hands('cheers')
        g = json.loads(fake_redis.get('cheers'))
        assert g['state'] == 'DISCARD'
        for player in game_dict['players'].keys():
            assert player in g['hands'].keys()
            assert len(g['hands'][player]) == g['hand_size']


class TestDiscard:

    def test_first_discard(self):
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'name': 'cheers',
            'state': 'DEAL',
            'players': {
                'sam': {'nickname': 'sam', 'points': 0},
                'diane': {'nickname': 'diane', 'points': 0},
            }
        }
        fake_redis.set('cheers', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.start_game('cheers')
        bev.deal_hands('cheers')

        g = json.loads(fake_redis.get('cheers'))
        player_done, all_done = bev.discard('cheers', 'sam', g['hands']['sam'][0])
        assert not player_done
        assert not all_done
        assert g['state'] == 'DISCARD'

    def test_first_to_be_done_discarding(self):
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'name': 'cheers',
            'state': 'DEAL',
            'players': {
                'sam': {'nickname': 'sam', 'points': 0},
                'diane': {'nickname': 'diane', 'points': 0},
            }
        }
        fake_redis.set('cheers', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.start_game('cheers')
        bev.deal_hands('cheers')

        g = json.loads(fake_redis.get('cheers'))
        _, _ = bev.discard('cheers', 'sam', g['hands']['sam'][0])
        player_done, all_done = bev.discard('cheers', 'sam', g['hands']['sam'][1])
        assert player_done
        assert not all_done
        assert g['state'] == 'DISCARD'

    def test_all_have_discarded(self):
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'name': 'cheers',
            'state': 'DEAL',
            'players': {
                'sam': {'nickname': 'sam', 'points': 0},
                'diane': {'nickname': 'diane', 'points': 0},
            }
        }
        fake_redis.set('cheers', json.dumps(game_dict))
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


class TestNextPlayer:

    def test_next_must_pass(self):
        """
        Kathy and Tom each have face cards, tom just played and the total is at 30

        Expected: It is now kathy's turn and she must pass
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'hands': {'kathy': ['5e1e7e60ab'], 'tom': ['95f92b2f0c']},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'tom',
                'passed': [],
                'run': [],
                'total': 30},
            'players': {'kathy': {'nickname': 'kathy', 'points': 0},
                        'tom': {'nickname': 'tom', 'points': 0}},
            'state': 'PLAY',
            'turn': 'tom'}
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
            'hands': {'kathy': ['6d95c18472'], 'tom': ['ace1293f8a']},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'tom',
                'passed': [],
                'run': [],
                'total': 30},
            'players': {'kathy': {'nickname': 'kathy', 'points': 0},
                        'tom': {'nickname': 'tom', 'points': 0}},
            'state': 'PLAY',
            'turn': 'tom'}
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
            'hands': {'kathy': ['5e1e7e60ab'], 'tom': ['95f92b2f0c']},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'tom',
                'passed': ['kathy'],
                'run': [],
                'total': 30},
            'players': {'kathy': {'nickname': 'kathy', 'points': 0},
                        'tom': {'nickname': 'tom', 'points': 0}},
            'state': 'PLAY',
            'turn': 'kathy'}
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['players']['tom']['points'] == 0
        assert g['turn'] == 'tom'
        assert g['pegging']['total'] == 30
        assert bev.get_player_action('test', g['turn']) == 'PASS'

    @mock.patch('cribbage.app.award_points', mock.MagicMock(return_value=True))
    def test_everyone_has_passed_and_tom_still_has_cards(self):
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'hands': {'kathy': ['5e1e7e60ab'], 'tom': ['95f92b2f0c']},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'tom',
                'passed': ['kathy', 'tom'],
                'run': [],
                'total': 30},
            'players': {'kathy': {'nickname': 'kathy', 'points': 0},
                        'tom': {'nickname': 'tom', 'points': 0}},
            'state': 'PLAY',
            'turn': 'kathy'}
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['players']['tom']['points'] == 1
        assert g['turn'] == 'tom'
        assert g['pegging']['total'] == 0
        assert bev.get_player_action('test', g['turn']) == 'PLAY'

    def test_everyone_else_has_passed_and_tom_can_play_again_this_round(self):
        """
        Tom has an Ace, kathy just passed and the total is at 30

        Expected: It is now Tom's turn to play, he does not receive a point for go
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'hands': {'kathy': ['5e1e7e60ab'], 'tom': ['6d95c18472']},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'tom',
                'passed': ['kathy'],
                'run': [],
                'total': 30},
            'players': {'kathy': {'nickname': 'kathy', 'points': 0},
                        'tom': {'nickname': 'tom', 'points': 0}},
            'state': 'PLAY',
            'turn': 'kathy'}
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['players']['tom']['points'] == 0
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
            'hands': {'kathy': ['5e1e7e60ab'], 'tom': ['95f92b2f0c']},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'kathy',
                'passed': [],
                'run': [],
                'total': 31},
            'players': {'kathy': {'nickname': 'kathy', 'points': 2},
                        'tom': {'nickname': 'tom', 'points': 0}},
            'turn': 'kathy'}
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['players']['kathy']['points'] == 2
        assert g['turn'] == 'kathy'
        assert g['pegging']['total'] == 0

    def test_kathy_hit_thirtyone_has_no_cards_left_and_others_do(self):
        """
        Kathy just hit 31, and has no cards left. Tom has a card left

        Expected: no new points for kathy, and its now Tom's turn with a fresh pegging area
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'hands': {'kathy': [], 'tom': ['95f92b2f0c']},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'kathy',
                'passed': [],
                'run': [],
                'total': 31},
            'players': {'kathy': {'nickname': 'kathy', 'points': 2},
                        'tom': {'nickname': 'tom', 'points': 0}},
            'turn': 'kathy'}
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['players']['kathy']['points'] == 2
        assert g['turn'] == 'tom'
        assert g['pegging']['total'] == 0

    def test_player_hit_thirtyone_and_no_one_has_cards_left(self):
        """
        Kathy just hit 31, and everyone is out of cards

        Expected: no new points for kathy, and it is now time to score hands
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'first_to_score': 'tom',
            'hands': {'kathy': [], 'tom': []},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'kathy',
                'passed': [],
                'run': [],
                'total': 31},
            'players': {'kathy': {'nickname': 'kathy', 'points': 2},
                        'tom': {'nickname': 'tom', 'points': 0}},
            'turn': 'kathy'}
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['players']['kathy']['points'] == 2
        assert g['pegging']['total'] == 0
        assert g['state'] == 'SCORE'
        assert g['turn'] == 'tom'

    @mock.patch('cribbage.app.award_points', mock.MagicMock(return_value=True))
    def test_no_one_has_cards_left(self):
        """
        Kathy just hit 24, and everyone is out of cards

        Expected: Kathy gets 1 point for go, and it is now time to score hands
        """
        fake_redis = fakeredis.FakeRedis()
        game_dict = {
            'first_to_score': 'tom',
            'hands': {'kathy': [], 'tom': []},
            'pegging': {
                'cards': ['75e734d054', '60575e1068', '1d5eb77128'],
                'last_played': 'kathy',
                'passed': [],
                'run': [],
                'total': 24},
            'players': {'kathy': {'nickname': 'kathy', 'points': 2},
                        'tom': {'nickname': 'tom', 'points': 0}},
            'turn': 'kathy'}
        fake_redis.set('test', json.dumps(game_dict))
        bev.cache = fake_redis
        bev.next_player('test')
        g = json.loads(fake_redis.get('test'))
        assert g['players']['kathy']['points'] == 3
        assert g['pegging']['total'] == 0
        assert g['state'] == 'SCORE'
        assert g['turn'] == 'tom'


