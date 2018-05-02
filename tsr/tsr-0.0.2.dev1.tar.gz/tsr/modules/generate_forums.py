from bs4 import BeautifulSoup
import requests, json, os, sys

sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from modules.os_info import *

def main():
    forum_dict={}

    forumPHP=requests.get('https://www.thestudentroom.co.uk/forum.php')
    soup=BeautifulSoup(forumPHP.text, 'html.parser')

    categories=soup.find_all('table', {'class':'forum-category'})
    for category in categories:
        category_title=category.find('th', {'class':'title'}).find('a').text.strip()
        forum_dict[category_title]={}
        forums=category.find_all('tr', {'class':'forum'})
        forums=[f for f in forums if f.find('div', {'class':'description'})]
        for f in forums:
            title=f.find('a').text.strip()
            forum_id=int(f.find('td', {'class':'info'})['id'][1:])
            try:
                nPosts=int(f.find('td', {'class':'count'}).text.strip().replace(',',''))
            except:
                nPosts=-1
            desc=f.find('div', {'class':'description'}).text.strip()
            forum_dict[category_title][forum_id]={
                'title':title,
                'id':forum_id,
                'nPosts':nPosts,
                'desc':desc,
            }

    json.dump(forum_dict, open(os.path.join(path.settings, 'forums.json'), 'w'))
