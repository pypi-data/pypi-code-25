import json
import requests





def pm25(city=''):
    if city == '':
        return -1
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_pm25.php'
    data = {}
    data['city'] = city
    r = requests.post(url, data=data)
    res = r.json()['result']
    if res:
        res_dict = {}
        res_dict['city']=res['city']
        res_dict['pm25']=res['pm2_524']
        res_dict['quality']=res['quality']
        res_dict['level']=res['aqiinfo']['level']
        res_dict['affect']=res['aqiinfo']['affect']
        res_dict['advise']=res['aqiinfo']['measure']
        res_dict['position'] = []
        for val in res['position']:
            pos_list = {}
            pos_list['posname'] = val['positionname']
            pos_list['pm25'] = val['pm2_524']
            pos_list['quality'] = val['quality']
            res_dict['position'].append(pos_list)
        return res_dict
    else:
        return -1


def main():
    print(pm25('哈尔滨'))

if __name__ == '__main__':
    main()
