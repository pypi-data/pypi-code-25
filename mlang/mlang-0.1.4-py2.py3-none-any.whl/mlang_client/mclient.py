# coding: utf-8

import os
import time
import logging
import requests

import progressbar

from requests_toolbelt.multipart.encoder import MultipartEncoder
from requests_toolbelt.multipart.encoder import MultipartEncoderMonitor

from mlang.config import DEFAULT_LM

from mlang.config import DEFAULT_D2V
from mlang.config import DEFAULT_W2V

from mlang.config import DEFAULT_VOCAB
from mlang.config import DEFAULT_VOCAB_SENTIMENT

from mlang.res.vocab import Vocab

SERVER_URL = 'http://127.0.0.1:5001'
VERSION = 'v1.0'

logger = logging.getLogger(__name__)


class MLang(object):
    """
    NLP基础功能
    """

    @classmethod
    def ssplit(cls, txt, impl='re', pattern='[\s,，.。:：!！?？、]'):
        """
        拆分子句
        :param txt: 文本
        :type txt: str
        :param impl: 实现算法 re/ltp
        :type impl: str
        :param pattern: 如果impl='re'，则可以通过这个参数配置拆分符
        :type pattern: str
        :return: 子句列表
        :rtype: list[str]
        """
        return call_post(furl('nlp/ssplit'), locals()).json()

    @classmethod
    def tokenize(cls, txt, impl='ltp', vocabid=DEFAULT_VOCAB, max_len=4, update_cache=False):
        """
        分词
        :param txt: 文本
        :type txt: str
        :param impl: 实现算法，ltp/jieba/fmm/rmm
        :type impl: str
        :param vocabid: 词表id，impl='fmm'/'rmm'时，通过这个参数配置词表
        :type vocabid: str
        :param max_len: 词的最大长度
        :type max_len: int
        :param update_cache: 是否更新缓存
        :type update_cache: bool
        :return: 单词列表
        :rtype: list[dict]
        """
        return call_post(furl('nlp/tokenize'), locals()).json()

    @classmethod
    def pos(cls, txt, impl='ltp', revise=False, norm=False):
        """
        词性标注
        :param txt: 文本
        :type txt: str
        :param impl: 实现算法，ltp/jieba
        :type impl: str
        :param revise: 是否进行词性修正，将标注错误的词性进行修正
        :type revise: bool
        :param norm: 是否将词性统一成ltp的词性集，imp!='ltp'生效
        :type norm: bool
        :return: 单词列表
        :rtype: list[dict]
        """
        return call_post(furl('nlp/pos'), locals()).json()

    @classmethod
    def ner(cls, txt, impl='ltp'):
        """
        命名实体识别
        并不好用，可以直接使用ltp进行分词，根据词性做识别
        :param txt: 文本
        :type txt: str
        :param impl: 实现算法，目前只有ltp
        :type impl: str
        :return:
        :rtype: list[dict]
        """
        return call_post(furl('nlp/ner'), locals()).json()

    @classmethod
    def parse(cls, txt, impl='ltp'):
        """
        依存句法解析
        :param txt: 文本
        :type txt: str
        :param impl: 实现算法，目前只有ltp
        :type impl: str
        :return: 单词关系列表
        :rtype: list[dict]
        """
        return call_post(furl('nlp/parse'), locals()).json()

    @classmethod
    def pinyin2hanzi(cls, txt, impl='Pinyin2Hanzi'):
        """
        拼音串转成汉子串
        :param txt: 拼音文本，空格分隔，mei zu shou ji bu cuo de
        :type txt: str
        :param impl: 实现算法，目前只有Pinyin2Hanzi
        :type impl: str
        :return: 汉字列表
        :rtype: list[str]
        """
        return call_post(furl('nlp/p2h'), locals()).json()

    @classmethod
    def hanzi2pinyin(cls, txt, impl='Pinyin2Hanzi'):
        """
        汉字串转成拼音串
        :param txt: 汉字文本
        :type txt: str
        :param impl: 实现算法，目前只有Pinyin2Hanzi
        :type impl: str
        :return: 拼音列表
        :rtype: list[str]
        """
        return call_post(furl('nlp/h2p'), locals()).json()

    @classmethod
    def simplified2traditional(cls, txt, impl='zhconv'):
        """
        简体字转换成繁体字
        :param txt: 文本
        :type txt: str
        :param impl: 实现算法，目前只有zhconv
        :type impl: str
        :return:
        :rtype: str
        """
        return call_post(furl('nlp/s2t'), locals()).json()

    @classmethod
    def traditional2simplified(cls, txt, impl='zhconv'):
        """
        繁体字转换成简体字
        :param txt: 文本
        :type txt: str
        :param impl: 实现算法，目前只有zhconv
        :type impl: str
        :return:
        :rtype: str
        """
        return call_post(furl('nlp/t2s'), locals()).json()


