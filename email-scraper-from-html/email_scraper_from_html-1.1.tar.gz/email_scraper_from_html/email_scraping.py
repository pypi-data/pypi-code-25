import re
import os
from bs4 import BeautifulSoup
import pandas as pd

def get_html_text(filepath):
    content = open(filepath)
    soup = BeautifulSoup(content, "lxml")
    return soup.get_text()

def get_emails(text):
    email_regex = r'[\w.-]+@[\w.-]+'
    return re.findall(email_regex,text)

def save_emails_as_csv(name,emails):
    df = pd.DataFrame(data=emails)
    csv_name = os.path.split(name)[1].strip('.html').strip('/') + '_emails.csv'
    if not os.path.exists(os.path.split(name)[0]+'/email_scraper_output'):
        os.makedirs(os.path.split(name)[0]+'/email_scraper_output')
    df.to_csv(os.path.join(os.path.split(name)[0]+'/email_scraper_output',csv_name),index=False,header=False)

def move_processed_html(filepath):
    if not os.path.exists(os.path.split(filepath)[0]+'/processed_files'):
        os.makedirs(os.path.split(filepath)[0]+'/processed_files')
    new_path = os.path.split(filepath)[0]+'/processed_files'
    os.rename(filepath,os.path.join(new_path, os.path.split(filepath)[1]))

def scrape_for_emails(filepath):
    email_list = get_emails(get_html_text(filepath))
    save_emails_as_csv(filepath,email_list)
    move_processed_html(filepath)