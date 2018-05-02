import os, sys, json

sys.path.insert(0,os.path.realpath(__file__))
from tsr.modules.colours import *
from tsr.modules.general import *
from tsr.modules.os_info import *

def load_forum_database(forumtype, forumid, **kwargs):
    toprint=''
    load_threads=False
    sorting='id'
    maximum_threads=100000
    if kwargs:
        if 'load_threads' in kwargs.keys():
            if kwargs['load_threads']:
                load_threads=True
        if 'sorting' in kwargs.keys():
            sorting=kwargs['sorting']
        if 'max_threads' in kwargs.keys():
            maximum_threads=kwargs['max_threads']
    ls_success=[]
    ls_warning=[]
    ls_error=[]
    ls_failure=[]
    ls_threads=[] # All threads that can load
    usernames_to_id={}
    
    try:
        threads=json.load(open(path.threads_json)) # json of all threads ever cached with json caching setting enabled
    except:
        threads={}
    
    if forumtype=='forum':
        fthreads_ls=[int(n) for n in open(os.path.join(path.forums, forumid, 'threads.txt')).read().split('\n') if n!=''] # We want integers, because 55 < 500 (but '55' > '500')
        fthreads_ls=sorted(list(set(fthreads_ls)), reverse=True)
        fthreads_ls=[str(n) for n in fthreads_ls]
        
        if sorting=='rid':
            fthreads_ls=fthreads_ls[::-1] # But by default, we want the newest threads first
        
        i,failures,errors,warnings,successes=0,0,0,0,0
        while (successes+warnings+errors<maximum_threads)&(i<len(fthreads_ls)):
            threadid=fthreads_ls[i]
            try:
                list_of_posts=[]
                if threadid in threads.keys(): 
                    thread_dict=threads[threadid]
                    list_of_postids=thread_dict['posts']
                    for postid in list_of_postids:
                        post=json.load(open(os.path.join(path.posts, str(postid)+'.json')))
                        post['datetime']=standardise_datetime(post['datetime'])
                        list_of_posts.append(post)
                    thread_dict['posts']=list_of_posts # Rather than list of post IDs
                else: # We'll see if we have it in loose form
                    tposts=open(os.path.join(path.threads, threadid, 'posts.txt')).read()
                    for postid in ls_rm_dupl(tposts.rstrip().split('\n')):
                        post=json.load(open(os.path.join(path.posts, postid+'.json')))
                        post['datetime']=standardise_datetime(post['datetime'])
                        list_of_posts.append(post)
                    thread_dict_file=open(os.path.join(path.threads, threadid, 'meta.json'))
                    thread_dict=json.load(thread_dict_file)
                    thread_dict['posts']=list_of_posts
                    if load_threads:
                        for p in list_of_posts:
                            usernames_to_id[p['user']['name']]=p['user']['id']
                    thread_dict['id']=threadid
                thread_dict['nPosts']=len(list_of_posts)
                if 'nPosts_claimed' in thread_dict.keys():
                    if thread_dict['nPosts']==thread_dict['nPosts_claimed']:
                        successes+=1
                        ls_success.append(int(threadid))
                        if load_threads:
                            ls_threads.append(thread_dict)
                        toprint+=myjoin(cl.green, threadid, '', successes, cl.yellow, warnings, cl.brown, errors, cl.red, failures, cl.end, '\r') # Replaces last line of output
                    else:
                        errors+=1
                        ls_error.append(int(threadid))
                        if load_threads:
                            ls_threads.append(thread_dict)
                        toprint+=myjoin(cl.brown, threadid, cl.green, successes, cl.yellow, warnings, cl.brown, errors, cl.red, failures, cl.red, 'nPosts:', thread_dict['nPosts'], 'nPosts_claimed:', thread_dict['nPosts_claimed'], cl.end)
                else:
                    if len(thread_dict['posts'])==0:
                        failures+=1
                        ls_failure.append(int(threadid))
                        toprint+=myjoin(cl.red, 'Cannot load any posts', cl.end)
                    else:
                        warnings+=1
                        ls_warning.append(int(threadid))
                        if load_threads:
                            ls_threads.append(thread_dict)
                        toprint+=myjoin(cl.yellow, threadid, cl.green, successes, cl.yellow, warnings, cl.brown, errors, cl.red, failures, cl.yellow, 'No nPosts_claimed', cl.end)
            except: # Probably KeyError, due to no posts attached to thread_dict, i.e. we haven't cached the thread except from the forum page
                try:
                    failures+=1
                    ls_failure.append(int(threadid))
                    toprint+=myjoin(cl.red, threadid, cl.green, successes, cl.yellow, warnings, cl.brown, errors, cl.red, failures, cl.end)
                except: # Probably blank
                    pass
            i+=1
    elif forumtype=='userid':
        posts_ls=json.load(open(os.path.join(path.users_json)))[str(forumid)]['posts']
        fthreads_titles={}
        for post_id in posts_ls:
            post=json.load(open(os.path.join(path.posts, str(post_id)+'.json')))
            title=post['title'].split(' - Page')[0].split(' - The Student Room')[0]
            toprint+=myjoin(post_id, title, '\r')
            try:
                fthreads_titles[title]['posts'].append(post)
            except:
                fthreads_titles[title]={
                    'title': title,
                    'posts': [post],
                    'user': {
                        'name':'?'
                    },
                    'nPosts_claimed': -1,
                }
        for thread in fthreads_titles:
            fthreads_titles[thread]['nPosts']=len(fthreads_titles[thread]['posts'])
            ls_threads.append(fthreads_titles[thread])
    
    return ls_success, ls_warning, ls_error, ls_failure, ls_threads, usernames_to_id
