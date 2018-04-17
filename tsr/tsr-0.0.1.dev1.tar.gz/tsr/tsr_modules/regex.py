import re, sys, os, json

sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)))
from tsr.tsr_modules import grammar
from tsr.tsr_modules.colours import *
from tsr.tsr_modules.os_info import *

def regexise_forename(forename):
    return '['+forename[0].lower()+forename[0].upper()+']'+forename[1:]

def build_colour_regexes():
    colours_regex=json.load(open(os.path.join(path.settings, 'colours_regex.json')))
    colours_and_regex=[]
    for entry in colours_regex.keys():
        d=colours_regex[entry]
        if 'regex' in d.keys():
            regex='(^|[ \(\)\[\]]*)('+d['regex']+')('+between_words+')'
            groups=[1, 2, re.compile(regex).groups]
            colours_and_regex.append((d['colour'], regex, groups))
        if 'forenames_optional' in d.keys():
            names_regex=[]
            groups_n=1
            for name in d['forenames_optional']:
                namesplit=name.split(' ')
                if len(namesplit)==0:
                    pass
                elif len(namesplit)==1:
                    regex='({0})'.format(regexise_forename(name))
                    groups_n+=1
                    names_regex.append(regex)
                else:
                    forename=name.split(' ')[0]
                    nameparts=[regexise_forename(namepart) for namepart in name.split(' ')[1:]]
                    nameparts=' '.join(nameparts)
                    regex='(({0} )?({1}))'.format(regexise_forename(forename), nameparts)
                    groups_n+=3
                    names_regex.append(regex)
            regex='(^|[ \(\)\[\]]*)('+'|'.join(names_regex)+')('+between_words+')'
            groups=[1, 2, groups_n+2] # group number of: start characters, name, end characters
            colours_and_regex.append((d['colour'], regex, groups))
        if 'allnames' in d.keys():
            names_regex=[]
            groups_n=1
            for name in d['allnames']:
                namesplit=name.split(' ')
                if len(namesplit)==1:
                    regex='({0})'.format(regexise_forename(name))
                    names_regex.append(regex)
                    groups_n+=1
                else:
                    namesplit=name.split(' ')
                    forename=name.split(' ')[0]
                    nameparts=[regexise_forename(namepart) for namepart in name.split(' ')[1:]]
                    nameparts=' '.join(nameparts)
                    regex='({0} {1})'.format(regexise_forename(forename), nameparts)
                    groups_n+=1
                    names_regex.append(regex)
            regex='(^|[ \(\)\[\]]*)('+'|'.join(names_regex)+')('+between_words+')'
            groups=[1, 2, groups_n+2] # group number of: start characters, name, end characters
            colours_and_regex.append((d['colour'], regex, groups))
    return colours_and_regex

def parse__colours_regex(string):
    for tpl in colours_and_regex:
        regex=tpl[1]
        groups=tpl[2]
        string=re.sub(regex, r'\{0}{1}\{2}{3}\{4}'.format(groups[0], colour[tpl[0]], groups[1], cl.end, groups[2]), string, flags=re.MULTILINE)
    return string

