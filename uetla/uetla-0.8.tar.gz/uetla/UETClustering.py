from .MachineLearning import UETMachineLearning
import pandas
from sklearn.cluster import AgglomerativeClustering
import operator


class UETClustering(UETMachineLearning):

    def __init__(self, n_cluster=5, modelname='', X=pandas.DataFrame(), filepath='',columnX=[]):
        super().__init__()
        self.n_cluster = n_cluster
        self.modelname = modelname
        self.dataset = X
        self.X = X[X.columns[0:5]]
        self.type = 'clustering'
        self.filepath = filepath

    def fit(self):
        self.model = AgglomerativeClustering(n_clusters=self.n_cluster)
        # self.transformData()
        self.model.fit(self.X)
        return self

    def predict(self, X):
        # X = self.scaler.transform(X)
        if self.model is None:
            self.loadModel()
        result = self.model.predict(X)
        return result

    def getLabels(self):
        if self.model is None:
            self.fit()
        labels = self.model.labels_
        return labels

    def bestResult(self):
        if self.model is None:
            self.fit()
        data = pandas.DataFrame(data=self.X, columns=['view', 'post', 'forumview', 'forumpost', 'successsubmission'])
        data['group'] = self.getLabels()
        return data

    def labelGrade(self, labels):
        data = pandas.DataFrame(data=self.dataset)
        column = {
            'w7_view': 'view',
            'w7_post': 'post',
            'w7_forumview': 'forumview',
            'w7_forumpost': 'forumpost',
            'w7_successsubmission': 'successsubmission',
            'w7_grade': 'grade',
            'w15_view': 'view',
            'w15_post': 'post',
            'w15_forumview': 'forumview',
            'w15_forumpost': 'forumpost',
            'w15_successsubmission': 'successsubmission',
            'w15_grade': 'grade'
        }
        data = data.rename(index=str, columns=column)
        data['group'] = self.getLabels()
        l = self.label(self.n_cluster, labels, data)
        data['group'] = l

        return data

    def label(self, ncluster, labels, data):
        tb = {}
        i = 0
        while (i < ncluster):
            temp = data[data.group == i]
            tb[i] = temp.grade.mean()
            i += 1
        sorted_x = sorted(tb.items(), key=operator.itemgetter(1))
        i = 0
        while i < ncluster:
            tb[sorted_x[i][0]] = labels[i]
            i += 1
        l = data['group'].map(tb)
        return l