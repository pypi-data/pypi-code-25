#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta

from PIL import Image


def trans_png(srcImageName, dstImageName):
    img = Image.open(srcImageName)
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = list()
    for item in datas:
        if item[0] > 220 and item[1] > 220 and item[2] > 220:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(dstImageName, "PNG")


def load_image(image_path):
    # 加载目标图片供对比用
    if os.path.isfile(image_path):
        load = Image.open(image_path)
        return load
    else:
        raise Exception("%s is not exist" % image_path)


def same_as(load_image, percent):
    # 对比图片，percent值设为0，则100%相似时返回True，设置的值越大，相差越大
    import math
    import operator

    image1 = Image.open('/var/folders/m6/qxn_swt902vd236j3f33b8cw0000gn/T/temp_screen.png')
    image1 = image1.convert('1')
    image2 = load_image

    histogram1 = image1.histogram()
    histogram2 = image2.histogram()

    differ = math.sqrt(
        reduce(operator.add, list(map(lambda a, b: (a - b) ** 2, histogram1, histogram2))) / len(histogram1))
    if differ <= percent:
        return True
    else:
        return False


if __name__ == '__main__':
    oneday = timedelta(days=1)
    day = datetime.now() - oneday
    date_from = datetime(day.year, day.month, day.day, 0, 0, 0)
    print date_from
