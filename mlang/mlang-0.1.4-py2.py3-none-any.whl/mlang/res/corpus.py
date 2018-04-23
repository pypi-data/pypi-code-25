# coding: utf-8

from mlang.utils import iter_file


'''
解析文本的几种方法
'''


def default_record_reader(line, **kwargs):
    if isinstance(line, str):
        return line.strip()
    else:
        return line


def split_record_reader(line, **kwargs):
    return line.strip().split()


class Corpus(object):
    """
    语料
    """
    def __init__(self, data, record_reader=default_record_reader, flat=False):
        self.record_reader = record_reader
        self.data = data
        self.flat = flat

    def __iter__(self):
        for i, d in enumerate(self.data):
            r = self.record_reader(d, index=i)
            if r is not None:
                if self.flat:
                    for x in r:
                        yield x
                else:
                    yield r

    def __len__(self):
        c = 0
        for _ in self.__iter__():
            c += 1
        return c


class ArrayCorpus(Corpus):
    """
    List语料
    """
    def __init__(self, txts, record_reader=default_record_reader):
        """
        :param txts: 文本列表
        :type txts: List[str]
        :param record_reader: 读取/解析文本方法
        :type record_reader: function
        """
        super().__init__(txts, record_reader=record_reader)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        """
        :param index:
        :type index: int
        """
        assert isinstance(index, int)
        return self.record_reader(self.data[index])


class FileCorpus(Corpus):
    """
    文本语料
    """
    def __init__(self, file_path, record_reader=default_record_reader, max_lines=None):
        """
        :param file_path: 文本文件路径
        :param record_reader: 行解析方法
        :param max_lines: 行数
        :type file_path: str
        :type record_reader: function
        :type max_lines: int
        """
        super().__init__(file_path, record_reader)
        self.max_lines = max_lines

    def __iter__(self):
        c = 0
        for line in iter_file(self.data):
            if self.max_lines and c > self.max_lines:
                break

            d = self.record_reader(line)
            if d is not None:
                c += 1
                yield d
