import numpy as np

import os
import random
import csv
import pickle
from itertools import combinations

from card import CribbageDeck, CribbageHand

# Classifiers
from sklearn.ensemble import (
    RandomForestClassifier,
    AdaBoostClassifier,
)

PICKLE_FILE = 'classifier.pickle'
DATASET_CSV = 'throwing_dataset.csv'


def run_classifier(label, features, classifier, validation_type):
    accuracies = []

    for train_index, test_index in validation_type.split(features):
        label_train, features_train = \
            label[train_index], features[train_index]
        label_test, features_test = \
            label[test_index], features[test_index]

        classifier.fit(features_train, label_train)

        accuracies.append(classifier.score(features_test, label_test))

    avg = sum(accuracies) / len(accuracies)
    return avg, accuracies


def gen_dataset(n_iter=5000):
    deck = CribbageDeck()

    fp = open(DATASET_CSV, 'a+')
    writer = csv.writer(fp)

    for is_dealer in [0, 1]:
        for i in range(n_iter):
            best = None
            best_score = float("-inf")

            deck.shuffle()
            full_hand = deck.deal(6)

            for combo in combinations(full_hand, 4):
                thrown = full_hand[:]
                for card in combo:
                    thrown.remove(card)

                avg_hand = CribbageHand(combo).predict(deck.remaining_cards, quality=0.1)
                avg_crib = CribbageHand(thrown).predict(deck.remaining_cards, quality=0.1)

                if is_dealer:
                    hand_score = avg_hand + avg_crib
                else:
                    hand_score = avg_hand - avg_crib

                if hand_score > best_score:
                    best_score = hand_score
                    best = thrown

            data_point = [
                str(is_dealer),  # Whether you're dealing
                *[str(card.serialize()) for card in full_hand],  # Cards
                *[str(full_hand.index(card)) for card in best],  # Best to throw
            ]

            writer.writerow(data_point)

            if not i % 100:
                print(f"Trial {i} done")

    fp.close()


class RandomThrowingClassifier:
    def __init__(self):
        self.card_indexes = list(range(6))

    def throw(self):
        return random.sample(self.card_indexes, 2)


class ThrowingClassifier:
    def __init__(self, classifier=None):
        import copy
        self.index_classifiers = []

        if classifier is not None:
            for i in range(6):
                self.index_classifiers.append(copy.deepcopy(classifier))

    def train(self, csv_path):
        data = np.loadtxt(csv_path, delimiter=',')
        features = data[:, :-2]  # Features
        class_1 = data[:, -1]    # Classification
        class_2 = data[:, -2]

        classes = [[], [], [], [], [], []]
        for indexes in zip(class_1, class_2):
            # The indexes represent the two cards that should be thrown
            for i in range(6):
                classes[i].append(int(i in indexes))

        for i in range(6):
            self.index_classifiers[i].fit(features, classes[i])

    @classmethod
    def load(cls, pickle_file):
        obj = cls()
        obj.index_classifiers = pickle.load(pickle_file)
        return obj

    def dump(self, pickle_file):
        pickle.dump(self.index_classifiers, pickle_file)

    def throw(self, is_dealer, serialized_card_array):
        features = [int(is_dealer), *serialized_card_array]
        scores = []

        for clf in self.index_classifiers:
            scores.append(float(clf.predict_proba([features])[0][0]))

        best_two = sorted(enumerate(scores), key=lambda t: t[1])[:2]

        indices = [index for index, _ in best_two]

        assert len(indices) == 2

        return indices


def test_dataset(num_trials=1000):
    clf = AdaBoostClassifier(
        base_estimator=RandomForestClassifier(n_estimators=20),
        n_estimators=20,
        learning_rate=1,
    )

    if os.path.exists(PICKLE_FILE):
        actual_clf = ThrowingClassifier.load(PICKLE_FILE)
    else:
        actual_clf = ThrowingClassifier(clf)
        actual_clf.train(DATASET_CSV)
        actual_clf.dump(PICKLE_FILE)

    random_clf = RandomThrowingClassifier()

    actual_total = 0.0
    random_total = 0.0

    deck = CribbageDeck()

    for is_dealer in [0, 1]:
        for i in range(num_trials):
            deck.shuffle()
            full_hand = deck.deal(6)
            cards_serialized = [card.serialize() for card in full_hand]

            assert len(cards_serialized) == 6

            actual_indices_to_throw = actual_clf.throw(is_dealer, cards_serialized)

            actual_hand = CribbageHand([
                card for i, card in enumerate(full_hand)
                if i not in actual_indices_to_throw
            ])

            actual_crib = CribbageHand([
                card for i, card in enumerate(full_hand)
                if i in actual_indices_to_throw
            ])

            random_indices_to_throw = random_clf.throw()

            random_hand = CribbageHand([
                card for i, card in enumerate(full_hand)
                if i not in random_indices_to_throw
            ])

            random_crib = CribbageHand([
                card for i, card in enumerate(full_hand)
                if i in random_indices_to_throw
            ])

            if is_dealer:
                actual_score = actual_hand.predict(deck.remaining_cards, quality=0.5) + \
                               actual_crib.predict(deck.remaining_cards, quality=0.2)

                random_score = random_hand.predict(deck.remaining_cards, quality=0.5) + \
                               random_crib.predict(deck.remaining_cards, quality=0.2)
            else:
                actual_score = actual_hand.predict(deck.remaining_cards, quality=0.5) - \
                               actual_crib.predict(deck.remaining_cards, quality=0.2)

                random_score = random_hand.predict(deck.remaining_cards, quality=0.5) - \
                               random_crib.predict(deck.remaining_cards, quality=0.2)

            actual_total += actual_score
            random_total += random_score

    actual_score = actual_total / num_trials
    random_score = random_total / num_trials

    return actual_score, random_score


def main():
    # gen_dataset(10000)

    actual_score, random_score = test_dataset(1000)

    print(f"ACTUAL {actual_score}")
    print(f"RANDOM {random_score}")


if __name__ == '__main__':
    main()