class MCorpus(object):
    """
    语料管理
    """

    @classmethod
    def list(cls):
        """
        获取服务器上所有语料的文件信息
        :return: list[dict]
        """
        return call_get(furl('corpus_list'), {}).json()

    @classmethod
    def info(cls, corpusid):
        """
        获取服务器上指定语料的文件信息
        :param corpusid:
        :type corpusid: str
        :return: 语料文件信息
        :rtype: dict
        """
        return call_get(furl('corpus_info/%s' % corpusid), {}).json()

    @classmethod
    def upload(cls, corpusid, file_path, action='overwrite'):
        """
        将本地语料文件上传到服务器
        :param corpusid: 指定给这个语料文件的id
        :param file_path: 本地语料文件路径
        :param action: overwrite/append，如果服务器上已经存在这个语料，做重写/追加操作
        """
        url = furl('corpus/%s' % corpusid)
        response = upload_file(url, file_path, 'corpus', {'action': action})
        return response.json()

    @classmethod
    def download(cls, corpusid, file_path):
        """
        从服务器上下载指定语料文件
        :param corpusid: 服务器上的语料的id
        :param file_path: 本地保存路径
        """
        url = furl('corpus/%s' % corpusid)
        download_file(url, file_path)

    @classmethod
    def remove(cls, corpusid):
        """
        从服务器上删除指定语料
        :param corpusid: 语料id
        """
        call_delete(furl('corpus/%s' % corpusid), {})


class MVocab(object):
    """
    词表管理
    """

    @classmethod
    def list(cls):
        """
        获取服务器上所有词表的信息
        :return:
        :rtype: list[dict]
        """
        return call_get(furl('vocab_list'), {}).json()

    @classmethod
    def info(cls, vocabid):
        """
        获取服务器上指定词表的信息
        :param vocabid:
        :rtype: dict
        """
        return call_get(furl('vocab_info/%s' % vocabid), {}).json()

    @classmethod
    def upload(cls, vocabid, file_path, action='overwrite'):
        """
        上传本地词表文件到服务器
        :param vocabid: 词表id
        :param file_path: 本地词表文件
        :param action: overwrite/append，如果服务器上已经存在这个语料，做重写/追加操作
        :return:
        """
        url = furl('vocab/upload/%s' % vocabid)
        response = upload_file(url, file_path, 'vocab', {'action': action})
        return response.json()

    @classmethod
    def remove(cls, vocabid):
        """
        从服务器上删除指定词表
        :param vocabid: 词表id
        """
        call_delete(furl('vocab/%s' % vocabid), {})

    @classmethod
    def download(cls, vocabid, file_path):
        """
        从服务器上下载词表文件
        :param vocabid: 服务器上的词表的id
        :param file_path: 本地保存路径
        """
        url = furl('vocab/%s' % vocabid)
        download_file(url, file_path)

    @classmethod
    def build(cls, vocabid, corpusid, impl='ltp', topn=5000, min_freq=5):
        """
        使用服务器上的语料构建词表
        :param vocabid: 词表id，保存在服务器上
        :param corpusid: 服务器上语料的id
        :param impl: 实现算法，ltp/jieba/full/fast
        :param topn: 取topn个词
        :param min_freq: 最小词频
        """
        logger.info('build vocab...')
        response = call_post(furl('vocab/%s' % vocabid), {
            'corpusid': corpusid,
            'impl': impl,
            'topn': topn,
            'min_freq': min_freq
        })

        if response.status_code != 200:
            raise Exception(response.text)

    @classmethod
    def get(cls, vocabid):
        """
        从服务器上获取词表对象
        :param vocabid: 词表id
        :type vocabid: str
        :return: 词表对象
        :rtype: Vocab
        """
        vocab_file = '%s.%s.txt' % (vocabid, int(time.time()))
        logger.info('get vocab file [%s].' % vocab_file)
        MVocab.download(vocabid, vocab_file)

        logger.info('build vocab from file [%s].' % vocab_file)
        vocab = Vocab()
        vocab.load_vocab(vocab_file=vocab_file)
        return vocab


