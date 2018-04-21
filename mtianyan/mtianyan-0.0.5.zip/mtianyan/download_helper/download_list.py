from bs4 import BeautifulSoup
import requests
import re
from mtianyan.path_helper import path_file_existed_or_create

def get_download_list_from_fileformat(page_url,file_format,merge=False):
    assert_path = ['./download_list/']
    path_file_existed_or_create(assert_path) 
    response = requests.get(page_url)
    html = BeautifulSoup(response.text, "lxml")
    if merge == True:
        file_reg = ''
        flag = 0
        for file in file_format:
            if flag ==  0:
                file_reg = file
                flag = 1
            else:
                file_reg = file_reg +'|'+ file
        links_all = html.find_all('a', href=re.compile(file_reg))
        f = open('./download_list/merge_list.txt', 'a')
        for x in range(1, len(links_all)):
            f.write(links_all[x]['href'] + '\n')
        print("./download_list/merge_list has been saved!")
        f.close()
    elif merge == False:
        for file_reg in file_format:
            links = html.find_all('a', href=re.compile(file_reg))
            f = open('./download_list/{0}_list.txt'.format(file_reg[1:]), 'a')
            for x in range(1, len(links)):
                f.write(links[x]['href'] + '\n')
            f.close()
            print('./download_list/{0}_list.txt'.format(file_reg[1:]) + 'has been saved!')

if __name__ == '__main__':
    file_format = ['.mpg',
            '.xml',
            '.tar.gz',]
    page_url = 'http://groups.inf.ed.ac.uk/vision/CAVIAR/CAVIARDATA1/'

    get_download_list_from_fileformat(page_url,file_format)