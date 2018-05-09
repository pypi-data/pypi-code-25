#!/usr/bin/env python
# coding=utf-8

import os
import base64
import time
import random
import re
import argparse

import requests


VERSION = "0.1.0"
HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://kan.msxiaobing.com/ImageGame/Portal?task=beauty",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
}
session = requests.Session()

TID_URL = "https://kan.msxiaobing.com/ImageGame/Portal?task=beauty"
IMG_URL = "https://kan.msxiaobing.com/Api/Image/UploadBase64"
SCORE_URL = "http://kan.msxiaobing.com/Api/ImageAnalyze/Process?service=beauty&tid={}"


def get_tid():
    """
    获取 tid
    """
    try:
        req = session.get(TID_URL, headers=HEADERS)
        return re.findall('name="tid" value="(.*?)"', req.text)[0]

    except Exception:
        pass


def get_img_url(img_path):
    """
    获取图片地址
    """
    file = base64.b64encode(open(img_path, "rb").read())
    try:
        req = session.post(IMG_URL, headers=HEADERS, data=file).json()
        return req["Host"] + req["Url"]

    except Exception:
        pass


def get_score(img_path):
    """
    获取颜值测试评价
    """
    current = str(int(time.time()))
    msg_id = current + str(random.randint(100, 999))

    forms = {
        "MsgId": msg_id,
        "CreateTime": current,
        "Content[imageUrl]": get_img_url(img_path),
    }
    try:
        req = session.post(
            SCORE_URL.format(get_tid()), data=forms, headers=HEADERS
        )
        try:
            return req.json()["content"]["text"]

        except Exception:
            return "好像出错了喔，要不再试一次"

    except Exception:
        pass


def get_parser():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        description="微软小冰颜值测试命令行工具", add_help=False
    )
    parser.add_argument("-i", "--images", type=str, help="测试照片")
    parser.add_argument("-v", "--version", action="store_true", help="版本信息")
    parser.add_argument(
        "-h", "--help", action="help", default=argparse.SUPPRESS, help="帮助页面"
    )
    return parser


def command_line_runner():
    """
    执行命令行操作
    """
    parser = get_parser()
    args = vars(parser.parse_args())

    if args["version"]:
        print(VERSION)
        return

    images = args["images"]
    if not images:
        parser.print_help()
        return

    if os.path.exists(images) and os.path.isfile(images):
        os.path.split(images)
        print(os.path.split(images)[-1], ":", get_score(images))
    else:
        raise Exception("测试照片路径不存在!")


if __name__ == "__main__":
    command_line_runner()
