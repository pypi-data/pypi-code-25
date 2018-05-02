import datetime, os, sys

sys.path.insert(0,os.path.realpath(__file__))
from tsr.modules.colours import *
from tsr.modules.os_info import *

users={}
username_colour_dict={} # temporary colour scheme for users without flairs/colours, for easier reading
username_to_id={}
users=json.load(open(os.path.join(path.settings, 'users.json')))
for entry in users:
    if not 'colour' in users[entry].keys():
        users[entry]['colour']='end'
settings=json.load(open(os.path.join(path.settings, 'settings.json')))

def userid_colour(userid):
    if type(userid)!='str':
        userid=str(userid)
    try:
        return colour[ users[userid]['colour'] ]
    except:
        raise Exception('userid {0} has no colour. users[{0}] = {1}'.format(userid, users[userid]))

def make_n_char_long(x, n, spacing=' '):
    y=str(x)
    while len(y)<n:
        y+=spacing
    if len(y)>n:
        y=y[:n]
    return y

def myjoin(*args):
    string=''
    for arg in args:
        string+='  '+str(arg)
    return string[2:]

def standardise_datetime(datestr):
    if isinstance(datestr, datetime.datetime):
        return datestr
    elif isinstance(datestr, datetime.date):
        return datetime.datetime.combine(datestr, datetime.time(0, 0)) # Sets to midnight
    try:
        return datetime.datetime.strptime(datestr, '%d-%m-%Y')
    except:
        try:
            return datetime.datetime.strptime(datestr, '%Y-%m-%d')
        except:
            if 'ago' in datestr:
                date_ls=datestr.split(' ')
                n=int(date_ls[0])
                date_type=date_ls[1]
                if date_type in ['second', 'seconds']:
                    return datetime.datetime.now()-datetime.timedelta(seconds=n)
                elif date_type in ['minute', 'minutes']:
                    return datetime.datetime.now()-datetime.timedelta(minutes=n)
                elif date_type in ['hour', 'hours']:
                    return datetime.datetime.now()-datetime.timedelta(hours=n)
                elif date_type in ['day', 'days']:
                    return datetime.datetime.now()-datetime.timedelta(days=n)
                elif date_type in ['week', 'weeks']:
                    return datetime.datetime.now()-datetime.timedelta(days=n*7)
                elif date_type in ['month', 'months']:
                    return datetime.datetime.now()-datetime.timedelta(months=n)
                elif date_type in ['year', 'years']:
                    return datetime.datetime.now()-datetime.timedelta(years=n)
                elif date_type in ['decade', 'decades']:
                    return datetime.datetime.now()-datetime.timedelta(years=n*10)
            else:
                for char in ['T', ' ', '_']:
                    if len(datestr)>18: # So probably includes seconds
                        try:
                            try:
                                datestr=datestr[:19] # Remove the trailing +00:00
                                return datetime.datetime.strptime(datestr, '%Y-%m-%d'+char+'%H:%M:%S')
                            except:
                                datestr=datestr[:19] # Remove the trailing +00:00
                                return datetime.datetime.strptime(datestr, '%d-%m-%Y'+char+'%H:%M:%S')
                        except:
                            pass
                    else:
                        try:
                            try:
                                return datetime.datetime.strptime(datestr, '%Y-%m-%d'+char+'%H:%M')
                            except:
                                return datetime.datetime.strptime(datestr, '%d-%m-%Y'+char+'%H:%M')
                        except:
                            pass
    raise Exception('Unknown datetime string: '+str(datestr))

def standardise_datetime_str(datestr):
    return str(standardise_datetime(datestr))

def standardise_date(string):
    return standardise_datetime(string).date()

def standardise_date_str(datestr):
    return str(standardise_date(datestr))

def standardise_time(timestr):
    return datetime.datetime.strptime(timestr, '%H:%M').time()

def is_number(x):
    try:
        dummy=int(x)
        return True
    except:
        return False


