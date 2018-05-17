CONF = '''
[Default]
type: sitemap
sitemap: /sitemap.xml
urls: /about,/contacts
async_num: 8

[Email]
smtp_server:
port:
user:
password:
sender:
receiver:

[Site-1]
url: http://texthost.org
type: urls
urls: /contacts,/politic


[Site-2]
url: https://example2.com/
'''


def get_conf():
    with open('site_pinger_conf.ini', 'w') as f:
        f.write(CONF)
