class DefaultList(list):

    def __init__(self, default=None):
        self.default = default
        super().__init__()

    def __getitem__(self, index):
        try:
            return super().__getitem__(index)
        except IndexError:
            return self.default
