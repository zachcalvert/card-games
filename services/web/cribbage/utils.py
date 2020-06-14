from .cards import CARDS


def rotate_turn(current, players):
    """
    :param current:
    :param players:
    :return:
    """
    try:
        next_player = players[players.index(current) + 1]
    except IndexError:
        next_player = players[0]
    return next_player


def play_or_pass(card_values, pegging_total):
    """
    :param cards:
    :param pegging_total:
    :return: action
    """
    action = 'PASS'
    print('Cards are : {}'.format(card_values))
    remainder = 31 - pegging_total
    if any(int(value) <= remainder for value in card_values):
        action = 'PLAY'
    return action
