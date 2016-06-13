# -*- coding: utf-8 -*-

from sklearn import preprocessing
from sklearn.feature_extraction import DictVectorizer

import numpy as np
import random

class Processor():
    CSS_UNITS = [
        'pt', 'px', 'vh', 'vw', 'em', '%',
        'ex', 'cm', 'mm', 'in', 'pc', 'vmin']

    # prepare data the same with training
    # data structure
    def prepare(self, object):
        # prepared object
        prepared = {
            'labels'    : [],
            'features'  : []
        }

        # iterate on each object
        for i in object:
            # append label
            prepared['labels'].append(i['label'])

            # get computed styles
            computed = i['computed']

            # convert units
            computed = self.convert_units(computed, ['font-size'])

            # set tag path
            computed['tag-path'] = ' > '.join(i['path'])

            # set bounding
            # computed['bouding-x'] = float(i['bound']['left'])
            # computed['bouding-y'] = float(i['bound']['top'])
            # computed['bouding-w'] = int(i['bound']['width'])
            # computed['bouding-h'] = int(i['bound']['height'])

            # append features
            prepared['features'].append(computed)

        return prepared

    # prepare training data set
    def prepare_training(self, object, vectorizer=None):
        # prepare features
        prepared = self.prepare(object)

        # vectorize features
        prepared['features'] = vectorizer.fit_transform(prepared['features']).toarray()

        # convert vector, i don't know if this will take effect
        prepared['features'] = np.array(prepared['features']).astype(np.float64)

        # scale features
        prepared['features'] = preprocessing.scale(prepared['features'])

        return prepared

    # prepare testing data set
    def prepare_testing(self, object, vectorizer=None):
        # prepare features
        prepared = self.prepare(object)

        # vectorize features
        prepared['features'] = vectorizer.transform(prepared['features']).toarray()

        # convert vector, i don't know if this will take effect
        prepared['features'] = np.array(prepared['features']).astype(np.float64)

        # scale features
        prepared['features'] = preprocessing.scale(prepared['features'])

        return prepared

    # process css units into decimal
    # representation with optional
    # parameter to select the styles
    # that needs to be converted
    def convert_units(self, object, filter=[]):
        computed = {}

        # iterate on each computed styles
        for k in object:
            # original value
            org = object[k]
            # percentage unit sign
            per = object[k][-1:]
            # other units
            val = object[k][-2:]

            # check if in filter
            if(len(filter) <= 0 or not k in filter):
                computed[k] = org
                continue

            # multiple values? e.g (0px 1px)
            if len(org.split(' ')) > 1:
                continue

            # is percentage?
            if per == '%':
                computed[k] = float(org[0:-1])

            # unit exists?
            if val in self.CSS_UNITS:
                try:
                    computed[k] = float(org[0:-2])
                except:
                    computed[k] = org

        return computed

    # reduce prepared dataset to balance
    # positive and negative samples
    def reduce(self, object):
        # positive data points
        positives = []
        # negative data points
        negatives = []

        index = 0

        # iterate on each data points
        for i in object['labels']:
            # get negatives
            if i == 'unknown':
                # append it to negative
                negatives.append({ 
                    'label'     : i,
                    'feature'  : object['features'][index]
                })
            else:
                # append it to positives
                positives.append({ 
                    'label'     : i,
                    'feature'  : object['features'][index]
                }) 
            
            index = index + 1

        # shuffle negatives
        random.shuffle(negatives, random.random)

        # cut negatives
        negatives = negatives[0:100]

        # stack features
        features = np.concatenate((positives, negatives), axis=0)

        # processed data
        processed = {
            'labels'    : [],
            'features'  : []
        }

        for data in features:
            processed['labels'].append(data['label'])
            processed['features'].append(data['feature'])

        return processed