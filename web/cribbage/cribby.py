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

BLOBS = {'hype', 'sigh', 'wink', 'bored', 'sad', 'gimme', 'rage', 'panic', 'smile', 'grimace', 'wat',
         'dancer', 'party', 'cheers', 'conga', 'yay', 'mad', 'sweating', 'stare', 'goodnight', 'babyangel'}


def find_gif(search_term):
    try:
        api_response = giphy_api_instance.gifs_search_get(giphy_api_key, search_term, limit=20)
    except ApiException as e:
        print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)
        return

    index = random.choice(range(20))
    gif = api_response.data[index]
    return gif.embed_url


def find_blob(blob_request):
    """
    Look for the blob with the given param. If can't find it, return a blob with text saying as much.
    """
    if blob_request in BLOBS:
        print('found the request blob: {}'.format(blob_request))
        return blob_request
    return False
