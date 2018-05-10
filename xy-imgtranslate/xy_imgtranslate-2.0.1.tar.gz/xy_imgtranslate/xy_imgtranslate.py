import requests
import json
import base64
import os
# def imgtrans(filename=''):
#     if not filename:
#         return -1
#     zh_url = 'https://www.phpfamily.org/imgTranslate.php'
#     filepath = os.path.abspath(filename)
#     b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
#     data = {}
#     data['b64img']=b64img
#     r = requests.post(zh_url, data=data)
#     res = r.json()
#     print(res)
#     if res['ret'] == 0:
#         del res['data']['x']
#         del res['data']['y']
#         del res['data']['width']
#         del res['data']['height']
#         return res['data']['image_records']
#     else:
#         return -1

'''英文翻译成中文'''
def img2zh(filename=''):
    if not filename:
        return -1
    zh_url = 'https://www.yuanfudao.com/tutor-ybc-course-api/img2zh.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img']=b64img
    r = requests.post(zh_url, data=data)
    res = r.json()
    # print(res)
    if res['ret'] == 0:
        if not res['data']['image_records']:
            return -1
        for val in res['data']['image_records']:
            del val['x']
            del val['y']
            del val['width']
            del val['height']
        return res['data']['image_records']
    else:
        return -1

'''中文翻译成英文'''
def img2en(filename=''):
    if not filename:
        return -1
    zh_url = 'https://www.yuanfudao.com/tutor-ybc-course-api/img2en.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img']=b64img
    r = requests.post(zh_url, data=data)
    res = r.json()
    if res['ret'] == 0:
        if not res['data']['image_records']:
            return -1
        for val in res['data']['image_records']:
            del val['x']
            del val['y']
            del val['width']
            del val['height']
        return res['data']['image_records']
    else:
        return -1

def main():
    res = img2zh('images.jpg ')
    print(res)
    res = img2en('22.jpeg')
    print(res)
if __name__ == '__main__':
    main()
