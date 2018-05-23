
class GUIException(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TooManyItemsChecked(GUIException):

    def __init__(self, *args):
        super().__init__('Expected 1 argument, received {}'.format(len(args)))

