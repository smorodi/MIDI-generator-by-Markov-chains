import midi_parser
import fitter_mark
import data_generator
import writter_midi

NUMBERS_OF_NOTES = 100
THE_ORDER_OF_THE_CHAIN = 2


class Resolver:
    @staticmethod
    def resolve():
        fitter = Resolver.fit_by_files()
        triplets = Resolver.generate_music(fitter)
        Resolver.write_music_to_midi(triplets)
        file = Resolver.get_midi_structure("e.mid")
        fitter.print_all_notes(file)

    @staticmethod
    def generate_music(fitter):
        generator = data_generator.Generator(fitter)
        triplets = []
        current_notes = generator.get_initial_triplet()
        triplets.append(current_notes[0])
        triplets.append(current_notes[1])
        for i in range(NUMBERS_OF_NOTES):
            new_triplet = generator.get_new_note_by_markov_chain(current_notes)
            current_notes = (current_notes[1], new_triplet)
            triplets.append(new_triplet)
        return triplets

    # дописать генерацию миди-файла
    @staticmethod
    def write_music_to_midi(triplets):
        writter = writter_midi.Writer()
        writter.write_to_midi_file(triplets)

    @staticmethod
    def fit_by_files():
        fitter = fitter_mark.Fitter()
        for file_name in Resolver.get_file_names():
            file = Resolver.get_midi_structure(file_name)
            fitter.fit(file)
        return fitter

    # дописать парсинг файла с названиями и обращение к текущей директории
    @staticmethod
    def get_file_names():
        file_names = list()
        file_names.append("turkish_march.mid")
        return file_names

    @staticmethod
    def get_midi_structure(file_name):
        file = midi_parser.MidiFile()
        file.open(file_name)
        file.read()
        file.close()
        return file


if __name__ == "__main__":
    Resolver.resolve()
