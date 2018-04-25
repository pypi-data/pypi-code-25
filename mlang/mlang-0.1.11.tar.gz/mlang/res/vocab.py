# coding: utf-8

import os
import re
import copy
import numpy as np
from collections import Counter
from collections import Iterable

from mlang.config import NLP_LEXICON_DIR

from mlang.utils import ClsGet
from mlang.utils import read_obj
from mlang.utils import save_obj
from mlang.utils import iter_file
from mlang.utils import write_file

from mlang.res.corpus import Corpus


class Token(object):
    """
    Token
    """
    def __init__(self, word=None, tag=None, freq=None, index=None):
        self.word = word
        self.tag = tag
        self.freq = freq
        self.index = index

    def write(self):
        return '%s %s %s' % (self.word, self.tag if self.tag else '', self.freq if self.freq is not None else '')

    def __str__(self):
        return '%s(%s, %s, %s)' % (self.word, self.tag, self.freq, self.index)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.word)

    def __eq__(self, other):
        return isinstance(other, Token) and self.word == other.word


class ScoreToken(Token):
    """
    带分值的Token
    """
    def __init__(self, score=0.0, **kwargs):
        self.score = score
        super().__init__(**kwargs)

    def __str__(self):
        return '%s(%s, %s, %s, %s)' % (self.word, self.tag, self.freq, self.index, self.score)


class Vocab(object):
    """
    词表
    """
    SYMBOL_UNK = '<UNK>'
    SYMBOL_BLANK = ' '

    def __init__(self, tokens=None, vocab_file=None, unk_blank=False):
        """
        :param tokens: token列表
        :param vocab_file: 词库文件
        :param unk_blank: 是否包含unk、blank
        :type tokens: Iterable[Token] | Iterable[str]
        :type vocab_file: str
        :type unk_blank: bool
        """
        self.unk_blank = unk_blank
        if self.unk_blank:
            self._word_dict = {
                Vocab.SYMBOL_UNK: Token(word=Vocab.SYMBOL_UNK, tag=Vocab.SYMBOL_UNK),
                Vocab.SYMBOL_BLANK: Token(word=Vocab.SYMBOL_BLANK, tag=Vocab.SYMBOL_BLANK),
            }
        else:
            self._word_dict = {}

        self._index2token = []

        if tokens:
            self._load_from_tokens(tokens)

        if vocab_file:
            self._load_from_file(vocab_file)

    def words(self):
        """
        获取所有单词
        :return: 单词集合
        :rtype: set[str]
        """
        return set([t.word for t in self])

    def tag_tokens(self, tag):
        """
        获取某个tag的所有token
        :param tag:
        :return:
        :rtype: list[Token]
        """
        return [t for t in self._word_dict.values() if t.tag == tag]

    def top_freq(self, topn=10000, reverse=False):
        """
        根据获取top词频
        :param topn:
        :param reverse:
        :return:
        :rtype: list[Token]
        """
        a = sorted(self._word_dict.values(), key=lambda t: -1 if t.freq is None else t.freq, reverse=True)
        if reverse:
            return a[-topn:][::-1]
        else:
            return a[:topn]

    def one_hot_encode(self, word):
        """
        将单词编码成one hot
        :param word:
        :return:
        :rtype: np.array
        """
        x = np.zeros((self.__len__(),))
        x[self.__getitem__(word).index] = 1
        return x

    def one_hot_decode(self, x):
        """
        将one hot编码解码成单词
        :param x:
        :return:
        :rtype: Token
        """
        return self.__getitem__(int(np.argmax(x)))

    def load_vocab(self, tokens=[], vocab_file=None):
        """
        加载词表
        :param tokens:
        :param vocab_file:
        :type tokens: Iterable[Token] | Iterable[str]
        :type vocab_file: str
        """
        if tokens:
            self._load_from_tokens(tokens)

        if vocab_file:
            self._load_from_file(vocab_file)

    def build_index(self):
        """
        构建词表索引
        """
        self._index2token = [_ for _ in sorted(self._word_dict.values(), key=lambda token: token.word, reverse=True)]
        for i, t in enumerate(self._index2token):
            t.index = i

    def write_vocab_file(self, vocab_file_path):
        """
        将词表写入到文件
        :param vocab_file_path:
        """
        lines = [t.write()+'\n' for t in self]
        if lines:
            lines[-1] = lines[-1][:-1]
        write_file(lines, vocab_file_path)

    def save(self, file_path):
        """
        保存vocab对象
        :param file_path:
        """
        save_obj(self, file_path)

    @classmethod
    def load(cls, file_path):
        """
        :param file_path:
        :return:
        :rtype: Vocab
        """
        obj = read_obj(file_path)
        assert isinstance(obj, Vocab)
        return obj

    def _load_from_tokens(self, tokens):
        """
        构建词表
        :param tokens:
        :type tokens: Iterable[Token] | Iterable[str]
        """
        for t in tokens:
            if isinstance(t, Token):
                self._word_dict[t.word] = copy.deepcopy(t)
            elif isinstance(t, str):
                self._word_dict[t] = Token(word=t)
            else:
                pass
        self.build_index()

    def _load_from_file(self, vocab_file):
        """
        构建词表，从文件中读取
        文件格式：
        token1 pos1 freq
        :param vocab_file:
        """
        for line in iter_file(vocab_file):
            splited = line.split()

            word = splited[0]
            tag = None
            freq = None

            for i in range(1, len(splited)):
                if re.match(r'\d+', splited[i]):
                    freq = int(splited[i])
                else:
                    tag = splited[i]

            self._word_dict[word] = Token(word=word, tag=tag, freq=freq)

        self.build_index()

    def __contains__(self, word):
        return word in self._word_dict

    def __getitem__(self, wordOrIndex):
        # 未知的词返回UNK
        if self.unk_blank:
            unk = self._word_dict[self.SYMBOL_UNK]
        else:
            unk = None

        if isinstance(wordOrIndex, str):
            return self._word_dict.get(wordOrIndex, unk)
        elif isinstance(wordOrIndex, int):
            if wordOrIndex > self.__len__()-1 or wordOrIndex < 0:
                return unk
            return self._index2token[wordOrIndex]
        else:
            raise Exception()

    def __len__(self):
        return len(self._index2token)

    def __iter__(self):
        for t in self._index2token:
            yield t


