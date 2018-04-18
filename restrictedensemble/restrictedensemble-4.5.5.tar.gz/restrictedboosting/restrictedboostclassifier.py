import numpy as np
from numpy import random
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
import pandas as pd
from sklearn.model_selection import train_test_split

__author__ = 'LiangjunFeng'

class SelectData():
    def __init__(self):
        self.classnum = 0
        self.classlist = 0
        self.bagging_train = [] 
        self.bagging_label = []
        self.subcount = 0
    
    def count(self,label):
        classlist = []
        for i in range(label.shape[0]):
            if label[i] not in classlist:
                classlist.append(label[i])
        return classlist,len(classlist)
    
    def adding(self,data_sub,label_sub,data_main,propotion):
        center_main = np.mean(data_main,axis = 0)
        distance = np.linalg.norm(data_sub - center_main,axis = 1) 
        resistance = distance / max(distance)
        self.subcount = 0
        lis = []
        while self.subcount <= int(propotion*data_sub.shape[0]):
            for i in range(len(distance)):
                if self.subcount > int(propotion*data_sub.shape[0]):
                    break
                if resistance[i] >= random.random() and i not in lis:
                    self.bagging_train.append(np.ravel(data_sub[i,:]))
                    self.bagging_label.append(np.ravel(label_sub[i,0]))
                    self.subcount += 1  
                    lis.append(i)

    def select(self,data,label,propotion):
        label = np.ravel(label)
        self.classlist,self.classnum = self.count(label)
        for i in range(self.classnum):
            data_main = []
            data_sub = []
            label_sub = []
            for j in range(data.shape[0]):
                if label[j] == self.classlist[i]:
                    data_sub.append(data[j,:])
                    label_sub.append(label[j])
                else: 
                    data_main.append(data[j,:])            
            self.adding(np.mat(data_sub),np.mat(label_sub).T,np.mat(data_main),propotion)

        self.bagging_train = np.mat(self.bagging_train)
        self.bagging_label = np.mat(self.bagging_label)
        return self.bagging_train,np.ravel(self.bagging_label)


class RBClassifier:
    def __init__(self,basetype = "Tree",
                 n_estimators = 100,
                 subsample = 0.8,
                 subfeature = 0.8,
                 searchtimes = 0.7,
                 a = 2):
        self.a = a
        self.label_record = 0
        self.basetype = basetype
        self.number = n_estimators
        self.subsample = subsample
        self.subfeature = subfeature
        self.searchtimes = searchtimes
        self.estimatorlist = []
        self.penaltyVector = []
        self.fealist = []
        self.acclist = []
        self.arr = []
        self.baseClassifierdict = {"SVC":SVC,"Tree":DecisionTreeClassifier}
        self.baseClassifier = self.baseClassifierdict[self.basetype]
    
    def accuracy(self,predictlabel,label,penaltyVector):
        label = np.ravel(label).tolist()
        predictlabel = predictlabel.tolist()
        count = 0
        for i in range(len(label)):
            if label[i] == predictlabel[i]:
                count += 1
        return (np.sum(penaltyVector)**self.a)*(1 - round(count/len(label),5))
    
    def get_randlist(self,maximum,num):
        randlist = []
        while len(randlist) < num:
            t = random.randint(0,maximum-1)
            if t not in randlist:
                randlist.append(t)
        return randlist
    
    def get_localPV(self,randlist):
        local_PV = []
        for i in range(len(randlist)):
            local_PV.append(self.penaltyVector[randlist[i]])
        return local_PV
    
    def get_minloc(self,errlist):
        minimum = 100
        loc = 0
        for i in range(len(errlist)):
            if errlist[i] < minimum:
                minimum = errlist[i]
                loc = i
        self.acclist.append(np.exp(1)-errlist[loc])
        return loc
    
    def refreshPV(self,err,randlist,times):
        for i in range(len(randlist)):
            self.penaltyVector[randlist[i]] = (self.penaltyVector[randlist[i]]*(times+1)+err)/(times+2)
        self.penaltyVector = self.penaltyVector/np.sum(self.penaltyVector)

    def count(self,label):
        classlist = []
        for i in range(len(label)):
            if label[i] not in classlist:
                classlist.append(label[i])
        return classlist,len(classlist)
    
    def labeltransfer(self,label):
        self.label_record = int(min(label))
        label -= self.label_record
        return np.ravel(label)
    
    def labelinver(self,label):
        label = label + self.label_record
        return np.ravel(label)
    
    def fit(self,data,label):
        label = self.labeltransfer(label.copy())
        self.penaltyVector = [1/data.shape[1]]*data.shape[1]
        for i in range(self.number):
            local_estimatorlist = []
            errlist = []
            local_list = []
            for j in range(int(self.searchtimes*data.shape[1])+1):
                randlist = self.get_randlist(data.shape[1],int(self.subfeature*data.shape[1]))
                local_list.append(randlist)
                local_PV = self.get_localPV(randlist)
                sel = SelectData()        
                local_data,local_label = sel.select(data[:,randlist],label,self.subsample)
                clf = self.baseClassifier()
                clf.fit(local_data,local_label)
                pre = clf.predict(local_data)
                err = self.accuracy(pre,local_label,local_PV)
                local_estimatorlist.append(clf)
                errlist.append(err)
            loc = self.get_minloc(errlist)
            self.estimatorlist.append(local_estimatorlist[loc])
            self.fealist.append(local_list[loc])
            self.refreshPV(errlist[loc],local_list[loc],i)
     
    def vote(self,resall):
       res = []
       for i in range(resall.shape[1]):
           vec = np.ravel(resall[:,i]).tolist()
           classlist,_ = self.count(vec)
           votlis = [0]*(max(classlist)+1)
           self.acclist = (np.array(self.acclist) / np.sum((self.acclist)).tolist())
           for j in range(len(vec)):
               votlis[vec[j]] += self.acclist[j]
           res.append(votlis.index(max(votlis)))
       
       return np.mat(res)

    def predict(self,data):
        reslist = []
        for i in range(len(self.estimatorlist)):
            res = self.estimatorlist[i].predict(data[:,self.fealist[i]])
            res = self.labelinver(res)
            reslist.append(res)
        res = self.vote(np.mat(reslist))
        return np.ravel(res) 
    
    def select_fea(self,data,label,num = -1):
        self.fit(data,label)
        if num == -1:
            num = int(0.2*data.shape[1])
        sf = pd.DataFrame()
        sf['PV'] = self.penaltyVector
        sf['index'] = range(len(self.penaltyVector))
        sf = sf.sort_values(by='PV')
        self.arr = np.ravel(sf.iloc[0:num,1].values).tolist()
        return data[:,self.arr]
    
    def fea_transform(self,data):
        return data[:,self.arr]
        
 
               
                    
                    
                    
                    
