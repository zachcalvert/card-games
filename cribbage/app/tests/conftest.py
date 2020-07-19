import pytest

from app.cards import CARDS


@pytest.fixture(scope="module")
def two_player_game_unstarted():
    return {
        'name': 'cheers',
        'state': 'INIT',
        'players': {'sam': 0, 'diane': 0}
    }


@pytest.fixture(scope="module")
def three_player_game_unstarted():
    return {
        'name': 'cheers',
        'state': 'INIT',
        'players': {'sam': 0, 'diane': 0,'norm': 0}
    }

@pytest.fixture(scope="module")
def two_player_game_fully_dealt():
    return {
        'cards': CARDS,
        'crib': ['04a70825ff', '5c6bdd4fee', '9aa045dd99', 'bd4b01946d'],
        'cutter': 'brendon',
        'dealer': 'jason',
        'deck': ['d00bb3f3b7', '64fe85d796', 'fc0f324620', '276f33cf69', '04f17d1351', 'f6571e162f', 'de1c863a7f',
                 'a482167f2a', 'ce46b344a3', 'ae2caea4bb', '4dfe41e461', '597e4519ac', 'c88623fa16', 'e26d0bead3',
                 'dd3749a1bc', '83ef982410', '4c8519af34', '6d95c18472', 'b1fb3bec6f', 'c88523b677', '32f7615119',
                 'd7ca85cf5e', '30e1ddb610', '85ba715700', 'a6a3e792b4', '1d5eb77128', '110e6e5b19', 'd1c9fde8ef',
                 '75e734d054', '36493dcc05', 'e356ece3fc', '95f92b2f0c', 'def8effef6', '60575e1068', '9eba093a9d',
                 'a20b6dac2c', 'f696d1f2d3', 'fa0873dd7d', 'ff2de622d8', '3698fe0420'],
        'first_to_score': 'brendon',
        'hand_size': 6,
        'hands': {
            'brendon': ['4de6b73ab8', 'e4fc8b9004', '5e1e7e60ab', 'ace1293f8a'],
            'jason': ['d3a2460e93', '56594b3880', '4f99bf15e5', 'c6f4900f82']},
        'jokers': False,
        'name': 'homemovies',
        'ok_with_next_round': [],
        'pegging': {'cards': [], 'passed': [], 'run': [], 'total': 0},
        'play_again': [],
        'played_cards': {'brendon': [], 'jason': []},
        'players': {'brendon': 0, 'jason': 0},
        'scored_hands': [],
        'state': 'CUT',
        'turn': 'jason',
        'winning_score': 121
    }