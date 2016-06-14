from sklearn import svm, preprocessing
from sklearn.feature_extraction import DictVectorizer
from sklearn.externals import joblib
import numpy as np
import simplejson as json
import sys
import random

sys.path.append('..')

from beta.src.preprocessing import Processor
from beta.src import utils

# discrete - can only take certain values
# continuous - can take any values (within the given range)

# training_data = json.loads(open('data/training/152b50573f16ebc9172ade2da72fb218.json').read())
training_data = utils.load_training()
testing_data  = json.loads(open('tmp/e438a9719116551ec977e97f45fd0259.json').read())

vectorizer = DictVectorizer()

training_processed = Processor().prepare_training(training_data, vectorizer)
testing_processed  = Processor().prepare_testing(testing_data['texts'], vectorizer)

training_labels   = training_processed['labels']

training_features = training_processed['features']
testing_features  = testing_processed['features']

# index = 0

# for i in training_features:
#     for k in testing_features:
#         if k['tag-path'] == i['tag-path'] and training_labels[index] != 'unknown':
#             print training_labels[index]
#             print i['tag-path']
#             print k['tag-path']
#             break

#     index = index + 1

# training_features = random.sample(training_features, len(training_features))

# if model exists
if utils.file_exists('data/models/000.pkl'):
    print 'Loading cached trained model from data/models/000.pkl'
    clf = joblib.load('data/models/000.pkl')
else:
    print 'Learning and making the model'
    clf = svm.SVC(
            C=1.0, 
            kernel='linear', 
            degree=3, 
            gamma='auto', 
            coef0=0.0, 
            shrinking=True, 
            probability=True, 
            tol=0.001, 
            cache_size=2000, 
            class_weight='balanced', 
            verbose=True, 
            max_iter=-1, 
            decision_function_shape=None, 
            random_state=None)

    clf.fit(training_features, training_labels)

    # save model
    # joblib.dump(clf, 'data/models/000.pkl')

results = clf.predict(testing_features)

index = 0
predicted = {}

for i in results:
    if i != 'unknown':
        predicted[i] = []

for i in results:
    if i != 'unknown':
        text = testing_data['texts'][index]['text']

        if i == 'title':
            text = text[0]

        if i == 'description':
            text = '\n'.join(text[1:])

        predicted[i].append(text)

    index = index + 1

utils.pretty(predicted)
utils.write_file('public/test_results.json', predicted, True)