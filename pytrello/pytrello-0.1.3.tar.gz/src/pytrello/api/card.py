from datetime import datetime
import sys

import pytrello.request_wrapper as request
import pytrello.api.board as board


def get_cards(board_id):
    url = 'https://api.trello.com/1/boards/{board_id}/cards'
    return request.get(url, board_id=board_id)


def get_card(board_id, card_id):
    url = 'https://api.trello.com/1/boards/{board_id}/cards/{cardid}'
    return request.get(url, board_id=board_id, cardid=card_id)


def get_card_id(board_name, card_name):
    board_id = board.get_board_id(board_name)
    cards = get_cards(board_id)
    for card in cards:
        if card['name'] == card_name:
            return card['id']
    sys.exit('Card not found: %s' % card_name)


def add_comment(card_id, comment=None):
    url = 'https://api.trello.com/1/cards/{card_id}/actions/comments'
    now = datetime.now()
    timestamp = '[%d-%d-%d %d:%d]' \
                % (now.year, now.month, now.day, now.hour, now.minute)
    if comment is None:
        comment = '%s Marked as done.' % (timestamp)
    else:
        comment = '%s %s' % (timestamp, comment)

    payload = {'text': comment}
    request.post(url, card_id=card_id, payload=payload)


def mark_as_done(card_id, comment=None):
    # Mark the card as done.
    url = 'https://api.trello.com/1/cards/{card_id}/dueComplete'
    payload = {'value': 'true'}
    request.put(url, card_id=card_id, payload=payload)

    # Add comment to the card.
    add_comment(card_id, comment=comment)


if __name__ == '__main__':
    id = get_card_id('pytrello', 'test card')
    print(mark_as_done(id))
