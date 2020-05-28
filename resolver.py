import logging

from config import NUMBERS_OF_NOTES, THE_ORDER_OF_THE_CHAIN, INPUT_PATH
import fitter_pitches
import fitter_chodrs
import os
import numpy as np
import parser_midi
import writer_midi

FORMAT = '%(message)s'
logging.basicConfig(format=FORMAT, level = logging.DEBUG)
logger = logging.getLogger('midi_mark_logger')


def resolve():
    logger.info('Start process')
    pitches_extractor, chords_fitter, programs_in_channels = fit_by_files()
    logger.info('Generating base')
    res = generate_music(pitches_extractor)
    logger.info('Generating chords')
    x_test = fitter_chodrs.FitterChords.process_test(pitches_extractor, res)
    chords = chords_fitter.predict(x_test)
    logger.info('Writing to midi')
    write_music_to_midi(res, pitches_extractor, chords, programs_in_channels)


def generate_music(fitter):
    features = fitter.encode_features(THE_ORDER_OF_THE_CHAIN)
    model = fitter_pitches.ChainModel()
    model.fit(features)
    res = model.predict(NUMBERS_OF_NOTES, np.random.choice(model.probabilities.nonzero()[0], 1)[0])
    return res


def write_music_to_midi(res, fitter, chords, programs_in_channels):
    writer = writer_midi.WriterMidi(fitter, res, chords, programs_in_channels)
    writer.write_music()


def fit_by_files():
    pitches_extractor = parser_midi.FeatureExtractor()
    chords_fitter = fitter_chodrs.FitterChords()
    file_names = get_file_names()
    logger.info('Parsing file: %s', file_names[0])
    highest_notes, chords, programs_in_channels = pitches_extractor.parse(os.path.join(INPUT_PATH, file_names[0]))
    # x, y = fitter_chodrs.FitterChords.process_train(highest_notes, chords)
    x, y, count_programs = fitter_chodrs.FitterChords.process_train_for_one(highest_notes, chords, programs_in_channels)
    # for i in range(max(1, len(file_names) - 1), len(file_names)):
    #     logger.info('Parsing file: %s', file_names[i])
    #     highest_notes, chords, programs_in_channels = pitches_extractor.parse(os.path.join(INPUT_PATH, file_names[i]))
    #     current_x, current_y = fitter_chodrs.FitterChords.process_train(highest_notes, chords)
    #     x = np.vstack((x, current_x))
    #     y = np.hstack((y, current_y))
    logger.info('Fitting')
    # highest_notes, chords, programs_in_channels = pitches_extractor.parse(os.path.join(INPUT_PATH, file_names[-1]))
    # current_x, current_y = fitter_chodrs.FitterChords.process_train(highest_notes, chords)
    # x = np.vstack((x, current_x))
    # y = np.hstack((y, current_y))
    chords_fitter.create_and_fit_classifiers(x, y, count_programs)
    return pitches_extractor, chords_fitter, programs_in_channels


def get_file_names():
    return os.listdir(INPUT_PATH)


if __name__ == "__main__":
    resolve()
    # test()
