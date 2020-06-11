from cribbage.cards import CARDS


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


def play_or_pass(cards, pegging_total):
    """
    :param cards:
    :param pegging_total:
    :return: action
    """
    action = 'PASS'
    card_values = [CARDS.get(card)['value'] for card in cards]
    remainder = 31 - pegging_total
    if any(value <= remainder for value in card_values):
        action = 'PLAY'
    return action


def next_player_who_can_take_action_this_round(game_dict):
    """
    Return the next player who still has cards and has not passed
    :return: nickname
    """
    if game_dict['pegging']['total'] >= 31:
        # we should never get above 31, but just in case
        return None

    player_order = list(game_dict['players'].keys())
    starting_point = player_order.index(game_dict['turn'])
    players_to_check_in_order = player_order[starting_point + 1:] + player_order[:starting_point + 1]
    for player in players_to_check_in_order:
        if player in game_dict['pegging']['passed']:  # skip if they've passed
            continue
        if not game_dict['hands'][player]:  # or have no cards left
            continue

        # if this player is the one who last played, and they also have to pass, they don't count
        if player == game_dict['pegging']['last_played']:
            next_action = play_or_pass(game_dict['hands'][player], game_dict['pegging']['total'])
            if next_action == 'PASS':
                return None

        return player

    print('everyone has already passed or has no cards left')
    return None


def next_player_who_can_play_at_all(game_dict):
    """
    Return the next player who still has cards
    :return:
    """
    player_order = list(game_dict['players'].keys())
    starting_point = player_order.index(game_dict['turn'])
    players_to_check_in_order = player_order[starting_point + 1:] + player_order[:starting_point + 1]
    for player in players_to_check_in_order:
        if not game_dict['hands'][player]:  # has no cards left
            continue
        return player
    return None
