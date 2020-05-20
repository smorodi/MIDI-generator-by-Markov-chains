import numpy as np
import fitter_pitches
import writter_midi
import parser_midi
import fitter_chodrs
import os

COUNT_NOTES = 88
NUMBERS_OF_NOTES = 500
THE_ORDER_OF_THE_CHAIN = 3
INPUT_PATH = os.path.join(os.getcwd(), "tracks for fitting")
OUT_PATH = os.path.join(os.getcwd(), "generated tracks")


def resolve():
    pitches_extractor, chords_fitter  = fit_by_files()
    res = generate_music(pitches_extractor)
    x_test = fitter_chodrs.FitterChords.process_test(pitches_extractor, res)
    y_test = chords_fitter.predict(x_test)
    write_music_to_midi(res, pitches_extractor)


def generate_music(fitter):
    features = fitter.encode_features(THE_ORDER_OF_THE_CHAIN)
    model = fitter_pitches.ChainModel()
    model.fit(features)
    res = model.predict(NUMBERS_OF_NOTES, np.random.choice(model.probabilities.nonzero()[0], 1)[0])
    return res


def write_music_to_midi(res, fitter):
    writter_midi.write_music(res, fitter)


def fit_by_files(is_chords=False):
    pitches_extractor = parser_midi.FeatureExtractor()
    chords_fitter = fitter_chodrs.FitterChords()
    for file_name in get_file_names():
        highest_notes, chords = pitches_extractor.parse(os.path.join(INPUT_PATH, file_name))
        x_train, y_train = fitter_chodrs.FitterChords.process_train(highest_notes, chords)
    chords_fitter.create_and_fit_classifiers(x_train, y_train)
    return pitches_extractor, chords_fitter


def get_file_names():
    return os.listdir(INPUT_PATH)


if __name__ == "__main__":
    resolve()
    # test()
