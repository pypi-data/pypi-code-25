class girlfriend(object):
    """docstring for girlfriend"""
    def __init__(self):
        self.name = "zhaotudou"
def love():
    print("love zhaotudou forever")

from random import randint


def colored_message(message):
    return '\033[0;{};01m{message}\033[0m'.format(randint(30, 37), message=message)

        