from .MachineLearning import UETMachineLearning
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier


class UETClassification(UETMachineLearning):
    def __init__(self, modelname='', X=[], y=[], filepath=''):
        super().__init__()
        self.modelname = modelname
        self.X = X
        self.y = y
        self.type = 'classification'
        self.filepath = filepath

    def fit(self):
        self.model = RandomForestClassifier()
        self.transformData()
        self.model.fit(self.X, self.y)
        return self

    def predict(self, X):
        X = self.scaler.transform(X)
        if self.model is None:
            self.loadModel()
        result = self.model.predict(X)
        return result
