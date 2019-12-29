import numpy as np
import fitter_mark
import writter_midi
import parser_midi
import os


NUMBERS_OF_NOTES = 100
THE_ORDER_OF_THE_CHAIN = 3
INPUT_PATH = os.path.join(os.getcwd(), "tracks for fitting")
OUT_PATH = os.path.join(os.getcwd(), "generated tracks")


def resolve():
    fitter = fit_by_files()
    features = fitter.encode_features(THE_ORDER_OF_THE_CHAIN)
    model = fitter_mark.ChainModel()
    model.fit(features)
    res = generate_music(fitter)
    write_music_to_midi(res, fitter)


def generate_music(fitter):
    features = fitter.encode_features(2)
    model = fitter_mark.ChainModel()
    model.fit(features)
    res = model.predict(200, np.random.choice(model.probabilities.nonzero()[0], 1)[0])
    return res


def write_music_to_midi(res, fitter):
    writter_midi.write_music(res, fitter)


def fit_by_files():
    fitter = parser_midi.FeatureExtractor()
    for file_name in get_file_names():
        fitter.parse(os.path.join(INPUT_PATH, file_name))
    return fitter


def get_file_names():
    return os.listdir(INPUT_PATH)


if __name__ == "__main__":
    resolve()
