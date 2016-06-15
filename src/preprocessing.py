# -*- coding: utf-8 -*-

from sklearn import preprocessing
from sklearn.feature_extraction import DictVectorizer

import numpy as np
import random

class Processor():
    # pre-defined css units
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

            # select properties
            computed = self.select_properties(i['computed'])

            # convert units
            computed = self.convert_units(computed)

            # set tag path
            computed['tag-path'] = self.process_selectors(i['selector'])

            # set area (requires scaling)
            # computed['area'] = float(i['bound']['height'] * i['bound']['width'])

            # set bounding (requires scaling)
            # computed['bounding-x'] = float(i['bound']['left'])
            # computed['bounding-y'] = float(i['bound']['top'])
            # computed['bounding-w'] = float(i['bound']['width'])
            # computed['bounding-h'] = float(i['bound']['height'])

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
        prepared['features'] = np.array(prepared['features']).astype(np.float32)

        # scale features
        # prepared['features'] = preprocessing.scale(prepared['features'])

        return prepared

    # prepare testing data set
    def prepare_testing(self, object, vectorizer=None):
        # prepare features
        prepared = self.prepare(object)

        # vectorize features
        prepared['features'] = vectorizer.transform(prepared['features']).toarray()

        # convert vector, i don't know if this will take effect
        prepared['features'] = np.array(prepared['features']).astype(np.float32)

        # scale features
        # prepared['features'] = preprocessing.scale(prepared['features'])

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

    # consolidate selectors either just the plain
    # element or with classes id included, we are
    # going to build something like, div#id.cls > h1.cls etc.
    def process_selectors(self, selectors, withIdCls=False):
        # processed selectors
        processed = []

        # iterate on each selectors
        for selector in selectors:
            # tag name
            tag = selector['name']

            # do we have an id?
            if len(selector['id']) > 0 and withIdCls == True:
                # set id on tag
                tag = tag + '#' + selector['id']

            # do we have classes?
            if len(selector['classes']) and withIdCls == True:
                # combine classes
                classes = '.'.join(selector['classes'])

                # append it
                tag = tag + '.' + classes

            # push to processed
            processed.append(tag)

        return ' > '.join(processed)

    # select css properties
    def select_properties(self, properties):
        # pick this properties
        # --------------------
        # font-size - 12px
        # font-weight - normal
        # line-height - normal
        # text-decoration - none
        # text-align - left
        # letter-spacing - normal
        
        selected = {}

        # if font-size
        if 'font-size' in properties:
            selected['font-size'] = properties['font-size']
        else:
            selected['font-size'] = '12px'

        # if font-weight
        if 'font-weight' in properties:
            selected['font-weight'] = properties['font-weight']
        else:
            selected['font-weight'] = 'normal'

        # if line-height
        if 'line-height' in properties:
            selected['line-height'] = properties['line-height']
        else:
            selected['line-height'] = 'normal'

        # if text-decoration
        if 'text-decoration' in properties:
            selected['text-decoration'] = properties['text-decoration']
        else:
            selected['text-decoration'] = 'none'

        # if text-align
        if 'text-align' in properties:
            selected['text-align'] = properties['text-align']
        else:
            selected['text-align'] = 'left'

        if 'letter-spacing' in properties:
            selected['letter-spacing'] = properties['letter-spacing']
        else:
            selected['letter-spacing'] = '12px'

        return selected

    # processed data samples and retain
    # unique data points to avoid collision
    # between positive and negative data points
    def unique(self, samples):
        # get the features
        features = samples['features']

        # iterate on the array
        processed = (np.ascontiguousarray(features)
        .view(np.dtype((np.void, features.dtype.itemsize * features.shape[1]))))

        # get the unique set of arrays
        _, idx = np.unique(processed, return_index=True)

        # get unique labels
        labels = []

        # iterate on each indexes
        for i in idx:
            # get the label
            labels.append(samples['labels'][i])

        # return new label and feature set
        unique = {
            'labels'   : labels,
            'features' : features[idx]
        }

        return unique