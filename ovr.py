from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import CCA
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
# training_data = utils.load_training()
# testing_data  = json.loads(open('tmp/609e472954b07f4edfa3d2e337e74c9f.json').read())

# vectorizer = DictVectorizer()

# training_processed = Processor().prepare_training(training_data, vectorizer)
# testing_processed  = Processor().prepare_testing(testing_data['texts'], vectorizer)

# training_labels   = training_processed['labels']

# training_features = training_processed['features']
# testing_features  = testing_processed['features']

# training_features = random.sample(training_features, len(training_features))

X = [
    [0., 2., 1., 3., 0., 5., 2., 3., 4.],
    [0., 0., 4., 1., 2., 3., 0., 0., 0.],
    [0., 1., 3., 2., 1., 4., 1., 3., 6.]]

Y = [0, 1, 2]

y = [[0., 0., 4., 1., 2., 3., 0., 0., 0.]]

clf = OneVsRestClassifier(SVC(kernel='linear', verbose=True))
clf.fit(X, y)

results = clf.predict(Y)

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