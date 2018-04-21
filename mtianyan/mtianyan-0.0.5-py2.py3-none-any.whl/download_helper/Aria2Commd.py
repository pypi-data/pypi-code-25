# -*- coding: utf-8 -*-
import subprocess


class Aria2DownloadTool:
    def __init__(self, aria2_path):
        self.aria2_path = aria2_path

    def download(self, download_url, filename=None, dir=None):
        aria2_opts = [self.aria2_path + '/aria2c', download_url]
        if filename:
            aria2_opts.extend(('--out', filename))
        if dir:
            aria2_opts.append(('--dir ', dir))
        # 这里只负责提交下载任务使用Popen 不阻塞等待返回，实际下载进度由YAAW维护。
        exit_code = subprocess.call(aria2_opts, shell=True)
        if exit_code != 0:
            raise Exception('aria2c exited abnormally')


def openAria2RPC(aria2_path):
    subprocess.call("\"" + aria2_path + "/aria2c\"   --conf-path=aria2.conf -D")

def start_webui_aria2(port):
    import os  
    os.chdir('../plugins/webui-aria2/')
    # 使用call 父进程会等待子进程直到完成，而使用popen不指定就不会阻塞
    subprocess.Popen('python -m http.server {0}'.format(port),shell=True)
    start_browser(port)

def start_browser(port):
    import webbrowser
    url = 'http://127.0.0.1:{0}'.format(port)
    webbrowser.open(url, new=0, autoraise=True)

if __name__ == '__main__':
    # aria2_path = "./"
    
    # openAria2RPC(aria2_path)
    # download_url = "http://groups.inf.ed.ac.uk/vision/CAVIAR/CAVIARDATA1/Walk2/Walk2.mpg"
    # filename = "master.zip";
    # dir = "./";
    # tool = Aria2DownloadTool(aria2_path)
    # tool.download(download_url, filename, dir);
    start_webui_aria2(9999)