class DefaultVocab(Vocab, ClsGet):
    """
    小型词典
    """
    VOCAB_FILE = os.path.join(NLP_LEXICON_DIR, '现代汉语常用词表.txt')

    def __init__(self):
        dict_file = os.path.join(self.VOCAB_FILE)
        super().__init__(vocab_file=dict_file, unk_blank=True)


class DefaultSentimentVocab(Vocab, ClsGet):
    """
    情感词库
    """
    TAG_NEGATIVE = 'negative'
    TAG_POSITIVE = 'positive'

    POSITIVE_FILE = os.path.join(NLP_LEXICON_DIR, 'positive.txt')
    NEGATIVE_FILE = os.path.join(NLP_LEXICON_DIR, 'negative.txt')

    def __init__(self):
        negatives = []
        for line in iter_file(self.NEGATIVE_FILE):
            negatives.append(ScoreToken(word=line.strip(), tag=self.TAG_NEGATIVE, score=1.0))

        positives = []
        for line in iter_file(self.POSITIVE_FILE):
            positives.append(ScoreToken(word=line.strip(), tag=self.TAG_POSITIVE, score=-1.0))

        super().__init__(tokens=negatives+positives)

    def is_positive(self, word):
        return self.__contains__(word) and self.__getitem__(word).tag == self.TAG_POSITIVE

    def is_negative(self, word):
        return self.__contains__(word) and self.__getitem__(word).tag == self.TAG_NEGATIVE

    def positives(self):
        return set([t.word for t in self if t.tag == self.TAG_POSITIVE])

    def negatives(self):
        return set([t.word for t in self if t.tag == self.TAG_NEGATIVE])


class DefaultDegreeVocab(Vocab, ClsGet):
    """
    程度词库
    """
    TAG = 'degree'

    VOCAB_FILE = os.path.join(NLP_LEXICON_DIR, 'degree.txt')

    def __init__(self):
        tokens = []
        for line in iter_file(self.VOCAB_FILE):
            if line.startswith('---'):
                s = float(re.findall(r'\[(.*)\]', line)[0])
            else:
                tokens.append(ScoreToken(word=line, tag=self.TAG, score=s))
        super().__init__(tokens=tokens)


class DefaultNegatorVocab(Vocab, ClsGet):
    """
    否定词库
    """
    TAG = 'negator'

    VOCAB_FILE = os.path.join(NLP_LEXICON_DIR, 'negator.txt')

    def __init__(self):
        super().__init__(vocab_file=self.VOCAB_FILE)


class DefaultStopWordVocab(Vocab, ClsGet):
    """
    停用词库
    """
    TAG = 'stop'

    VOCAB_FILE = os.path.join(NLP_LEXICON_DIR, 'stop.txt')

    def __init__(self):
        super().__init__(vocab_file=self.VOCAB_FILE)


class VocabBuilder(object):
    """
    Vocab构建工具类
    读取纯文本，切词，构建词表
    """

    def __init__(self, tokenizer=None, extractor=None, topn=3000, min_freq=5, **kwargs):
        """
        tokenizer/extractor必须指定其中一个
        :param tokenizer: 分词器
        :param extractor: 抽词器
        :param topn:  取topn
        :param min_freq:  最小词频
        :type tokenizer: function
        :type extractor: function
        :type topn: int
        :type min_freq: int
        """
        self.extractor = extractor
        self.tokenizer = tokenizer
        self.topn = topn
        self.min_freq = min_freq
        self.kwargs = kwargs

    def build(self, corpus):
        """
        构建方法
        :param corpus: 文本列表
        :type corpus: Corpus
        """
        if self.tokenizer:
            return self._tokenize_build(corpus)
        elif self.extractor:
            return self._extract_build(corpus)
        else:
            raise Exception('miss tokenizer and extractor')

    def _extract_build(self, corpus):
        tokens = [(t[0], t[1]) for t in self.extractor(corpus, min_count=self.min_freq, **self.kwargs)]
        tokens = sorted(tokens, key=lambda t: t[1], reverse=True)
        tokens = tokens[:self.topn]
        tokens = [Token(word=t[0], freq=t[1]) for t in tokens]
        return Vocab(tokens=tokens)

    def _tokenize_build(self, corpus):
        counter = Counter()
        for doc in corpus:
            tokens = [t.word for t in self.tokenizer(doc)]
            counter.update(tokens)

        tokens = []
        for t, c in counter.most_common():
            if c < self.min_freq:
                continue
            tokens.append(t)

        tokens = tokens[:self.topn]
        tokens = [Token(word=t, freq=counter.get(t)) for t in tokens]
        return Vocab(tokens=tokens)
