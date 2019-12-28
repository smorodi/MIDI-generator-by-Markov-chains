import numpy as np


class Fitter:
    def __init__(self):
        self.probabilities = dict()
        self.score_matrix = dict()
        self.current_triplet = None
        self.prev_triplet = None
        self.feature_triplet = None

    @staticmethod
    def is_a_chord(event, next_event):
        return event.time == next_event.time

    @staticmethod
    def get_the_highest_note_and_count(file, i, j):
        event = file.tracks[i].events[j]
        next_event = file.tracks[i].events[j+2]
        the_highest_note = event.pitch
        count = 1
        while event.time == next_event.time:
            j += 2
            event = next_event
            try:
                next_event = file.tracks[i].events[j+2]
            except IndexError:
                break
            the_highest_note = max(the_highest_note, event.pitch)
            count += 1
        return the_highest_note, count

    def print_all_notes(self, file):
        for i in range(len(file.tracks)):
            for j in range(min(len(file.tracks[i].events),30)):
                print(file.tracks[i].events[j])

    def fit(self, file):
        for i in range(len(file.tracks)):
            j = 1
            while j < len(file.tracks[i].events):
                event = file.tracks[i].events[j]
                print(event)
                if event.type == "NOTE_ON":
                    delta = file.tracks[i].events[j + 1]
                    print(delta)
                    if event.pitch is not None:
                        if Fitter.is_a_chord(event, file.tracks[i].events[j+2]):
                            chord_pitch, chord_dimension = Fitter.get_the_highest_note_and_count(file, i, j)
                            j += chord_dimension * 2 - 2
                            pitch = chord_pitch
                            time = file.tracks[i].events[j + 1].time
                            j += chord_dimension * 2 - 2
                        else:
                            pitch = event.pitch
                            time = delta.time
                        pause = file.tracks[i].events[j + 3].time
                        triplet = (pitch, time, pause)
                        self.update_probabilities(triplet)
                        self.update_score_matrix(triplet)
                j += 2
        self.normalize_probabilities()
        self.normalize_score_matrix()

    def update_probabilities(self, triplet):
        if triplet in self.probabilities:
            self.probabilities[triplet] += 1
        else:
            self.probabilities[triplet] = 1

    # переписать работу с марковскими цепями с учетом её порядка
    def update_score_matrix(self, triplet):
        self.prev_triplet = self.current_triplet
        self.current_triplet = self.feature_triplet
        self.feature_triplet = triplet
        if self.prev_triplet is not None and self.current_triplet is not None:
            if (self.prev_triplet, self.current_triplet) in self.score_matrix:
                if self.feature_triplet in self.score_matrix[(self.prev_triplet, self.current_triplet)]:
                    self.score_matrix[(self.prev_triplet, self.current_triplet)][self.feature_triplet] += 1
                else:
                    self.score_matrix[(self.prev_triplet, self.current_triplet)][self.feature_triplet] = 1
            else:
                self.score_matrix[(self.prev_triplet, self.current_triplet)] = dict()
                self.score_matrix[(self.prev_triplet, self.current_triplet)][self.feature_triplet] = 1

    def normalize_score_matrix(self):
        for sample in self.score_matrix:
            array = np.array(list(self.score_matrix[sample].values()))
            size = array.sum()
            for note in self.score_matrix[sample]:
                self.score_matrix[sample][note] /= size

    def normalize_probabilities(self):
        array = np.array(list(self.probabilities.values()))
        size = array.sum()
        for key in self.probabilities.keys():
            self.probabilities[key] /= size
