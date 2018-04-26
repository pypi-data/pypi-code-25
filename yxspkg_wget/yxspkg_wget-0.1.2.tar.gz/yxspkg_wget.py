
import requests
import re,os
from multiprocessing.pool import ThreadPool
from os import path
from hashlib import md5
from bs4 import BeautifulSoup 
import sys
import shelve
import time
__version__='0.1.2'
__author__="Blacksong"
class Wget:
    def __init__(self,url,**kargs):
        url0=url
        url=url.split('?')[0]
        self.n=0
        dbname=md5(url.encode()).hexdigest()[:7]+'.pydb'
        record_db=shelve.open(dbname)
        self.filetype=kargs.get('filetype','.jpg')
        self.session=self.setbrowser()
        self.srcpro=None
        self.rule=kargs.get('rule',list())
        self.re_rule=kargs.get('re_rule',list())
        self.max_download=8
        self.num_download = 0
        self.asyncThread=ThreadPool(self.max_download)
        self.htm=url.split('/')[2]
        dirname = kargs.get('dirname',None)
        if dirname is None:
            dirname = self.htm
        if not path.isdir(dirname): 
            os.makedirs(dirname)
        self.dirname = dirname
        self.auto=kargs.get('auto',True)
        print(self.htm)

        self.rule_list=[re.sub('[^A-Za-z]','', url)]
        [self.rule_list.append(re.sub('[^A-Za-z]','', i)) for i in self.rule]
        self.rule_list=list(set(self.rule_list))
        self.rule_dir=[path.dirname(url)]
        [self.rule_dir.append(path.dirname(i)) for i in self.rule]
        self.rule_dir=list(set(self.rule_dir))

        self.re_rule=[re.compile(i) for i in self.re_rule]
        url=url0
        print(self.re_rule,'\n',self.rule_dir,'\n',self.rule_list)
        self.autofind(url)
        try:
            halt=record_db.get('halt',False)
            if halt == True:
                self.href=record_db.get('href',[(url,{})])
                self.pagedb = record_db.get('pagedb',set())
                self.srcdb = record_db.get('srcdb',set())
                record_db['halt']=False
            else:
                self.href=[(url,{})]
                self.pagedb=set()
                self.srcdb=set()
            self.main()
            record_db.close()
            if path.isfile(dbname): os.remove(dbname)
        except:
            print('the program is halted!')
            record_db['halt']=True
            record_db['srcdb']=self.srcdb
            record_db['pagedb']=self.pagedb
            record_db['href']=[i for i in self.href if i!=None]
        self.asyncThread.close()
        self.asyncThread.join()
    def my_hash(self,x):
        return int(md5(x.encode()).hexdigest()[:8],16)
    def setbrowser(self):
        headers='''User-Agent: Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0
DNT: 1
Connection: keep-alive
Upgrade-Insecure-Requests: 1'''
        headers=headers.split('\n')
        d=dict()
        for i in headers:
            n=i.find(':')
            d[i[:n]]=i[n+1:]
        headers=d
        s=requests.session()
        s.auth = ('user', 'pass')
        # s.headers=headers
        return s
    def autofind(self,url):
        print('Autofind the label of the target picture')
        volume=0
        x,y=self.Analyze(url)
        r=set()
        for i in y:
            s=str(i[1])
            if s in r:continue
            r.add(s)
            try:
                t=len(self.session.get(i[0],timeout=30).content)
            except:
                t=0
            if volume<t:
                volume=t
                tt=i[1]
        self.srcpro=tuple(tt.items())
    def main(self):
        '''主循环函数，控制寻找页面以及查找页面资源链接，主要起控制作用'''
        def run(u):
            print('Analyse the html ',u)
            hr,src=self.Analyze(u)

            for i in src:
                if self.UsefulSrc0(*i):
                    self.num_download+=1
                    self.asyncThread.apply_async(self.Download,(i[0],u))
                    while self.num_download>self.max_download+4:
                        time.sleep(1)
                        print('Downloading !!')
                    # self.Download(i[0],u)
            self.pagedb.add(self.my_hash(u))
            for i in hr:
                if self.UsefulHtml0(*i):
                    self.href.append(i)
        while True:
            ii=0
            n=len(self.href)
            while ii<n:
                if self.UsefulHtml0(*self.href[ii]):
                    run(self.href[ii][0])
                self.href[ii]=None
                ii+=1
            self.href=[i for i in self.href if i!=None]
            if len(self.href)==0:break
    def DivSplit(self,s):
        '''将一个html页面分成多个div块，主要通过寻找div标签的位置，返回一个记录了div块所在位置以及各个块的名字的链表'''
        a=[]
        [a.append((-1,i.span())) for i in re.finditer('< *div[^><]*>', s)]
        b=[]
        for i,j in a:
            if i==1:
                b.append((i,j[0]))
            else:
                t=s[j[0]:j[1]]
                n=re.findall('id *= *"[^"]*"|class *= *"[^"]*"', t)
                d=dict([i.replace('"','').split('=') for i in n])
                b.append((i,j[0],d))
        b.sort(key=lambda x:x[1])
        return b
    def DivSplit2(self,s):
        '''将一个html页面分成多个div块，主要通过寻找div标签的位置，返回一个记录了div块所在位置以及各个块的名字的链表'''
        a=[(-1,0,{'id':'mystart'})]
        for i in re.finditer('(id|class) *=["\' ]*[^"\']*', s):
            j=re.sub('["\' ]', '',i.group())
            n=j.find('=')
            d={j[:n]:j[n+1:]}
            a.append((-1,i.span()[1],d))
        a.sort(key=lambda x:x[1])
        return a
    def Download(self,url,purl,nn=[0]):
        '''下载url'''
        
        tf=re.sub('\W','', purl)
        filename=self.dirname+'/'+tf[-min(len(tf),10):]+md5(url.encode()).hexdigest()[:5]+self.filetype
        if not path.isfile(filename):
            nn[0]+=1
            if nn[0]%50==0:
                print('Downloading ',url)
            x=self.session.get(url,timeout=30)
            t=open(filename,'wb').write(x.content)
        else:
            print('file already exist')
        self.srcdb.add(self.my_hash(url))
        self.num_download -= 1
        return filename
    def UsefulHtml0(self,url,pro):
        '''判断一个页面的url是否是有用的'''
        if self.my_hash(url) in self.pagedb:return False
        if self.re_rule:
            for i in self.re_rule_list:
                if i.search(url):return True
        if not self.rule:
            if not re.search(self.htm, url):return False
        t= re.sub('[^A-Za-z]','', url)
        d=path.dirname(url)
        if t in self.rule_list:return True
        if d in self.rule_dir:return True
        if self.auto:
            return False
        return self.UsefulHtml(url,pro)
    def UsefulHtml(self,url,pro):
        '''判断一个页面的url是否是 有用的，这个函数可以在不同的环境中重写，其中pro是该链接所在div的属性'''
        return True
    def UsefulSrc0(self,url,pro):
        if self.my_hash(url) in self.srcdb:return False
        if self.auto:
            for k,v in self.srcpro:
                if v.isdigit():continue
                if pro.get(k)!=v:return False
        return self.UsefulSrc(url,pro)
    def UsefulSrc(self,url,pro):
        return True
    def correct_url(self,s,website,webdir):
        if s[0]=='/':return website+s
        elif s=='#':return ''
        elif s.find('http')!=-1:return s
        else: return webdir+s
    def Analyze(self,url):
        '''返回 href 和 src的链接，返回值为一个二元tuple'''
        s=self.session.get(url,timeout=30).text
        divs=self.DivSplit(s)
        href=[]
        src=[]
        split_url=url.split('/')
        website='/'.join(split_url[:3])
        webdir='/'.join(split_url[:-1])+'/'
        for i in re.finditer(' *(href|src) *=["\' ]*[^ )("\';\+>}]+', s):
            div=self.FindDiv(divs, i.span()[0])
            j=i.group()
            j=re.sub('["\' \\\\]', '', j) #针对某些网站将url写在javascript中，用到了转义符\
            if j[0]=='h':
                j=j.replace('href=', '')
                j=self.correct_url(j,website,webdir)
                if len(j)==0:continue
                href.append((j,div))
            if j[0]=='s':
                j=j.replace('src=', '')
                if j.find(self.filetype)==-1:continue
                div=self.FindDiv(divs, i.span()[0])
                j=self.correct_url(j,website,webdir)
                if len(j)==0:continue
                src.append((j,div))
        return href,src
    def FindDiv(self,divs,pos):
        a,b=0,len(divs)
        if b==0:
            return {'id':'nodivs'}
        if pos>divs[-1][1]:return divs[-1][2]
        while b-a>1:
            t=int((a+b)/2)
            p0=divs[t][1]
            if pos>p0:a=t
            else:b=t
        return divs[a][2]
