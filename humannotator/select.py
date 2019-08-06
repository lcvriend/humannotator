# standard library
import re


class Select():
    pass


class SelectSample():
    pass


class SelectPhrase():
    def __init__(self, phrase):
        self.phrase = phrase
        self.regex = rf"\b{phrase}\b"
