#coding=utf-8
import certifi
import urllib3
import re


from bs4 import BeautifulSoup

class emeraldInsightMain(object):
    def __init__(self):
        self.result = []
    def craw_get(self,url):
        try:
            http= urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
            res=http.request("get", url, fields={}, headers={'cookie':'I2KBRCK=1'})
            data= res.data.decode('utf-8')
            fout=open("D:\\output.html",'w')
            fout.write(data)
            fout.close()
            soup=BeautifulSoup(data,'html.parser',from_encoding='utf-8')
            title_nodes=soup.find_all('span','hlFld-Title')

            for n in title_nodes:
                href=n.find('a')
                self.result.append(href.text)

        except Exception as e:
            print(e)

        return data


    def craw_post(self,url,data):
        
            http= urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
            res=http.request("post", url, fields=data, headers={'cookie':'I2KBRCK=1'})
            data= res.data.decode('utf-8')
            print(data)

if  __name__=="__main__":
    root_url="https://www.emeraldinsight.com/action/doSearch?AllField=computer&content=articlesChapters"
    root_url="https://www.emeraldinsight.com"
    emeralMain=emeraldInsightMain()
    #emeralspider=emeralMain.craw_get(root_url)
    #print(emeralMain.result)
    #for m in emeralMain.result:
    #    print("%s\r\n" % m)
    root_url="https://www.emeraldinsight.com/action/downloadCitation"
    data={'doi':'10.1108/al.1999.8.2.54.1','format':'bibtex'}
    emeralMain.craw_post(root_url,data)
    