class Wget_novel:#下载小说
    def __init__(self,url,novel_name='wz.txt'):
        content = requests.get(url)
        html = content.content.decode('gbk').encode('utf8').decode('utf8')
        bs=BeautifulSoup(html)
        self.url=url
        self.fp=open(novel_name,'w')
        self.__get_author(bs)
        # self.__start(url)
    def __start(self,url):
        error=0
        while True:
            content = requests.get(url)
            html = content.content.decode('gbk').encode('utf8').decode('utf8')
            bs=BeautifulSoup(html)
            title_info=self.__get_chapter(bs)
            print(title_info)
            content_info=self.__get_content(bs)
            next_info=self.__get_next(bs)
            if title_info is not None:
                self.fp.write('\n'+title_info[0]+' '+title_info[1]+'\n')
                self.fp.write(content_info)
            if next_info is False:break
            url=next_info
    def __get_author(self,bs):
        m=0
        for i in bs.center.find_all('span'):
            m+=1
            print(i.text)
            if m==3:break
    def __get_content(self,bs):
        x=bs.find(attrs={'id':'content'})
        sx=str(x)
        a=x.find_all('a')
        for i in a:
            sx=sx.replace(str(i),'')
        sx=re.sub('<[^>]*>','\n',sx)
        sx=re.sub('[\n]+','\n',sx)
        return sx
    def __get_next(self,bs,html=None):
        c=bs.find(attrs={'class':'page'})
        t=c.find_all('a')
        for i in t:
            if i.text.find('下')!=-1:
                href=i['href']
        if len(href)==0:return False
        if href[0]!='/':
            url=self.url.split('/')
            url[-1]=href
            return '/'.join(url)
    def __get_chapter(self,bs,html=None):
        title=bs.find(attrs={'class':'title'}).h1.string
        title_re='(第? ?([一二三四五六七八九十零百千万\d]*)章)'
        t=re.findall(title_re,title)
        if len(t)==0:return None
        n=self.__ChineseNumber_to_number(t[0][1])
        m=title.find(t[0][0][-1])
        name=title[m+1:].strip()
        if name[0]=='：' or name[0]==':':name=name[1:].lstrip()
        return t[0][0],name,n
    def __ChineseNumber_to_number(self,s):
        t=str.maketrans('一二三四五六七八九','123456789')
        t2=str.maketrans(dict(zip(['零','十','百','千','万','亿'],['','0 ','00 ','000 ',' 10000 ',' 100000000 '])))
        t.update(t2)
        s=s.translate(t)
        l=s.rstrip().split()
        n,m=0,0
        for i in l:
            j=int(i)
            if j<10000:
                if j==0:j=10
                n+=j
            else:
                n*=j
                m+=n
                n=0
        m+=n
        return m
def main(*d,**karg):

    url = sys.argv[1]
    Wget(url)
if __name__=='__main__':
    pass
    main()