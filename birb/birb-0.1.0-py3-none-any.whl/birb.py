#!/usr/bin/python3
# -*- coding: utf-8 -*-

from TwitterAPI import TwitterAPI
from cryptography.fernet import Fernet
import getpass
import birb_keys
import importlib
import click
import os

@click.group(invoke_without_command=True)
@click.pass_context
def birb(context):
    if (birb_keys.consumer_key is None
        or birb_keys.consumer_secret is None 
        or birb_keys.access_token_key is None
        or birb_keys.access_token_secret is None
        or birb_keys.enc_key is None):
        init_birb()
    if context.invoked_subcommand is None:
        send_tweet()

@birb.command('tweet', short_help='send a tweet')
def send_tweet():
    tweet_length = 280
    api = get_keys()
    tweet = input(colors.PROCESSING + 'Compose your tweet: ' + colors.ENDC)
    if parse_tweet(tweet, tweet_length):
        r = api.request('statuses/update', {'status': tweet})
        print(colors.OKGREEN + 'Tweet sent! (°∋°)' + colors.ENDC 
              if r.status_code == 200 
              else colors.FAIL + 'Error: ' + r.text + colors.ENDC)
    else:
        print(colors.WARNING +
              'Your tweet is ' + str(len(tweet) - tweet_length) +
                 ' character(s) too long, please try again' +
              colors.ENDC)
        send_tweet()

@birb.command('oops', short_help='delete your most recent tweet')
@click.option('--resend', is_flag=True, help='resend a tweet immediately')
@click.pass_context
def delete_last_tweet(context, resend):
    api = get_keys()
    tweet_id = get_last_tweet_id(api)
    r = api.request('statuses/destroy/:' + str(tweet_id))
    print(colors.FAIL + 'Last tweet deleted' + colors.ENDC
          if r.status_code == 200 
          else colors.FAIL + 'Error: ' + r.text + colors.ENDC)
    if resend:
        context.invoke(send_tweet)

# ------------
#  Helpers and init
# ------------

def init_birb():
    key = Fernet.generate_key()
    f = Fernet(key)
    here = os.path.abspath(os.path.dirname(__file__))
    credentials = ['consumer_key', 'consumer_secret',
                   'access_token_key', 'access_token_secret']
                   
    # Ask for twitter API keys
    print('Create an app on https://apps.twitter.com and paste the following infos to use it: ')
    for element in range(len(credentials)):
        credentials[element] = encode_encrypt(f, getpass.getpass('Paste ' + credentials[element] + ' here: '))

    with open(os.path.join(here, 'birb_keys.py'), 'r+', encoding='utf-8') as script:
            content = script.readlines()
            script.seek(0)
            for line in content:
                if 'consumer_key =' in line:
                    script.write('consumer_key = ' + '\'' + credentials[0].decode('utf-8') + '\'\n')
                elif 'consumer_secret =' in line:
                    script.write('consumer_secret = ' + '\'' + credentials[1].decode('utf-8') + '\'\n')
                elif 'access_token_key =' in line:
                    script.write('access_token_key = ' + '\'' + credentials[2].decode('utf-8') + '\'\n')
                elif 'access_token_secret =' in line:
                    script.write('access_token_secret = ' + '\'' + credentials[3].decode('utf-8') + '\'\n')
                elif 'enc_key =' in line:
                    script.write('enc_key = ' + '\'' + key.decode('utf-8') +'\'\n')
                else:
                    script.write(line)
            script.truncate()
            importlib.reload(birb_keys)

def get_keys():
    f = Fernet(birb_keys.enc_key)
    api = TwitterAPI(f.decrypt(str.encode(birb_keys.consumer_key)),
                     f.decrypt(str.encode(birb_keys.consumer_secret)),
                     f.decrypt(str.encode(birb_keys.access_token_key)),
                     f.decrypt(str.encode(birb_keys.access_token_secret)))
    return api

# handle colors for terminal
class colors:
    PROCESSING = '\033[95m' + '[~] '
    OKBLUE = '\033[94m' + '[+] '
    OKGREEN = '\033[92m' + '[+] '
    WARNING = '\033[93m' + '[!] '
    FAIL = '\033[91m' + '[-] '
    ENDC = '\033[0m'

def parse_tweet(tweet, tweet_length):
    return False if len(tweet) > tweet_length else True

def get_last_tweet_id(api):
    r = api.request('statuses/user_timeline', {'count': 1})
    tweet_id = [False if 'id' not in item else item['id'] for item in r]
    try:
        if tweet_id[0]:
            return tweet_id[0]
        else:
            raise Exception(tweet_id)
    except Exception:
        print(colors.FAIL + 
              'Stopping: tweet id not found. Status code returned: ' + 
              str(r.status_code) + colors.ENDC)

def encode_encrypt(f, string):
    return f.encrypt(str.encode(string))


if __name__ == '__main__':
    birb()