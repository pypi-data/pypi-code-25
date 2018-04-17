import os, json, sys, re, shlex, subprocess, matplotlib # import os and call help(os.path) for reasons
import pandas as pd
from math import ceil
try:
    from nltk import word_tokenize, pos_tag, PorterStemmer
    use_nltk=True
except ImportError:
    use_nltk=False
from collections import Counter
from time import sleep as time_sleep

sys.path.insert(0,os.path.realpath(__file__))
from tsr.tsr_modules.os_info import * # path.$PATH is convenient
from tsr.tsr_modules.colours import * # cl.$CL is convenient
from tsr.tsr_modules.general import *
from tsr.tsr_modules import grammar, threaddisplay, regex, forumload, forumdisplay
from tsr.tsr_scrapers import forumpage
import tsr.tsr_scrapers.thread

def load_dict_users():
    users={}
    username_colour_dict={} # temporary colour scheme for users without flairs/colours, for easier reading
    username_to_id=json.load(open(os.path.join(path.settings, 'username_to_id.json'))) # Merge into users.json?
    users=json.load(open(os.path.join(path.settings, 'users.json')))
    for entry in users:
        if not 'colour' in users[entry].keys():
            users[entry]['colour']='end'
        if users[entry]['colour'] is None:
            users[entry]['colour']='end'
        username=users[entry]['name']
        if type(username)=='str':
            username=[username]
        users[entry]['name']=ls_rm_dupl(username) # tmp
    return users

def count_domains(obj, only_image_hosts):
    search_strings=str(obj).split('\n')
    i=0
    while i<len(search_strings):
        if search_strings[i][0]=='>':
            print('RM: '+search_strings[i][:10])
            del search_strings[i]
        else:
            i+=1
    search_string=''.join(search_strings)
    
    domains=regex.findall_domains(search_string, only_image_hosts=only_image_hosts)
    
    domains_d=Counter(domains)
    return domains_d

def count_domains_dict(j, arguments, *args):
    if j=={}:
        print(cl.red, 'No forum-like object loaded', cl.end)
        return
    only_image_hosts=False
    if args:
        if args[0] in ['img','image','imgs','images']:
            only_image_hosts=True
    
    try:
        max_domains=int(arguments[0])
    except:
        max_domains=25
    try:
        if arguments[1]=='%':
            percent_mode=True
        else:
            percent_mode=False
    except:
        percent_mode=False
    raw_contents=[]
    for thread in j:
        for post in thread['posts']:
            raw_contents.append(post['content'])
    
    domains_d=count_domains(raw_contents, only_image_hosts)

    header1=cl.cyan+'Domain'+cl.end
    header2=cl.purple+'Count'+cl.end
    column1=[]
    column2=[]
    for d in domains_d:
        column1.append(d)
        column2.append(int(domains_d[d]))
    # Pandas doesnt work for some reason
    total=sum(column2)
    print(header1, header2, 'total='+str(total))
    i=max(column2)
    number_printed=0
    try:
        max_domains=int(max_domains)
    except: # No argument given
        max_domains=25
    try:
        if int(arguments[1])==0:
            silent_count=True
    except:
        silent_count=False
    while i>0:
        for d in domains_d:
            if domains_d[d]==i:
                if number_printed<max_domains:
                    if silent_count:
                        print(d)
                    else:
                        if percent_mode:
                            print(d, 100*domains_d[d]/total)
                        else:
                            print(d, domains_d[d])
                    number_printed+=1
        i-=1

def count_domains_thread(thread, max_domains):
    raw_contents=[]
    for post in thread['posts']:
        raw_contents.append(post['content'])
    
    domains_d=count_domains(raw_contents)

    header1=cl.cyan+'Domain'+cl.end
    header2=cl.purple+'Count'+cl.end
    column1=[]
    column2=[]
    for d in domains_d:
        column1.append(d)
        column2.append(int(domains_d[d]))
    # Pandas doesnt work for some reason
    total=sum(column2)
    print(header1, header2, 'total='+str(total))
    i=max(column2)
    number_printed=0
    try:
        max_domains=int(max_domains)
    except: # No argument given
        arguments=[9999]
    try:
        if int(arguments[1])==0:
            silent_count=True
    except:
        silent_count=False
    while i>0:
        for d in domains_d:
            if domains_d[d]==i:
                if number_printed<max_domains:
                    if silent_count:
                        print(d)
                    else:
                        print(d, domains_d[d])
                    number_printed+=1
        i-=1

def share_dictionaries():
    threaddisplay.username_to_id=username_to_id

def list_forum_ids(forums):
    for category in forums.keys():
        print(cl.yellow, cl.bold, category, cl.end)
        for forum in forums[category].keys():
            print(colour_alternating('', '', make_n_char_long( forums[category][forum]['id'], 4), make_n_char_long( forums[category][forum]['nPosts'], 7), forums[category][forum]['title'], cl.end))
            print('', '', '', '', '', '', forums[category][forum]['desc'])
