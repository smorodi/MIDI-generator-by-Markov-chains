from skmultilearn.problem_transform import BinaryRelevance
from sklearn.naive_bayes import GaussianNB


class BinaryPitchClassifier:
    def __init__(self, number):
        self.classifier = BinaryRelevance(GaussianNB())
        self.pitch_number = number

    def fit(self, x_train, y_train):
        self.classifier.fit(x_train, y_train.ravel())

    def predict(self, x_test):
        return self.classifier.predict(x_test)
