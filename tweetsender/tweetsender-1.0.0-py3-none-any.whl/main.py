# -*- coding: utf-8 -*-

import argparse
import os
from os.path import join, dirname

from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv


from cliff.app import App  
from cliff.commandmanager import CommandManager  
  
import sys  
import logging  
  
class TweetSender(App):  
      
    def __init__(self):  
        super(TweetSender, self).__init__(  
                description='Send-only Twitter CLI',  
                version='1.0',  
                command_manager=CommandManager('tweet.command'),                   
        )  
  
def main(argv=sys.argv[1:]):  
    tweetSender = TweetSender()  
    return tweetSender.run(argv)  