def list_commands(commands):
    for entry in commands:
        print(cl.end+cl.bold, entry, cl.end)
        colour_alternating('', commands[entry]['desc'][0])
        print_usages=True
        try:
            print('', cl.yellow, commands[entry]['common']['usage'], cl.end)
            print_usages=False
            usage_str=''
        except:
            pass
        for subentry in commands[entry]['commands'].keys():
            if print_usages:
                usage_str=commands[entry]['commands'][subentry]['usage']
            command=commands[entry]['commands'][subentry]['alts'][0]
            colour_alternating('', cl.end, make_n_char_long(command, 15), cl.yellow, usage_str, cl.end)

def main_init():
    mkdir(path.images)
    
    settings=json.load(open(os.path.join(path.settings, 'settings.json')))
    commands=json.load(open(os.path.join(path.settings, 'commands.json')))
    words_colour_dict=json.load(open(os.path.join(path.settings, 'colours_words.json')))
    domain_colour_dict=json.load(open(os.path.join(path.settings,'colours_domains.json')))
    if settings['matplotlib']['headless_backend']:
        matplotlib.use('Agg')
        print(cl.yellow, 'Using Agg backend for matplotlib')
    
    forums=json.load(open(os.path.join(path.settings, 'forums.json')))
    if forums=={}:
        import tsr.tsr_scrapers.forums
        tsr.tsr_scrapers.forums.main()
    
    j_meta={
        'forum_id':0,
        'number':0,
        'sorting':''
    }
    browsing={
        'logged_in':False,
        'browsing':True,
        'forum_id':0,
        'sorting':''
    }
    securitytoken=''
    
    return forums, settings, commands, users, words_colour_dict, domain_colour_dict, j_meta, browsing, securitytoken

