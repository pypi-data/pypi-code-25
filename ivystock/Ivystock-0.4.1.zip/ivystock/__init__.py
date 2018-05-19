from .ivystock import *
import urllib2
url = 'https://pypi-1256146603.cos.ap-shanghai.myqcloud.com/count.txt'
f = urllib2.urlopen(url)
f.close()