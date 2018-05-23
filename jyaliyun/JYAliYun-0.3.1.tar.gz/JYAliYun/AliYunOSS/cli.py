#! /usr/bin/env python
# coding: utf-8

import os
import sys
import argparse
from JYAliYun.AliYunOSS import OSSBucket

__author__ = '鹛桑够'

env_oss_conf = "OSS_CONF_PATH"


def print_table(t):
    def char_len(c):
        return len(c)

    def calc_tab(l, down=False):
        n = l / 8
        if l % 8 != 0 and down is False:
            n += 1
        return n
    max_len = []
    for line in t:
        for i in range(len(line)):
            l_c = char_len(line[i])
            if i >= len(max_len):
                max_len.append(l_c)
            elif l_c > max_len[i]:
                max_len[i] = l_c
    tabs = []
    for m_item in max_len:
        tabs.append(calc_tab(m_item) + 1)
    for line in t:
        line_s = []
        for i in range(len(line)):
            p_s = line[i] + "\t" * (tabs[i] - calc_tab(char_len(line[i]), down=True))
            line_s.append(p_s)
        print("".join(line_s))


def receive_conf_path(conf_path):
    if conf_path is None:
        conf_path = os.environ.get(env_oss_conf)
        if conf_path is None:
            sys.stderr.write("Please use -c or --conf-path set oss configure path\n")
            sys.exit(1)
    return conf_path


def oss_head():
    arg_man = argparse.ArgumentParser()
    arg_man.add_argument("-c", "--conf-path", dest="conf_path", help="oss configure file path", metavar="")
    arg_man.add_argument("-b", "--bucket-name", dest="bucket_name", help="oss bucket name", metavar="")
    arg_man.add_argument("-o", "-O", "--object", dest="object", help="oss object path", action="append", metavar="",
                         default=[])
    arg_man.add_argument("objects", metavar="object", nargs="*", help="oss object path")
    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    args = arg_man.parse_args()
    conf_path = receive_conf_path(args.conf_path)
    o_objects = args.object
    o_objects.extend(args.objects)
    kwargs = dict(conf_path=conf_path)
    if args.bucket_name is not None:
        kwargs["bucket_name"] = args.bucket_name
    bucket_man = OSSBucket(**kwargs)
    exit_code = 0
    for o_item in set(o_objects):
        print("-" * 20 + "start head %s" % o_item + "-" * 20)
        resp = bucket_man.head_object(o_item)
        if resp.status_code != 200:
            print("head fail! oss server return %s" % resp.status_code)
            exit_code += 1
            continue
        t = [["Header Key", "Header Value"], ["------------", "------------"]]
        for k, v in resp.headers.items():
            t.append([k, v])
        print_table(t)
    sys.exit(exit_code)


if __name__ == "__main__":
    oss_head()