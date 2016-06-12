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

training_data = json.loads(open('data/training/7c8d733af92973d7284e6bc1bd75f745.json').read())
testing_data  = json.loads(open('tmp/537f5cc1d2bfb4b6b971818ff3ae0697.json').read())

training_parsed = Processor().prepare(training_data)
testing_parsed  = Processor().prepare(testing_data['texts'])

vectorizer = DictVectorizer()

training_labels     = training_parsed['labels']
training_features   = vectorizer.fit_transform(training_parsed['features']).toarray()

testing_features    = vectorizer.transform(testing_parsed['features']).toarray()

training_features = np.array(training_features).astype(np.float64)
testing_features  = np.array(testing_features).astype(np.float64)

clf = svm.SVC(kernel='linear')

clf.fit(training_features, training_labels)

results = clf.predict(testing_features)

index = 0

for i in results:
    if i != 'unknown':
        text = testing_data['texts'][index]['text']
        text = '\n'.join(text)

        print i + ': ' + text[0:100]

    index = index + 1