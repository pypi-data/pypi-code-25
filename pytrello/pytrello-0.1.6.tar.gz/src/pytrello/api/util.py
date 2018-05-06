from datetime import datetime
import sys

from pytrello.api import board as board_api
from pytrello.api import card as card_api
from pytrello.api import label as label_api


def get_board_id(board_name):
    boards = board_api.get_my_boards()

    for board in boards:
        if board['name'] == board_name:
            return board['id']
    sys.exit('Board not found: %s' % board_name)


def get_list_id(board_name, list_name):
    board_id = get_board_id(board_name=board_name)

    for list_ in board_api.get_board_lists(board_id=board_id):
        if list_['name'] == list_name:
            return list_['id']
    sys.exit('List not found: %s' % list_name)


def get_card_id(board_name, card_name):
    board_id = get_board_id(board_name=board_name)

    for card in board_api.get_board_cards(board_id=board_id):
        if card['name'] == card_name:
            return card['id']
    sys.exit('Card not found: %s' % card_name)


def get_label_id(board_name, label_name):
    board_id = get_board_id(board_name=board_name)

    for label in board_api.get_board_labels(board_id=board_id):
        if label['name'] == label_name:
            return label['id']
    sys.exit('Label not found: %s' % label_name)


def create_card(board_name, list_name, card_name):
    list_id = get_list_id(board_name=board_name, list_name=list_name)
    card_api.create_card(name=card_name, idList=list_id)


def delete_card(board_name, card_name):
    card_id = get_card_id(board_name=board_name, card_name=card_name)
    card_api.delete_card(card_id=card_id)


def add_comment(board_name, card_name, comment_):
    card_id = get_card_id(board_name=board_name, card_name=card_name)
    card_api.add_card_comment(card_id=card_id, text=comment_)


def add_label(board_name, card_name, label_name):
    card_id = get_card_id(board_name=board_name, card_name=card_name)
    label_id = get_label_id(board_name=board_name, label_name=label_name)
    card_api.add_card_label(card_id=card_id, value=label_id)


def create_label(board_name, label_name, label_color):
    board_id = get_board_id(board_name=board_name)
    label_api.create_label(name=label_name,
                           color=label_color,
                           idBoard=board_id)


def mark_as_done(board_name, card_name, comment_):
    card_id = get_card_id(board_name=board_name, card_name=card_name)
    # Mark the card as done.
    card_api.update_card_as_done(card_id=card_id)

    if comment_ is not None:
        # Add comment to the card.
        card_api.add_card_comment(card_id=card_id,
                                  text=comment_)
    else:
        # Add default comment to the card.
        now = datetime.now()
        timestamp = '[%d-%d-%d %d:%d]' \
            % (now.year, now.month, now.day, now.hour, now.minute)
        card_api.add_card_comment(card_id=card_id,
                                  text='%s Marked as done.' % timestamp)


def mark_as_not_done(board_name, card_name, comment_):
    card_id = get_card_id(board_name=board_name, card_name=card_name)
    # Mark the card as done.
    card_api.update_card_as_not_done(card_id=card_id)

    if comment_ is not None:
        # Add comment to the card.
        card_api.add_card_comment(card_id=card_id,
                                  text=comment_)
    else:
        # Add default comment to the card.
        now = datetime.now()
        timestamp = '[%d-%d-%d %d:%d]' \
            % (now.year, now.month, now.day, now.hour, now.minute)
        card_api.add_card_comment(card_id=card_id,
                                  text='%s Reverted completion.' % timestamp)


def set_due_date(board_name, card_name, due_date):
    card_id = get_card_id(board_name=board_name, card_name=card_name)
    card_api.update_card_due(card_id=card_id, due=due_date)
