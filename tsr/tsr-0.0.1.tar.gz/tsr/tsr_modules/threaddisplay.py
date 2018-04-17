import os, sys, re

sys.path.insert(0,os.path.realpath(__file__))
from tsr.tsr_modules.general import *
from tsr.tsr_modules import regex




def sort_posts_list_by_attr(list_of_posts, attr):
    return sorted(list_of_posts, key=lambda k: k[attr], reverse=True)

def print_posts(posts_list, **kwargs):
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
                contents[i]=re.sub(regex.famous_domain, r'\3{0}\2\4{1}\8'.format(cl.lcyan, cl.end), contents[i], flags=re.MULTILINE) # Colour suspected famous domains in lcyan
                # \.? seperate from ([\n;,...]) is so that we avoid matching urls - we want to catch eg "Google. " not "Google.com"
                contents[i]=re.sub(regex.nation, r'\1{0}\2{1}\17'.format(cl.yellow, cl.end), contents[i], flags=re.MULTILINE) # NB: Groups are not counted the way I expected them to be (parent-to-child then left-to-right), but rather just from left-to-right
                if contents[i][0]=='>':
                    contents[i]=contents[i].replace(cl.end, cl.blue) # So that having e.g. urls in a quote won't break the blue-ness
                    #contents[i]=cl.blue+contents[i].replace(cl.end,'').replace(' ',' '+cl.blue)+cl.end
                    contents[i]=cl.blue+contents[i]+cl.end # So next line wont necessarily be blue
                contents[i]=cl.end+contents[i]
                
                contents[i]=regex.parse__colours_regex(contents[i])
                
                contents[i]+='\n'
            except:
                pass
        to_print+='\n'.join(contents)
        for tag in post['tags']:
            to_print+=cl.blue+post['tags'][tag]+cl.end+'    '
        print(mystrip(to_print))

def print_thread(thread, sorting, *args):
    print(cl.bold, thread['title'], cl.end, thread['id'])
    
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
        #posts_list=sort_posts_list_by_attr( thread['posts'], sorting )[::-1] # Reverse sorting
    elif sorting=='urls':
        #silent=True
        #print_urls_again=True
        urls = re.findall(regex.url, str(raw_contents))
        for u in urls:
            print(u.split('\n')[0])
        posts_list=[]
    elif sorting=='domains':
        count_domains_thread(thread, number_of_domains)
        posts_list=[]
    else:
        posts_list=thread['posts']
    print_posts(posts_list)
