from pytrello.api import decorators

from pytrello import request_wrapper as request


@decorators.basic_api
def get_card(card_id):
    pass


@decorators.basic_api
def get_card_field(card_id, field):
    pass


@decorators.basic_api
def get_card_actions(card_id):
    pass


@decorators.basic_api
def get_card_attachments(card_id):
    pass


@decorators.basic_api
def get_card_attachment(card_id, attachment_id):
    pass


@decorators.basic_api
def get_card_board(card_id):
    pass


@decorators.basic_api
def get_card_checklist_item_state(card_id):
    pass


@decorators.basic_api
def get_card_checklists(card_id):
    pass


@decorators.basic_api
def get_card_checklist_item(card_id, checklist_item_id):
    pass


@decorators.basic_api
def get_card_custom_fields(card_id):
    pass


@decorators.basic_api
def get_card_list(card_id):
    pass


@decorators.basic_api
def get_card_members(card_id):
    pass


@decorators.basic_api
def get_card_voted_members(card_id):
    pass


@decorators.basic_api
def get_card_plugin_data(card_id):
    pass


@decorators.basic_api
def get_card_stickers(card_id):
    pass


@decorators.basic_api
def get_card_sticker(card_id, sticker_id):
    pass


@decorators.basic_api
def update_card(card_id):
    pass


@decorators.basic_api
def update_card_as_done(card_id):
    pass


@decorators.basic_api
def update_card_as_not_done(card_id):
    pass


@decorators.basic_api
def update_card_due(card_id, due):
    pass


@decorators.basic_api
def update_card_comment(card_id, action_id):
    pass


@decorators.basic_api
def update_card_checklist_item(checklist_item_id):
    pass


@decorators.basic_api
def update_card_sticker(card_id, sticker_id):
    pass


@decorators.basic_api
def create_card(name,
                idList,
                desc=None,
                pos=None,
                due=None,
                dueComplete=None,
                idMembers=None,
                idLabels=None,
                urlSource=None,
                fileSource=None,
                idCardSource=None,
                keepFromSource=None):
    pass


@decorators.basic_api
def add_card_comment(card_id, text):
    pass


@decorators.basic_api
def add_card_attachment(card_id):
    pass


@decorators.basic_api
def create_card_checklist(card_id):
    pass


@decorators.basic_api
def add_card_label(card_id, value):
    pass


@decorators.basic_api
def add_card_member(card_id):
    pass


@decorators.basic_api
def add_card_new_label(card_id):
    pass


@decorators.basic_api
def mark_card_notifications_read(card_id):
    pass


@decorators.basic_api
def add_card_vote(card_id):
    pass


@decorators.basic_api
def delete_card(card_id):
    pass


@decorators.basic_api
def delete_card_comment(card_id):
    pass


@decorators.basic_api
def delete_card_attachment(card_id, attachment_id):
    pass


@decorators.basic_api
def delete_card_checklist_item(card_id, checklist_item_id):
    pass


@decorators.basic_api
def delete_card_checklist(card_id, checklist_id):
    pass


@decorators.basic_api
def remove_card_label(card_id, label_id):
    pass


@decorators.basic_api
def remove_card_member(card_id, member_id):
    pass


@decorators.basic_api
def remove_card_vote(card_id, member_id):
    pass


@decorators.basic_api
def remove_card_sticker(card_id, sticker_id):
    pass


def add_label(card_id, label_id):
    url = 'https://api.trello.com/1/cards/{card_id}/idLabels'
    payload = {'value': label_id}
    return request.post(url, card_id=card_id, payload=payload)


def delete_label(card_id, label_id):
    url = 'https://api.trello.com/1/cards/{card_id}/idLabels/{label_id}'
    return request.delete(url, card_id=card_id, label_id=label_id)


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
