import os
import random

import giphy_client
from giphy_client.rest import ApiException
from pprint import pprint

giphy_api_instance = giphy_client.DefaultApi()
giphy_api_key = 'qUzMZY2GSYY8yk1nOk2cOsKF3naPtlZF'

ZERO_POINT_RESPONSES = [
    'whelp',
    'woof!',
    'that sucks lol',
    '😐',
    '😩😩😩',
    'well.. huh',
    'lmao',
    'bruh..',
]

GREAT_HAND_RESPONSES = [
    'wow!',
    'nice hand!',
    '👏👏👏',
    'you go glenn coco!',
]


def find_gif(search_term):
    try:
        api_response = giphy_api_instance.gifs_search_get(giphy_api_key, search_term, limit=20)
    except ApiException as e:
        print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)
        return

    index = random.choice(range(20))
    gif = api_response.data[index]
    return gif.embed_url


def find_animation(type, instance):
    instances = set([instance.strip('.gif') for instance in os.listdir('cribbage/static/img/{}/'.format(type))])
    if instance in instances:
        return True, []
    return False, instances
