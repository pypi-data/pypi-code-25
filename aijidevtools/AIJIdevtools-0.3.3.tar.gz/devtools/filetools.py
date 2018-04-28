import re


class FileWrapper:
    """Wrapper to convert file-like objects to iterables"""

    def __init__(self, filelike, blksize=8192):
        self.filelike = filelike
        self.blksize = blksize
        if hasattr(filelike,'close'):
            self.close = filelike.close

    def __getitem__(self,key):
        data = self.filelike.read(self.blksize)
        if data:
            return data
        raise IndexError

    def __iter__(self):
        return self

    def __next__(self):
        data = self.filelike.read(self.blksize)
        if data:
            return data
        raise StopIteration

def csvtodict(f, sep):
    res = {}
    for l in f.readlines():
        l = re.split(sep, l.strip())
        addr = ()

        foo = l[0].strip()
        if ':' in foo:
            ip, port = foo.split(':') 
            addr = (ip, int(port))
        else:
            addr = (foo, 8080)
        res[addr] = tuple(l[1:])
    return res

if __name__ == '__main__':
    res = {}
    with open('test.txt', 'r') as f:
        res.update(csvtodict(f, '[,，]'))
    print(res)

