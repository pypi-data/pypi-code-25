from pytrello.api import board as board_api


if __name__ == '__main__':
    board_id = board_api.get_board_id('pytrello')
    # print(board_api.get_board(board_id=board_id))
    print(board_api.get_board_field(board_id=board_id, field_name='name'))
