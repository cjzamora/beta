# -*- coding: utf-8 -*-

from sklearn import svm
from sklearn.svm import SVC
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.multiclass import OneVsRestClassifier

# svm.SVC - 'linear'
class Classifier:
    # svc with linear kernel
    def svc(self, features, labels, log=False):
        # initialize svm svc
        classifier = svm.SVC(
            C=1.0, 
            kernel='linear', 
            degree=3, 
            gamma='auto', 
            coef0=0.0,
            shrinking=True, 
            probability=False, 
            tol=0.001,
            cache_size=2000, 
            class_weight='balanced', 
            verbose=log, 
            max_iter=-1, 
            decision_function_shape=None, 
            random_state=None)

        # fit training features with labels
        classifier.fit(features, labels)

        return classifier

    # ovr-svc
    def ovrSVC(self, features, labels, log=False):
        # initialze ovr
        ovr = OneVsRestClassifier(SVC(
            C=1.0, 
            kernel='linear', 
            degree=3, 
            gamma='auto', 
            coef0=0.0, 
            shrinking=True, 
            probability=False, 
            tol=0.001, 
            cache_size=200, 
            class_weight='balanced', 
            verbose=log, 
            max_iter=-1, 
            decision_function_shape=None, 
            random_state=None), n_jobs=1)

        ovr.fit(features, labels)

        return ovr

    # linear svc
    def linearSVC(self, features, labels, log=False):
        # initialize linear svc
        classifier = svm.LinearSVC(verbose=log)

        # fit training features with labels
        classifier.fit(features, labels)

        return classifier

    # sgd classifier
    def sgdClassifier(self, features, labels):
        # initialize sgd classifier
        classifier = SGDClassifier(loss='hinge', penalty='l2', shuffle=True)

        # fit training features with labels
        classifier.fit(features, labels)

        return classifier

    # k-neighbors classifier
    def kNeighborsClassifier(self, features, labels):
        # initialize k-neighbors classifier
        neighbors = KNeighborsClassifier(n_neighbors=1)
        
        # fit training features with labels
        neighbors.fit(features, labels) 

        return neighbors

    # gaussian naive bayes
    def gaussianNB(self, features, labels):
        # initialize gaussian nb
        gaussian = GaussianNB()

        # fit training features with labels
        gaussian.fit(features, labels)

        return gaussian