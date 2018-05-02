import os, sys, re

sys.path.insert(0,os.path.realpath(__file__))
from tsr.modules.general import *
from tsr.modules import regex




def sort_posts_list_by_attr(list_of_posts, attr):
    return sorted(list_of_posts, key=lambda k: k[attr], reverse=True)

def toprint_posts(posts_list, **kwargs):
    if 'sorting' in kwargs.keys():
        if kwargs['sorting'][:4]=='user':
            sorting=kwargs['sorting'][4:]
            posts_list=sorted(posts_list, key=lambda k: k[ sorting ])
        else:
            posts_list=sorted(posts_list, key=lambda k: k[ kwargs['sorting'] ])
    usernames=set([re.escape(post['user']['name']) for post in posts_list]) # re.escape means special characters dont affect our regex later
    usernames_regex='|'.join(usernames)
    for post_n in range(len(posts_list)):
        post=posts_list[post_n]
        try:
            datestamp=str(post['date'])+'_'+post['time']
        except:
            datestamp='yyyy-mm-dd_hh:mm'
        posttitle=post['title'].replace(' - The Student Room','')
        
        to_print=colour_alternating(post_n)
        to_print+='  {0}{1}  {2}{3}  {4}{5}{6}  '.format(cl.bold, posttitle, cl.end, datestamp, cl.cyan, post['id'], cl.end)
        reps=int(post['reps'])
        if reps>0:
            to_print+=cl.green+str(reps)+cl.end+'    '
        to_print+='\n'
        
        to_print+=display_username(post)#'\n{0}{1}  {2}{3}  {4}{5}{6}  '.format(cl.purple, display_username(post), cl.lcyan, post['user']['id'], cl.yellow, usertag, cl.end )
        
        contents=post['content'].split('\n')
        for i in range(len(contents)):
            try:
                contents[i]=re.sub(regex.url2, r'{0}\1{1}'.format(cl.cyan, cl.end), contents[i], flags=re.MULTILINE) # Colour urls CYAN
                contents[i]=re.sub(regex.image, r'{0}\1{1}'.format(cl.purple, cl.end), contents[i], flags=re.MULTILINE) # Colour images (inc. image filenames in urls) purple
                contents[i]=re.sub(r'({0})'.format(usernames_regex), r'{0}\1{1}'.format(cl.bold, cl.end), contents[i], flags=re.MULTILINE) # Colour suspected usernames (in text) bold
                contents[i]=regex.parse__colours_regex(contents[i])
                if contents[i][0]=='>':
                    contents[i]=contents[i].replace(cl.end, cl.blue) # So that having e.g. urls in a quote won't break the blue-ness
                    contents[i]=cl.blue+contents[i]+cl.end # So next line wont necessarily be blue
                contents[i]=cl.end+contents[i]
                contents[i]+='\n'
            except:
                pass
        to_print+='\n'.join(contents)
        for tag in post['tags']:
            to_print+=cl.blue+post['tags'][tag]+cl.end+'    '
        return mystrip(to_print)

def toprint_thread(thread, sorting, *args):
    if args:
        number_of_domains=args[0]
    else:
        number_of_domains=50
    
    raw_contents=[]
    for post in thread['posts']:
        raw_contents.append(post['content'])
        username_to_id[post['user']['name']]=post['user']['id']
    
    if sorting in ['reps']:
        posts_list=sorted(thread['posts'], key=lambda x: x['reps'], reverse=True) # sort by occurances, most to least
    else:
        posts_list=thread['posts']
    return thread['title']+' | '+thread['id']+'\n\n'+toprint_posts(posts_list)
