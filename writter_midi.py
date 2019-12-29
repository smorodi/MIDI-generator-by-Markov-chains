import mido
from parser_midi import Type
from resolver import OUT_PATH
import os


def write_music(res, fitter):
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    time = 0.0
    for num in res:
        decoded_feature = fitter.coder.decode(num)[0]
        print(decoded_feature)
        if decoded_feature.type == Type.NOTE:
            track.append(mido.Message(
                'note_on', note=decoded_feature.note, velocity=64, time=max(int(time), 32)
            ))
            track.append(mido.Message(
                'note_off', note=decoded_feature.note, velocity=127,
                time=int(decoded_feature.duration)
            ))
            time = 0.0
        else:
            time = decoded_feature.duration
    mid.save(os.path.join(OUT_PATH, "new_song.mid"))