class MRepresentation(object):
    """
    表征
    """

    @classmethod
    def represent(cls, obj, impl, **kwargs):
        pass

    @classmethod
    def similarity(cls, obj1, obj2, impl):
        pass


class MWordRepresentation(MRepresentation):
    """
    单词表征
    """

    @classmethod
    def represent(cls, word, impl='w2v', update_cache=False, vocabid=DEFAULT_VOCAB, w2vid=DEFAULT_W2V):
        """
        :param word: 单词
        :param impl: 表征算法，onehot/w2v
        :param update_cache: 是否更新缓存
        :param w2vid: word2vec模型id，impl='w2v'时生效
        :param vocabid: 词表id，impl='onehot'时生效
        :return: 词向量
        :rtype: list[float]
        """
        if impl == 'onehot':
            url = furl('rep/word/onehot')
            return call_get(url, {'word': word, 'vocabid': vocabid, 'update_cache': update_cache}).json()
        elif impl == 'w2v':
            url = furl('rep/word/w2v')
            return call_get(url, {'word': word, 'w2vid': w2vid, 'update_cache': update_cache}).json()
        else:
            raise Exception('[impl] value is invalid. [onehot/w2v]')

    @classmethod
    def similarity(cls, word1, word2, impl='w2v', w2vid=DEFAULT_W2V, update_cache=False):
        """
        :param word1:
        :param word2:
        :param impl: 单词表征的方式，用于计算相似度的表征只有w2v
        :param w2vid: word2vec模型id
        :param update_cache: 是否更新缓存
        :return 夹角余弦相似度
        :rtype: float
        """
        if impl == 'w2v':
            url = furl('rep/word/sim')
            return call_get(url, {'word1': word1, 'word2': word2, 'w2vid': w2vid, 'update_cache': update_cache}).json()
        else:
            raise Exception('[impl] value is invalid. [w2v]')


class MTextRepresentation(MRepresentation):
    """
    文本表征
    """

    @classmethod
    def represent(cls, txt, impl='w2v', d2vid=DEFAULT_D2V, w2vid=DEFAULT_W2V, vocabid=DEFAULT_VOCAB, update_cache=False,
                  tokenize='ltp', max_len=4):
        """
        :param txt: 单词
        :param impl: 表征算法，vocab/d2v/w2v
        :param update_cache: 是否更新缓存
        :param d2vid: doc2vec模型id，impl='d2v'时生效
        :param w2vid: word2vec模型id, impl='w2v'时生效
        :param vocabid: 词表id，impl='vocab'时生效
        :param tokenize:
        :param max_len:
        :return: 词向量
        :rtype: list[float]
        """
        if impl == 'vocab':
            url = furl('rep/text/vocab')
            return call_post(url, {'txt': txt, 'vocabid': vocabid, 'update_cache': update_cache}).json()
        elif impl == 'd2v':
            url = furl('rep/text/d2v')
            return call_post(url, {'txt': txt, 'd2vid': d2vid, 'tokenize': tokenize, 'vocabid': vocabid,
                                   'max_len': max_len, 'update_cache': update_cache}).json()
        elif impl == 'w2v':
            url = furl('rep/text/w2v')
            return call_post(url, {'txt': txt, 'w2vid': w2vid, 'tokenize': tokenize, 'vocabid': vocabid,
                                   'max_len': max_len, 'update_cache': update_cache}).json()
        else:
            raise Exception('[impl] value is invalid. [d2v/vocab]')

    @classmethod
    def similarity(cls, txt1, txt2, impl='w2v', d2vid=DEFAULT_D2V, w2vid=DEFAULT_W2V, vocabid=DEFAULT_VOCAB,
                   update_cache=False, tokenize='ltp', max_len=4):
        """
        :param txt1:
        :param txt2:
        :param impl: 文本的表征方式，d2v/w2v/vocab
        :param d2vid: doc2vec模型id
        :param w2vid: word2vec模型id
        :param vocabid: 词表id
        :param update_cache: 是否更新缓存
        :param tokenize: 对文本分词的方法，ltp/jieba/fmm/rmm，使用fmm/rmm时，最好配置vocabid
        :param max_len: 最大词长
        :return 夹角余弦相似度
        :rtype: float
        """
        if impl == 'vocab':
            url = furl('rep/text/sim/vocab')
            return call_post(url, {'txt1': txt1, 'txt2': txt2, 'vocabid': vocabid, 'update_cache': update_cache}).json()
        elif impl == 'w2v':
            url = furl('rep/text/sim/w2v')
            return call_post(url, {'txt1': txt1, 'txt2': txt2, 'w2vid': w2vid, 'tokenize': tokenize, 'vocabid': vocabid,
                                   'max_len': max_len, 'update_cache': update_cache}).json()
        elif impl == 'd2v':
            url = furl('rep/text/sim/d2v')
            return call_post(url, {'txt1': txt1, 'txt2': txt2, 'd2vid': d2vid, 'tokenize': tokenize, 'vocabid': vocabid,
                                   'max_len': max_len, 'update_cache': update_cache}).json()
        else:
            raise Exception('[impl] value is invalid. [d2v/vocab]')


