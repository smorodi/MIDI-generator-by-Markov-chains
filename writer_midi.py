import mido
from parser_midi import Type
import config
import os
import numpy as np


class WriterMidi:
    def __init__(self, fitter, res, chords,  programs_in_channels):
        self.fitter = fitter
        self.res = res
        self.chords = chords
        self.track = []
        self.time = 0.0
        self.programs_in_channels = programs_in_channels

    def write_music(self):
        mid = mido.MidiFile()
        self.track = mido.MidiTrack()
        mid.tracks.append(self.track)
        # self.track.append(mido.MetaMessage("set_tempo", tempo=8000000))
        # self.track.append(mido.MetaMessage("time_signature", numerator =4, denominator = 4, clocks_per_click=24,
        #                                    notated_32nd_notes_per_beat=8, time=0))
        cont = self.res[config.THE_ORDER_OF_THE_CHAIN - 1:]
        prob = [p[1] for p in self.programs_in_channels.values()]
        channels = list(self.programs_in_channels.keys())
        for ch in self.programs_in_channels.keys():
            self.track.append(mido.Message('program_change', channel=ch,
                                           program=self.programs_in_channels[ch][0], time=0))
        for i in range(len(self.chords)):
            decoded_feature = self.fitter.coder.decode(cont[i])[0]
            channel = np.random.choice(channels, p=prob)
            if decoded_feature.type == Type.NOTE:
                for pitches in self.chords[i]:
                    for k in range(len(pitches)):
                        pitch = pitches[k]
                        self.track.append(mido.Message(
                            'note_on', note=pitch + 5, velocity=127, time=0, channel=channel
                        ))
                for pitches in self.chords[i]:
                    for k in range(len(pitches)):
                        pitch = pitches[k]
                        if k != len(pitches) - 1:
                            self.track.append(mido.Message(
                                'note_off', note=pitch + 5, velocity=127,
                                time=min(int(decoded_feature.duration), 190)))
                        else:
                            self.track.append(mido.Message(
                                'note_off', note=pitch + 5, velocity=127,
                                time=0
                            ))
                self.time = 0.0
            else:
                self.time = min(decoded_feature.duration, 960)
        mid.save(os.path.join(config.OUT_PATH, "new_song.mid"))
