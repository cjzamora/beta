from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC
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
testing_data  = json.loads(open('tmp/34d300364b6528c05e9362ef8adce7d1.json').read())

vectorizer = DictVectorizer()

training_processed = Processor().prepare_training(training_data, vectorizer)
testing_processed  = Processor().prepare_testing(testing_data['texts'], vectorizer)

training_labels   = training_processed['labels']

training_features = training_processed['features']
testing_features  = testing_processed['features']

# training_features = random.sample(training_features, len(training_features))

