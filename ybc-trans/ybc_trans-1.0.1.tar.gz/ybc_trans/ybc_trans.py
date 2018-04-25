import json
import requests
import re

def en2zh(text='',_type='baidu',_from='en',_to='zh-cn'):
    '''英译汉'''
    if text == '':
        return -1
    data = {}
    data["type"] = _type
    data["from"] = _from
    data["to"] = _to
    data["text"] = text
    data["op"] = 'en2zh'
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_trans.php'
    r = requests.post(url, data=data)
    res = r.json()['result']
    if res['result']:
        res['result'] = res['result'].replace('<br />','\n')
        dr = re.compile('<[^>]+>',re.S)
        res_str = dr.sub('',res['result']).strip()
        return res_str
    else:
        return -1

def zh2en(text='',_type='baidu',_from='zh-cn',_to='en'):
    '''汉译英'''
    if text == '':
        return -1
    data = {}
    data["type"] = _type
    data["from"] = _from
    data["to"] = _to
    data["text"] = text
    data["op"] = 'zh2en'
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_trans.php'
    r = requests.post(url, data=data)
    res = r.json()['result']
    if res['result']:
        res['result'] = res['result'].replace('<br />','\n')
        dr = re.compile('<[^>]+>',re.S)
        res_str = dr.sub('',res['result']).strip()
        return res_str
    else:
        return -1

def main():
    print(zh2en('苹果'))
    print(en2zh('test'))

if __name__ == '__main__':
    main()
