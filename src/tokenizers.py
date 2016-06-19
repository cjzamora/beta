# -*- code: utf-8 -*-

from external import stemmer
import utils

import re
import os

# generic string tokenizer
class GenericTokenizer(object):
    def tokenize(self, *texts):
        tokens_list = []

        for text in texts:
            if not text:
                continue
            tokens_list += text.lower().split()

        return ''.join(tokens_list)

# english string tokenizer
class EnglishTokenizer(object):
    DELIMITERS_RE = re.compile(r'[^a-z]+')
    MAX_LENGTH = 25
    MIN_LENGTH = 3

    def __init__(self):
        stop = os.path.join(utils.get_path('nlp'), 'english.stop')

        self.stemmer = stemmer.PorterStemmer()
        self.stop_words = self.load_stop_words(stop)

    def load_stop_words(self, path):
        with open(path, 'r') as f:
            stop_words = [str(word.strip()) for word in f]

        return set([self.stem(word) for word in set(stop_words)])

    def stem(self, word):
        return self.stemmer.stem(word, 0, len(word) - 1)

    def tokenize(self, *texts):
        tokens_list = []

        for text in texts:
            if not text:
                continue

            tokens = self.DELIMITERS_RE.split(text.lower())
            tokens = [self.stem(str(token)) for token in tokens if token and len(token) <= self.MAX_LENGTH]
            tokens = [token for token in tokens if len(token) >= self.MIN_LENGTH and token not in self.stop_words]
            tokens_list += tokens

        return tokens_list
