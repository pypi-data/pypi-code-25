import v_vk_api

import os, json

def get_credentials():
    cfg_path = 'config_test.json'
    if os.path.isfile(cfg_path):
        with open('config_test.json') as f:
            r = json.load(f)
            return r
credentials = get_credentials()
api = v_vk_api.create(
    app_id=credentials.get('app_id'),
    login=credentials.get('login'),
    password=credentials.get('password'),
    proxies=credentials.get('proxies'))
print(api.request_clear_status())