def main():
  (forums, settings, commands, users, words_colour_dict, domain_colour_dict, j_meta, browsing, securitytoken)=main_init()
  username_to_id={}
  j={}
  while True:
    print(cl.end)
    print('RAM:',memory_usage())
    print(j_meta)
    print(cl.yellow, securitytoken, cl.end)
    
    share_dictionaries()
    
    command=input('  :')
    
    
    arguments=shlex.split(command)
    
    command=arguments[0]
    arguments=arguments[1:]
    
    for entry in commands['threaddisplay']['commands'].keys():
        if command in ['grep', 'egrep']:
            pass # temporary
        elif command in commands['threaddisplay']['commands'][entry]['alts']:
            attr_value=arguments[0] 
            arguments=arguments[1:]
            try:
                number_to_print=int(arguments[1])
                arguments=arguments[1:]
            except:
                number_to_print=50
            try:
                sorting=arguments[0]
            except:
                sorting='date'
            posts_to_print=[]
            post_ids=[]
            attr_is_user_attr=False
            for thread in j:
                for post in thread['posts']:
                    if entry in post.keys():
                        if post[entry]==attr_value:
                            posts_to_print.append(post)
                    elif (entry[:4]=='user'):
                        attr=entry[4:]
                        attr_is_user_attr=True
                        if attr in post['user'].keys():
                            if post['user'][attr]==attr_value:
                                posts_to_print.append(post)
            try:
                posts_to_print=sorted(posts_to_print, key=lambda x: x['user'][sorting])
            except:
                posts_to_print=sorted(posts_to_print, key=lambda x: x[sorting])
            threaddisplay.print_posts(posts_to_print)
    if command=='total':
        if len(arguments)==0:
            print(cl.red, 'Requires an argument', cl.end)
            print('total [postAttribute/"user"+userAttribute] [numberToPrint]?')
            print('Attributes include', cl.yellow, 'username userid date reps domain imghost', cl.end)
            print('eg', 'total username', cl.blue, 'Table of usernames to frequency')
            print('eg', 'total hour 50', cl.blue, 'Table with 50 entries of posts made at 23:00')
            '''print('total [postAttribute/"user"+userAttribute] [attributeValue]?')
            print('eg', 'total username', cl.blue, 'Table of usernames to frequency')
            print('eg', 'total hour 23', cl.blue, 'Number of posts made at 23:00')
            print('eg', 'total month 1', cl.blue, 'Number of posts made in January')'''
        else:
            filter_attr=arguments[0]
            arguments=arguments[1:]
            attr_is_user_attr=False
            if filter_attr[:4]=='user':
                filter_attr=filter_attr[4:]
                attr_is_user_attr=True
            try:
                number_to_print=int(arguments[0])
                arguments=arguments[1:]
            except:
                number_to_print=50
            try:
                min_occurances=int(arguments[1])
                arguments=arguments[1:]
            except:
                min_occurances=1
            try:
                sort_by=arguments[0]
            except:
                sort_by='count'
            
            attrs=Counter([])
            datetimes=[]
            for thread in j:
                attrs_to_append=[] # Clear it each time to avoid memory explosion in the case of words. Listing every word from every post from every thread is bad idea. Counter is probably more easy on RAM.
                thread_new={x:thread[x] for x in thread.keys() if x!='posts'}
                thread_new['posts']=[]
                for post in thread['posts']:
                    if attr_is_user_attr:
                        if filter_attr in post['user'].keys():
                            append_this=True
                            to_append=post['user'][filter_attr]
                    else:
                        if filter_attr in ['all', 'time', 'date', 'minute', 'hour', 'day', 'month', 'year']:
                            to_append=standardise_date_str(post['date'])+'_'+post['time'][:5]
                            append_this=False
                            datetimes.append(to_append)
                        elif filter_attr in post.keys():
                            to_append=post[filter_attr]
                            append_this=True
                        elif filter_attr in ['word', 'words']:
                            to_append=regex.ls_words(post['content']) # WARNING: This can eat up a lot of memory, probably a bad idea to use on an entire forum consisting of 500 threads.
                            append_this=True
                        elif filter_attr in ['domain', 'domains']:
                            to_append=regex.findall_domains(post['content'])
                            append_this=True
                        elif filter_attr in ['imghost', 'imagehost', 'imghosts', 'imagehosts']:
                            to_append=regex.findall_domains(post['content'], only_image_hosts=True)
                            append_this=True
                    if append_this:
                        if type(to_append).__name__ in ['list']:
                            for child in to_append:
                                attrs_to_append.append(child)
                        else:
                            attrs_to_append.append(to_append)
                attrs=attrs+Counter(attrs_to_append)
            attrs=[(x, attrs[x]) for x in attrs if attrs[x]>min_occurances]
            if len(attrs)==0:
                print(cl.yellow, 'No results', cl.end)
            if filter_attr in ['all', 'time', 'date', 'minute', 'hour', 'day', 'month', 'year']:
                df=pd.DataFrame()
                df['datetime']=pd.to_datetime(datetimes, format='%Y-%m-%d_%H:%M')
                if filter_attr in ['all', 'date']: # Has to come first, before df=df.groupby
                    #df['datetime']=df['datetime'].dt.date #pd.to_datetime(df['datetime'])
                    #df['datetime']=df['datetime'].dt.normalize() # Normalises the dates to midnights
                    df=df.groupby(df['datetime'].dt.normalize())
                    df.count().plot(figsize=(settings['matplotlib']['w']/100, settings['matplotlib']['h']/100))
                else:
                    if filter_attr in ['all', 'time']:
                        df=df.groupby(df['datetime'].dt.time)
                    if filter_attr in ['all', 'minute']:
                        df=df.groupby(df['datetime'].dt.minute)
                    if filter_attr in ['all', 'hour']:
                        df=df.groupby(df['datetime'].dt.hour)
                    if filter_attr in ['all', 'day']:
                        df=df.groupby(df['datetime'].dt.weekday)
                    if filter_attr in ['all', 'month']:
                        df=df.groupby(df['datetime'].dt.month)
                    if filter_attr in ['all', 'year']:
                        df=df.groupby(df['datetime'].dt.year)
                    df.count().plot(kind='bar', figsize=(settings['matplotlib']['w']/100, settings['matplotlib']['h']/100))
                if settings['matplotlib']['headless_backend']:
                    previous_plots=[x for x in os.listdir(path.main) if x.split('.')[-1]=='png']
                    path_plot=os.path.join(path.images, filter_attr+'.png')
                    #matplotlib.pyplot.figure(figsize=(settings['matplotlib_w']/100, settings['matplotlib_h']/100))
                    matplotlib.pyplot.savefig(path_plot) # dpi of 1 doesnt work well with fonts etc, 100 is near standard dpi of 96
                    print(cl.green, 'Saved as', path_plot)
                    matplotlib.pyplot.close()
                else:
                    matplotlib.pyplot.figure(figsize=(settings['matplotlib']['w']/100, settings['matplotlib']['h']/100))
                    matplotlib.pyplot.show()
                    matplotlib.pyplot.close()
            else:
                attrs=sorted(attrs, key=lambda x: x[1], reverse=True)
                attrs=attrs[:number_to_print]
                for x in attrs:
                    print(colour_alternating(make_n_char_long(x[1], 5), x[0]))
    elif command=='help':
        if len(arguments)==0:
            list_forum_ids(forums)
            list_commands(commands)
            print('If errors, check ~/tsr_paths.json and $settingsPath/settings.json')
        elif len(arguments)==1:
            try:
                print(commands[arguments[0]]['common']['help'])
            except:
                print(commands[arguments[0]]['desc'][-1])
        elif len(arguments)==2:
            print(commands[arguments[0]]['commands'][arguments[1]]['help'])
    elif command=='back': # in commands['forumdisplay']['commands']['back']['alts']: # Not elif, so that previous forum can be returned to easily
        if browsing['browsing']:
            forumdisplay.print_forumpage(thread_meta_list)
        else: # So we can load more meta information when displaying the forum-like object
            try:
                number_of_threads=int(arguments[0])
                try:
                    sorting=arguments[1]
                except:
                    sorting='date'
            except:
                number_of_threads=500
                try:
                    sorting=arguments[0]
                except:
                    sorting='date'
            forumdisplay.print_forum(j, sorting)
    elif command in ['setting', 'settings']:
        key=arguments[0]
        if key in settings.keys():
            value=arguments[1]
            if value in ['false', 'False']:
                value=False
            elif value in ['true', 'True']:
                value=True
            else:
                try:
                    value=int(value)
                except:
                    try:
                        value=float(value)
                    except:
                        pass
            settings[key]=value
    elif command in ['tag','flair','colour']:
        username=arguments[0]
        if command=='colour':
            if arguments[1] not in colour.keys():
                print(cl.red, 'Colour not available', cl.end)
                print('Available colours:')
                for key in colour.keys():
                    print(colour[key], key, cl.end)
        try:
            userid=str(username_to_id[username])
            username_is_name=True
            proceed=True
        except:
            username_is_name=False
            try:
                userid=str(int(username))
                proceed=True
            except:
                userid='' # Prevent us from using the last value of userid, ie the wrong user
                print('Known usernames:')
                print(username_to_id.keys())
                print(cl.red, 'Use user ID')
                proceed=False
        if proceed:
            try:
                if username_is_name:
                    try:
                        if username not in users[userid]['name']:
                            users[userid]['name'].append(username)
                    except:
                        users[userid]['name']=[username]
                users[userid][command]=arguments[1]
            except:
                users[userid]={'name':[username], command:arguments[1]}
            print(cl.green, users[userid], cl.end)
            users=load_dict_users()
    elif command in ['dictionary', 'dict']:
        command=arguments[0]
        arguments=arguments[1:]
        if command=='save':
            if arguments[0]=='all':
                arguments=commands['dictionary']['commands']['save']['help']['dictionary']
            if 'settings' in arguments:
                with open(os.path.join(path.settings, 'settings.json'), 'w') as f:
                    json.dump(settings, f)
                print(cl.green, 'Saved settings.json')
            if 'users' in arguments:
                with open(os.path.join(path.settings, 'users.json'), 'w') as f:
                    json.dump(users, f)
                print(cl.green, 'Saved users.json')
            if 'domains' in arguments:
                with open(os.path.join(path.settings, 'colours_domains.json'), 'w') as f:
                    json.dump(domain_colour_dict, f)
                print(cl.green, 'Saved colours_domains.json')
            if 'words' in arguments:
                with open(os.path.join(path.settings, 'colours_words.json'), 'w') as f:
                    json.dump(words_colour_dict, f)
                print(cl.green, 'Saved colours_words.json')
            if 'commands' in arguments:
                with open(os.path.join(path.settings, 'commands.json'), 'w') as f:
                    json.dump(commands, f)
                print(cl.green, 'Saved commands.json')
            if 'username_to_id' in arguments:
                with open(os.path.join(path.settings, 'username_to_id.json'), 'w') as f:
                    json.dump(username_to_id, f)
                print(cl.green, 'Saved username_to_id.json')
            if 'j' in arguments:
                with open(os.path.join(path.settings, '{0}_{1}_{2}.json'.format(str(j_meta['forum_id']), str(j_meta['number']), j_meta['sorting'])), 'w') as f:
                    json.dump(j, f)
                print(cl.green, 'Saved j to .json')
            if 'j_forum' in arguments:
                with open(os.path.join(path.settings, '{0}_{1}_{2}.json'.format(str(j_meta['forum_id']), str(j_meta['number']), j_meta['sorting'])), 'w') as f:
                    json.dump(j_forum, f)
                print(cl.green, 'Saved j_forum to .json')
            print(cl.end)
    elif command in ['url','browser']+settings['browsers']: # Open forum/thread in web browser
        if command=='browser':
            command=settings['browsers'][0] # Use default browser
        command_old=command
        command=arguments[0]
        argument=arguments[1]
        url=''
        if command[:2]=='f=':
            url='https://www.thestudentroom.co.uk/forumdisplay.php?'+command
        elif command[:2] in ['t=', 'p=']:
            url='https://www.thestudentroom.co.uk/showthread.php?'+command
        elif (command[:2]=='u=')|(command=='user'):
            try:
                int(command[2:])
                url='https://www.thestudentroom.co.uk/member.php?'+command
            except:
                try:
                    url='https://www.thestudentroom.co.uk/member.php?'+str(int(argument))
                except:
                    url='https://www.thestudentroom.co.uk/member.php?'+username_to_id[argument]
        elif is_number(command):
            thread_id=j[int(command)]['id']
            url='https://www.thestudentroom.co.uk/showthread.php?t='+thread_id
        if command_old=='url':
            print(url)
        elif url!='':
            subprocess.call([command, url])
    elif command=='browse':
        if len(arguments)==0:
            #list_forum_ids(forums)
            print(cl.red, 'Requires at least one argument', cl.end)
            print('browse f [forumid] [page]?')
            print('browse t [threadid] [page]? [sorting]?')
            print('browse [threadNumber from forum-like object] [page]?')
            print('sorting methods include:  reps, date')
            print('eg', 'browse f 143')
            print('eg', 'browse t 12345678 3')
            print('eg', 'browse 73 1')
            print('Hint', 'Each thread page holds 20 posts')
            print('If thread, also accepts page value of "all"')
        else:
            if len(arguments)==0:
                print(cl.red, 'Requires more arguments', cl.end)
                browse_type='failed'
            else:
                if is_number(arguments[0]):
                    browse_type='thread_list_index'
                    thread_list_index=int(arguments[0])
                    arguments=arguments[1:]
                    try:
                        page_n=int(arguments[0])
                        arguments=arguments[1:]
                    except:
                        page_n=1
                    try:
                        sorting=arguments[0]
                    except:
                        pass
                elif len(arguments)==1:
                    print(cl.red, 'Requires more arguments', cl.end)
                    browse_type='failed'
                else:
                    browsing['browsing']=True
                    browse_type=arguments[0]
                    browse_id=int(arguments[1])
                    arguments=arguments[2:]
                    if len(arguments)==0:
                        page_n=1
                    else:
                        if arguments[-1] in ['all', 'last']:
                            sorting=arguments[-1]
                            arguments=arguments[:-1]
                        elif len(arguments)==1:
                            page_n=int(arguments[0])
                        else:
                            sorting=arguments[0]
                            page_n=int(arguments[1])
            if browse_type=='f':
                browsing['forum_id']=browse_id
                (thread_meta_list, _, securitytoken)=forumpage.load_forumpage_threadmeta(browsing['forum_id'], page_n) # We shouldnt attempt to load all forum pages
                try:
                    forumdisplay.print_forumpage(thread_meta_list, sorting=sorting)
                except:
                    forumdisplay.print_forumpage(thread_meta_list)
            elif browse_type in ['t', 'thread_list_index']:
                if browse_type=='t':
                    thread_id=int(browse_id)
                else:
                    thread_id=int(thread_meta_list[thread_list_index]['id']) # Requires us to have run "browse f $FORUM_ID" before!
                if page_n=='last':
                    page_n=ceil(thread_meta_list[thread_list_index]['nPosts_claimed']/20) # total number of pages in thread
                if page_n=='all':
                    page_n=ceil(thread_meta_list[thread_list_index]['nPosts_claimed']/20) # total number of pages in thread
                    if browsing['logged_in']:
                        (posts_list, securitytoken)=tsr.tsr_scrapers.thread.load_thread(thread_id, page_n, session=session)
                    else:
                        (posts_list, securitytoken)=tsr.tsr_scrapers.thread.load_thread(thread_id, page_n)
                else:
                    if browsing['logged_in']:
                        (posts_list, securitytoken)=tsr.tsr_scrapers.thread.load_thread_page(thread_id, page_n, session=session)
                    else:
                        (posts_list, securitytoken)=tsr.tsr_scrapers.thread.load_thread_page(thread_id, page_n)
                try:
                    threaddisplay.print_posts(posts_list, sorting=sorting)
                except:
                    threaddisplay.print_posts(posts_list)
                username_to_id_new={post['user']['name']:post['user']['id'] for post in posts_list}
                username_to_id=dict(username_to_id, **username_to_id_new) # Combine dicts
                del username_to_id_new
                
                browsing['thread_id']=thread_id
                del thread_id
                
                if j_meta['forum_id']!=browsing['forum_id']:
                    j=[]
                j=[post for post in j if post['title']!=posts_list[0]['title']] # So we can replace it with the updated thread
                j.append({
                    'date':posts_list[0]['date'],
                    'user':{
                        'name':posts_list[0]['user']['name'],
                        'id':posts_list[0]['user']['id']
                    },
                    'title':posts_list[0]['title'],
                    'nPosts':len(posts_list),
                    'nPosts_claimed':len(posts_list),
                    'posts':posts_list
                })
    elif command=='post': # Not working yet
        if len(arguments)==0:
            print(cl.red, 'Requires at least one argument', cl.end)
            print('post [postcontent]')
            print('eg', 'post "I say this"')
            print('eg', 'post "[quote=MrUsername]I say this[/quote] This, 100%. Updooted"')
        else:
            if not browsing['logged_in']:
                import requests # Why start off importing something we may not use?
                session=requests.Session()
                credentials=json.load(open(os.path.join(path.settings, 'credentials.json')))
                if len(credentials.keys())==0:
                    credentials['vb_login_username']=input('Username:    ')
                    credentials['vb_login_password']=input('Password:    ')
                    credentials['userid']=input('User ID:    ')
                    json.dump(open(os.path.join(path.settings, 'credentials.json')))
                credentials['do']='login'
                credentials['securitytoken']='guest'
                credentials['utcoffset']='0'
                credentials['cookieuser']='1'
                url='https://www.thestudentroom.co.uk/login.php?do=login'
                print('Logging in as', credentials)
                session.post(url, credentials)
                time_sleep(2)
                browsing['logged_in']=True
            if securitytoken=='guest':
                (_, securitytoken)=tsr.tsr_scrapers.thread.load_thread_page(browsing['thread_id'], 1, session=session)
            url='https://www.thestudentroom.co.uk/newreply.php?do=postreply&t='+str(browsing['thread_id']) # We are assuming we've run 'browse $THREAD' before this
            content=arguments[0]
            data={
                'fromquickreply':'1',
                'securitytoken':securitytoken,
                'do':'postreply',
                't':str(browsing['thread_id']),
                'p':'who cares',
                'specifiedpost':'0',
                'parseurl':'1',
                'loggedinuser':str(credentials['userid']),
                'postroute':'thread/bottom',
                'message':content,
                'signature':'1',
                'sbutton':'Submit Reply',
            }
            session.post(url, data)
            print(cl.green, data, cl.end)
    elif command=='load': # in commands['forumdisplay']['commands']['forum']['alts']: # Not elif, so that previous forum can be returned to easily
        if len(arguments)==0:
            print(cl.red, 'Requires at least one argument', cl.end)
            print('load [forum/f/user/u] [forumid/username]')
            print('eg', 'load f 143')
            print('eg', 'load u MrUsername')
        else:
            browsing['browsing']=False # So we can load more meta information when displaying the forum-like object
            command=arguments[0]
            arguments=arguments[1:]
            failed=True
            if command in ['f', 'forum']:
                forum_type='forum'
                try:
                    forum_id=str(int(arguments[0]))
                    failed=False
                except:
                    list_forum_ids()
            elif command in ['u', 'user', 'username']:
                try:
                    forum_id=str(username_to_id[arguments[0]])
                except:
                    try:
                        forum_id=str(int(arguments[0]))
                    except:
                        print(cl.red, 'No userid found for username', cl.end)
                        print('Try loading the forum, or browsing a thread, in which the user was active, and then executing', cl.yellow, 'dict save username_to_id', cl.end, 'to expand the list of userids')
                forum_type='userid'
                failed=False
            if not failed:
                try:
                    number_of_threads=int(arguments[1])
                    try:
                        sorting=arguments[2]
                    except:
                        sorting='date'
                except:
                    number_of_threads=500
                    try:
                        sorting=arguments[1]
                    except:
                        sorting='date'
                if (forum_id,number_of_threads,sorting)!=(j_meta['forum_id'],j_meta['number'],j_meta['sorting']):
                    if (forum_id,number_of_threads)!=(j_meta['forum_id'],j_meta['number']):
                        (_, _, _, _, j_forum, username_to_id_new)=forumload.load_forum_database(forum_type, forum_id, max_threads=number_of_threads, sorting=sorting, load_threads=True)
                        username_to_id=dict(username_to_id, **username_to_id_new) # Combine dicts
                        username_to_id_new={}
                        j_meta['forum_id']=forum_id
                        j_meta['number']=number_of_threads
                    j_meta['sorting']=sorting
                j=j_forum
                forumdisplay.print_forum(j, sorting)
    elif command=='filter':
        if len(arguments)<2:
            print(cl.red, 'Requires at least two arguments', cl.end)
            print('filter [postAttribute/"user"+userattribute] [attributeValue]')
            print('eg', 'filter user MrUsername')
        else:
            filter_attr=arguments[0]
            attr_is_user_attr=False
            if filter_attr[:4]=='user':
                filter_attr=filter_attr[4:]
                attr_is_user_attr=True
            filter_value=arguments[1]
            try:
                sorting=arguments[2]
            except:
                sorting='date'
            j=[]
            for thread in j_forum:
                thread_new={x:thread[x] for x in thread.keys() if x!='posts'}
                thread_new['posts']=[]
                for post in thread['posts']:
                    if attr_is_user_attr:
                        if filter_attr in post['user'].keys():
                            if post['user'][filter_attr]==filter_value:
                                thread_new['posts'].append(post)
                    else:
                        if filter_attr in post.keys():
                            if post[filter_attr]==filter_value:
                                thread_new['posts'].append(post)
                if len(thread_new['posts'])>0:
                    j.append(thread_new)
            forumdisplay.print_forum(j, sorting)
    elif command=='t':
        if len(arguments)==0:
            print(cl.red, 'Requires at least one argument', cl.end)
            print('t [thread_id]')
        else:
            thread_id=int(arguments[0])
            dummy=[thread for thread in j if j[thread]['id']==thread_id][0]
            threaddisplay.print_thread(dummy, arguments)
    elif command in ['byday', 'bydate']:
        if len(arguments)==0:
            print(cl.red, 'Requires at least one argument', cl.end)
            print('byday [postAttribute]')
            print('postAttributes include:', 'word noun title user quote domain')
            print('eg', 'byday username')
            print('eg', 'byday word')
        else:
            words_to_ignore=regex.words_to_ignore+['png','jpg','jpeg','gif','webm','mp4']
            try:
                attr=arguments[0]
            except:
                attr='word'
            dates=[]
            for thread in j:
                for post in thread['posts']:
                    date=post['date']
                    try:
                        dummy=date.day
                        dates.append(date)
                    except:
                        dates.append(standardise_date(post['date'])) # not sure why it has been failing on one forum and not the other
            dates=set(dates) # rm duplicates
            dates=sorted(dates, reverse=True) # Most recent first
            words_counters={}
            words_counter_monthly=Counter([])
            toprint_monthly=[]
            for i in range(len(dates)):
                date=dates[i]
                words_counter=Counter([])
                for thread in j:
                    for post in thread['posts']:
                        if date in [post['date'], standardise_date(post['date'])]: # Do NOT use "is" instead of "==". Will only return first post for each date.
                            if attr=='word':
                                words=regex.ls_words(post['content'])
                            elif attr=='noun':
                                if use_nltk:
                                    content=' '.join(re.split(regex.between_words, post['content']))
                                    words_nltk_tokenised=word_tokenize(content)
                                    words_nltk_tagged=pos_tag(words_nltk_tokenised)
                                    
                                    words_nltk_tagged=[(w[0].lower(), w[1]) for w in words_nltk_tagged]
                                    
                                    nouns=[w[0] for w in words_nltk_tagged if w[1]=='NN']
                                    verbs=[w[0] for w in words_nltk_tagged if w[1] in ['VBG','VB']]
                                    misc=[w[0] for w in words_nltk_tagged if w[1]=='JJ']
                                    stemmer=PorterStemmer()
                                    nouns=[stemmer.stem(w) for w in nouns]
                                    verbs=[stemmer.stem(w) for w in verbs]
                                    misc=[stemmer.stem(w) for w in misc]
                                    words=nouns+verbs+misc
                                    words=[w for w in words if (len(w)>2)&(w not in words_to_ignore)]
                                else:
                                    print(cl.red, 'nltk modules word_tokenize, pos_tag, PorterStemmer not installed', cl.end)
                            elif attr=='title':
                                words=re.split(regex.between_words_title, post['thread']['title'])
                                words=[w.lower() for w in words]
                                words=[grammar.singularise(w) for w in words if (len(w)>2)&(w not in words_to_ignore)]
                            elif attr=='user':
                                words=[post['user']['name']]
                                #username_to_id[post['user']['name']]=post['user']['id'] # May as well do this, and might want to add flairs to active users
                            elif attr=='domain':
                                words=regex.findall_domains(post['content'])
                            elif attr in ['quote','quotes']:
                                words=[x['user'] for x in post['quotes']]
                            words_counter=words_counter+Counter(words)
                words=[]
                words_countls=[(words_counter[x], x) for x in words_counter] # list of tuples (username, #occurances)
                results=sorted(words_countls, key=lambda x: x[0], reverse=True)[:10]
                results=[r[1] for r in results]
                #result=' '.join(results)
                results_coloured=[]
                n_colour=0
                if attr in ['word','title','noun']:
                    for r in results:
                        try:
                            results_coloured.append(colour[words_colour_dict[r]]+r+cl.end)
                        except:
                            words_colour_dict[r]=cl_to_assign[n_colour%len(cl_to_assign)]
                            n_colour+=1
                            results_coloured.append(colour[words_colour_dict[r]]+r+cl.end)
                elif attr in ['user','quote','quoted']:
                    for r in results:
                        try:
                            results_coloured.append(userid_colour(username_to_id[r])+r+cl.end)
                        except:
                            if 'only-tagged' not in arguments:
                                username_colour_dict[r]=cl_to_assign[n_colour%len(cl_to_assign)]
                                n_colour+=1
                                results_coloured.append(username_colour_dict[r]+r+cl.end)
                elif attr in ['domain']:
                    for r in results:
                        try:
                            results_coloured.append(domain_colour_dict[r]+r+cl.end)
                        except:
                            domain_colour_dict[r]=cl_to_assign[n_colour%len(cl_to_assign)]
                            n_colour+=1
                            results_coloured.append(domain_colour_dict[r]+r+cl.end)
                print(colour_alternating(str(date), cl.end, results_coloured))
                
                words_counter_monthly=words_counter_monthly+words_counter
                words_counter=Counter([])
                print_monthly_counter=False
                if i==len(dates):
                    print_monthly_counter=True
                if i+1<len(dates):
                    if date.month!=dates[i+1].month:
                        print_monthly_counter=True
                if print_monthly_counter:
                    words_countls=[(words_counter_monthly[x], x) for x in words_counter_monthly] # list of tuples (username, #occurances)
                    results=sorted(words_countls, key=lambda x: x[0], reverse=True)[:10]
                    results=[r[1] for r in results]
                    #result=' '.join(results)
                    results_coloured=[]
                    n_colour=0
                    if attr in ['word','title','noun']:
                        for r in results:
                            try:
                                results_coloured.append(colour[words_colour_dict[r]]+r+cl.end)
                            except:
                                words_colour_dict[r]=cl_to_assign[n_colour%len(cl_to_assign)]
                                n_colour+=1
                                results_coloured.append(colour[words_colour_dict[r]]+r+cl.end)
                    elif attr in ['user','quote','quoted']:
                        for r in results:
                            try:
                                results_coloured.append(userid_colour(username_to_id[r])+r+cl.end)
                            except:
                                if 'only-tagged' not in arguments:
                                    username_colour_dict[r]=cl_to_assign[n_colour%len(cl_to_assign)]
                                    n_colour+=1
                                    results_coloured.append(username_colour_dict[r]+r+cl.end)
                    elif attr in ['domain']:
                        for r in results:
                            try:
                                results_coloured.append(domain_colour_dict[r]+r+cl.end)
                            except:
                                domain_colour_dict[r]=cl_to_assign[n_colour%len(cl_to_assign)]
                                n_colour+=1
                                results_coloured.append(domain_colour_dict[r]+r+cl.end)
                    toprint_monthly.append(colour_alternating(make_n_char_long(str(date.year)+'-'+str(date.month), 7), cl.end, results_coloured))
                    words_counter_monthly=Counter([])
            for xxx in toprint_monthly:
                print(xxx)
    elif command in ['grep', 'egrep']:
        if len(arguments)==0:
            print(cl.red, 'Requires at least one arguments', cl.end)
            print('[grep/egrep] [pattern]')
            print('eg', 'grep exam')
            print('eg', 'grep "STEP prep"')
            print('eg', 'egrep "(aqa|AQA) "')
        else:
            posts_to_print=[]
            search_string=arguments[0]
            if command=='egrep':
                regexp=re.compile(search_string)
            for thread in j:
                for post in thread['posts']:
                    print_post=False
                    post_content=post['content']
                    post_contents=post_content.split('\n')
                    for line in post_contents:
                        #try:
                        if len(line)>0:
                            if line[0]!='>':
                                if command=='grep':
                                    if search_string in line:
                                        print_post=True
                                        post['content']=post['content'].replace(search_string, cl.red + search_string + cl.end)
                                if command=='egrep':
                                    if regexp.search(line):
                                        print_post=True
                                        post['content']=re.sub(r'({0})'.format(search_string), r'{0}\1{1}'.format(cl.red, cl.end), post['content'], flags=re.MULTILINE) # Credit: https://stackoverflow.com/users/100297/martijn-pieters # If not flags=re.MULTILINE, will fail to find any matches if \n gets in the way
                        #except:
                        #    pass
                    if print_post:
                        posts_to_print.append(post)
            psuedothread={
                'posts':posts_to_print,
                'id':-1,
                'title':command,
            }
            threaddisplay.print_thread(psuedothread, arguments[1:])
    elif command=='rep': # eg "reps >10" to show all posts with rep > 10, "reps" to show all posts sorted by rep
        posts_to_print=[]
        for thread in j:
            for post in thread['posts']:
                print_post=False
                if arguments[0][0]=='>':
                    if post['reps']>int(arguments[0][1:]):
                        print_post=True
                if print_post:
                    posts_to_print.append(post)
        psuedothread={
            'posts':posts_to_print,
            'id':-1,
            'title':command,
        }
        threaddisplay.print_thread(psuedothread, arguments[1:])
    elif command=='debug':
        if arguments[0]=='path':
            print(paths) # The dictionary of paths that the path class is built from
        elif arguments[0]=='dict':
            if arguments[1]=='users':
                print(users)
    else:
        if is_number(command):
            n=int(command)
            try:
                sorting=arguments[0]
            except:
                sorting='date'
            attr_is_user_attr=False
            if sorting[:4]=='user':
                attr_is_user_attr=True
                sorting=sorting[4:]
            posts_to_print=j[n]['posts']
            try:
                if attr_is_user_attr:
                    posts_to_print=sorted(posts_to_print, key=lambda x: x['user'][sorting])
                else:
                    posts_to_print=sorted(posts_to_print, key=lambda x: x[sorting])
                threaddisplay.print_posts(posts_to_print)
            except:
                print(cl.yellow, commands['threaddisplay']['common']['help'], cl.end)
        else:
            print(cl.red, 'Not a recognised command', cl.end)
