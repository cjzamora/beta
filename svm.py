from sklearn import svm, preprocessing
from sklearn.feature_extraction import DictVectorizer
from sklearn.externals import joblib
import numpy as np
import simplejson as json
import sys
import random
import time
import math

sys.path.append('..')

from beta.src.preprocessing import Processor
from beta.src.classifier import Classifier
from beta.src import utils

# discrete - can only take certain values
# continuous - can take any values (within the given range)

# training_data = json.loads(open('data/training/152b50573f16ebc9172ade2da72fb218.json').read())
training_data = utils.load_training()
testing_data  = json.loads(open('tmp/ee080d57ea0bf3fdfa2b06a1d0c0bfad.json').read())

vectorizer = DictVectorizer()

training_processed = Processor().prepare_training(training_data, vectorizer)
testing_processed  = Processor().prepare_testing(testing_data['texts'], vectorizer)

print 'Before reduce: %s training samples.' % len(training_processed['features'])
training_processed = Processor().unique(training_processed)
print 'After reduce: %s training samples.' % len(training_processed['features'])

time.sleep(5)

training_labels   = training_processed['labels']

training_features = training_processed['features']
testing_features  = testing_processed['features']

# if model exists
if utils.file_exists('data/models/000.pkl'):
    print 'Loading cached trained model from data/models/000.pkl'
    clf = joblib.load('data/models/000.pkl')
else:
    print 'Learning and making the model'
    # clf = Classifier().linearSVC(training_features, training_labels)
    clf = Classifier().svc(training_features, training_labels, True)
    # clf = Classifier().sgdClassifier(training_features, training_labels)
    # clf = Classifier().kNeighborsClassifier(training_features, training_labels)
    # clf = Classifier().gaussianNB(training_features, training_labels)
    # clf = Classifier().ovrSVC(training_features, training_labels, True)

    # save model
    # joblib.dump(clf, 'data/models/000.pkl')

results = clf.predict(testing_features)

index = 0
predicted = {}

for i in results:
    if i != 'unknown':
        predicted[i] = []

extracted = Processor().prepare(testing_data['texts'])

for i in results:
    if i != 'unknown':
        text = testing_data['texts'][index]['text']

        if i == 'title':
            text = { 
                'label'     : i,
                'tag'       : testing_data['texts'][index]['element']['name'],
                'computed'  : extracted['features'][index], 
                'text'      : text[0] 
            }

        if i == 'description':
            text = { 
                'label'    : i,
                'tag'      : testing_data['texts'][index]['element']['name'],
                'computed' : extracted['features'][index],
                'text'     : '\n'.join(text[1:]) 
            }

        predicted[i].append(text)

    index = index + 1

# utils.pretty(predicted)
utils.write_file('public/test_results.json', predicted, True)



# -------->



def score_titles(object):
    threshold = {
        'x'     : [20, 900],
        'y'     : [120, 500],
        'size'  : 13
    }

    tags = ['h1', 'h2', 'div']

    min_score = 2.0

    # filter non empty text
    object = [i for i in object if len(i['text']) > 0]

    # list of titles
    titles = []

    # coordinates scoring
    for i in object:
        x = math.ceil(float(i['computed']['x']))
        y = math.ceil(float(i['computed']['y']))
        
        # above our threshold?
        if ((float(x) >= float(threshold['x'][0])
        and  float(x) <= float(threshold['x'][1]))
        and float((y) >= float(threshold['y'][0])
        and  float(y) <= float(threshold['y'][1]))):
            i['score'] = 0.0

            titles.append(i)

    # feature scoring
    for i in titles:
        if i['tag'] in tags:
            i['score'] += 1.0

        if i['computed']['font-size'] >= threshold['size']:
            i['score'] += 1.0

    # final results
    final = []

    # iterate on each high score
    for i in titles:
        if i['score'] >= min_score:
            final.append(i)


    utils.pretty(final)

score_titles(predicted['title'])