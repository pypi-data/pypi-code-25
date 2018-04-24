class BasicTransformer:
    def __init__(self):
        raise NotImplementedError

    @staticmethod
    def transform():
        raise NotImplementedError


class CompositeTransformer:
    def __init__(self, childTransformer=None):
        self.childTransformer = childTransformer

    def transform():
        raise NotImplementedError


class ListTransformer(BasicTransformer):
    def __init__(self):
        super(ListTransformer, self).__init__()

    @staticmethod
    def transform(string):
        return string.splitlines()


class FileReadTransformer(CompositeTransformer):
    def __init__(self, childTransformer=None):
        super(FileReadTransformer, self).__init__(childTransformer)

    def transform(self, file_path):
        with open(file_path) as inFile:
            string = inFile.read()
            if self.childTransformer is not None:
                return self.childTransformer.transform(string)
            else:
                return inFile.read()
