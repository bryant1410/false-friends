#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import sys

import numpy as np

PARENT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/..')
sys.path.insert(0, PARENT_DIR)

from falsefriends import bilingual_lexicon, classifier, linear_trans, util, word_vectors

#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

model_es = word_vectors.load_model(PARENT_DIR + '/resources/big/jairo/vectors_es.bin')
model_pt = word_vectors.load_model(PARENT_DIR + '/resources/big/jairo/vectors_pt.bin')

lexicon = bilingual_lexicon.most_frequent_bilingual_lexicon_based_on_external_count(model_es.vocab, model_pt.vocab)

logging.info("getting vector pairs")
X, Y = zip(*word_vectors.bilingual_lexicon_vectors(model_es, model_pt, bilingual_lexicon=lexicon))

X_array = np.vstack(X)
Y_array = np.vstack(Y)

logging.info("Computing linear transformations and classifying with cross-validation...")
print("  N\t Acc")

training_friend_pairs = util.read_words(PARENT_DIR + '/resources/sepulveda2011_training.txt')
testing_friend_pairs = util.read_words(PARENT_DIR + '/resources/sepulveda2011_testing.txt')
friend_pairs = training_friend_pairs + testing_friend_pairs

clf = classifier.build_classifier()

sizes = [50, 100, 500, 1000, 5000, 10000, 15000, 20000, 25000, 30000, len(X)]
sizes = [size for size in sizes if size <= len(X)]
for size in sizes:
    indices = np.random.choice(list(range(X_array.shape[0])), size, replace=False)

    T = linear_trans.linear_transformation(list(X_array[indices, :]), list(Y_array[indices, :]))
    linear_trans.save_linear_transformation(PARENT_DIR
                                            + '/resources/big/jairo/linear_trans_most_frequent_{}'.format(size), T)

    X, y = classifier.features_and_labels(friend_pairs, model_es, model_pt, T)

    measures = classifier.classify_with_cross_validation(X, y, clf=clf)

    print("{: >5}\t{:0.4f}".format(size, measures['Accuracy'][0]))