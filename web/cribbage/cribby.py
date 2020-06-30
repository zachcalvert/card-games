import random

import giphy_client
from giphy_client.rest import ApiException
from pprint import pprint


class Cribby:

    def __init__(self):
        self.api_instance = giphy_client.DefaultApi()
        self.api_key = 'qUzMZY2GSYY8yk1nOk2cOsKF3naPtlZF'  # str | Giphy API Key.

    def gif(self, search_term):
        try:
            api_response = self.api_instance.gifs_search_get(self.api_key, search_term, limit=20)
        except ApiException as e:
            print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)
            return

        index = random.choice(range(20))
        gif = api_response.data[index]
        return gif.embed_url
