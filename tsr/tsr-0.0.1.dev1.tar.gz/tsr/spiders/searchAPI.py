# -*- coding: utf-8 -*-
import scrapy, json, io, re, os, sys, shutil
from bs4 import BeautifulSoup
from scrapy.spider import BaseSpider
from scrapy import Selector
from scrapy.http import HtmlResponse

sys.path.insert(0,os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from tsr_modules.general import *
from tsr_modules.os_info import *
from tsr_modules import regex
from tsr_modules import forumload
from tsr_scrapers import thread

mkdir(path.main) # Superfluous, since mkdir() is recursive, but ignoring would look odd
mkdir(path.posts)
mkdir(path.threads)
mkdir(path.users)
mkdir(path.forums)
mkdir(path.settings)
touch(path.log)

settings=json.load(open(os.path.join(path.settings, 'settings.json')))

class ForumSpider(scrapy.Spider):
    d={}
    thread_ids=[]
    def __init__(self, **kwargs):
        self.download_delay = settings['crawl_delay']
        super(ForumSpider, self).__init__(**kwargs)
        try:
            self.page_n_start=int(self.page_n_start)
        except:
            self.page_n_start=1
        try:
            self.page_n_end=int(self.page_n_end)+1 # saves on adding 1 each time
        except:
            self.page_n_end=999999
        try:
            if self.overwrite_threads in ['true', 'True']:
                self.overwrite_threads=True
        except:
            self.overwrite_threads=False
        try:
            if self.overwrite_posts in ['true', 'True']:
                self.overwrite_posts=True
        except:
            self.overwrite_posts=False
        
        print(cl.yellow,'forum_id:',self.forum_id,cl.end,'pages',self.page_n_start,'to',self.page_n_start, cl.end)
        
        if self.overwrite_threads:
            print(cl.yellow, 'Bulldozing forum', cl.end)
            self.threads_cannot_load=[]
        elif os.path.isfile(os.path.join(path.forums, self.forum_id, 'threads.txt')):
            thread_ids_loaded=forumload.load_forum_database('forum', self.forum_id)
            self.threads_cannot_load=thread_ids_loaded[2]+thread_ids_loaded[3] # errors and failures
            print(cl.yellow, self.threads_cannot_load, cl.end)
        else:
            print(cl.yellow, 'New forum', cl.end)
            self.threads_cannot_load=[]
        if self.thread_type=='t':
            self.start_urls = ['https://www.thestudentroom.co.uk/search.php?filter[type]=thread&filter[forumid]={0}&page={1}'.format(self.forum_id, str(self.page_n_start))]
            self.end_url='https://www.thestudentroom.co.uk/search.php?filter[type]=thread&filter[forumid]={0}&page={1}'.format(self.forum_id, str(self.page_n_end))
        elif self.thread_type=='p':
            self.start_urls = ['https://www.thestudentroom.co.uk/search.php?filter[userid]={0}&page={1}'.format(self.forum_id, str(self.page_n_start))]
            self.end_url='https://www.thestudentroom.co.uk/search.php?filter[userid]={0}&page={1}'.format(self.forum_id, str(self.page_n_end))
    name = "search_forum"
    allowed_domains = ["thestudentroom.co.uk"]
    
    def errback(self, response):
        print(cl.red, 'ERROR', cl.end)
    
    def parse(self, response):
        ForumSpider.current_page=self.page_n_start
        forum_id=self.forum_id
        self.page_n_end=min(self.page_n_end, int(response.css('a.pager-last::attr(href)').extract()[0].split('&page=')[-1].split('&')[0]))
        print(cl.yellow, 'Last page:', self.page_n_end, cl.end)
        while ForumSpider.current_page<self.page_n_end: # Default order is from oldest posts to latest
            if self.thread_type=='t':
                next_page_url='https://www.thestudentroom.co.uk/search.php?filter[type]=thread&filter[forumid]={0}&page={1}'.format(forum_id, str(ForumSpider.current_page))
            elif self.thread_type=='p':
                next_page_url='https://www.thestudentroom.co.uk/search.php?filter[userid]={0}&page={1}'.format(forum_id, str(ForumSpider.current_page))
            yield scrapy.Request(url=next_page_url, callback=self.parse_forumpage)
            ForumSpider.current_page+=1
            
    def parse_forumpage(self, response):
        forum_id=self.forum_id
        soup=BeautifulSoup(response.css('body').extract_first(), 'html.parser')#BeautifulSoup(t, 'html.parser')
        try:
            rows_threads=soup.find('table', {'id':'search_results_posts'}).find_all('tr') # Get every row in table
        except:
            print(cl.red, 'No table rows', cl.end)
            print('', soup.text[200:])
            rows_threads=[]
        rows_threads=[t for t in rows_threads if t.find('td', {'class':'alt2'})] # Removes the first three descriptive rows
        rows_threads=[t for t in rows_threads if t.find('td', {'class':'alt2'}).find('a')] # Check contains title
        thread_ids=[]
        thread_meta_dict={}
        
        for row in rows_threads:
            x=row.find('td', {'class':'alt2'})
            try:
                nReplies=int(row.find_all('td')[3].text.strip().split(' replies')[0])
            except:
                nReplies=-1
            thread_id=x.find('a')['href'].split('?'+self.thread_type+'=')[-1].split('&')[0]
            ForumSpider.thread_ids.append( thread_id )
            thread_ids.append( thread_id )
            try:
                author_name=x.find('span').find('a').text
            except:
                author_name=[y for y in row.find_all('a') if y['href']]
                try:
                    author_name=[y for y in author_name if 'member.php?u=' in y['href']][0]
                except:
                    print(row)
                author_name=author_name.text
            thread_meta_dict[thread_id]={ # For print() descriptive purposes only
                'title':x.find('a').text,
                #'id':thread_id,
                'user':{
                    'name':author_name
                },
                #'author_id':x.find('span').find('a')['href'].split('?u=')[-1],
                'nPosts_claimed':nReplies+1,
            }
        
        current_page_n_str=soup.find('li', {'class':'current'}).text.strip()
        print('\n')
        print('Page', current_page_n_str)
        with open(path.log, 'a') as f:
            f.write(current_page_n_str)
            f.close()
        for n in thread_ids:
            nstr=str(n)
            
            thread_meta=thread_meta_dict[n]
            
            #for meta in thread_meta:
            #    print(cl.purple, meta, cl.end, thread_meta[meta])
            
            archive_thread=self.overwrite_threads # False by default
            if not self.overwrite_threads:
                if nstr not in os.listdir(path.threads):
                    print(cl.green, 'New thread', cl.end)
                    archive_thread=True
            if n in self.threads_cannot_load: # Integers
                print(cl.yellow, 'Thread error. Re-archiving', cl.end)
                archive_thread=True
            
            update_metadata=False
            if not archive_thread:
                thread_dump_filepath=os.path.join(path.threads, nstr, 'meta.json')
                
                try:
                    thread_dump_file=open(thread_dump_filepath, 'r+')
                    thread_dump_file_dict=json.load(thread_dump_file)
                except:
                    update_metadata=True
                
                if 'nPosts_claimed' not in thread_dump_file_dict.keys():
                    update_metadata=True
                    print(cl.yellow, 'Updating metadata', cl.end)
            
            if (archive_thread)|(update_metadata):
                if self.thread_type=='t':
                    thread_meta_parent_path=os.path.join(path.threads, nstr)
                elif self.thread_type=='p':
                    thread_meta_parent_path=os.path.join(path.threads, 'p'+nstr)
                mkdir(thread_meta_parent_path)
                thread_dump_filepath=os.path.join(thread_meta_parent_path, 'meta.json')
                try:
                    thread_dump_file=open(thread_dump_filepath)
                    thread_dump_file.close()
                except:
                    update_metadata=True
                if update_metadata:
                    touch(thread_dump_filepath)
                    with open(thread_dump_filepath, 'w') as fp:
                        json.dump(thread_meta, fp)
                if archive_thread:
                    yield response.follow(url='https://www.thestudentroom.co.uk/showthread.php?{0}={1}'.format(self.thread_type, nstr), callback=self.parse_threadpage)
            else:
                print(cl.yellow, 'Already scanned thread '+nstr, cl.end)
    def parse_threadpage(self, response):
        soup=response.css('html')
        thread.parse_threadpage(soup, response.url, self.thread_type, self.overwrite_posts)
        try:
            current_page_number=int(response.url.split('&page=')[-1])
        except:
            current_page_number=1
        if current_page_number<nPages:
            next_page_url='https://www.thestudentroom.co.uk/showthread.php?{0}={1}&page={2}'.format(self.thread_type, str(thread_id), str(current_page_number+1))
            yield response.follow(url=next_page_url, callback=self.parse_threadpage)
