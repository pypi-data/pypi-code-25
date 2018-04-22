import json
import requests
#import re


def channels():
    '''获取新闻分类'''
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_news.php'
    data = {}
    data['op'] = 'channels'
    r = requests.post(url, data=data)
    res = r.json()
    if res['status'] == '0' and res['result'] :
        return res['result']
    else :
        return -1

def news(channel='科技',num=10,start=0):
    '''获取指定分类下的新闻'''
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_news.php'
    data = {}
    data['op'] = 'news'
    data['channel'] = channel
    data['num'] = num
    data['start'] = start
    r = requests.post(url, data=data)
    res = r.json()
    if res['status'] == '0' and res['result'] :
        news_list = []
        for item in res['result']['list'] :
            res_info = []
            # if item['pic'] == '' :
            #     continue
            res_info.append(item['title'])
            res_info.append(item['time'])
            res_info.append(item['pic'])
            #item['content'] = item['content'].replace('<br />','')
            #dr = re.compile('<[^>]+>',re.S)
            #item['content'] = dr.sub('',item['content']).strip()
            # res_info.append(item['content'])
            news_list.append(res_info)
        return news_list
    else :
        return -1
    # res = jsonarr['result']
    # if res :
    #     news_list = []
    #     for item in res['list'] :
    #         res_info = []
    #         if item['pic'] == '' :
    #             continue
    #         res_info.append(item['title'])
    #         res_info.append(item['time'])
    #         res_info.append(item['pic'])
    #         #item['content'] = item['content'].replace('<br />','')
    #         #dr = re.compile('<[^>]+>',re.S)
    #         #item['content'] = dr.sub('',item['content']).strip()
    #         # res_info.append(item['content'])
    #         news_list.append(res_info)
    #     return news_list
    # else :
    #     return -1


# def recommend(type='keji'):
#     '''返回新闻列表'''
#     APPKEY='279242fdf73bc44118057e142f81cabb'
#     API_URL='http://v.juhe.cn/toutiao/index'
#     data = {}
#     data['key'] = APPKEY
#     url_values = urllib.parse.urlencode(data)
#     url = API_URL + '?type=' + type +'&'+ url_values
#     result = urllib.request.urlopen(url)
#     jsonarr = json.loads(result.read())
#     if jsonarr['error_code'] != 0:
#         print(jsonarr['reason'])
#         exit()
#     res = jsonarr['result']['data']
#     news = []
#     i = 0
#     for new in res:
#         resinfo = []
#         resinfo.append(res[i]['title'])
#         resinfo.append(res[i]['thumbnail_pic_s'])
#         resinfo.append(res[i]['date'])
#         news.append(resinfo)
#         i += 1
#     return news

def main():
    print(channels())
    print(news('科技'))
    # print(news('新闻'))
    # print(news('新闻'))


if __name__ == '__main__':
    main()
