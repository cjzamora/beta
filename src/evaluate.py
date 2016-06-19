# -*- coding: utf-8 -*-

import math
import utils

from tokenizers import EnglishTokenizer, GenericTokenizer
from analyzers import TermFrequencyAnalyzer, LongestAnalyzer

class Evaluate:
    # extracted document to evaluate
    document = None
    # prediction data
    predicted = None
    # prediction labels
    labels = None
    # minimum score
    min_score = 2.0

    # gets the extracted data that
    # we can use later for evaluation.
    def __init__(self, document, predicted, labels):
        # set the document
        self.document = document
        # set the prediction data
        self.prediction = predicted
        # set the prediction labels
        self.labels = labels

    # score based on the given results
    def score(self, min_score=2.0):
        # set min score
        self.min_score = min_score

        # is title set?
        if 'title' in self.prediction:
            self.prediction['title'] = self.score_title(self.prediction['title'])
        else:
            print 'Finding a way to fetch title'

        # is description set?
        if 'description' in self.prediction:
            print 'Scoring Descriptions'
        else:
            print 'Finding a way to fetch description'

        # is srp set?
        if 'srp' in self.prediction:
            print 'Scoring srp'
        else:
            print 'Finding a way to fetch srp'

        # is discounted set?
        if 'discounted' in self.prediction:
            print 'Scoring discounted'
        else:
            print 'Finding a way to fetch discounteds'

        return self.prediction

    # score title based on the
    # possible points like, tf-idf
    # open graph attribute, possible
    # tag and element feature set.
    def score_title(self, titles):
        # load hints from document
        hints  = self.document['titles']
        # copy over titles
        object = titles

        # threshold
        threshold = {
            'x'     : [20, 900],
            'y'     : [120, 500],
            'size'  : 13
        }

        # possible tags
        tags = ['h1', 'h2', 'div']

        # get minimum score
        min_score = self.min_score

        # filter non empty text
        object = [i for i in object if len(i['text']) > 0]

        # list of titles
        titles = []

        # coordinates scoring
        for i in object:
            x = math.ceil(float(i['computed']['x']))
            y = math.ceil(float(i['computed']['y']))
            
            # above our threshold for coordinates?
            if ((float(x) >= float(threshold['x'][0])
            and  float(x) <= float(threshold['x'][1]))
            and (float(y) >= float(threshold['y'][0])
            and  float(y) <= float(threshold['y'][1]))):
                # set initial score
                i['score'] = 0.0

                # append it
                titles.append(i)

        # feature scoring
        for i in titles:
            # is possbile tag?
            if i['tag'] in tags:
                i['score'] += 1.0

            # is font size above or equal our threshold?
            if i['computed']['font-size'] >= threshold['size']:
                i['score'] += 1.0

            # open graph?
            if i['og'] == 'name':
                i['score'] += 0.5

        # get relevance score of texts
        titles = self.compute_lcs(titles, hints)

        # final results
        final = []

        # iterate on each high score
        for i in titles:
            # remove low scored
            if i['score'] >= min_score:
                # append results
                final.append(i)

        # do we have a result?
        if len(final) == 0:
            return final

        # sort based on high score
        final = self.sort_results(final)

        # do we have a result?
        return final[0:1]

    # get relavance score of the tokens
    # based on how many times it appears
    # on the given document.
    def compute_lcs(self, data, gold):
        # collect tokenized texts
        hints = []
        
        # iterate on each gold text    
        for text in gold:
            hints += EnglishTokenizer().tokenize(text)

        # we're going to use LCS
        analyzer = LongestAnalyzer()

        # set of tokens
        tokens = []
        # token index
        index  = 0

        # tokenize each texts
        for text in data:
            # tokenize each text
            tokens.append(EnglishTokenizer().tokenize(text['text']))
            # increment index
            index = index + 1

        # reset index
        index = 0

        # compute similarity
        for text in tokens:
            # get relevance score
            relevance = analyzer.get_similarity(text, hints)

            # update score
            data[index]['score'] += relevance

            # increment index
            index = index + 1

        return data

    # sort out based on highest score
    def sort_results(self, data):
        return sorted(data, key=lambda value: value['score'], reverse=True)         