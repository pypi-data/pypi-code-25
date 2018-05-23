#! /usr/bin/env python
# coding: utf-8

import os
import sys
import argparse
from JYAliYun.AliYunOSS import OSSBucket

__author__ = '鹛桑够'

env_oss_conf = "OSS_CONF_PATH"


def receive_conf_path(conf_path):
    if conf_path is None:
        conf_path = os.environ.get(env_oss_conf)
        if conf_path is None:
            sys.stderr.write("Please use -c or --conf-path set oss configure path")
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
        for k, v in resp.headers.items():
            print("%s\t%s" % (k, v))
    sys.exit(exit_code)


if __name__ == "__main__":
    oss_head()