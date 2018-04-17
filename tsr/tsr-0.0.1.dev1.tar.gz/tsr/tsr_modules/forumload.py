import os, sys, json

sys.path.insert(0,os.path.realpath(__file__))
from tsr.tsr_modules.colours import *
from tsr.tsr_modules.general import *
from tsr.tsr_modules.os_info import *

def load_forum_database(forumtype, forumid, **kwargs):
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
                tposts=open(os.path.join(path.threads, threadid, 'posts.txt')).read()
                list_of_posts=[]
                for postid in ls_rm_dupl(tposts.rstrip().split('\n')):
                    dummy=open(os.path.join(path.posts, postid+'.json'))
                    p = json.load(dummy)
                    p['date']=standardise_date(p['date'])
                    list_of_posts.append(p)
                    dummy.close()
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
                        print(cl.green, threadid, '', successes, cl.yellow, warnings, cl.brown, errors, cl.red, failures, cl.end, end='\r') # Replaces last line of output
                    else:
                        errors+=1
                        ls_error.append(int(threadid))
                        if load_threads:
                            ls_threads.append(thread_dict)
                        print(cl.brown, threadid, cl.green, successes, cl.yellow, warnings, cl.brown, errors, cl.red, failures, cl.red, 'nPosts:', thread_dict['nPosts'], 'nPosts_claimed:', thread_dict['nPosts_claimed'], cl.end)
                else:
                    warnings+=1
                    ls_warning.append(int(threadid))
                    if load_threads:
                        ls_threads.append(thread_dict)
                    print(cl.yellow, threadid, cl.green, successes, cl.yellow, warnings, cl.brown, errors, cl.red, failures, cl.yellow, 'No nPosts_claimed', cl.end)
            except: # Probably because we are still crawling it!
                try:
                    failures+=1
                    ls_failure.append(int(threadid))
                    print(cl.red, threadid, cl.green, successes, cl.yellow, warnings, cl.brown, errors, cl.red, failures, cl.end)
                except: # Probably blank
                    pass
            i+=1
    elif forumtype=='userid':
        posts_ls=[int(n) for n in open(os.path.join(path.users, str(forumid), 'posts.txt')).read().split('\n') if n!=''] # still want integers so we can sort the posts
        fthreads_titles={}
        for post_id in posts_ls:
            post=json.load(open(os.path.join(path.posts, str(post_id)+'.json')))
            title=post['title'].split(' - Page')[0].split(' - The Student Room')[0]
            print(post_id, title, end='\r')
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
