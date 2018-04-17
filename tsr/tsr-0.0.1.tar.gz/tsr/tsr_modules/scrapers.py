import sys, os

sys.path.insert(0,os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from tsr.tsr_modules.general import *

def replace_images_with_hrefs(soup):
    images=soup.find_all('img')
    for img in images:
        try:
            src=img['src']
            src=src.split('/smilies/')[-1]
            src=src.split('/attachment.php?')[-1]
            img.replaceWith(' '+src)
        except:
            pass
def replace_lists(soup):
    ls=soup.find_all('li')
    for l in ls:
        l.replaceWith('- '+l.text)
def replace_tags(soup):
    l=[]
    try:
        tags=soup.find_all('a', {'class':"bb-user"})
        tags=tags[1:] # First result is the author
        for tag in tags:
            href=tag['href']
            user_id=int(href.split('?u=')[-1])
            name=tag.text
            tag.decompose()
            user={ user_id:{name} }
            l.append(user)
    except:
        pass
    return l
def full_urls(soup):
    urls=soup.find_all('a')
    for u in urls:
        if ls_in_str( ['http://','https://','ftp://','smb://','magnet:?xt='], u.text):
            try:
                u.replaceWith( u['href'] )
            except: # Probably not an url
                pass

def get_security_token(soup):
    # I think the first part reserves a thread/comment/post/message ID, the second half being an actual security token allocated by the server. It is served up as part of the script embedded in individual webpages, unfortunately isn't a cookie
    securitytoken=[x.text for x in soup.find_all('script') if 'var SECURITYTOKEN' in x.text][0]
    #securitytoken=[x for x in securitytoken if 'guest' not in securitytoken][0]
    securitytoken=securitytoken.split('var SECURITYTOKEN = "')[-1].split('"')[0]
    return securitytoken
