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


def rotate_reverse(current, players):
    """
    :param current:
    :param players:
    :return:
    """
    try:
        next_player = players[players.index(current) - 1]
    except IndexError:
        next_player = players[-1]
    return next_player


def play_or_pass(card_values, pegging_total):
    """
    :param cards:
    :param pegging_total:
    :return: action
    """
    action = 'PASS'
    remainder = 31 - pegging_total
    if any(int(value) <= remainder for value in card_values):
        action = 'PLAY'
    return action


def card_object_from_text(text):
    """
    Expects text in the form: 'Ace of diamonds', 'Ten of clubs', 'Queen of spades'

    :return: card_dict of the corresponding card
    """
    # find the requested card in CARDS
    rank, suit = text.split(' of ')
    suits_of_that_rank = {k: v for k, v in CARDS.items() if v['name'] == rank}
    card_dict = {k: v for k, v in suits_of_that_rank.items() if v['suit'] == suit}
    return card_dict


def card_text_from_id(card_id):
    """
    Return text representation of card
    :param card_id:
    :return:
    """
    if 'joker' in card_id:
        return 'a joker'
    else:
        card = CARDS[card_id]
        return 'the {} of {}'.format(card['name'], card['suit'])