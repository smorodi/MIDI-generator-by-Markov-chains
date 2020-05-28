import numpy as np
from scipy.sparse import lil_matrix


class ChainModel:
    def __init__(self):
        self.probabilities = None

    def fit(self, encoded_features):
        encoded_features = np.asarray(encoded_features, dtype=int)
        size = np.max(encoded_features) + 1
        self.probabilities = lil_matrix((size, size), dtype=float)
        for curr_state, next_state in encoded_features:
            self.probabilities[curr_state, next_state] += 1
        for row in range(self.probabilities.shape[0]):
            if self.probabilities[row].count_nonzero() != 0:
                div = self.probabilities[row].sum()
                for col in self.probabilities[row].nonzero()[1]:
                    self.probabilities[row, col] /= div

    def predict_next(self, state):
        indices = self.probabilities[state].nonzero()[1]
        p = self.probabilities[state, indices].toarray().ravel()
        return np.random.choice(indices, 1, p=p)[0]

    def predict(self, count, initial):
        result = []
        for _ in range(count):
            result.append(initial)
            try:
                initial = self.predict_next(initial)
            except ValueError:
                print("Can't generate > {}, there are no transitions for this state".format(len(result)))
                return result
        return result
