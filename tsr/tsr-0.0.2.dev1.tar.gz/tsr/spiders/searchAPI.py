# -*- coding: utf-8 -*-
import json, io, re, os, sys, shutil, argparse
from bs4 import BeautifulSoup

sys.path.insert(0,os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from modules.general import *
from modules.os_info import *
from modules import regex, forumload, soups

parser=argparse.ArgumentParser()
parser.add_argument('--port', type=int)
parser.add_argument('--forum-id', type=int)
parser.add_argument('--user-id', type=int)
parser.add_argument('--thread_type', type=str)
parser.add_argument('--page-first', type=int)
parser.add_argument('--page-last', type=int)
parser.add_argument('--overwrite-threads', dest='overwrite-threads', action='store_true')
parser.add_argument('--no-overwrite-threads', dest='overwrite-threads', action='store_false')
parser.add_argument('--overwrite-posts', dest='overwrite-posts', action='store_true')
parser.add_argument('--no-overwrite-posts', dest='overwrite-posts', action='store_false')
parser.add_argument('--delay', type=float)

mkdir(path.main) # Superfluous, since mkdir() is recursive, but ignoring would look odd
mkdir(path.posts)
mkdir(path.threads)
mkdir(path.users)
mkdir(path.forums)
mkdir(path.settings)
touch(path.log)

settings=json.load(open(os.path.join(path.settings, 'settings.json')))

def main(kwargs):
    forum_id=False
    user_id=False
    thread_type='t'
    page_first=1
    page_last=999999
    overwrite_threads=True
    overwrite_posts=False
    delay=11.0
    if 'forum-id' in kwargs.keys():
        forum_id=kwargs['forum-id']
    elif 'user-id' in kwargs.keys():
        user_id=kwargs['user-id']
    if 'thread-type' in kwargs.keys():
        thread_type=kwargs['thread-type']
    if 'page-first' in kwargs.keys():
        page_first=int(kwargs['page-first'])
    if 'page-last' in kwargs.keys():
        page_last=int(kwargs['page-last'])
    if 'overwrite-threads' in kwargs.keys():
        overwrite_threads=kwargs['overwrite-threads']
    if 'overwrite-posts' in kwargs.keys():
        overwrite_posts=kwargs['overwrite-posts']
    if 'delay' in kwargs.keys():
        delay=int(kwargs['delay'])
    session=requests.Session()
    if 'port' in kwargs.keys():
        session.mount('https://', Port_Source(kwargs['port']))
    
    d={}
    thread_ids=[]
    threads_cannot_load=[]
    
    page_current=page_first
    
    if forum_id:
        id_value=forum_id
        filter_type='forumid'
    elif user_id:
        id_value=user_id
        filter_type='userid'
    
    while page_current<=page_last:
        if thread_type=='t':
            url='https://www.thestudentroom.co.uk/search.php?filter[type]=thread&filter[{}]={}&page={}'.format(str(filter_type), str(id_value), str(page_current))
        elif thread_type=='p':
            url='https://www.thestudentroom.co.uk/search.php?filter[{}]={}&page={}'.format(str(filter_type), str(id_value), str(page_current))
        
        request=session.get(url)
        soup=BeautifulSoup(request.text, 'html.parser')
        
        page_current+=1
        page_last=int(soup.find('a', {'class':'pager-last'})['href'].split('&page=')[-1].split('&')[0])
        
    def parse_forumpage(soup):
        try:
            rows_threads=soup.find('table', {'id':'search_results_posts'}).find_all('tr') # Get every row in table
        except:
            print(cl.red, 'No table rows', cl.end)
            print('', soup.text[200:])
            rows_threads=[]
        rows_threads=[t for t in rows_threads if t.find('td', {'class':'alt2'})] # Removes the first three descriptive rows
        rows_threads=[t for t in rows_threads if t.find('td', {'class':'alt2'}).find('a')] # Check contains title
        thread_ids=[]
        thread_meta_dict={}
        
        for row in rows_threads:
            x=row.find('td', {'class':'alt2'})
            try:
                nReplies=int(row.find_all('td')[3].text.strip().split(' replies')[0])
            except:
                nReplies=-1
            thread_id=x.find('a')['href'].split('?'+thread_type+'=')[-1].split('&')[0]
            thread_ids.append( thread_id )
            thread_ids.append( thread_id )
            try:
                author_name=x.find('span').find('a').text
            except:
                author_name=[y for y in row.find_all('a') if y['href']]
                try:
                    author_name=[y for y in author_name if 'member.php?u=' in y['href']][0]
                except:
                    print(row)
                author_name=author_name.text
            thread_meta_dict[thread_id]={ # For print() descriptive purposes only
                'title':x.find('a').text,
                #'id':thread_id,
                'user':{
                    'name':author_name
                },
                #'author_id':x.find('span').find('a')['href'].split('?u=')[-1],
                'nPosts_claimed':nReplies+1,
            }
        
        current_page_n_str=soup.find('li', {'class':'current'}).text.strip()
        print('\n')
        print('Page', current_page_n_str)
        with open(path.log, 'a') as f:
            f.write(current_page_n_str)
            f.close()
        for n in thread_ids:
            nstr=str(n)
            
            thread_meta=thread_meta_dict[n]
            
            archive_thread=overwrite_threads # False by default
            if not overwrite_threads:
                if nstr not in os.listdir(path.threads):
                    print(cl.green, 'New thread', cl.end)
                    archive_thread=True
            if n in threads_cannot_load: # Integers
                print(cl.yellow, 'Thread error. Re-archiving', cl.end)
                archive_thread=True
            
            update_metadata=False
            if not archive_thread:
                thread_dump_filepath=os.path.join(path.threads, nstr, 'meta.json')
                
                try:
                    thread_dump_file=open(thread_dump_filepath, 'r+')
                    thread_dump_file_dict=json.load(thread_dump_file)
                except:
                    update_metadata=True
                
                if 'nPosts_claimed' not in thread_dump_file_dict.keys():
                    update_metadata=True
                    print(cl.yellow, 'Updating metadata', cl.end)
            
            if (archive_thread)|(update_metadata):
                if thread_type=='t':
                    thread_meta_parent_path=os.path.join(path.threads, nstr)
                elif thread_type=='p':
                    thread_meta_parent_path=os.path.join(path.threads, 'p'+nstr)
                mkdir(thread_meta_parent_path)
                thread_dump_filepath=os.path.join(thread_meta_parent_path, 'meta.json')
                try:
                    thread_dump_file=open(thread_dump_filepath)
                    thread_dump_file.close()
                except:
                    update_metadata=True
                if update_metadata:
                    touch(thread_dump_filepath)
                    with open(thread_dump_filepath, 'w') as fp:
                        json.dump(thread_meta, fp)
                if archive_thread:
                    yield response.follow(url='https://www.thestudentroom.co.uk/showsoups.php?{0}={1}'.format(thread_type, nstr), callback=parse_threadpage)
            else:
                print(cl.yellow, 'Already scanned thread '+nstr, cl.end)
    def parse_threadpage(page_current):
        soups.parse_threadpage(soup, response.url, thread_type, overwrite_posts=overwrite_posts)
        try:
            page_current=int(response.url.split('&page=')[-1])
        except:
            page_current=1
        if page_current<nPages:
            next_page_url='https://www.thestudentroom.co.uk/showsoups.php?{0}={1}&page={2}'.format(thread_type, str(thread_id), str(page_current+1))
    
    def parse_threadpages():
        while page_current<page_last:
            soup=BeautifulSoup(session.get('https://www.thestudentroom.co.uk/showsoups.php?{0}={1}&page={2}'.format(thread_type, str(thread_id), str(page_current+1))), 'html.parser')
            parse_threadpage(page_current)

if __name__=='__main__':
    main(parser.parse_args())
