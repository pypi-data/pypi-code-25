import sys, tempfile, os, json
from getpass import getpass
from os.path import join, dirname
from subprocess import call

from .util import CONFIG_PATH, load_config, update_config

from requests_oauthlib import OAuth1Session
from cliff.command import Command

class Config(Command):
    "Config API key"

    def take_action(self, parsed_args):

        config = load_config(CONFIG_PATH)

        CK = input("CONSUMER_KEY: ")
        CS = getpass("CONSUMER_SECRET: ")
        AT = input("ACCESS_TOKEN: ")
        AS = getpass("ACCESS_TOKEN_SECRET: ")

        config["TWITTER_CK"] = CK
        config["TWITTER_CS"] = CS
        config["TWITTER_AT"] = AT
        config["TWITTER_AS"] = AS

        update_config(config, CONFIG_PATH)
        print("API keys has been set.")

class Tweet(Command):
    "Create and send a new tweet"

    def take_action(self, parsed_args):

        def parse_error(res):
            return res["errors"][0]['message']

        def send_tweet(params):
            url = "https://api.twitter.com/1.1/statuses/update.json"
            
            config = load_config(CONFIG_PATH)

            CK = config['TWITTER_CK']
            CS = config['TWITTER_CS']
            AT = config['TWITTER_AT']
            AS = config['TWITTER_AS']

            twitter = OAuth1Session(CK, CS, AT, AS)
            req = twitter.post(url, params)
            
            if req.status_code == 200:
                print("Tweet has successfully sent.")
            else:
                res = req.json()
                err = parse_error(res)
                print("Error: " + err)
        
        initial_message = ["\n", "# Write your tweet above.\n"]
        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            for msg in initial_message:
                tf.write(msg.encode('utf-8'))
            tf.flush()
            call(['vim', '+set backupcopy=yes', tf.name])
            tf.flush()
            
            tf.seek(0)
            contents = ""
            for line in tf:
                decoded_line = line.decode("utf-8")
                if decoded_line != "# Write your tweet above.\n":
                    contents += decoded_line
                else:
                    break

        params = {"status": contents}
        if not params["status"] or params["status"] == "\n":
            print("Aborted")
            return

        send_tweet(params)
