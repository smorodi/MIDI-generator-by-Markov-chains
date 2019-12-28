import numpy as np


class Generator:
    def __init__(self, model):
        self.model = model

    # переписать генерацию с учетом начального распределения и порядка цепи
    def get_initial_triplet(self):
        numbers = [i for i in range(len(self.model.score_matrix.keys()))]
        generate_numbers = np.random.choice(numbers, 1)
        triplets = list(self.model.score_matrix.keys())[generate_numbers[0]]
        return triplets

    def get_new_note_by_markov_chain(self, prev):
        numbers = [i for i in range(len(self.model.score_matrix[prev]))]
        generate_number = np.random.choice(numbers, 2, p=list(self.model.score_matrix[prev].values()))[0]
        return list(self.model.score_matrix[prev].keys())[generate_number]
