import os
import random
import json
import requests



def jizhuanwan(keyword='',pagesize=1,pagenum=1):
    '''脑筋急转弯'''
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_funny.php'
    data = {}
    data['pagesize'] = pagesize
    data['pagenum'] = pagenum
    data['keyword'] = keyword
    data['op'] = 'jizhuanwan'
    r = requests.post(url, data=data)
    res = r.json()['result']
    if res:
        res_dict = {}
        res_dict['answer']=res['list'][0]['answer']
        res_dict['content']=res['list'][0]['content'].replace('<br />','')
        res_str = '问题：' + res_dict['content'] + os.linesep + '答案：' + res_dict['answer']
        return res_str
    else:
        return -1




def raokouling(keyword='',pagesize=1,pagenum=1):
    '''绕口令'''
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_funny.php'
    data = {}
    data['pagesize'] = pagesize
    data['pagenum'] = pagenum
    data['keyword'] = keyword
    data['op'] = 'raokouling'
    r = requests.post(url, data=data)
    res = r.json()['result']
    if res:
        res_dict = {}
        res_dict['title']=res['list'][0]['title']
        # res_dict['content']=res['list'][0]['content'].replace('<br />',os.linesep)
        res_dict['content']=res['list'][0]['content'].replace('<br />','')
        res_str = res_dict['content']
        return res_str
    else:
        return -1



def xiehouyu(keyword='',pagesize=1,pagenum=1):
    '''歇后语'''
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_funny.php'
    data = {}
    data['pagesize'] = pagesize
    data['pagenum'] = pagenum
    data['keyword'] = keyword
    data['op'] = 'xiehouyu'
    r = requests.post(url, data=data)
    res = r.json()['result']
    if res:
        res_dict = {}
        res_dict['answer']=res['list'][0]['answer']
        res_dict['content']=res['list'][0]['content'].replace('<br />','')
        res_str = '问题：' + res_dict['content'] + os.linesep + '答案：' + res_dict['answer']
        return res_str
    else:
        return -1




def miyu(keyword='',pagesize=1,pagenum=1):
    '''谜语'''
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_funny.php'
    data = {}
    data['pagesize'] = pagesize
    data['pagenum'] = pagenum
    data['keyword'] = keyword
    data['classid'] = random.randint(1,11)
    data['op'] = 'miyu'
    r = requests.post(url, data=data)
    res = r.json()['result']
    if res:
        res_dict = {}
        res_dict['answer']=res['list'][0]['answer']
        res_dict['content']=res['list'][0]['content'].replace('<br />','')
        res_str = '问题：' + res_dict['content'] + os.linesep + '答案：' + res_dict['answer']
        return res_str
    else:
        return -1

def main():
    print(jizhuanwan())
    print(raokouling())
    print(xiehouyu())
    print(miyu())

if __name__ == '__main__':
    main()
