import mido
from enum import Enum
from collections import namedtuple

Feature = namedtuple('Feature', ('type', 'duration', 'note'))


class Type(Enum):
    NOTE = 1
    PAUSE = 2


class FeaturesToInt:
    def __init__(self):
        self.__dct = {}
        self.__inv_dct = {}
        self.__index = 0

    def encode(self, tup):
        if tup in self.__inv_dct:
            return self.__inv_dct[tup]
        self.__dct[self.__index] = tup
        self.__inv_dct[tup] = self.__index
        self.__index += 1
        return self.__index - 1

    def decode(self, num):
        return self.__dct[num]


def get_ngrams(seq, n):
    array = list(seq)
    return zip(*[array[i:] for i in range(n)])


class FeatureExtractor:
    def __init__(self, ):
        self.mid = None
        self.coder = None
        self.encoded_features = None
        self.features = []

    def parse(self, filename):
        self.mid = mido.MidiFile(filename)
        time = 0.0
        all_messages = []
        programs_in_channels = {}
        pitch_count = 0
        for i, track in enumerate(self.mid.tracks):
            for msg in track:
                time += msg.time
                if msg.type == "program_change":
                    programs_in_channels[msg.channel] = (msg.program, 0)
                elif msg.type in ["note_on", "note_off"]:
                    if msg.type == "note_on":
                        pitch_count += 1
                        count = programs_in_channels[msg.channel][1]
                        program = programs_in_channels[msg.channel][0]
                        programs_in_channels[msg.channel] = (program, count + 1)
                    msg.time = time
                    all_messages.append(msg)
        for i in programs_in_channels.keys():
            program = programs_in_channels[i][0]
            programs_in_channels[i] = (program, programs_in_channels[i][1] / pitch_count)
        current_notes = {}
        chords = {}
        highest_notes = {}
        time = 0.0
        for msg in all_messages:
            if msg.type == "note_on":
                if msg.time in highest_notes.keys():
                    if highest_notes[msg.time].note < msg.note:
                        highest_notes[msg.time] = msg
                else:
                    highest_notes[msg.time] = msg
                if msg.time != time and len(current_notes) == 0:
                    self.features.append(Feature(
                        type=Type.PAUSE, duration=msg.time - time, note=None
                    ))
                if msg.time in chords.keys():
                    chords[msg.time].append(msg)
                else:
                    chords[msg.time] = [msg]
                if msg.note not in current_notes:
                    current_notes[msg.note] = msg
                time = msg.time

            elif msg.type == "note_off" and msg.note in current_notes:
                time = msg.time
                max_note = max(current_notes)
                if msg.note == max_note:
                    self.features.append(Feature(
                        type=Type.NOTE, note=msg.note,
                        duration=msg.time - current_notes[max_note].time))
                current_notes.pop(msg.note)
        return highest_notes, chords, programs_in_channels

    def encode_features(self, order):
        self.coder = FeaturesToInt()
        self.encoded_features = tuple(get_ngrams(map(
            lambda tup: self.coder.encode(tup),
            get_ngrams(self.features, order)), 2))
        return self.encoded_features
