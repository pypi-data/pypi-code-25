# coding: utf-8

import numpy as np

from flask_restful import reqparse
from flask_restful import Resource
from flask_restful.inputs import boolean

from mlang.nlp import get_tokenize

from mlang.semantic.representation import OneHotWordRepresentation
from mlang.semantic.representation import VocabTextRepresentation

from mlang.semantic.representation import W2VWordRepresentation
from mlang.semantic.representation import D2VTextRepresentation
from mlang.semantic.representation import W2VTextRepresentation

from mlang.semantic.representation import cosine_similary

from mlang_server.service.vocab import get_vocab
from mlang_server.service.vocab import DEFAULT_VOCAB

from mlang_server.service.w2v import get_word2vec
from mlang_server.service.w2v import DEFAULT_W2V

from mlang_server.service.d2v import DEFAULT_D2V
from mlang_server.service.d2v import get_doc2vec


def init(api, furl):
    api.add_resource(WordOneHotRepresentation, furl('/rep/word/onehot'))
    api.add_resource(WordW2vRepresentation, furl('/rep/word/w2v'))

    api.add_resource(TextVocabRepresentation, furl('/rep/text/vocab'))
    api.add_resource(TextD2vRepresentation, furl('/rep/text/d2v'))
    api.add_resource(TextW2vRepresentation, furl('/rep/text/w2v'))

    api.add_resource(WordSimilarity, furl('/rep/word/sim'))
    api.add_resource(TextVocabSimilarity, furl('/rep/text/sim/vocab'))
    api.add_resource(TextD2vSimilarity, furl('/rep/text/sim/d2v'))
    api.add_resource(TextW2vSimilarity, furl('/rep/text/sim/w2v'))


class WordOneHotRepresentation(Resource):
    """
    单词one hot表征
    """
    def get(self):
        rqp = reqparse.RequestParser()
        rqp.add_argument('word', type=str, required=True, help='word')
        rqp.add_argument('vocabid', type=str, required=False, default=DEFAULT_VOCAB, help='vocab id')
        rqp.add_argument('update_cache', type=boolean, required=False, default=False, help='update cache')
        args = rqp.parse_args()

        word = args['word']
        vocabid = args['vocabid']
        update_cache = args['update_cache']

        vocab = get_vocab(vocabid, update_cache)
        rep = OneHotWordRepresentation(vocab=vocab)
        return rep.represent(word).tolist()


class WordW2vRepresentation(Resource):
    """
    单词word2vec表征
    """
    def get(self):
        rqp = reqparse.RequestParser()
        rqp.add_argument('word', type=str, required=True, help='word')
        rqp.add_argument('w2vid', type=str, required=False, default=DEFAULT_W2V, help='vocab id')
        rqp.add_argument('update_cache', type=boolean, required=False, default=False, help='update cache')

        args = rqp.parse_args()

        word = args['word']
        w2vid = args['w2vid']
        update_cache = args['update_cache']

        w2v_model = get_word2vec(w2vid, update_cache)
        rep = W2VWordRepresentation()
        rep.w2v = w2v_model
        return rep.represent(word).tolist()


class TextVocabRepresentation(Resource):
    """
    文本表征，词表方式
    """
    def post(self):
        rqp = reqparse.RequestParser()
        rqp.add_argument('txt', type=str, required=True, help='vocab id')
        rqp.add_argument('vocabid', type=str, required=False, default='defaultvocab', help='vocab id')
        rqp.add_argument('update_cache', type=boolean, required=False, default=False, help='update cache')
        args = rqp.parse_args()

        txt = args['txt']
        vocabid = args['vocabid']
        update_cache = args['update_cache']

        vocab = get_vocab(vocabid, update_cache)
        rep = VocabTextRepresentation(vocab=vocab)
        return rep.represent(txt).tolist()


class TextD2vRepresentation(Resource):
    """
    文本表征，word2vec方式
    """
    def post(self):
        rqp = reqparse.RequestParser()
        rqp.add_argument('txt', type=str, required=True, help='txt')
        rqp.add_argument('d2vid', type=str, required=False, default=DEFAULT_D2V, help='doc2vec id')
        rqp.add_argument('tokenize', type=str, required=False, default='ltp', help='tokenize method, [ltp/jieba/fmm/rmm], fmm/rmm -> vocabid + max_len')
        rqp.add_argument('vocabid', type=str, required=False, help='vocabid: token vocab id', default=DEFAULT_VOCAB)
        rqp.add_argument('max_len', type=int, required=False, default=4, help='max_len: max word length')
        rqp.add_argument('update_cache', type=boolean, required=False, default=False, help='update cache')

        args = rqp.parse_args()

        txt = args['txt']
        d2vid = args['d2vid']
        update_cache = args['update_cache']

        tokenize_impl = args['tokenize']
        vocabid = args['vocabid']
        max_len = args['max_len']
        vocab = get_vocab(vocabid, update_cache)
        tokenize = get_tokenize(tokenize_impl, dictionary=vocab, max_len=max_len)

        d2v_model = get_doc2vec(d2vid, update_cache)
        rep = D2VTextRepresentation(tokenize=tokenize)
        rep.d2v = d2v_model
        return rep.represent(txt).tolist()