class MCluster(object):
    """
    聚类
    """

    @classmethod
    def fit(cls, data, corpus, represent):
        pass


class MWordCluster(MCluster):
    """
    单词聚类
    """

    @classmethod
    def fit(cls, vocabid, n_clusters=None, represent='w2v', w2vid=DEFAULT_W2V, update_cache=False):
        """
        对服务器上的词表里的词进行聚类，需要指定一种单词的表征方式，这里只能使用word2vec模型
        :param vocabid: 需要聚类的词表
        :param n_clusters: 类簇个数，可以不指定，如果指定了则使用kmean算法，否则使用AP算法
        :param represent: 单词的表征方式，这里只能使用w2v
        :param w2vid: word2vec模型id
        :param update_cache: 是否更新缓存
        :return:
        """
        if represent != 'w2v':
            raise Exception('param [represent] is invalid.')

        url = furl('cluster/word')
        params = {
            'vocabid': vocabid,
            'w2vid': w2vid,
            'update_cache': update_cache
        }

        if n_clusters is not None:
            params['n_clusters'] = int(n_clusters)

        return call_post(url, params).json()


class MTextCluster(MCluster):
    """
    文本聚类
    """

    @classmethod
    def fit(cls, corpusid, n_clusters=None, represent='w2v', d2vid=DEFAULT_D2V, w2vid=DEFAULT_W2V,
            vocabid=DEFAULT_VOCAB, update_cache=False,
            tokenize='ltp', max_len=4):
        """
        :param corpusid: 语料id
        :param n_clusters: 类簇个数；如果指定了，使用kmean聚类，否则使用AP聚类
        :param represent: 表征算法，vocab/d2v/w2v
        :param update_cache: 是否更新缓存
        :param d2vid: doc2vec模型id，represent='d2v'时生效
        :param w2vid: word2vec模型id, represent='w2v'时生效
        :param vocabid: 词表id，用于分词算法
        :param tokenize: 分词方式，ltp/jieba/fmm/rmm
        :param max_len:
        :return: 词向量
        :rtype: list[float]
        """
        params = {'update_cache': update_cache}

        if n_clusters is not None:
            params['n_clusters'] = int(n_clusters)

        if represent == 'vocab':
            url = furl('cluster/text/vocab')
            params.update({'corpusid': corpusid, 'vocabid': vocabid})
            return call_post(url, params).json()

        elif represent == 'd2v':
            url = furl('cluster/text/d2v')
            params.update({
                'corpusid': corpusid,
                'd2vid': d2vid,
                'tokenize': tokenize,
                'vocabid': vocabid,
                'max_len': max_len
            })
            return call_post(url, params).json()

        elif represent == 'w2v':
            url = furl('cluster/text/w2v')
            params.update({
                'corpusid': corpusid,
                'w2vid': w2vid,
                'tokenize': tokenize,
                'vocabid': vocabid,
                'max_len': max_len
            })
            return call_post(url, params).json()
        else:
            raise Exception('[represent] value is invalid. [d2v/w2v/vocab]')


