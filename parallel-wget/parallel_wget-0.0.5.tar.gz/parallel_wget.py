import sys, os
from os import path as op
import os, sys
op.dirname(sys.executable)
import wget
import tarfile
from multiprocessing import Pool

def wget_file(file_url):
    try:
      wget.download(file_url)
      print("File {} downloaded!".format(file_url))
    except Exception as e:
      print('Got exception: {0}'.format(e))
      pass

def parallel_wget(host, path, files):
    file_urls = ['{0}{1}{2}'.format(host, path, f['filename']) for f in files]
    print("Downloading files~")
    p = Pool(len(file_urls))
    p.map(wget_file, file_urls)
    downloaded_files = [op.join(os.getcwd(), f) for f in os.listdir(".") if op.isfile(f)]
    for file in downloaded_files:
        if file.endswith(".tgz"):
            print("unziping {}".format(file))
            tar = tarfile.open(file, "r:gz")
            tar.extractall()
            tar.close()
            os.remove(file)
            print("{} has remove".format(file))
    print('Completed download of {0} files'.format(len(files)))
