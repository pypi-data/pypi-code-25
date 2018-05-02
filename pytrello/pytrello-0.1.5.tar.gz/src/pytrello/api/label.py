import pytrello.request_wrapper as request
import pytrello.api.board as board


LABEL_COLORS = ['yellow', 'purple', 'blue', 'red', 'green', 'orange', 'black',
                'sky', 'pink', 'lime', 'null']


def get_label(label_id):
    url = 'https://api.trello.com/1/labels/{label_id}'
    return request.get(url, board_id=label_id)


def update_label(label_id):
    url = 'https://api.trello.com/1/labels/{label_id}'
    return request.put(url, label_id=label_id)


def update_label_color(label_id, color):
    url = 'https://api.trello.com/1/labels/{label_id}/color'
    payload = {'value': color}
    return request.put(url, label_id=label_id, payload=payload)


def update_label_name(label_id, name):
    url = 'https://api.trello.com/1/labels/{label_id}/name'
    payload = {'value': name}
    return request.put(url, label_id=label_id, payload=payload)


def create_label(name, color, board_id):
    url = 'https://api.trello.com/1/labels'

    assert color in LABEL_COLORS, "Invalid label color: %s" % color
    payload = {'name': name, 'color': color, 'idBoard': board_id}
    return request.post(url, payload=payload)


def delete_label(label_id):
    url = 'https://api.trello.com/1/labels/{label_id}'
    return request.delete(url, label_id=label_id)