class MSentimentAnalyser(object):
    """
    情感分析
    """

    @classmethod
    def score(cls, txt, positive_vocabid=DEFAULT_VOCAB_SENTIMENT, negative_vocabid=DEFAULT_VOCAB_SENTIMENT, update_cache=False):
        """
        计算文本的情感分值
        :param txt: 文本
        :param positive_vocabid: 正面情感词词库
        :param negative_vocabid: 负面情感词词库
        :param update_cache: 是否更新缓存
        :return:
        """
        url = furl('sa/score')
        return call_post(url, locals()).json()

    @classmethod
    def is_subject(cls, txt, positive_vocabid=DEFAULT_VOCAB_SENTIMENT, negative_vocabid=DEFAULT_VOCAB_SENTIMENT, update_cache=False):
        """
        判断文本是否是主观的
        :param txt: 文本
        :param positive_vocabid: 正面情感词词库
        :param negative_vocabid: 负面情感词词库
        :param update_cache: 是否更新缓存
        :return:
        """
        url = furl('sa/subjective')
        return call_post(url, locals()).json()

    @classmethod
    def extract_terms(cls, corpusid, s_seed=None, top_n=3000):
        """
        从语料中提取评价对象次/评价词
        :param corpusid: 语料id
        :param s_seed: 评价种子词
        :param top_n:
        """
        if s_seed is None:
            s_seed = ['漂亮', '不错', '差劲', '很好']

        url = furl('sa/terms')
        return call_post(url, locals()).json()

    @classmethod
    def extract_opinions(cls, txt, target_vocabid, sentiment_vocabid=DEFAULT_VOCAB_SENTIMENT, positive_vocabid=None, negative_vocabid=None, update_cache=False):
        """
        从文本中提取评价观点
        :param txt: 文本
        :param target_vocabid: 评价对象词表 id
        :param sentiment_vocabid: 情感词词表id，默认使用通用情感词
        :param positive_vocabid: 正面情感词词表id，用来配置特殊的情感词
        :param negative_vocabid: 负面情感词词表id，用来配置特殊的情感词
        :param update_cache: 是否更新缓存
        :return:
        """
        url = furl('sa/opinions')
        return call_post(url, locals()).json()


class MLM(object):
    """
    语言模型
    """

    @classmethod
    def list(cls):
        """
        列出服务器上所有的lm模型
        :return:
        :rtype: list[dict]
        """
        return call_get(furl('lm_list'), {}).json()

    @classmethod
    def info(cls, lmid):
        """
        获取指定lmid的信息
        :param lmid:
        :return:
        :rtype: dict
        """
        return call_get(furl('lm_info/%s' % lmid), {}).json()

    @classmethod
    def prob(cls, txt, lmid=DEFAULT_LM, tokenize=None, vocabid=DEFAULT_VOCAB, max_len=4, update_cache=False):
        """
        计算一段文本的概率
        :param txt: 文本，一句话
        :param lmid: 语言模型id
        :param tokenize: 分词方法，None/ltp/jieba/fmm/rmm，需要跟语言模型的分词方法一致
        :param vocabid: 分词用的词表id
        :param max_len: 最大词长
        :param update_cache: 是否更新缓存
        :return: 概率
        :rtype: float
        """
        return call_post(furl('lm/prob'), locals()).json()

    @classmethod
    def build(cls, lmid, corpusid, order=3, tokenize=None, vocabid=DEFAULT_VOCAB, max_len=4, update_cache=False):
        """
        训练语言模型
        :param lmid: 语言模型id
        :param corpusid: 训练用的语料id
        :param order: n-gram阶数
        :param tokenize: 分词方法，默认是None，一个字一个词。None/jieba/ltp/fmm/rmm
        :param vocabid: 分词用到的词表id
        :param max_len: 最大词长
        :param update_cache: 是否更新缓存
        :return:
        """
        return call_post(furl('lm/%s' % lmid), {
            'corpusid': corpusid,
            'order': order,
            'tokenize': tokenize,
            'vocabid': vocabid,
            'max_len': max_len,
            'update_cache': update_cache
        }).json()

    @classmethod
    def download(cls, lmid, file_path):
        """
        下载语言模型文件
        :param lmid: 语言模型id
        :param file_path: 本地存储路径
        """
        url = furl('lm/%s' % lmid)
        download_file(url, file_path)

    @classmethod
    def remove(cls, lmid):
        return call_delete(furl('lm/%s' % lmid), {}).json()


