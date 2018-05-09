import requests
import sys
from contextlib import closing


class ProgressBar(object):

    def __init__(self, title, count=0.0, total=100.0, unit='', sep='/', chunk_size=1024):
        super(ProgressBar, self).__init__()
        self.info = "%.2f%% %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # Percent%  进度 单位 分割线 总数 单位
        _info = self.info % (100*self.count/self.total, self.count/self.chunk_size, self.unit, self.seq, self.total/self.chunk_size, self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        end_str = "\r"
        if self.count >= self.total:
            print('\nDownload Finished')
            print('File stored at %s\\' % sys.path[0])
            return ''
        print(self.__get_info(), end=end_str)

file_name='test.m4a'
url = 'http://www.midishow.com/midi/file/44017.mid'

with closing(requests.get(url, stream=True)) as response:
    chunk_size = 1024
    print(response.headers)
    content_size = int(response.headers['content-length']) # 内容体总大小
    progress = ProgressBar('test', total=content_size,
                                     unit="KB", chunk_size=chunk_size)
    with open(file_name, "wb") as file:
       for data in response.iter_content(chunk_size=chunk_size):
           file.write(data)
           progress.refresh(count=len(data))
