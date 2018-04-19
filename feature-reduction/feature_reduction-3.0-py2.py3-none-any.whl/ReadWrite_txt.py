'''
@author:wujunming
create date:2018-4-13
'''
import datetime
import time
import os
import sys
#过滤
import glob
# list all files

def list_all_files(now_dir):
    '''
    #列出目录下的所有文件
    :param now_dir:
    :return:
    '''
    if os.path.isfile(now_dir):
        print(now_dir)
    else:
        listdir = os.listdir(now_dir)
        for i in listdir:
            if os.path.isfile(i):
                print(i)
            else:
                i = now_dir + '/' + i
                list_all_files(i)
print(os.path.split(sys.argv[0])[0])
file_dir=sys.path[0]
# for i in os.listdir(file_dir):
#     if os.path.isfile(i):
#         print(i)
#     else:
#         print("不是文件，是目录")
for dirpath, dirnames, filenames in os.walk(file_dir):
    print('Directory', dirpath)
    for filename in filenames:
        print(' File', filename)
#读取txt文件
print(os.path.isfile("SST10.125.txt"))
#异常处理,可以通过try-except来捕获异常
try:
    with open("SST10.12.txt","r") as fr:
    #读取文件的所有行，返回的是文件行的列表
        fr_readlines=fr.readlines()
    #遍历文件的每一行
        line_row=[]
        for line in fr_readlines:
            print(line)
            line_list=line.strip().split()
            print(line_list)
            date_time='{}-{}-{}'.format(line_list[0],line_list[1],line_list[2])
            print(date_time)
            t2 = time.mktime(time.strptime(date_time, '%Y-%m-%d'))
            print("格式化后的日期为",date_time)
            temperature=float(line_list[3])
            time_temperature=[date_time,temperature]
            line_row.append(time_temperature)
        print(line_row)
except IOError as info:
    print("找不到相应的txt文件",info)
else:
    print("内容读取成功!")
finally:
    print("hello world!")
# with open("125.txt","w") as wr:
#     wr.write("Date Temperature\n")
#     for element in line_row:
#         element_str='{0} {1}'.format(element[0],element[1])
#         wr.write(element_str)
#         wr.write("\n")
for parent, dirnames, filenames in os.walk("F:\刘老师文件"):
    # 三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
    for dirname in dirnames:  # 输出文件夹信息
        print("parent is:" + parent)
        print("dirname is" + dirname)

    for filename in filenames: # 输出文件信息
        print("parent is:" + parent)
        print("filename is:" + filename)
        # os.path.join合并目录
        print("the full name of the file is:" + os.path.join(parent, filename))
        # 输出文件路径信息
print(".........................")
for filename in glob.glob(r"F:\刘老师文件\*.ppt"):
    print(filename)