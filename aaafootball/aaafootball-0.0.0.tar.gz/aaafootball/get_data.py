import requests
from bs4 import BeautifulSoup #html5lib
import pandas as pd

def mapf(f,l):
    return list(map(f,l))

def makeparams(tid,p):
    return {'block_id':'page_team_1_block_team_matches_3',
            'callback_params': '{"page":0, "block_service_id":"team_matches_block_teammatches", "team_id":%d, "competition_id":0, "filter":"all", "new_design":false}' % tid,
             'action':'changePage',
             'params':'{"page":%d}' % p
             }

def process_row(tr):
    try:
        tds = tr.find_all('td')
        return {'timestamp':tds[0].find('span')['data-value'],
                'compname':tds[2].find('a')['title'],
                't1':tds[3].find('a')['href'].split('/')[-2],
                't1-name':tds[3].text,
                't2':tds[5].find('a')['href'].split('/')[-2],
                't2-name':tds[5].text,
                'score':tds[4].text,
                'mid':tds[4].find('a')['href']}
    except:
        return {}

def get_team(tid,maxp=-1):

    baseurl = 'https://int.soccerway.com/a/block_team_matches'

    p = 0

    dfl = []

    while True:
        print(-p, " of maximum ",maxp)
        params = makeparams(tid,p)
        p -= 1
        r = requests.get(baseurl, params=params)
        data = r.json()
        trs = BeautifulSoup(data['commands'][0]['parameters']['content'],
                'html5lib').find_all('tr')[1:]
        isnext = data['commands'][1]['parameters']['attributes']['has_previous_page']
        dfl += mapf(process_row,trs)
        if isnext != '1':
            break
        if maxp >= 1:
            if -maxp > p:
                break

    return pd.DataFrame(dfl)

