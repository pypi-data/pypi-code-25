# -*- coding: utf-8 -*-
import json, re, os, sys, shutil, requests
from bs4 import BeautifulSoup
from math import ceil

sys.path.insert(0,os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from tsr.tsr_modules.general import *
from tsr.tsr_modules.os_info import *
from tsr.tsr_modules import regex, forumload, scrapers

mkdir(path.main) # Superfluous, since mkdir() is recursive, but ignoring would look odd
mkdir(path.posts)
mkdir(path.threads)
mkdir(path.users)
mkdir(path.forums)
mkdir(path.settings)
touch(path.log)

settings=json.load(open(os.path.join(path.settings, 'settings.json')))

post_list=[] # We want to load just the first page of a thread, then display the results, then load the other pages in the background, continually appending them to this list as we refresh tsr_on_cl.py (probably so that every time we return to the main prompt, we get the latest page). Hence we probably want to do threading, and it is neater to do it here rather than mess the main thing up.
# Actually, having said that, it makes more sense to do it in tsr_on_cl.py. This is because we will probably want to utilise threading in other tasks.

def load_thread(thread_id, page_max, **kwargs):
    page_current=1
    post_list=[]
    while page_current<1+page_max:
        (post_list_new, securitytoken)=load_thread_page(thread_id, page_max, **kwargs)
        post_list+=post_list_new
        post_list_new=[]
        page_current+=1
    return post_list, securitytoken

def load_thread_page(thread_id, page_n, **kwargs):
    url='https://www.thestudentroom.co.uk/showthread.php?t={0}&page={1}'.format(str(thread_id), str(page_n))
    if 'session' in kwargs.keys():
        request=kwargs['session'].get(url)
    else:
        request=requests.get(url)
    soup=BeautifulSoup(request.text, 'html.parser')
    post_list, securitytoken=parse_threadpage(soup, url, 't', False)
    return post_list, securitytoken

def parse_threadpage(soup_main, url, thread_type, overwrite_posts):
    post_list=[]
    forum={
        'name':[x.find('a').text for x in soup_main.find_all('span', {'class':'navbar'})][-1],
        'id':[x.find('a')['href'] for x in soup_main.find_all('span', {'class':'navbar'})][-1].split('?f=')[-1],
        }
    #url=soup_main.find('link', {'rel':'canonical'})['href']
    if '?t=' in url:
        thread_id=int(url.split('?t=')[-1].split('&page=')[0].split('&')[0])
    elif '?p=' in url:
        thread_id=soup_main.find('a', {'class':'twitter-share-button'})['data-url']
        thread_id=int(thread_id.split('t=')[-1].split('&')[0])
    mkdir(os.path.join(path.forums, str(forum['id'])))
    outfile_path=os.path.join(path.forums, str(forum['id']), 'threads.txt')
    touch(outfile_path)
    with open(outfile_path, 'a') as outfile:
        outfile.write(str(thread_id)+'\n')
        outfile.close()
    
    securitytoken=scrapers.get_security_token(soup_main)
    posts=soup_main.find_all('li', {'class':'post'})
    for p in posts:
        try: # There are different formats for dates
            date_reverse=p.find('span', {'class':'datestamp'}).text # 13-01-2018
            date_reverses=date_reverse.split('-')
            date_str=''
            for x in date_reverses:
                date_str+='-'+x
            date_str=date_str[1:]
            
            time=p.find('span', {'class':'timestamp'}).text # 18:26
        except:
            datetime_str=p.find('time', {'class':'standard'})['datetime'] # 2018-01-13T15:45:30+00:00
            date_str=datetime_str[:10]
            time=datetime_str.split('T')[-1].split('+')[0]
            
        userdata=p.find('div', {'class':'username'}).find('a')
        user_id=int(userdata['href'].split('?u=')[-1])
        user_name=userdata.text.strip()
        user_avatar=p.find('div', {'class':'avatar'}).find('img')['src']
        download_user_avatar=False
        if '/genericavatar/' not in user_avatar:
            download_user_avatar=True
        user_avatar_url='https:'+user_avatar
        user_avatar=user_avatar.split('/')[-1]
        
        try:
            gender=p.find('div', {'class':'sex'}).find('div')['title']
        except:
            gender=''
        try:
            user_rank=p.find('li', {'class':'rank'}).text.strip()
        except:
            user_rank=''
        
        try:
            user_reps_data=p.find('span', {'class':'rep'})['title']
            user_reps=int(user_reps_data.split(' +')[-1])
        except:
            user_reps=-1 # Some users hide their reps
        
        try:
            post_reps=int(p.find('span', {'class':'score '}).text)
        except:
            post_reps=int(p.find('span', {'class':'score'}).text)
        
        #post_number=int(p.find('li', {'class':'post-number'}).text.strip()) # NOT post_id
        post_id=int(p.find('a', {'class':'postanchor'})['id'].split('post')[-1])
        
        try:
            post_title=p.find('div', {'class':'post-title'}).text.strip()
        except: # ie doesnt exist, probably because is thread starter
            try:
                post_title=p.find('title').text
            except:
                post_title=[x.find('span', {'class':'text'}).text for x in soup_main.find_all('h1')][0] # Why not use this from the start? Well, it seems that TSR does allow replies to have different titles to the original post title (the thread title). Not only are replies distinguished by "Re: " at the start, but it might also tell us if and when the thread title was changed.
        
        post_content_data=p.find('div', {'class':'post-content'})
        scrapers.replace_images_with_hrefs(post_content_data) # FIRST, to replace images in quotes and spoilers
        scrapers.full_urls(post_content_data)
        
        anchors = post_content_data.find_all('a') # FIRST, to replace images in quotes and spoilers
        for a in anchors:
            if a['href']=='http://www.thestudentroom.co.uk/app':
                a.decompose()
        for a in anchors:
            try:
                a.replaceWith(' '+a['href']+' ')
            except:
                pass
        quote_origins=post_content_data.find_all('span', {'class':"origin"})
        post_quotes=[]
        for q in quote_origins:
            try:
                quoted_post=q.find('a')['href'].split('#post')[-1]
            except:
                quoted_post=''
            quoted_user=q.find('strong').text
            post_quotes.append({'user':quoted_user, 'post-id':quoted_post})
            q.replaceWith( '>'+quoted_user+'  '+str(quoted_post) ) # <strong>User quoted</strong>
        quotes=post_content_data.find_all('div', {'class':"quote_block"})
        for q in quotes:
            qtext=q.text
            qtext=qtext.replace('\n','\n>').rstrip()
            q.replaceWith('>'+qtext)
        tags=scrapers.replace_tags(post_content_data) # AFTER quotes, to only add tags in the current post (not quotes)
        spoilers=post_content_data.find_all('div', {'class':"spoiler-content"})
        for s in spoilers:
            stext = s.text.replace('\n','\n~ ')
            s.replaceWith('~ '+stext)
        prespoilers=post_content_data.find_all('span', {'class':"pre-spoiler"})
        for s in prespoilers:
            s.decompose()
        
        content=mystrip( post_content_data.find('blockquote').text )
        
        post_dict={
            'id':post_id,
            'title':post_title,
            'date':standardise_date_str(date_str),
            'time':time,
            'reps':post_reps,
            'tags':tags,
            'quotes':post_quotes,
            'quoted-by':[],
            'domains':regex.findall_domains(content),
            'user':{
                'id':user_id,
                'name':user_name,
                'reps':user_reps,
                'gender':gender,
                'rank':user_rank,
            },
            'thread':{
                'id':thread_id,
                'title':[x.find('span', {'class':'text'}).text for x in soup_main.find_all('h1')][0],
            },
            'content':content,
        }
        post_list.append(post_dict)
        thread_path=os.path.join(path.threads, str(thread_id))
        if thread_type=='p':
            thread_meta_parent_path=os.path.join(path.threads, 'p'+str(post_id))
            if os.path.isdir(thread_meta_parent_path):
                if os.path.isdir(thread_path):
                    shutil.rmtree(thread_meta_parent_path)
                else:
                    shutil.move(thread_meta_parent_path, thread_path)
        
        post_outfile=os.path.join(path.posts, str(post_id)+'.json')
        if (not os.path.isfile(post_outfile))|(overwrite_posts):
            touch(post_outfile)
            with open(post_outfile,'w') as fp:
                json.dump(post_dict, fp)
            mkdir(thread_path)
            with open(os.path.join(thread_path, 'posts.txt'),'a') as thread_postlist:
                thread_postlist.write(str(post_id)+'\n')
                thread_postlist.close()
            user_path=os.path.join(path.users, str(user_id))
            mkdir(user_path)
            with open(os.path.join(user_path, 'posts.txt'), 'a') as user_postlist:
                user_postlist.write(str(post_id)+'\n')
                user_postlist.close()
            mkdir(os.path.join(user_path, 'avatars'))
            try:
                user_avatarlist=open(os.path.join(user_path, 'avatars', 'list.txt'),'r').read().split('\n')
            except:
                touch(os.path.join(user_path, 'avatars', 'list.txt'))
                user_avatarlist=['this is probably not a valid avatar name, although i may eventually be proven wrong.']
            user_avatarlist=[x for x in user_avatarlist if x.strip()] # Removes blank elements
            if user_avatarlist[-1] != user_avatar:
                with open(os.path.join(user_path, 'avatars', 'list.txt'),'a') as user_avatarlist:
                    user_avatarlist.write(str(user_avatar))
                    if download_user_avatar:
                        download_file(user_avatar_url, os.path.join(user_path, 'avatars'))
    return post_list, securitytoken