class MWord2Vec(object):
    """
    word2vec模型
    """
    @classmethod
    def list(cls):
        """
        列出服务器上所有训练好的word2vec模型信息
        :return:
        """
        return call_get(furl('w2v/list'), {}).json()

    @classmethod
    def info(cls, w2vid):
        """
        获取指定word2vec模型信息
        :param w2vid:
        :return:
        """
        return call_get(furl('w2v/info/%s' % w2vid), {}).json()

    @classmethod
    def build(cls, w2vid, corpusid,
              tokenize='ltp', vocabid=DEFAULT_VOCAB, max_len=4,
              update_cache=False,
              size=100, epochs=5, window=5, alpha=0.025, min_count=5, max_vocab_size=None, workers=None,
              sg=0, hs=0, negative=5, cbow_mean=1, compute_loss=False):
        """
        构建word2vec模型
        :param w2vid: 模型id
        :param corpusid: 使用到的服务器上的语料
        :param tokenize: 分词方式, ltp/jieba/fmm/rmm
        :param vocabid: 分词用的词库
        :param max_len: 最大词长
        :param update_cache: 是否更新缓存
        :param size: word2vec模型训练参数，向量维度
        :param epochs: word2vec模型训练参数，语料迭代次数
        :param window: word2vec模型训练参数，上下文窗口
        :param alpha: word2vec模型训练参数，学习率
        :param min_count: word2vec模型训练参数，最小词频，少于的被抛弃
        :param max_vocab_size: word2vec模型训练参数，限制词数，控制内存
        :param workers: word2vec模型训练参数，训练用的线程数量
        :param sg: word2vec模型训练参数，选择训练算法，1：skip-gram，0：CBOW:
        :param hs: word2vec模型训练参数，1/0，1：hierarchical softmax，0 and negative：negative sampling
        :param negative: word2vec模型训练参数，负采样值
        :param cbow_mean: word2vec模型训练参数，择了cbow算法时，0：sum上下文向量，1：mean上下文向量
        :param compute_loss: word2vec模型训练参数，是否计算损失 model.get_latest_training_loss()
        :return:
        """
        return call_post(furl('w2v/%s' % w2vid), locals()).json()

    @classmethod
    def download(cls, w2vid, file_path):
        """
        下载服务器上训练好的模型文件到本地
        :param w2vid: 服务器上的模型id
        :param file_path: 本地保存路径
        """
        download_file(furl('w2v/%s' % w2vid), file_path)

    @classmethod
    def remove(cls, w2vid):
        """
        删除模型
        :param w2vid:
        """
        call_delete(furl('w2v/%s' % w2vid), locals()).json()


class MDoc2Vec(object):
    """
    doc2vec模型
    """
    @classmethod
    def list(cls):
        """
        列出服务器上所有训练好的doc2vec模型信息
        :return:
        """
        return call_get(furl('d2v/list'), {}).json()

    @classmethod
    def info(cls, d2vid):
        """
        获取指定doc2vec模型信息
        :param d2vid:
        :return:
        """
        return call_get(furl('d2v/info/%s' % d2vid), {}).json()

    @classmethod
    def build(cls, d2vid, corpusid,
              tokenize='ltp', vocabid=DEFAULT_VOCAB, max_len=4,
              update_cache=False,
              size=100, dm=1, dm_mean=1, epochs=5, window=5, alpha=0.025, min_count=5, max_vocab_size=None, workers=None,
              hs=0, negative=5, compute_loss=False):
        """
        构建doc2vec模型
        :param d2vid: 模型id
        :param corpusid: 使用到的服务器上的语料
        :param tokenize: 分词方式, ltp/jieba/fmm/rmm
        :param vocabid: 分词用的词库
        :param max_len: 最大词长
        :param update_cache: 是否更新缓存
        :param size: doc2vec模型训练参数，向量维度
        :param dm: doc2vec模型训练参数，选择训练算法. dm=1:'distributed memory' (PV-DM). dm=0: `distributed bag of words` (PV-DBOW)
        :param dm_mean: doc2vec模型训练参数，0：sum上下文向量，1：mean上下文向量
        :param epochs: doc2vec模型训练参数，语料迭代次数
        :param window: doc2vec模型训练参数，上下文窗口
        :param alpha: doc2vec模型训练参数，学习率
        :param min_count: doc2vec模型训练参数，最小词频，少于的被抛弃
        :param max_vocab_size: doc2vec模型训练参数，限制词数，控制内存
        :param workers: doc2vec模型训练参数，训练用的线程数量
        :param hs: doc2vec模型训练参数，1/0，1：hierarchical softmax，0 and negative：negative sampling
        :param negative: doc2vec模型训练参数，负采样值
        :param compute_loss: doc2vec模型训练参数，是否计算损失 model.get_latest_training_loss()
        :return:
        """
        return call_post(furl('d2v/%s' % d2vid), locals()).json()

    @classmethod
    def download(cls, d2vid, file_path):
        """
        下载服务器上训练好的模型文件到本地
        :param d2vid: 服务器上的模型id
        :param file_path: 本地保存路径
        """
        download_file(furl('d2v/%s' % d2vid), file_path)

    @classmethod
    def remove(cls, d2vid):
        """
        删除模型
        :param d2vid: 
        """
        call_delete(furl('d2v/%s' % d2vid), {'d2vid': d2vid}).json()


