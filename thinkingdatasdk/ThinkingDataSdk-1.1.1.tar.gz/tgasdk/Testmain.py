#encoding:utf-8
import datetime
import threading
import time

from tgasdk.sdk import TGAnalytics, BatchConsumer, LoggingConsumer, AsyncBatchConsumer

# tga = TGAnalytics(AsyncBatchConsumer("server_uri","appid"))
# tga = TGAnalytics(BatchConsumer("http://10.25.38.223:44444/logagent","quanjie-python-sdk"))
tga = TGAnalytics(LoggingConsumer("F:/home/sdk/log"))


properties = {
    #"#time":'2018-01-12 20:46:56',
    "custome":datetime.datetime.now(),
    "#ip":"192.168.1.1",
    "Product_Name":"a",
    '#os':'windows',
    "today":datetime.date.today()

}

tga.track('dis',None,"shopping",properties)
tga.close()






