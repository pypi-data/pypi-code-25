import re
import MeCab


def load_message(path):
    with open(path, 'rt') as f:
        lines = f.readlines()
    lines = [line for line in lines if len(line) > 10]
    return lines


class Parser:
    def __init__(self):
        pattern = r'[\n 　]'
        self.compiled = re.compile(pattern)
        self.mecab = MeCab.Tagger('-Owakati -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')

    def clean(self, sent):
        clean_sent = self.compiled.sub('', sent)
        return clean_sent

    def parse(self, sent):
        separated = self.mecab.parse(sent)
        separated = separated.strip('\n')
        tokens = separated.split(' ')
        tokens = [token for token in tokens if token]
        return tokens