class TextW2vRepresentation(Resource):
    """
    取得文本的向量表征，word2vec方式
    """
    def post(self):
        rqp = reqparse.RequestParser()
        rqp.add_argument('txt', type=str, required=True, help='txt')
        rqp.add_argument('w2vid', type=str, required=False, default=DEFAULT_W2V, help='word2vec id')
        rqp.add_argument('tokenize', type=str, required=False, default='ltp', help='tokenize method, [ltp/jieba/fmm/rmm], fmm/rmm -> vocabid + max_len')
        rqp.add_argument('vocabid', type=str, required=False, help='vocabid: token vocab id', default=DEFAULT_VOCAB)
        rqp.add_argument('max_len', type=int, required=False, default=4, help='max_len: max word length')
        rqp.add_argument('update_cache', type=boolean, required=False, default=False, help='update cache')

        args = rqp.parse_args()

        txt = args['txt']
        w2vid = args['w2vid']
        tokenize_impl = args['tokenize']
        vocabid = args['vocabid']
        max_len = args['max_len']

        update_cache = args['update_cache']

        vocab = get_vocab(vocabid, update_cache)
        tokenize = get_tokenize(tokenize_impl, dictionary=vocab, max_len=max_len)

        w2v_model = get_word2vec(w2vid, update_cache)

        rep = W2VTextRepresentation(tokenize=tokenize)
        rep.w2v = w2v_model
        return rep.represent(txt).tolist()


class WordSimilarity(Resource):
    """
    比较两个单词的相似度
    """
    def get(self):
        rqp = reqparse.RequestParser()
        rqp.add_argument('word1', type=str, required=True, help='word1')
        rqp.add_argument('word2', type=str, required=True, help='word2')
        rqp.add_argument('w2vid', type=str, required=False, default=DEFAULT_W2V, help='word2vec id')
        rqp.add_argument('update_cache', type=boolean, required=False, default=False, help='update cache')

        args = rqp.parse_args()

        word1 = args['word1']
        word2 = args['word2']
        w2vid = args['w2vid']
        update_cache = args['update_cache']

        w2v_model = get_word2vec(w2vid, update_cache)
        rep = W2VWordRepresentation()
        rep.w2v = w2v_model
        return float(rep.similarity(word1, word2))


class TextVocabSimilarity(Resource):
    """
    取得两个文本的相似度，词表方式
    """
    def post(self):
        rqp = reqparse.RequestParser()
        rqp.add_argument('txt1', type=str, required=True, help='txt1')
        rqp.add_argument('txt2', type=str, required=True, help='txt2')
        rqp.add_argument('vocabid', type=str, required=False, default='defaultvocab', help='vocab id')
        rqp.add_argument('update_cache', type=boolean, required=False, default=False, help='update cache')
        args = rqp.parse_args()

        txt1 = args['txt1']
        txt2 = args['txt2']
        vocabid = args['vocabid']
        update_cache = args['update_cache']

        vocab = get_vocab(vocabid, update_cache)
        rep = VocabTextRepresentation(vocab=vocab)
        return float(rep.similarity(txt1, txt2))


class TextD2vSimilarity(Resource):
    """
    取得两个文本的相似度，doc2vec方式
    """
    def post(self):
        rqp = reqparse.RequestParser()
        rqp.add_argument('txt1', type=str, required=True, help='txt')
        rqp.add_argument('txt2', type=str, required=True, help='txt')
        rqp.add_argument('d2vid', type=str, required=False, default=DEFAULT_D2V, help='doc2vec id')
        rqp.add_argument('tokenize', type=str, required=False, default='ltp', help='tokenize method, [ltp/jieba/fmm/rmm], fmm/rmm -> vocabid + max_len')
        rqp.add_argument('vocabid', type=str, required=False, help='vocabid: token vocab id', default=DEFAULT_VOCAB)
        rqp.add_argument('max_len', type=int, required=False, default=4, help='max_len: max word length')
        rqp.add_argument('update_cache', type=boolean, required=False, default=False, help='update cache')

        args = rqp.parse_args()

        txt1 = args['txt1']
        txt2 = args['txt2']
        d2vid = args['d2vid']
        tokenize_impl = args['tokenize']
        vocabid = args['vocabid']
        max_len = args['max_len']

        update_cache = args['update_cache']

        vocab = get_vocab(vocabid, update_cache)

        tokenize = get_tokenize(tokenize_impl, dictionary=vocab, max_len=max_len)

        d2v_model = get_doc2vec(d2vid, update_cache)

        rep = D2VTextRepresentation(tokenize=tokenize)
        rep.d2v = d2v_model

        return float(rep.similarity(txt1, txt2))


class TextW2vSimilarity(Resource):
    """
    取得两个文本的相似度，word2vec方式
    """
    def post(self):
        rqp = reqparse.RequestParser()
        rqp.add_argument('txt1', type=str, required=True, help='txt')
        rqp.add_argument('txt2', type=str, required=True, help='txt')
        rqp.add_argument('w2vid', type=str, required=False, default=DEFAULT_W2V, help='word2vec id')
        rqp.add_argument('tokenize', type=str, required=False, default='ltp', help='tokenize method, [ltp/jieba/fmm/rmm], fmm/rmm -> vocabid + max_len')
        rqp.add_argument('vocabid', type=str, required=False, help='vocabid: token vocab id', default=DEFAULT_VOCAB)
        rqp.add_argument('max_len', type=int, required=False, default=4, help='max_len: max word length')
        rqp.add_argument('update_cache', type=boolean, required=False, default=False, help='update cache')

        args = rqp.parse_args()

        txt1 = args['txt1']
        txt2 = args['txt2']
        w2vid = args['w2vid']
        tokenize_impl = args['tokenize']
        vocabid = args['vocabid']
        max_len = args['max_len']

        update_cache = args['update_cache']

        vocab = get_vocab(vocabid, update_cache)
        tokenize = get_tokenize(tokenize_impl, dictionary=vocab, max_len=max_len)

        w2v_model = get_word2vec(w2vid, update_cache)

        rep = W2VTextRepresentation(tokenize=tokenize)
        rep.w2v = w2v_model

        return float(cosine_similary(rep.represent(txt1), rep.represent(txt2)))
