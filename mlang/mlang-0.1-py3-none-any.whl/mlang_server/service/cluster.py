# coding: utf-8

from collections import defaultdict
from flask_restful import Resource
from flask_restful import reqparse
from flask_restful.inputs import boolean

from mlang.nlp import get_tokenize
from mlang.res.corpus import Corpus

from mlang.semantic.cluster import WordCluster
from mlang.semantic.cluster import TextCluster

from mlang.semantic.representation import W2VWordRepresentation
from mlang.semantic.representation import W2VTextRepresentation
from mlang.semantic.representation import D2VTextRepresentation
from mlang.semantic.representation import VocabTextRepresentation

from mlang_server.service.w2v import DEFAULT_W2V
from mlang_server.service.w2v import get_word2vec
from mlang_server.service.d2v import get_doc2vec
from mlang_server.service.d2v import DEFAULT_D2V

from mlang_server.service.corpus import get_corpus
from mlang_server.service.vocab import get_vocab
from mlang_server.service.vocab import DEFAULT_VOCAB


def init(api, furl):
    api.add_resource(WordClustering, furl('/cluster/word'))
    api.add_resource(VocabTextClustering, furl('/cluster/text/vocab'))
    api.add_resource(D2vTextClustering, furl('/cluster/text/d2v'))
    api.add_resource(W2vTextClustering, furl('/cluster/text/w2v'))


class WordClustering(Resource):
    def __init__(self):
        self.rqp = reqparse.RequestParser()
        self.rqp.add_argument('vocabid', required=True, type=str, help='vocabid: word vocab id')
        self.rqp.add_argument('n_clusters', required=False, type=int, help='n_clusters: cluster number.')
        self.rqp.add_argument('w2vid', required=False, type=str, default=DEFAULT_W2V, help='w2vid: word2vec model id')
        self.rqp.add_argument('update_cache', required=False, type=boolean, default=False)

    def post(self):
        args = self.rqp.parse_args()

        vocabid = args['vocabid']
        w2vid = args['w2vid']
        update_cache = args['update_cache']
        n_clusters = args['n_clusters']

        w2v = get_word2vec(w2vid, update_cache)
        rep = W2VWordRepresentation()
        rep.w2v = w2v

        vocab = get_vocab(vocabid, update_cache)
        words = list(vocab.words())
        corpus = Corpus(words)

        cluster = WordCluster(n_clusters, represent=rep)
        labels = cluster.fit(corpus)

        result = defaultdict(list)

        for word, label in zip(words, labels):
            result[str(label)].append(word)

        return result


class VocabTextClustering(Resource):
    def __init__(self):
        self.rqp = reqparse.RequestParser()
        self.rqp.add_argument('corpusid', required=True, type=str, help='vocabid: word vocab id')
        self.rqp.add_argument('vocabid', required=False, type=str, default=DEFAULT_VOCAB, help='vocabid: word vocab id')
        self.rqp.add_argument('n_clusters', required=False, type=int, help='n_clusters: cluster number.')
        self.rqp.add_argument('update_cache', required=False, type=boolean, default=False)

    def post(self):
        args = self.rqp.parse_args()

        vocabid = args['vocabid']
        corpusid = args['corpusid']
        update_cache = args['update_cache']
        n_clusters = args['n_clusters']

        vocab = get_vocab(vocabid, update_cache)
        rep = VocabTextRepresentation(vocab=vocab)

        corpus = get_corpus(corpusid)
        cluster = TextCluster(n_clusters=n_clusters, x_dimension=len(vocab), represent=rep)
        labels = cluster.fit(corpus)

        result = defaultdict(list)
        for txt, label in zip(corpus, labels):
            result[str(label)].append(txt)

        return result


class D2vTextClustering(Resource):

    def __init__(self):
        self.rqp = reqparse.RequestParser()
        self.rqp.add_argument('corpusid', required=True, type=str, help='corpusid')
        self.rqp.add_argument('d2vid', required=False, type=str, default=DEFAULT_D2V, help='d2vid: doc2vec model id')
        self.rqp.add_argument('tokenize', type=str, required=False, default='ltp', help='tokenize method, [ltp/jieba/fmm/rmm], fmm/rmm -> vocabid + max_len')
        self.rqp.add_argument('vocabid', required=False, type=str, default=DEFAULT_VOCAB, help='vocabid: word vocab id')
        self.rqp.add_argument('max_len', type=int, required=False, default=4, help='max_len: max word length')
        self.rqp.add_argument('n_clusters', required=False, type=int, help='n_clusters: cluster number.')
        self.rqp.add_argument('update_cache', required=False, type=boolean, default=False)

    def post(self):
        args = self.rqp.parse_args()

        corpusid = args['corpusid']

        d2vid = args['d2vid']
        update_cache = args['update_cache']
        n_clusters = args['n_clusters']

        tokenize_impl = args['tokenize']
        max_len = args['max_len']
        vocabid = args['vocabid']
        vocab = get_vocab(vocabid, update_cache)
        tokenize = get_tokenize(tokenize_impl, dictionary=vocab, max_len=max_len)

        d2v_model = get_doc2vec(d2vid, update_cache)
        rep = D2VTextRepresentation(tokenize=tokenize)
        rep.d2v = d2v_model

        corpus = get_corpus(corpusid)

        cluster = TextCluster(n_clusters, represent=rep)
        labels = cluster.fit(corpus)

        result = defaultdict(list)

        for txt, label in zip(corpus, labels):
            result[str(label)].append(txt)

        return result


class W2vTextClustering(Resource):

    def __init__(self):
        self.rqp = reqparse.RequestParser()
        self.rqp.add_argument('corpusid', required=True, type=str, help='corpusid')
        self.rqp.add_argument('w2vid', required=False, type=str, default=DEFAULT_W2V, help='w2vid: word2vec model id')
        self.rqp.add_argument('tokenize', type=str, required=False, default='ltp', help='tokenize method, [ltp/jieba/fmm/rmm], fmm/rmm -> vocabid + max_len')
        self.rqp.add_argument('vocabid', required=False, type=str, default=DEFAULT_VOCAB, help='vocabid: word vocab id')
        self.rqp.add_argument('max_len', type=int, required=False, default=4, help='max_len: max word length')
        self.rqp.add_argument('n_clusters', required=False, type=int, help='n_clusters: cluster number.')
        self.rqp.add_argument('update_cache', required=False, type=boolean, default=False)

    def post(self):
        args = self.rqp.parse_args()

        corpusid = args['corpusid']

        w2vid = args['w2vid']
        update_cache = args['update_cache']
        n_clusters = args['n_clusters']

        tokenize_impl = args['tokenize']
        max_len = args['max_len']
        vocabid = args['vocabid']
        vocab = get_vocab(vocabid, update_cache)
        tokenize = get_tokenize(tokenize_impl, dictionary=vocab, max_len=max_len)

        w2v_model = get_word2vec(w2vid, update_cache)
        rep = W2VTextRepresentation(tokenize=tokenize)
        rep.w2v = w2v_model

        corpus = get_corpus(corpusid)

        cluster = TextCluster(n_clusters, represent=rep)
        labels = cluster.fit(corpus)

        result = defaultdict(list)

        for txt, label in zip(corpus, labels):
            result[str(label)].append(txt)

        return result
