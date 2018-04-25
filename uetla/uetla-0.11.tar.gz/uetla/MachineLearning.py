import pickle
from abc import ABC
from abc import abstractmethod
from .Database import Database
from sklearn import preprocessing
import os


class UETMachineLearning(ABC):

    def __init__(self):
        self.model = None
        self.modelname = ""
        self.type = ""
        self.X = []
        self.y = []
        self.filepath = ''
        self.scaler = preprocessing.MinMaxScaler()

    def filterData(self):
        pass

    def transformData(self):
        self.X = self.scaler.fit_transform(self.X)
        # self.y = scaler.fit_transform(self.y)
        return self.X

    @abstractmethod
    def fit(self):
        pass

    @abstractmethod
    def predict(self, X):
        pass

    def saveModel(self,model = None):
        if model is None:
            model = self.fit()
        db = Database()
        version = int(db.checkModelVersion(self.modelname)) + 1
        filename = self.filepath +'/model/' + self.modelname + '_' + self.type + '_' + str(version)
        pickle.dump(model, open(filename, 'wb'),protocol=2)
        db.saveModelVersion(self.modelname, self.type, version)
        return model

    def loadModel(self):
        db = Database()
        version = db.checkModelVersion(self.modelname)
        if version == 0:
            self.saveModel()
            version = 1
        filename = self.filepath +'/model/' + self.modelname + '_' + self.type + '_' + str(version)
        model = pickle.load(open(filename, 'rb'))
        return model
