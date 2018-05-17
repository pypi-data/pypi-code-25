from JUtil.Util import Util
from JPhoto.Photo import Photo
import os
import shutil
import datetime
import argparse
import time

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="사진을 날짜별로 폴더로 정리하기")
    parser.add_argument('--input', type=str, required=True, default='', help='정리할 사진 폴더')
    parser.add_argument('--output', type=str, required=True, default='', help='이동될 사진 폴더')
    parser.add_argument('--thumnailsize', type=int, required=False, default='1024', help='이동될 사진 폴더')

    args = parser.parse_args()

    photo = Photo()
    util = Util()

    file_list = photo.getImageFileList(str(args.input))
    thumnail_size = args.thumnailsize
    # print(file_list)
    if len(file_list) == 0:
        print("정리할 사진이 없습니다")
    else:
        for idx, file in enumerate(file_list):
            create_date = ''
            try:
                exif = photo.getExif(file)
                if exif != None:
                    if 'DateTimeOriginal' in exif:
                        create_date = exif['DateTimeOriginal']
                    elif 'DateTime' in exif:
                        create_date = exif['DateTime']
                    else:
                        create_date = datetime.datetime.fromtimestamp(os.stat(file).st_mtime)
                else:
                    create_date = datetime.datetime.fromtimestamp(os.stat(file).st_mtime)
            except:
                create_date = datetime.datetime.fromtimestamp(os.stat(file).st_mtime)
            create_date = str(create_date).replace(":", "-").split(" ")[0]

            util.makeDir(util.getAbsPath(str(args.output)) + os.path.sep + create_date)
            util.makeDir(util.getAbsPath(str(args.output)) + os.path.sep + create_date + os.path.sep + 'thumbnail')
            # print(util.getAbsPath(str(args.output)) + os.path.sep + create_date + os.path.sep + 'thumbnail')

            shutil.move(file, util.getAbsPath(str(args.output)) + os.path.sep + create_date)  ## to move files from
            photo.resizePhoto(
                util.getAbsPath(str(args.output)) + os.path.sep + create_date + os.path.sep + file.split(os.path.sep)[
                    -1], util.getAbsPath(str(
                    args.output)) + os.path.sep + create_date + os.path.sep + 'thumbnail' + os.path.sep + 'resize_' +
                file.split(os.path.sep)[-1], basewidth=thumnail_size)

            print(idx + 1, "번", file + "->" + util.getAbsPath(str(args.output)) + os.path.sep + create_date)
        print("정리 완료!")
