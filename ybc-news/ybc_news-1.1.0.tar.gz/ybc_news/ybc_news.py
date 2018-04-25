import json
import requests
#import re


def channels():
    '''获取新闻分类'''
    return ['头条','社会','国内','国际','娱乐','体育','军事','科技','财经','时尚']

def news(channel='科技'):
    '''获取指定分类下的新闻'''
    url='https://www.yuanfudao.com/tutor-ybc-course-api/juhe_news.php'
    data = {}
    data['op'] = 'news'
    data['channel'] = channel
    r = requests.post(url, data=data)
    res = r.json()
    res = res['result']
    if res['stat'] == '1' and res['data'] :
        news_list = []
        for item in res['data'] :
            res_info = []
            res_info.append(item['title'])
            res_info.append(item['date'])
            res_info.append(item['thumbnail_pic_s'])
            #item['content'] = item['content'].replace('<br />','')
            #dr = re.compile('<[^>]+>',re.S)
            #item['content'] = dr.sub('',item['content']).strip()
            # res_info.append(item['content'])
            news_list.append(res_info)
        return news_list
    else :
        return -1


def main():
    print(channels())
    print(news('科技'))
    # print(news('新闻'))
    # print(news('新闻'))


if __name__ == '__main__':
    main()