def ls_rm_dupl(ls): # Useful to have rather than list(set(, since it preserves order. Perhaps sorted(list(set( would be more performative, I will look into this eventually.
    l=[]
    for x in ls:
        if x not in l:
            l.append(x)
    return l

def ls_in_str(ls,string):
    for element in ls:
        try:
            if element in string:
                return True
        except:
            pass
    return False



def mystrip(text):
    while '  ' in text:
        text=text.replace('  ',' ')
    while '\n\n' in text:
        text=text.replace('\n\n','\n')
    while ' \n' in text:
        text=text.replace(' \n','\n')
    while '\n ' in text:
        text=text.replace('\n ','\n')
    while '\n> > ' in text:
        text=text.replace('\n> > ','\n> ')
    while '>\n' in text:
        text=text.replace('>\n','')
    while '~\n' in text:
        text=text.replace('~\n','\n')
    while '\n\n' in text:
        text=text.replace('\n\n','\n')
    while '\r\n' in text:
        text=text.replace('\r\n','\n')
    while '\n\r' in text:
        text=text.replace('\n\r','\n')
    while '\n\n' in text:
        text=text.replace('\n\n','\n')
    return text.strip()

def toprint_expanded(*args):
    to_print=''
    for i in range(len(args)):
        try:
            to_print+=args[i]+cl.end+'  '
        except:
            try:
                to_print+=str(int(args[i]))+cl.end+'  '
            except:
                try:
                    to_print+=str(float(args[i]))+cl.end+'  '
                except:
                    raise ValueError('to_print arguments must be strings or numbers')
    return to_print

def toprint_expanded_ls(*args):
    tpl=[]
    def aaa(tpl, *args):
        tpl=[]
        for arg in args:
            if type(arg).__name__ in ['str','int','float','datetime.date']:
                tpl.append(str(arg))
            elif type(arg).__name__ in ['list', 'tuple']:
                for x in arg:
                    tpl+=aaa([], x)
        return tpl
    tpl+=aaa(tpl, args)
    to_print=''
    for i in range(len(tpl)):
        try:
            to_print+=tpl[i]+cl.end+'  '
        except:
            pass
    return to_print


def display_username(post, n=False, spacing=' '): # lowercase letters are getting dropped form the starts of some usernames...
    try:
        u=post['user']
    except:
        if type(post['author'])=='str':
            u={'name':post['author']}
            try:
                u['id']=post['authorid']
            except:
                try:
                    u['id']=username_to_id[ post['author'] ]
                except:
                    u['id']=-1
        else: # dict
            u=post['author']
    n_invisible_chars=0
    user_id=str(u['id'])
    x=u['name']
    if user_id in users.keys():
        x=userid_colour(user_id)+x+cl.end
        n_invisible_chars=len(userid_colour(user_id))
        try:
            x+=cl.blue+'  '+users[user_id]['flair']+cl.end
        except:
            pass
    if n:
        x=make_n_char_long(x, n+n_invisible_chars, spacing)
    else:
        x+='  '+cl.purple+str(u['id'])+cl.end
    if settings['show_avatars']:
        try:
            avatar_path=os.path.join(path.users, u['id'], 'avatars')
            current_avatar=open(os.path.join(avatar_path, 'list.txt'), 'r').read().split('\n')[-1]
            x+=os.path.join(avatar_path, current_avatar)
        except:
            pass
    return x

def display_username___(post, n=False, spacing=' '): # lowercase letters are getting dropped form the starts of some usernames...
    u=post['user']
    user_id=str(u['id'])
    x=u['name']
    if args:
        x=make_n_char_long(x, n, spacing) # this is first, because the colour messes up the char length calculations
    else:
        x=x+'  '+cl.purple+str(u['id'])+cl.end
    if user_id in users.keys():
        x=userid_colour(user_id)+x+cl.end
        n_invisible_chars=len(userid_colour(user_id))
        try:
            x+=cl.blue+'  '+users[user_id]['flair']+cl.end
        except:
            pass
    return x
