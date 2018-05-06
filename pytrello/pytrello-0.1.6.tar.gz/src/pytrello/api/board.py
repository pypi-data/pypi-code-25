import sys

from pytrello.api import decorators


@decorators.basic_api
def get_board(board_id):
    pass


@decorators.basic_api
def get_board_field(board_id, field_name):
    pass


@decorators.basic_api
def get_board_actions(board_id):
    pass


@decorators.basic_api
def get_board_plugins(board_id):
    pass


@decorators.basic_api
def get_board_stars(board_id):
    pass


@decorators.basic_api
def get_board_cards(board_id):
    pass


@decorators.basic_api
def get_board_filtered_cards(board_id, filter):
    pass


@decorators.basic_api
def get_board_card(board_id, card_id):
    pass


@decorators.basic_api
def get_board_checklists(board_id):
    pass


@decorators.basic_api
def get_board_custom_fields(board_id):
    pass


@decorators.basic_api
def get_board_tags(board_id):
    pass


@decorators.basic_api
def get_board_labels(board_id):
    pass


@decorators.basic_api
def get_board_lists(board_id):
    pass


@decorators.basic_api
def get_board_filtered_lists(board_id, filter):
    pass


@decorators.basic_api
def get_board_members(board_id):
    pass


@decorators.basic_api
def get_board_memberships(board_id):
    pass


@decorators.basic_api
def update_board(board_id):
    pass


@decorators.basic_api
def update_board_members(board_id):
    pass


@decorators.basic_api
def add_board_member(board_id, member_id):
    pass


@decorators.basic_api
def update_board_membership(board_id, membership_id):
    pass


@decorators.basic_api
def create_board():
    pass


@decorators.basic_api
def enable_plugin(board_id):
    pass


@decorators.basic_api
def generate_calender_key(board_id):
    pass


@decorators.basic_api
def create_board_checklist(board_id):
    pass


@decorators.basic_api
def generate_email_key(board_id):
    pass


@decorators.basic_api
def create_board_label(board_id):
    pass


@decorators.basic_api
def create_board_list(board_id):
    pass


@decorators.basic_api
def delete_board(board_id):
    pass


@decorators.basic_api
def disable_plugin(board_id, plugin_id):
    pass


@decorators.basic_api
def delete_member(board_id, member_id):
    pass


@decorators.basic_api
def delete_powerup(board_id, powerup_name):
    pass


@decorators.basic_api
def get_my_boards():
    pass
