import base64

from PIL import Image
from PIL.ExifTags import TAGS

from JUtil.Util import Util
import os
import piexif


class Photo(object):

    def __init__(self):
        self.className = 'JPhoto'
        self.util = Util()

    def getExif(self, filename):
        ret = {}
        image = Image.open(filename)
        info = image._getexif()
        if info != None:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                ret[decoded] = value

        else:
            ret = None
        return ret

    def resizePhoto(self, input_filename, output_filename, basewidth=300):
        img = Image.open(input_filename)
        if img.size[0] > basewidth:
            wpercent = (basewidth / float(img.size[0]))
        else:
            wpercent = 1.0

        hsize = int((float(img.size[1]) * float(wpercent)))

        try:
            exif_dict = piexif.load(img.info["exif"])
            exif_bytes = piexif.dump(exif_dict)

            img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            img.save(output_filename, exif=exif_bytes)
        except:
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            img.save(output_filename)

    def getFileList(self, input_path):
        file_list = os.listdir(input_path)
        abs_input_path = Util().getAbsPath(input_path)
        ret_file_list = []
        for idx, file in enumerate(file_list):
            # print(idx, self.util.getAbsPath(abs_input_path + os.path.sep + file) )
            if not os.path.isdir(self.util.getAbsPath(abs_input_path + os.path.sep + file)) and self.isImageFile(
                    self.util.getAbsPath(abs_input_path + os.path.sep + file)):
                ret_file_list.append(self.util.getAbsPath(abs_input_path + os.path.sep + file))

        # print(ret_file_list)
        return ret_file_list

    def isImageFile(self, filename):
        try:
            img = Image.open(filename)
            img.verify()
            return True
        except Exception:
            return False
