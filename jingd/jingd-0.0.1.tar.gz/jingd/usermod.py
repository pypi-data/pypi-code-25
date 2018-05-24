#! /usr/bin/env python
# coding: utf-8

import sys
import os
import requests
import argparse

user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"


def write_error(msg, code=1):
    sys.stderr.write("%s\n" % msg)
    sys.exit(code)


def request_auth(method, url, data):
    auth_endpoint = os.environ.get("JINGD_AUTH_ENDPOINT")
    if auth_endpoint is None:
        write_error("Please Set ENV JINGD_AUTH_ENDPOINT", -1)
    headers = {"Content-Type": "application/json", "User-Agent": user_agent}
    url = "%s%s" % (auth_endpoint, url)
    resp = requests.request(method, url, headers=headers, json=data)
    if resp.status_code != 200:
        write_error(resp.status_code)
    r_data = resp.json()
    if r_data["status"] % 10000 < 100:
        print(r_data["message"])
    else:
        write_error(r_data["message"])


def reset_password(account, password):
    url = "/auth/password/reset/admin/"
    method = "PUT"
    data = {"account": account, "new_password": password}
    request_auth(method, url, data)


def block_user(account):
    url = "/auth/account/block/admin/"
    method = "PUT"
    data = {"account": account}
    request_auth(method, url, data)


def unlock_user(account):
    url = "/auth/account/unlock/admin/"
    method = "PUT"
    data = {"account": account}
    request_auth(method, url, data)


def main():
    usage = "Help you modify jingd user"
    description = "Please use follow arguments modify jingd user"
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("-a", "--action", dest="action", help="action")
    parser.add_argument("-u", "--user", dest="user", help="jingdu user")
    parser.add_argument("-p", "--password", dest="password", help="jingdu password", default="123456")
    args = parser.parse_args()
    if args.action is None:
        write_error("Please Set [action] use -a or --action", 1)
    if args.user is None:
        write_error("Please Set [user] use -u or --user", 2)
    if args.action == "reset":
        reset_password(args.user, args.password)
    elif args.action == "block":
        block_user(args.user)
    elif args.action == "unlock":
        unlock_user(args.user)
    else:
        write_error("Invalid action")

if __name__ == "__main__":
    main()
