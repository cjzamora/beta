# -*- coding: utf-8 -*-

import math
import utils

from preprocessing import Processor
from tokenizers import EnglishTokenizer, GenericTokenizer
from analyzers import TermFrequencyAnalyzer, LongestAnalyzer

class Evaluate:
    # extracted document to evaluate
    document = None
    # processed documents
    processed = None
    # prediction data
    predicted = None
    # prediction labels
    labels = None
    # minimum score
    min_score = 5.0

    # gets the extracted data that
    # we can use later for evaluation.
    def __init__(self, document, predicted, labels):
        # set the document
        self.document = document
        # set the processed documents
        self.processed = Processor().prepare(document['texts'])
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
            print None

        # is description set?
        if 'description' in self.prediction:
            self.prediction['description'] = self.score_description(self.prediction['description'])
        else:
            print None

        # is srp set?
        if 'srp' in self.prediction:
            self.prediction['srp'] = self.score_srp(self.prediction['srp'])
        else:
            print None

        # is discounted set?
        if 'discounted' in self.prediction:
            self.prediction['discounted'] = self.score_discounted(self.prediction['discounted'])
        else:
            print None

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
        tags = ['h1', 'h2', 'div', 'span']

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

    # score description based on the
    # possible points like title, plus
    # the term frequency and text length
    def score_description(self, descriptions):
        # load hints from document
        hints  = self.document['gold_text']
        # copy over descriptions
        object = descriptions

        # threshold
        threshold = {
            'x'     : [20, 900],
            'y'     : [200, 1500],
            'size'  : 10
        }

        # possbile tags
        tags = ['div', 'p', 'ul']

        # get minimum score
        min_score = self.min_score

        # filter non empty text
        object = [i for i in object if len(i['text']) > 0]

        # list of descriptions
        descriptions = []

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
                descriptions.append(i)

        # feature scoring
        for i in descriptions:
            # is possbile tag?
            if i['tag'] in tags:
                i['score'] += 1.0

            # is font size above or equal our threshold?
            if i['computed']['font-size'] >= threshold['size']:
                i['score'] += 1.0

            # open graph?
            if i['og'] == 'description':
                i['score'] += 0.5

        utils.pretty(descriptions)

        # compute relavance score of text,
        # NOTE: this is temporary, we might need
        # to change this to tf-idf or mcs if possible
        # but right now, lcs works great.
        descriptions = self.compute_lcs(descriptions, hints)

        # final results
        final = []

        # iterate on each high score
        for i in descriptions:
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

    def fallback_description(self):
        threshold = {
            'x'     : [20, 900],
            'y'     : [200, 1500],
            'size'  : 10
        }

        # fallback data
        fallback = []
        # index
        index     = 0

        # iterate on each results
        for i in self.processed['features']:
            x = math.ceil(float(i['x']))
            y = math.ceil(float(i['y']))
            
            # above our threshold for coordinates?
            if (not (float(x) >= float(threshold['x'][0])
            and  float(x) <= float(threshold['x'][1]))
            and (float(y) >= float(threshold['y'][0])
            and  float(y) <= float(threshold['y'][1]))):
                continue;

            # get the text
            text = self.document['texts'][index]['text']

            # check ogprop
            if not 'ogprop' in self.document['texts'][index]:
                self.document['texts'][index]['ogprop'] = ''

            # generate information
            data = {
                'tag'       : self.document['texts'][index]['element']['name'],
                'og'        : self.document['texts'][index]['ogprop'],
                'computed'  : i,
                'text'      : '\n'.join(text)
            }

            # append the information
            fallback.append(data)

            index = index + 1

        descriptions = self.score_description(fallback)

        print descriptions

    def score_srp(self, srps):
        return srps[0:1]

    def score_discounted(self, discounted):
        return discounted[0:1]

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