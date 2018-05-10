try: #Python3
    import configparser
except ImportError: #Python2
    import ConfigParser as configparser
import os
from docopt import docopt
args = docopt("""
    Usage:
    rest_helper.py [options]
    
    Options:
    --help, -h                Shows this
    --num NUM, -n NUM         Number of URLs
    --config FILE, -c FILE    Config file location
    """)
numUrl = args['--num']
configFile = args['--config']
if configFile == None:
    configFile = "config.ini"
if numUrl == None:
    numUrl = 4
config = configparser.ConfigParser()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, configFile)
if not os.path.isfile(file_path):
    exit("File does not exit")
config.read(file_path)
loop = 0
try: #Python3
    for url in config['Urls']:
        restUrl = config['Urls'][url].replace('//','//'+config['Data']['username']+'@')
        restUrl +=config['Data']['urlpath']
        print(restUrl)
        loop+=1
        if int(numUrl) <= loop:
            break
except AttributeError: #Python2
    for url in config.items('Urls'):
        restUrl = url[1].replace('//','//'+config.get('Data','username')+'@')
        restUrl +=config.get('Data','urlpath')
        print(restUrl)
        loop+=1
        if int(numUrl) <= loop:
            break
