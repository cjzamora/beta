from sklearn import svm, preprocessing
from sklearn.feature_extraction import DictVectorizer
import numpy as np
import simplejson as json
import sys

sys.path.append('..')

from beta.src.preprocessing import Processor
from beta.src import utils

# discrete - can only take certain values
# continuous - can take any values (within the given range)

# training_data = json.loads(open('data/training/152b50573f16ebc9172ade2da72fb218.json').read())
training_data = utils.load_training()
testing_data  = json.loads(open('tmp/3f8c73d049f1265bdfdb910c6ea4f97e.json').read())

vectorizer = DictVectorizer()

training_processed = Processor().prepare_training(training_data, vectorizer)
testing_processed  = Processor().prepare_testing(testing_data['texts'], vectorizer)

training_labels   = training_processed['labels']

training_features = training_processed['features']
testing_features  = testing_processed['features']

clf = svm.SVC(
        C=1.0, 
        kernel='linear', 
        degree=3, 
        gamma='auto', 
        coef0=0.0, 
        shrinking=True, 
        probability=False, 
        tol=0.001, 
        cache_size=2000, 
        class_weight=None, 
        verbose=True, 
        max_iter=-1, 
        decision_function_shape='ovr', 
        random_state=None)

clf.fit(training_features, training_labels)

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

print predicted
utils.write_file('public/test_results.json', predicted, True)