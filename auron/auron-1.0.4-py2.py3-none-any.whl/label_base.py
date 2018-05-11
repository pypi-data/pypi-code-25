

class UserBase(object):
    _ID = 0

    def __init__(self, id0=None):
        self._type = 5
        self.color = '#CC99FF'

        if id0:
            self.id = id0
        else:
            self.id = 'u{}'.format(UserBase._ID)
            UserBase._ID += 1
