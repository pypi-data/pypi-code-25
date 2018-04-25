"""
Handle the different kinds of word embedding
    * word2vec
    * GloVe
    * FastText
"""
import os
import json
import pickle
import logging
import numpy as np

logger = logging.getLogger(__name__)


def load_word2vec(wv_model_path, binary=False):
    """
    使用 gensim 加载 Word2Vec 模型

    Args:
        wv_model_path(str): 词向量模型路径
        binary(bool): 词向量模型的类型；
            若为 True，则为 gensim 保存的二进制格式；反之为原始 C word2vec-tool 生成的格式

        原始 C word2vec-tool 生成的格式为：
            ```
            2519370 300
            the -0.065334 -0.093031 -0.017571 ...
            of 0.048804 -0.28528 0.018557 ...
            ```
    """
    logger.info("loading the Word2Vec model...")

    if not binary:
        from gensim.models import KeyedVectors
        wv_model = KeyedVectors.load_word2vec_format(wv_model_path)
    else:
        from gensim.models import Word2Vec
        wv_model = Word2Vec.load(wv_model_path)

    logger.info("loading the Word2Vec model finished.")
    return wv_model


def load_fasttext(model_path):
    """
    加载 FastText 模型（加载时间较长）

    Args:
        model_path(str): /path/to/model.bin
            fasttext GitHub 提供了预训练的模型，可以直接导入 gensim
    """
    logger.info("loading the FastText model...")

    from gensim.models import FastText
    model = FastText.load_fasttext_format(model_path)

    logger.info("loading the FastText model finished.")
    return model


def extract_embeddings(wv_model_path, words, save_path=None, binary=False):
    """
    从 wv_model 中抽取 words 的词向量

    Args:
        wv_model_path(str): 预训练的词向量模型路径
        words(list): 待抽取词向量的单词
        save_path(str): 文件保存路径
        binary(bool): 词向量模型的类型

    Examples:
        >>> wv_model_path = r""
        >>> words = ['the', 'of', 'apple', 'UNK']
        >>> embeddings, id2word, word2id = extract_embeddings(wv_model_path, words, save_path='D:/tmp')

    Returns:

    """
    wv_model = load_word2vec(wv_model_path, binary=binary)

    embeddings = []
    id2word = dict()
    for id, word in enumerate(words):
        try:
            embeddings.append(wv_model[word])
            id2word[id + 1] = word
        except KeyError:
            pass

    embeddings = np.array(embeddings)

    from collections import defaultdict
    word2id = defaultdict(int, zip(id2word.values(), id2word.keys()))

    if save_path is not None:
        np.save(os.path.join(save_path, "embeddings.npy"), embeddings)
        with open(os.path.join(save_path, "id2word.json"), 'w', encoding='utf8') as f:
            json.dump(id2word, f, indent=2)
        with open(os.path.join(save_path, "word2id.pkl"), 'wb') as f:
            pickle.dump(word2id, f)

    return embeddings, id2word, word2id


def build_vocab_from_word2vec(wv_model_path, save_path=None, save_embeddings=False, binary=False, zero_start=True):
    """
    从训练好的词向量模型中构建词汇集

    Args:
        wv_model_path(str): 预训练的词向量模型路径
        save_path(str): 文件保存路径
        save_embeddings(bool): 是否保存 embeddings，默认不保存
        binary(bool): 词向量模型的类型
        zero_start(bool): id2word 是否从 0 开始
            若从 0 开始，即不留位置给未登录词，未登录需要在传入模型前处理
            若从 1 开始，则 0 的位置留给未登录词，所有未登录词将被映射到 id == 0；
                此时，一般的做法是将一个 0 向量拼接到所有词向量之前，所有未登录词将映射到该 0 向量

    Returns:

    """
    wv_model = load_word2vec(wv_model_path, binary=binary)
    embeddings = wv_model.wv.vectors

    if zero_start:
        id2word = {i: j for i, j in enumerate(wv_model.wv.index2word)}
        word2id = dict(zip(id2word.values(), id2word.keys()))
    else:
        id2word = {i + 1: j for i, j in enumerate(wv_model.wv.index2word)}
        word2id = dict(zip(id2word.values(), id2word.keys()))
        from collections import defaultdict
        word2id = defaultdict(int, word2id)

    if save_path is not None:
        with open(os.path.join(save_path, "id2word.json"), 'w', encoding='utf8') as f:
            json.dump(id2word, f, indent=2)
        with open(os.path.join(save_path, "word2id.pkl"), 'wb') as f:
            pickle.dump(word2id, f)

        if save_embeddings:
            np.save(os.path.join(save_path, "embeddings.npy"), embeddings)

    return id2word, word2id, embeddings


def build_vocab_from_fasttext(model_path, save_path=None, save_embeddings=False, zero_start=True):
    """"""
    model = load_fasttext(model_path)
    embeddings = model.wv.vectors

    if zero_start:
        id2word = {i: j for i, j in enumerate(model.wv.index2word)}
        word2id = dict(zip(id2word.values(), id2word.keys()))
    else:
        id2word = {i + 1: j for i, j in enumerate(model.wv.index2word)}
        word2id = dict(zip(id2word.values(), id2word.keys()))
        from collections import defaultdict
        word2id = defaultdict(int, word2id)

    if save_path is not None:
        with open(os.path.join(save_path, "id2word.json"), 'w', encoding='utf8') as f:
            json.dump(id2word, f, indent=2)
        with open(os.path.join(save_path, "word2id.pkl"), 'wb') as f:
            pickle.dump(word2id, f)

        if save_embeddings:
            np.save(os.path.join(save_path, "embeddings.npy"), embeddings)

    return id2word, word2id, embeddings
