from app import jim

KNOWN_BLOBS = {'dundundun', 'party', 'cry', 'bored', 'yep', 'bongo', 'grimace', 'eyeroll', 'smile',
               'goodnight', 'nervous', 'stare', 'hype', 'triggered', 'wink', 'gimme', 'wave', 'ugh', 'conga', 'panic',
               'confused', 'happy', 'aww', 'cheers', 'babyangel', 'nope', 'wat', 'yay', 'kiss', 'rage', 'dancer'}

KNOWN_MEOWS = {'yay', 'maracas', 'stretch', 'thinking', 'peekaboo', 'smug', 'sip', 'bounce', 'party', 'hero', 'rage',
               'avicii', 'bongo', 'popcorn', 'wat', 'wave', 'shocked', 'gimme'}

KNOWN_PIGGYS = {'kiss', 'serenade', 'scoot', 'sparkle', 'trot', 'hello', 'hugs', 'boom', 'cry', 'wave', 'happy',
                'silly', 'angry'}


class TestFindAnimation:

    def test_find_blob(self):
        request = 'wave'
        assert jim.find_animation('blob', request) == (True, [])

    def test_unknown_blob(self):
        request = 'not_a_blob'
        assert jim.find_animation('blob', request) == (False, KNOWN_BLOBS)

    def test_find_meow(self):
        request = 'wave'
        assert jim.find_animation('meow', request) == (True, [])

    def test_unknown_meow(self):
        request = 'not_a_blob'
        assert jim.find_animation('meow', request) == (False, KNOWN_MEOWS)

    def test_find_piggy(self):
        request = 'wave'
        assert jim.find_animation('piggy', request) == (True, [])

    def test_unknown_piggy(self):
        request = 'not_a_blob'
        assert jim.find_animation('piggy', request) == (False, KNOWN_PIGGYS)
