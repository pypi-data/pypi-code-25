import pandas as pd
import numpy as np
from sklearn import svm
from datetime import datetime, timedelta
import spiralOrg as spiral
from itertools import permutations
from threading import Thread
from bokeh.plotting import figure, output_file, show, ColumnDataSource

data = pd.read_csv('/home/nachiket/works/works/projekt/datasets/SUSY/99856_susy')
np.set_printoptions(threshold=np.inf)
# data.fillna(0.24218259723098992, inplace=True)
perm = list(permutations(data.drop(columns=['class', 'cos(theta_r1)']).columns.values, 2))
# p = timedelta()
result_list = []
# Spiral organize

threadlist = []

def work(features):
    # features = ['class', 'axial MET', 'M_TR_2']
    print("Features: [ '" + features[1] + "' , " + features[2] + "' ]")
    obj = spiral.organise(data, features, threshold='stdev')
    flatmat = obj[0]
    # p += obj[1]
    features.append('tag')
    temp = np.stack(flatmat, axis=1).T
    # print(temp.T)
    data_magic = pd.DataFrame(temp, columns=features)
    x = np.vstack((data_magic[features[1]].values,data_magic[features[2]].values)).T
    y = data_magic[features[0]].values
    # print(len(y))
    n_sample = len(x)
    X_train = x[:int(.8 * n_sample)]
    y_train = y[:int(.8 * n_sample)]
    X_test = x[int(.8 * n_sample):]
    y_test = y[int(.8 * n_sample):]


    #Train SVM
    # start_time = datetime.now()
    clf = svm.SVC(kernel='linear')
    # clf = svm.LinearSVC()
    clf.fit(X_train,y_train)
    # p += datetime.now() - start_time

    # Predict
    # start_time = datetime.now()
    answers = clf.predict(X_test)
    # p += datetime.now() - start_time


    # Confusion Matrix?
    total = answers == y_test
    tn=0
    tp=0
    bad = 'False'
    cnt = 0
    for i in answers:
        if i == 1 and y_test[cnt]==1:
            tp += 1
        if i == 0 and y_test[cnt]==0:
            tn += 1
        cnt += 1

    result = ((tp+tn)/len(answers)*100)
    if result == 100:
        return
    print(print('Accuracy: ' + str(result) + "%"))
    temp = [result, features[1], features[2]]
    result_list.append(temp)

for combo in perm:
    features = ['class']
    features.append(combo[0])
    features.append(combo[1])
    # print([features])
    t = Thread(target=work, args=(features,))
    threadlist.append(t)

workers = len(threadlist)-1
print("Total Pairs:" + str(workers))
print("Listing Pairs and their calculated accuracies and then selecting the best one:")
i=0
count = 0
for thread in threadlist:
    i += 1
    count+=1
    print("Pass: " + str(count))
    thread.start()
    if i == 3:
        while i>=0:
            i=i-1
            workers = workers-1
            thread.join()

# print(p)
# print(result_list)
res_set = max(result_list)
print("Sleeping 1s to let all threads complete their execution.")
# sleep(1)
print('Accuracy: ' + str(res_set[0]) + "%")
print('Features: [ ' + str(res_set[1]) + ", " + str(res_set[2]) + " ]")
#BOKEH
# output_file('Spiral-full.html')
# colors = {0:'yellow', 1:'black'}
# answerplot = figure(plot_width=1250, plot_height=1250)
# fullplot = figure(plot_width=1250, plot_height=1250)

# temp = X_test.T
# cols = [colors[key] for key in answers]
# answerplot.circle(temp[1], temp[0], fill_color=cols)
# y_testcols = [colors[key] for key in y_test]
# plot.circle(temp[1], temp[0], fill_color=y_testcols)
# data_magic =
#Plot entire Thing
# data_magic['colorColumn'] = [colors[key] for key in data_magic[features[0]].values]
# df = ColumnDataSource(data_magic)
# answerplot.circle(feature2, feature1, fill_color='colorColumn', source=df)

# show(answerplot)
# output_file('Spiral-orig.html')
# data['colorColumn'] = [colors[key] for key in data[features[0]].values]
# dforig = ColumnDataSource(data)
# fullplot.circle(feature2, feature1, fill_color='colorColumn', source=dforig)
# show(fullplot)
