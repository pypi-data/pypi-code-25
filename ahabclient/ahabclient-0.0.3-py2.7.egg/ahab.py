#!/bin/env python

import json
import docker
import semantic_version
import os
import sys
import argparse

AHAB_SERVER = "https://api.ahab.xyz/"

class AhabClient():
    def __init__(self, folder = os.getcwd()):
        self.folder = folder 
        self.dockerclient = docker.from_env()
        self.descriptor = ".ahab.json"

    def init(self, tag):
        try:
            self.read_descriptor()
            print("already initialized!")
        except:
            self.conf = {
                "global":{"image":tag},
                "local":{}
            }
            self.write_descriptor(init=True)

    def pull(self, mode="latest"):
        self.read_descriptor()
        url = AHAB_SERVER + "?tag="+self.conf.get("global")["image"]
        r = requests.get(url)
        cver = r.json.get("latest")
        self.conf.get("local")["version"] = cver

    def read_descriptor(self):
        with open(self.descriptor, "rb") as tf:
            self.conf = json.load(tf)
            self.tag = self.conf.get("global").get("image")
            self.prev_version = self.conf.get("local").get("version")

    def generate_version(self, major=False, minor=False, patch=True):
        self.next_version = semantic_version.Version(self.prev_version, partial=True)
        if patch:
            self.next_version = self.next_version.next_patch()
        if minor:
            self.next_version = self.next_version.next_minor()
        if major:
            self.next_version = self.next_version.next_major()
        self.new_tag = self.tag.format(self.next_version)
        print("version bumped to {}".format(self.new_tag))

    def build(self):
        print("building {} in folder {}".format(self.new_tag, self.folder))
        self.built = self.dockerclient.images.build(path=self.folder, tag=self.new_tag)
        print("built")

    def push(self):
        print("pushing {}".format(self.new_tag))
        self.dockerclient.images.push(self.new_tag)
        print("pushed")

    def write_descriptor(self, init=False):
        with open(self.descriptor, "wb") as tf:
            if not init:
                self.conf.get("local")["version"] = str(self.next_version)
            json.dump(self.conf, tf)

    def run(self, major=False, minor=False, patch=True, push=True):
        try:
            self.read_descriptor()
            self.generate_version(major, minor, patch)
            self.build()
            if push:
                self.push()
            self.write_descriptor()
        except IOError as ex:
            print("ARRR! {} is missing".format(self.descriptor))
        except Exception as ex:
            print("ARRR! We need a whale to go whale hunting. Docker must be running.")
            print(ex)

def main():
    parser = argparse.ArgumentParser(description='Ahab Docker Client')

    subparsers = parser.add_subparsers(help='Ahab Operations', destination="operation")
    
    parser_init = subparsers.add_parser('init', help='initialization')
    parser_init.add_argument('image', type=str)

    parser_pull = subparsers.add_parser('pull', help='initialization')
    parser_pull.add_argument('image', type=str)


    parser_build = subparsers.add_parser('build', help='initialization')
    parser_pull.add_argument('bump', type=str, default="patch")

    parser_push = subparsers.add_parser('push', help='initialization')
    parser_pull.add_argument('bump', type=str, default="patch")


    args = parser.parse_args(sys.argv[1:])
    args = vars(args)
    print args
    #c = AhabClient()
    #if args.get("operation") == "init":
    #    c.init(args.get("tag"))
    #if args.get("operation") == "pull":
    #    c.pull()
    #if args.get("operation") == "build":
    #    c.run(push=False)
    #if args.get("operation") == "push":
    #    c.run()

if __name__ == "__main__":
    main()