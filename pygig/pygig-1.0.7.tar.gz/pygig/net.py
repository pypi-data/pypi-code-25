import urllib.request
from bs4 import BeautifulSoup

basurl = 'https://github.com'


def getFileUrlMap():
    doc = urllib.request.urlopen(basurl + '/github/gitignore')

    data = doc.read()  # 读取全部
    bsObj = BeautifulSoup(data, "html.parser")
    aList = bsObj.findAll("a", {"class": "js-navigation-open"})

    map = {}
    for a in aList:
        if len(a['class']) > 1 or a.string == '.github' or a.string == 'README.md' or a.string == 'LICENSE':
            continue
        if a.string == 'Global':
            data2 = urllib.request.urlopen(basurl + a['href']).read()
            aList2 = BeautifulSoup(data2, "html.parser").findAll("a", {"class": "js-navigation-open"})
            for a2 in aList2:
                if len(a2['class']) > 1 or a2.string == '..' or a2.string == 'README.md':
                    continue
                s = str(a2.string)
                s = s[:s.rindex('.')].lower()
                map[s] = basurl + a2['href']
        else:
            s = str(a.string)
            s = s[:s.rindex('.')].lower()
            map[s] = basurl + a['href']
    return map

def getFileContent(url):
    doc = urllib.request.urlopen(url)

    data = doc.read()
    bsObj = BeautifulSoup(data, "html.parser")
    table = bsObj.findAll("table", {"class": "js-file-line-container"})
    content = []
    for line in table[0].findAll("td", {"class": "js-file-line"}):
        content.append(line.string)
    return '\n'.join(content)
