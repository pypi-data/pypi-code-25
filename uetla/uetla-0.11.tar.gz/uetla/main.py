from uetla.UETAnalytics import UETAnalytics
import sys

arg = sys.argv
import os
import pandas
import json


def check(p, r):
    if p == "F" and r < 4:
        return 1
    if p == "D" and (4 <= r < 5.5):
        return 1
    if p == "C" and (5.5 <= r < 6.5):
        return 1
    if p == "B" and (6.5 <= r < 8):
        return 1
    if p == "A" and (8 <= r <= 10):
        return 1

    return 0


filepath = os.path.dirname('/home/bachnguyen/public_html/moodle3/mod/uetanalytics/backend/model')

uet = UETAnalytics(filepath=filepath)
# uet.createModel()
grade = pandas.read_csv('../test/grade842.csv')
dataframe = pandas.read_csv('../test/export6w.csv')
# test = pandas.DataFrame(dataframe[dataframe.columns[4:9]])
dataframe = dataframe.merge(grade, on=['courseid', 'userid'], suffixes=('', '_grade'))
dataframe = dataframe.drop(['grade', 'stt_grade'], 1)
# print(dataframe)
m = 0
f = 0
for index, row in dataframe.iterrows():
    data = {
        'view': row['view'],
        'post': row['post'],
        'forumview': row['forumview'],
        'forumpost': row['forumpost'],
        'successsubmission': row['successsubmission']
    }
    p = uet.predict(week=6, data=data)
    print(p)
    p = json.loads(p)

    if(check(p['w7'], row['mid']) == 1):
        m += 1
    if check(p['w15'], row['final']) == 1:
        f +=1
print(str(m) + '     ' + str(f))