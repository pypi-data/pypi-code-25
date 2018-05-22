#!/usr/bin/env python3
"""Bulk deletion of files on your Slack workspace
   Requires a valid token from:
       https://api.slack.com/custom-integrations/legacy-tokens
"""
import os
import sys
import json
import urllib.parse
import http.client
import calendar
import argparse
import time
from datetime import datetime, timedelta

URL_DOMAIN="slack.com"
URL_LIST="/api/files.list"
URL_DEL="/api/files.delete"

def parse_args(argv):
    TOKEN = None
    if 'SLACK_TOKEN' in os.environ and os.environ['SLACK_TOKEN'] is not '':
        TOKEN = os.environ['SLACK_TOKEN']
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', '-t', help="Your Slack API Token. If none is provided, we'll try to use your SLACK_TOKEN environment variable instead.", default=TOKEN)
    parser.add_argument('--days', '-d',
                        help='Only remove files older than the specified amount of days',
                        type=int, default=10)
    parser.add_argument('--retries', '-r', help='Number of retries before aborting cleaning',
                        type=int, default=10)
    parser.add_argument('--cooldown', '-c', help='Time (s) to wait before another attempt to clean',
                        type=int, default=3)
    
    return parser.parse_args(argv)

def no_error(response):
    status = response.code
    if status != 200:
        print("Shit happened !")
        print("Status: %s" % status)
        print("Reason: %s" % response.reason)
        return False
    else:
        return True

def _delete_file(f, headers, cnt, total, token):
    """Delete one file with the Slack API (actual implementation)
    """
    timestamp = str(calendar.timegm(datetime.now().utctimetuple()))
    params = urllib.parse.urlencode({
        'token': token,
        'file': f['id'],
        'set_active': 'true',
        '_attempts': '1',
        't': timestamp
    })
    conn = http.client.HTTPSConnection(URL_DOMAIN)
    conn.request("POST", URL_DEL, body=params, headers=headers)
    response = conn.getresponse()
    if no_error(response):
        print("[{}/{}] deleted {} ({})".format(cnt, total, f['name'].encode('utf-8'), f['id']))
        return True
    else:
        return False
        print("Will exit because an error occured during the deletion of %s" % f['id'])
        sys.exit(1)    

def delete_file(f, headers, cnt, total, args):
    """Delete one file with the Slack API
    """
    cooldown_try = 0
    while cooldown_try <= args.retries:
        if _delete_file(f, headers, cnt, total, args.token):
            return True
        elif cooldown_try > args.retries:
            print("Max number of retries reached !")
            return False
        else:
            print(f"Let's cool down for {args.cooldown} seconds...")
            time.sleep(args.cooldown)
            cooldown_try += 1

def get_all_files(files_list, params, headers, args):
    """Fetch all files going through all the pages
    """
    files = files_list['files']
    paging = files_list['paging']
    current_page = paging['page']
    print("Fetching all files to delete")
    while current_page < paging['pages']:
        print("Fetching page {}/{}".format(current_page, paging['pages']-1))
        conn = http.client.HTTPSConnection(URL_DOMAIN)
        conn.request("POST", URL_LIST, body=params, headers=headers)
        response = conn.getresponse()
        responsejson = json.loads(response.read())
        files = files + responsejson['files']
        current_page += 1
        paging = responsejson['paging']
    total_nb_files = len(files)
    print("There's %s files to delete" % total_nb_files)
    for i in range(total_nb_files):
        f = files[i]
        if not delete_file(f, headers, i+1, total_nb_files, args):
            print("Will exit because an error occured during the deletion of %s" % f['id'])
            sys.exit(1)    

def main(argv=None):
    args = parse_args(argv)
    DAYS = args.days
    if args.token is None:
        print("Could not find a valid Slack Token")
        sys.exit(1)
    date = str(calendar.timegm((datetime.now() + timedelta(- args.days)).utctimetuple()))
    params = urllib.parse.urlencode({
        'token': args.token,
        'ts_date': date
    })
    headers = {
        'Content-type': 'application/x-www-form-urlencoded'
    }
    conn = http.client.HTTPSConnection(URL_DOMAIN)
    conn.request("POST", URL_LIST, body=params, headers=headers)
    response = conn.getresponse()
    response_code = response.code
    if no_error(response):
        get_all_files(json.loads(response.read()), params, headers, args)
    else:
        print("Will exit because an error occured during the initial fetch of the files list")
        sys.exit(1)

if __name__ == "__main__":
    main()
