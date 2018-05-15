"""
2018/02/02 numata
backlog APIのクライアントライブラリ
config.jsonからapi keyをロードして、requestを投げる
"""


from .backlogclient import BacklogClient
from .resourse import *


def _check_parameter(params, required):
    """
    checking parameter type
    :rtype: None
    """
    key = params.keys()
    for req_word in required:
        if req_word not in key:
            print(req_word, ': ')
            raise Exception('Not input required parameter.')
    return None
