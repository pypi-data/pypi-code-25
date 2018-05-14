import os, json

CONFIG_PATH = os.path.expanduser('~') + os.sep + '.tweetsender_config.json'

def load_config(path):
    if not os.path.exists(path):
        return {}

    with open(path, 'r') as f:
        config = json.load(f)
    return config

def update_config(config, path):
    with open(path, 'w') as f:
        json.dump(config, f)