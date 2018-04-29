import sys

import pytrello.request_wrapper as request


def get_my_boards():
    url = 'https://api.trello.com/1/members/me/boards'
    return request.get(url)


def get_board(board_id):
    url = 'https://api.trello.com/1/boards/{board_id}'
    return request.get(url, board_id=board_id)


def get_board_id(board_name):
    boards = get_my_boards()
    for board in boards:
        if board['name'] == board_name:
            return board['id']
    sys.exit('Board not found: %s' % board_name)
