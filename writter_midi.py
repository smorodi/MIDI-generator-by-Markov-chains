from midiutil.MidiFile import MIDIFile
class Writer:
    @staticmethod
    def write_to_midi_file(triplets):
        degrees = [60, 62, 64, 65, 67, 69, 71, 72]
        track = 0
        channel = 0
        time = 0
        tempo = 120
        volume = 15
        MyMIDI = MIDIFile(1)
        MyMIDI.addTrackName(track, time , "Sample Track")
        MyMIDI.addTempo(track, 120, tempo)
        for triplet in triplets:
            pitch = triplet[0]
            new_time = triplet[1]
            print(triplet)
            print("Записываю ноту " +str(pitch) + " и время " + str(time/960))
            MyMIDI.addNote(track, channel, pitch, time/960, new_time/960, volume)
            time += new_time
        with open("e.mid", "wb") as output_file:
            MyMIDI.writeFile(output_file)