import json
import requests


def brands():
    '''返回所有汽车品牌'''
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_carinfo.php'
    r = requests.post(url)
    res = r.json()
    if res['status'] == '0' and res['result'] :
        result = res['result']
        cars = []
        for val in result:
            cars.append(val['name'])
        return cars
    else :
        return -1



def info():
    '''返回所有品牌的信息'''
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_carinfo.php'
    r = requests.post(url)
    res = r.json()
    if res['status'] == '0' and res['result'] :
        result = res['result']
        carsinfo = []
        for val in result:
            carsinfo.append([val['name'],val['initial'],val['logo']])
        return carsinfo
    else :
        return -1

def main():
    # print(brands())
    print(info())

if __name__ == '__main__':
    main()
