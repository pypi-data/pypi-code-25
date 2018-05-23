
class DappError(Exception):

    def __init__(self, *args, **kwargs):
        self.code = kwargs.pop('code', -1)
        self.msg = kwargs.pop('msg', "Undefined")

        json_error = kwargs.pop('json_error', None)

        if json_error is not None:
            self.code = json_error.get('rc', self.code)
            self.msg = json_error.get('msg', self.msg)

        super(DappError, self).__init__(*args, **kwargs)

    def __str__(self):
        return "Code:{}\nMessage:{}".format(self.code, self.msg)
