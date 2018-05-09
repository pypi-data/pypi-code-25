# -*- coding: utf-8 -*-
from __future__ import division

import sys
import math
import click
import requests
import threading
from tqdm import tqdm
from Queue import Queue

try:
    import urlparse
except ImportError:
    from urllib.parse import urlparse


s = requests.session()


class FileDownException(Exception):
    pass


def parse_headers(range=None, user_agent=None, **kwargs):
    headers = {}
    if range:
        headers.update(range)
    if user_agent:
        headers.update(user_agent)
    headers.update(kwargs)
    return headers


def parse_cookie():
    return {}


def parse_proxy():
    return {}


def do_request(method, url, range=None, **kwargs):
    headers = parse_headers(range)
    cookies = parse_cookie()
    proxies = parse_proxy()
    resp = s.request(method=method,
                     url=url,
                     headers=headers,
                     cookies=cookies,
                     proxies=proxies,
                     timeout=10,
                     allow_redirects=False,
                     **kwargs)
    return resp


def get_content_length(url):
    resp = do_request('HEAD', url)
    if resp.status_code != 200:
        raise FileDownException("HEAD request not allow")
    return int(resp.headers['Content-Length'])


def ceildiv(a, b):
    return int(math.ceil(a / b))


class DownloadProcess(object):
    def __init__(self, url, thread_num, filename=None):
        self.url = url
        self.thread_num = thread_num
        self.filename = filename or self.parse_filename()
        self.queue = Queue(thread_num * 2)
        self.content_length = get_content_length(self.url)
        self.interval = ceildiv(self.content_length, self.thread_num)
        self.progress =tqdm(total=self.content_length, unit='B', unit_scale=True, desc=self.filename)

    def parse_filename(self):
        return urlparse.urlparse(self.url).path.rsplit('/')[-1]

    def process(self):
        sys.stdout.write("\033[2K\033[E")
        sys.stdout.write('download process start. \n')
        sys.stdout.write('length %d, filename %s \n' % (self.content_length, self.filename))

        f = open(self.filename, 'wb')
        f.truncate(self.content_length)
        f.close()

        t = threading.Thread(target=self.update_progress)
        t.setDaemon(True)
        t.start()

        download_handlers = []
        for i in range(self.thread_num):
            start = i * self.interval
            end = start + self.interval
            download_handlers.append(DownloadHandler(self.url, self.filename, self.queue, start, end, str(i)))

        for d in download_handlers:
            d.start()
        for d in download_handlers:
            d.join()

        self.progress.close()
        sys.stdout.write('download process end. \n')

    def update_progress(self):
        while 1:
            self.progress.update(self.queue.get())


class DownloadHandler(threading.Thread):
    def __init__(self, url, filename, queue, start, end, name):
        super(DownloadHandler, self).__init__()
        self.url = url
        self.range_start = start
        self.range_end = end
        self.filename = filename
        self.queue = queue
        self.name = name
        self.chunk_size = 1024 * 10
        self.downloaded = 0

    def run(self):
        sys.stdout.write('Thread-%s start range %d-%d\n' % (self.name, self.range_start, self.range_end))
        range_header = {'Range': 'bytes={}-{}'.format(self.range_start, self.range_end)}

        resp = do_request('GET', self.url, range=range_header, stream=True)
        with open(self.filename, 'rb+') as f:
            f.seek(self.range_start)
            for data in resp.iter_content(chunk_size=self.chunk_size):
                f.write(data)
                self.queue.put(len(data))
                self.downloaded += len(data)

        sys.stdout.write("Thread-%s end range %d-%d\n" % (self.name, self.range_start, self.range_end))


@click.command()
@click.option('-t', '--thread_num', default=8, help='Number of threads')
@click.option('-f', '--filename', help='filename of download')
@click.argument('url')
def main(url, thread_num, filename):
    DownloadProcess(url, thread_num, filename).process()


if __name__ == '__main__':
    main()
