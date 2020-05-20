import numpy as np

import classificator
import parser_midi


COUNT_NOTES = 88
THE_ORDER_OF_THE_CHAIN = 3


class FitterChords:
    def __init__(self):
        self.classifiers = []

    @staticmethod
    def process_train(highest_notes, chords):
        x_train, y_train = [], []
        for time in highest_notes.keys():
            current_pitch = np.zeros((1, 88))
            current_pitches = np.zeros((1, 88))
            current_pitch[0][highest_notes[time].note] = 1
            x_train.append(current_pitch[0])
            for pitch in chords[time]:
                current_pitches[0][pitch.note] = 1
            y_train.append(np.array(current_pitches))
        x_train = np.array(list(parser_midi.get_ngrams(np.array(x_train), THE_ORDER_OF_THE_CHAIN)))
        x_train = np.array(list(map(lambda x: np.hstack(x).ravel(), x_train)))
        y_train = [FitterChords.get_y_train(i, y_train) for i in range(COUNT_NOTES)]
        return np.array(x_train), np.array(y_train)

    @staticmethod
    def get_y_train(i, y):
        mask = np.zeros((1, COUNT_NOTES))
        mask[0][i] = 1
        return np.array(list(map(lambda x: (x @ mask.transpose())[0], y)))[THE_ORDER_OF_THE_CHAIN - 1:]

    @staticmethod
    def process_test(pitches_extractor, res):
        x = map(lambda x: pitches_extractor.coder.decode(x)[0].note, res)
        x_test = []
        for pitch in x:
            current_pitch = np.zeros((1, 88))
            if pitch is not None:
                current_pitch[0][pitch] = 1
                x_test.append(current_pitch[0])
        x_test = np.array(x_test)
        x_test = np.array(list(parser_midi.get_ngrams(x_test, THE_ORDER_OF_THE_CHAIN)))
        return np.array(list(map(lambda x: np.hstack(x).ravel(), x_test)))

    def create_and_fit_classifiers(self, x_train, y_train):
        for i in range(COUNT_NOTES):
            classifier = classificator.BinaryPitchClassificator(i)
            classifier.fit(x_train, y_train[i])
            self.classifiers.append(classifier)

    def predict(self, x_test):
        predictions = []
        for cl in self.classifiers:
            predictions.append(cl.predict(x_test))
        return predictions