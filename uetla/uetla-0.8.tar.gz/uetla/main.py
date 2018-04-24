from uetla.UETAnalytics import UETAnalytics
import sys
arg = sys.argv
import os
import pandas

filepath = os.path.dirname('/home/bachnguyen/public_html/moodle3/mod/uetanalytics/backend/model')

uet = UETAnalytics(filepath=filepath)
uet.createModel()
# grade = pandas.read_csv('../test/grade842.csv')
dataframe = pandas.read_csv('../test/export6w.csv')
# test = pandas.DataFrame(dataframe[dataframe.columns[4:9]])
# dataframe = dataframe.merge(grade, on=[ 'courseid', 'userid'], suffixes=('', '_grade'))
# dataframe = dataframe.drop(['grade','stt_grade'],1)
# print(dataframe)
for index,row in dataframe.iterrows():
    data = {
        'view': row['view'],
        'post':  row['post'],
        'forumview': row['forumview'],
        'forumpost': row['forumpost'],
        'successsubmission': row['successsubmission']
    }
    print(uet.predict(week=6, data=data))
    # print(str(row['mid']) + " " + str(row['final']))