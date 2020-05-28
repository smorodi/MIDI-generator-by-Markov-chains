import numpy as np
from config import THE_ORDER_OF_THE_CHAIN, COUNT_NOTES
import classificator
import parser_midi


class FitterChords:
    def __init__(self):
        self.classifiers = []

    @staticmethod
    def process_train_for_one(highest_notes, chords, programs_in_channels):
        # programs_uniq = np.unique(list(map(lambda x: x[0], programs_in_channels.values())))
        # programs = dict()
        # for i in range(len(programs_uniq)):
        #     programs[programs_uniq[i]] = i
        # count_programs = len(programs.keys())
        programs = dict()
        channels = list(programs_in_channels.keys())
        print(channels)
        for i in range(len(programs_in_channels.keys())):
            programs[channels[i]] = i
        count_programs = len(programs.keys())
        x_train, y_train = [], []
        print(str(len(highest_notes)) + " - вот столько разных времен")
        for time in highest_notes.keys():
            current_pitch = np.zeros((1, COUNT_NOTES))
            current_pitches = np.zeros((1, COUNT_NOTES * count_programs))
            current_pitch[0][highest_notes[time].note] = 1
            x_train.append(current_pitch[0])
            for pitch in chords[time]:
                number_of_programms = programs[pitch.channel]
                current_pitches[0][number_of_programms * COUNT_NOTES + pitch.note] = 1
            y_train.append(np.array(current_pitches))
        x_train = np.array(list(parser_midi.get_ngrams(np.array(x_train), THE_ORDER_OF_THE_CHAIN)))
        x_train = np.array(list(map(lambda x: np.hstack(x).ravel(), x_train)))
        y_train = [FitterChords.get_y_train_for_ones(i, y_train, count_programs)
                   for i in range(COUNT_NOTES * count_programs)]
        return np.array(x_train), np.array(y_train), count_programs

    @staticmethod
    def get_y_train_for_ones(i, y, count_programms):
        mask = np.zeros((1, COUNT_NOTES * count_programms))
        mask[0][i] = 1
        y_train = np.array(list(map(lambda x: int(i in np.where(x == 1)[1]), y)))[THE_ORDER_OF_THE_CHAIN - 1:]
        test = np.array(list(map(lambda x: (x @ mask.transpose())[0], y)))[THE_ORDER_OF_THE_CHAIN - 1:]
        return y_train
        # return np.array(list(map(lambda x: (x @ mask.transpose())[0], y)))[THE_ORDER_OF_THE_CHAIN - 1:]

    @staticmethod
    def process_train(highest_notes, chords):
        x_train, y_train = [], []
        for time in highest_notes.keys():
            current_pitch = np.zeros((1, COUNT_NOTES))
            current_pitches = np.zeros((1, COUNT_NOTES))
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
    def decode_pred(y_test):
        size = len(y_test[0].toarray().ravel())
        res = np.zeros(size)
        for y in y_test:
            res = np.vstack((res, y.toarray().ravel()))
        return np.transpose(res)

    @staticmethod
    def process_test(pitches_extractor, res):
        x = map(lambda x_: pitches_extractor.coder.decode(x_)[0].note, res)
        x_test = []
        for pitch in x:
            current_pitch = np.zeros((1, COUNT_NOTES))
            if pitch is not None:
                current_pitch[0][pitch] = 1
                x_test.append(current_pitch[0])
        x_test = np.array(x_test)
        x_test = np.array(list(parser_midi.get_ngrams(x_test, THE_ORDER_OF_THE_CHAIN)))
        return np.array(list(map(lambda x_: np.hstack(x_).ravel(), x_test)))

    def create_and_fit_classifiers(self, x_train, y_train, count_programs):
        for i in range(COUNT_NOTES * count_programs):
            classifier = classificator.BinaryPitchClassifier(i)
            classifier.fit(x_train, y_train[i])
            self.classifiers.append(classifier)

    def predict(self, x_test):
        predictions = []
        for cl in self.classifiers:
            pr = cl.predict(x_test)
            predictions.append(pr)
        decode_predictions = FitterChords.decode_pred(predictions)
        decode_predictions = list(map(lambda x: np.where(x == 1), decode_predictions))
        return decode_predictions
