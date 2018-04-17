# -*- coding: utf-8 -*-
import json, io, re, os, sys, shutil, requests
from bs4 import BeautifulSoup
from math import ceil

sys.path.insert(0,os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from tsr_modules import general, scrapers
from tsr_modules.os_info import *

def load_forumpage_threadmeta(forum_id, page_n, **kwargs):
    mkdir(path.main) # Superfluous, since mkdir() is recursive, but ignoring would look odd
    mkdir(path.posts)
    mkdir(path.threads)
    mkdir(path.users)
    mkdir(path.forums)
    mkdir(path.settings)
    touch(path.log) # Doesn't overwrite the log if it exists

    request=requests.get('https://www.thestudentroom.co.uk/forumdisplay.php?f={0}&page={1}'.format(str(forum_id), str(page_n)))
    soup=BeautifulSoup(request.text, 'html.parser')

    thread_meta_dict={}
    thread_meta_list=[]

    rows=soup.find_all('tr', {'class':'thread'})
    securitytoken=scrapers.get_security_token(soup)
    for row in rows:
        thread_id=int(row.find('td', {'class':'title'})['data-id'])
        title=row.find('span', {'class':'titleline'}).find('a').text
        if title=='': # Not sure why, sometimes blank
            title=row.find('td', {'class':'title'})['title'].replace('\n',' ') # Despite what the name suggests, this is not the title, but rather, a glimpse of the opening post
        if 'Moved' not in row.find('span', {'class':'titleline'}).find('span', {'class':'prefix'}).text:
            nPosts=int(row.find('span', {'class':'replies'}).text.strip().replace(',','').split(' ')[-1])+1
            author=row.find('td', {'class':'title'}).find('span', {'class':'byline'})
            try: # requires javascript
                author_name=author.find('a', {'class':'username'}).text.strip()
                author_id=int(author.find('a', {'class':'username'})['href'].split('u=')[-1])
            except:
                author_name=author.text.strip()[2:].strip()
                author_id=-1
            try: # requires javascript
                last_author_name=row.find('td', {'class':'last-post'}).find('span', {'class':'byline'}).find('a', {'class':'username'}).text.strip()
                last_author_id=int(row.find('td', {'class':'last-post'}).find('span', {'class':'byline'}).find('a', {'class':'username'})['href'].split('u=')[-1])
            except:
                last_author_name=row.find('td', {'class':'last-post'}).find('span', {'class':'byline'}).text.strip()[2:].strip()
                last_author_id=-1
            date=general.standardise_date_str(row.find('span', {'class':'date_text'}).text)
            thread_meta_dict[thread_id]={
                'title':title,
                'user':{
                    'name':author_name,
                    'id': author_id
                },
                'nPosts_claimed':nPosts,
                'date':date
            }
            thread_meta_parent_path=os.path.join(path.threads, str(thread_id))
            mkdir(thread_meta_parent_path)
            thread_dump_filepath=os.path.join(thread_meta_parent_path, 'meta.json')
            if not os.path.isfile(thread_dump_filepath): # Dont want to wear out the SSD/HDD
                touch(thread_dump_filepath)
                with open(thread_dump_filepath, 'w') as f:
                    json.dump(thread_meta_dict[thread_id], f)
            thread_meta_dict[thread_id]['id']=thread_id # Dont want to waste space appending this to the file we write
            thread_meta_dict[thread_id]['last_post_username']=last_author_name # nor this, since it changes rapidly
            thread_meta_list.append(thread_meta_dict[thread_id])
    if 'sorting' in kwargs.keys():
        thread_meta_list=sorted(thread_meta_list, key=lambda x: x[ sorting ])
    else:
        thread_meta_list=thread_meta_list[::-1] # Reverse order, to put most recent posts at the bottom
    return thread_meta_list, thread_meta_dict, securitytoken # Give us the choice
