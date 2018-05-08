#coding:utf-8
# write  by  zhou
from celery import  Celery
import redis
import time
import hashlib
import urlparse

_app = None
_redis_conn = redis.Redis('192.168.8.185',6379,6)


def data_to_online(dataset,key,data):
    '''
    数据转移到线上
    :param dataset: 数据集的名称，str, 如： hy88_product
    :param key:     数据的key， str,  如：http://www.huangye88.com/xinxi/11.html
    :param data:    数据的内容， dict 如: {"cate1":11,"cate2":111,"url":"xxxxx"}
    :return:
    True
    '''
    global  _app
    if _app == None:
        #
        _app = Celery(broker="redis://192.168.8.185:6379/6")
        _app.conf.task_ignore_result = True
        _app.conf.task_queue_max_priority = 255
    while 1:
        if _redis_conn.llen("rawhttp.data_transfer") > 40000:
            time.sleep(1)
        else:
            break
    _app.send_task("rawhttp.data_transfer.transfer", kwargs={"dataset": dataset,
                                                            "key": key,
                                                            "data": data,
                                                            "http_proxy": ["192.168.14.%s:3128"%i for \
                                                                           i in range(120,131)]},
                  queue="rawhttp.data_transfer")
    return True



def md5(str, hex=True):
    '获取字符串的md5校验'
    m = hashlib.md5()
    m.update(str)
    if hex == True:
        return m.hexdigest()
    else:
        return m.digest()


def img_url_handle(img_url):
    try:
        _ = img_url.split(".")
        a, b = ".".join(_[:-1]), _[-1]
        if b.startswith("jpg"):
            return a + ".jpg"
        if b.startswith("jpeg"):
            return a + ".jpeg"
        if b.startswith("png"):
            return a + ".png"
        if b.startswith("gif"):
            return a + ".gif"
        if b.startswith("JPEG"):
            return a + ".JPEG"
        if b.startswith("JPG"):
            return a + ".JPG"
        raise Exception()
    except:
        return img_url


def image_to_upyun(page_url,img_url):
    '''图片转移到又拍云
    参数说明：
    page_url    图片所属页面的url
    img_url     图片的url
    返回值说明：
    new_url 图片转移到又拍云之后的新的地址
    '''
    global  _app
    if _app == None:
        #
        _app = Celery(broker="redis://192.168.8.185:6379/6")
        _app.conf.task_ignore_result = True
        _app.conf.task_queue_max_priority = 255
    while 1:
        if _redis_conn.llen("rawhttp.image_spider") > 100000:
            time.sleep(1)
        else:
            break
    try:
        img_url = urlparse.urljoin(page_url, img_url)
        url_md5 = md5(img_url)
        new_url = "//imgse.cn.gcimg.net/" + url_md5 + "." + img_url.split(".")[-1]
        while 1:
            try:
                _app.send_task("rawhttp.image_spider.crawl_to_upyun", (
                    img_url,), kwargs={"page_url": page_url},
                              queue="rawhttp.image_spider")
            except:
                pass
            else:
                break
    except:
        new_url = ''
    return new_url