class MSeq2Seq(object):
    """
    sequence 2 sequence 模型
    """
    @classmethod
    def list(cls):
        return call_get(furl('s2s_list'), {}).json()

    @classmethod
    def info(cls, s2sid):
        return call_get(furl('s2s_info/%s' % s2sid), {}).json()

    @classmethod
    def download(cls, s2sid, file_path):
        return download_file(furl('s2s/%s' % s2sid), file_path)

    @classmethod
    def build(cls, s2sid, corpusid, epochs=10, batch_size=128, min_freq=5, max_length=50, hidden_size=128, layers=3):
        call_post(furl('s2s/%s' % s2sid), locals())

    @classmethod
    def predict(cls, s2sid, raw_seq, update_cache=False):
        return call_post(furl('s2s/predict'), {'s2sid': s2sid, 'seqs': raw_seq, 'update_cache': update_cache}).json()

    @classmethod
    def remove(cls, s2sid):
        return call_delete(furl('s2s/%s' % s2sid), {}).json()


def furl(uri):
    return '%s/api/%s/%s' % (SERVER_URL, VERSION, uri)


def call_post(url, data):
    logger.debug('request [POST] [%s]' % url)
    logger.debug('request params: %s' % data)
    return requests.post(url, data=data)


def call_get(url, params):
    logger.debug('request [GET] [%s]' % url)
    logger.debug('request params: %s' % params)
    return requests.get(url, params=params)


def call_delete(url, data):
    logger.debug('request [DELETE] [%s]' % url)
    logger.debug('request params: %s' % data)
    return requests.delete(url, params=data)


def upload_file(url, file_path, file_field_name, other_params=None):
    """
    上传本地文件到指定url
    :param url:
    :param file_path: 本地文件路径，将要上传的文件
    :param file_field_name: 文件字段名
    :param other_params: 除了文件字段外的其他参数
    :type other_params: dict
    :return: requests.Response
    """
    file_name = os.path.basename(file_path)

    if other_params is None:
        other_params = {}

    params = other_params
    with open(file_path, 'rb') as f:
        params.update({file_field_name: (file_name, f, 'text/plain')})

        encoder = MultipartEncoder(fields=params)

        bar = progressbar.ProgressBar(widgets=[
            'Test: ', progressbar.Percentage(),
            ' ', progressbar.Bar(marker=progressbar.RotatingMarker()),
            ' ', progressbar.ETA(),
            ' ', progressbar.FileTransferSpeed(),
        ], max_value=encoder.len).start()

        def callback(monitor_):
            bar.update(monitor_.bytes_read)

        logger.debug('request [POST] [%s]' % url)

        monitor = MultipartEncoderMonitor(encoder, callback)
        response = requests.post(url, data=monitor, headers={'Content-Type': monitor.content_type})
    bar.finish()
    return response


def download_file(url, file_path):
    """
    下载文件到本地
    :param url: 请求地址
    :param file_path: 本地保存路径
    """
    logger.debug('request [GET] [%s]' % url)

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
            f.flush()
    else:
        raise Exception(response.text)

    return response