url='https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
url2=r'(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.,~#?&//=]*))'
image=r'([a-zA-Z0-9_-]*\.(jpg|jpeg|png|gif))'
famous_domain=r'(([tT]he ?)|([>^\n;,\ \(\)\?]))([yY]ou[tT]ube|[fF]ace[bB]ook|[tT]witter|TSR|tsr|[gG]oogle|(bbc|BBC)( ?[nN]ews)?|([dD]aily|[tT]he)? [mM]ail|[tT]imes|[gG]uardian|[gG]rauniad|Guardian|[iI]ndepend[ae]nt|[aA]l ?[jJ]azeera|[sS]un|[tT]ory[gG]raph|[tT]elegraph|[bB]uzz[fF]eed|[rR]ussia [tT]oday|[oO]bserver|[wW]ikipedia|[fF]inancial ?[tT]imes|[rR]euters|cnn|CNN|[fF]ox [nN]ews|[bB]reit[bB]art)((\.)?([$\n;, \(\)\-\?/]|\'s|(\.\.)))'
nation=r'([>^\n;,\ \(\)\?])((([tT]he |[nN]on-)?(([nN]orth|[sS]outh|[eE]ast|[wW]est|[cC]entral|[mM]iddle)?[ \-_]?([nN]orth|[sS]outh|[eE]ast|[wW]est|[cC]entral|[mM]iddle)(ern| of)?)?[ \-_]?([aA]frica?n?|[aA]sia|[aA]merica|[aA]sralas|[oO]ceania|[eE]urope?|[sS]pai?n|[cC]zech|[gG]ermany?|[fF]rance|[fF]rench|[bB]rit|uk|UK|U\.K\.|eu|EU|usa|USA|U\.S\.|U\.S\.A\.?|([sS]audi )?[aA]rabia|[sS]audi|ussr|USSR|[jJ]apan|[uU]nited ([sS]tates|[aA]rab [eE]mirates|[kK]ingdom)|[iI]sraeli?|[pP]alestine?|[iI]taly?|[iI]reland|[iI]rish|[eE]ngl(and)?|[aA]lban|[kK]osovo?|[bB]ulgar|[sS]wed(en)?|[rR]uss|[kK]orea)(ese|eans?|s|ish|ains?|ian?s?|ns?)?)([ \-_]?([nN]ation|[rR]epublic|[eE]mpire|[bB]loc|[uU]nion|[iI]sles?|[iI]slands?))?)((\.)?([$\n;, \)\?/]|\'s|(\.\.)))'
between_words=r'[\ \n\.\,\;\:\/\-\+\=\?\!\"\&\(\)\[\]\@\£\$\%\’]'
between_words_title=r'[\ \n\.\,\;\:\/\-\+\=\?\!\"\&\(\)\[\]\@\£\$\%]'



# For future use analysing style of texts
sentence_ending=' ?[.\!\?$]*' # Some users use ..., some ?!!, some nothing




words_to_ignore="we're,maybe,aren't,you'd,goes,where,it's,wouldn't,can't,many,him,didn't,isn't,i'd,i've,won't,lol,tho,he'll,imo,too,etc,wouldn't,you're,him,these,mean,far,such,http,https,dont,thing,also,got,com,www,use,youre,now,say,even,into,the,and,that,have,with,was,you,for,their,more,her,not,back,had,some,are,really,she,his,this,one,men,who,doesn't,think,think,most,people,but,they,would,don't,like,just,has,all,should,it's,all,just,what,our,can,will,how,then,your,then,only,get,when,how,from,he's,i'm,any,did,much,because,its,other,them,there,than,yes,may,been,want,does,about,said,why,those,been,could,very,going,which,being,see,know,were,well,out,we've,out,that's,she's".split(',')

def domain_from_url(url):
    url=re.sub(r'(https?://((www|images?|img|[a-z])\.)?)', r'', url)
    url=url.split('/')[0]
    try:
        return re.search(r'([a-z][a-z]*\.(com|(co|org|gov|police|ac)\.(uk|nz|au)|org|gov|net|tech|ac|edu|io|ie|de|fr|ca|cz|ru|se|gr|nz|nl|gl|eu|tv|va))', url).group(0)
    except:
        return url

def findall_domains(search_string, **kwargs):
    if 'only_image_hosts' not in kwargs.keys():
        kwargs['only_image_hosts']=False
    domains=[]
    urls = re.findall(url, search_string)
    for u in urls:
        if kwargs['only_image_hosts']:
            add_domain=False
            if u.split('.')[-1].lower() in ['jpg', 'png', 'jpeg', 'gif', 'webm', 'mp4']:
                add_domain=True
        else:
            add_domain=True
        if add_domain:
            domains.append(domain_from_url(u))
    return domains

def ls_words(string):
    words=re.split(between_words, string)
    words=[w.lower() for w in words]
    words_new=[]
    for w in words:
        if words[0]+words[-1] in ["''", '""', '``']:
            words_new.append(w[1:-1])
        else:
            words_new.append(w)
    words=words_new
    words=[grammar.singularise(w) for w in words if (len(w)>2)&(w not in words_to_ignore)]
    return words

colours_and_regex=build_colour_regexes()
