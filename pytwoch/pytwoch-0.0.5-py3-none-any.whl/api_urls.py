class APIUrls(object):
    @staticmethod
    def get_board(board_id: str):
        return 'http://2ch.hk/{}/catalog.json'.format(board_id)

    @staticmethod
    def get_thread(board_id: str, thread_id: str):
        return 'http://2ch.hk/{}/res/{}.json'.format(board_id, thread_id)
