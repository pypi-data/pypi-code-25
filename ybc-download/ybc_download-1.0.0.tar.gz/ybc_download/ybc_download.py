import os
import urllib.request as rq
import shutil

def create_my_world():
    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/L1_res.tar.tgz'
    filename = 'L1_res.tar.tgz'
    rq.urlretrieve(url,filename)
    shutil.unpack_archive(filename)
    os.remove(filename)


def main():
    create_my_world()

if __name__ == '__main__':
    main()
