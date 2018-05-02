import os, sys, json
from shutil import get_terminal_size

sys.path.insert(0,os.path.realpath(__file__))
from tsr.modules.general import *
from tsr.modules.os_info import *

settings=json.load(open(os.path.join(path.settings, 'settings.json')))
if settings['use_pandas_for_forum_and_thread_display']:
    import pandas as pd


def display_username_forumdisplay(post):
    return display_username(post, 15)

def display_thread_headers(thread):
    terminal_w=get_terminal_size((80, 20))[0]
    return '  '.join([str(thread['posts'][0]['date']), str(thread['posts'][-1]['date']), make_n_char_long(thread['title'], terminal_w-4-2-10-2-15-2-3-2-3-16, '.'), display_username_forumdisplay(thread['posts'][0]), make_n_char_long(thread['nPosts'], 3), cl.green+make_n_char_long(str(thread['posts'][0]['reps']), 3)])

def toprint_forum(j, attr):
    toprint=''
    sort_ascending=True
    if attr in ['rdate', 'rreps', 'rcreation', 'rposts']:
        attr=attr[1:]
        sort_ascending=False
    if settings['use_pandas_for_forum_and_thread_display']:
        df=pd.DataFrame()
        df['reps']=pd.Series([], dtype=object) # Stop pandas converting the integers to floats
        df['posts']=pd.Series([], dtype=object)
        df['id']=pd.Series([], dtype=object)
        df['creation']=pd.Series([], dtype='datetime64[ns]')
        df['date']=pd.Series([], dtype='datetime64[ns]')
        pd.set_option('colheader_justify', 'left')
        for thread in j:
            df=df.append({
                'id':thread['id'],
                'creation':thread['posts'][0]['date'],
                'date':thread['posts'][-1]['date'],
                'title':thread['title'],
                'user':{
                    'name':display_username(thread['posts'][0])
                },
                'posts':thread['nPosts'], # integer
                'reps':thread['posts'][0]['reps'], # integer
                }, ignore_index=True)
        df.sort_values([attr, 'date', 'reps'], ascending=[sort_ascending, True, True]) # Most rep towards bottom
        df=df[['id', 'creation', 'date', 'title', 'author', 'posts', 'reps']]
        toprint+='\n'+df.to_string()
    else:
        for i in range(len(j)):
            j[i]['order']=i # We want to change the order threads are displayed, while retaining the original index value for the user to reference
        if attr in ['reps','op-date']:
            j=sorted(j, key=lambda k: k['posts'][0][attr])
            if attr in ['rdate']:
                j=j[::-1]
        elif attr in ['date']:
            j=sorted(j, key=lambda k: k['posts'][-1][attr])
            if attr in ['rdate']:
                j=j[::-1]
        elif attr in ['posts']:
            j=sorted(j, key=lambda k: k['nPosts'], reverse=True)
            if attr in ['rposts']:
                j=j[::-1]
        for thread in j:
            toprint+='\n'+make_n_char_long(thread['order'], 4)+'  '+display_thread_headers(thread)
    return toprint

def toprint_forumpage(thread_meta_list, **kwargs):
    for i in range(len(thread_meta_list)):
        thread_meta_list[i]['order']=i
    terminal_w=get_terminal_size((80, 20))[0]
    toprint='n   date . . .'+make_n_char_long(' title', terminal_w-4-2-10-2-15-2-3-2-3-16)+'  author         last_post_by    nPosts'
    if 'sorting' in kwargs.keys():
        thread_meta_list=sorted(thread_meta_list, key=lambda k: k[ kwargs['sorting'] ], reverse=True)
    for i in range(len(thread_meta_list)):
        thread=thread_meta_list[i]
        toprint+='\n'+make_n_char_long(thread_meta_list[i]['order'], 4)+myjoin(thread['date'], make_n_char_long(thread['title'], terminal_w-4-2-10-2-15-2-3-2-3-16, '.'), display_username_forumdisplay(thread), make_n_char_long(thread['last_post_username'], 15), thread['nPosts_claimed'] )
    return toprint
