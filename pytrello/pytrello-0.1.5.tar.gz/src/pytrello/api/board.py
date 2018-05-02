import sys

import pytrello.request_wrapper as request


def get_my_boards():
    url = 'https://api.trello.com/1/members/me/boards'
    return request.get(url)


def get_board(board_id):
    url = 'https://api.trello.com/1/boards/{board_id}'
    return request.get(url, board_id=board_id)


def get_labels(board_id):
    url = 'https://api.trello.com/1/boards/{board_id}/labels'
    return request.get(url, board_id=board_id)


def get_board_id(board_name):
    boards = get_my_boards()
    for board in boards:
        if board['name'] == board_name:
            return board['id']
    sys.exit('Board not found: %s' % board_name)


def get_label_id(board_name, label_name):
    board_id = get_board_id(board_name)

    for label in get_labels(board_id):
        if label['name'] == label_name:
            return label['id']

    sys.exit('Label not found: %s' % label_name)
