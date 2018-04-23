# coding: utf-8

from flask_restful import reqparse
from flask_restful import Resource
from flask_restful.inputs import boolean

from mlang.nlp import ssplit
from mlang.nlp import pos
from mlang.nlp import ner
from mlang.nlp import parse
from mlang.nlp import to_pinyin
from mlang.nlp import to_hanzi
from mlang.nlp import to_simplified
from mlang.nlp import to_traditional
from mlang.nlp import get_tokenize

from mlang_server.service.vocab import get_vocab
from mlang.config import DEFAULT_VOCAB


def init(api, furl):
    api.add_resource(Ssplit, furl('/nlp/ssplit'))
    api.add_resource(Tokenize, furl('/nlp/tokenize'))
    api.add_resource(Pos, furl('/nlp/pos'))
    api.add_resource(Ner, furl('/nlp/ner'))
    api.add_resource(Parse, furl('/nlp/parse'))
    api.add_resource(Hanzi2Pinyin, furl('/nlp/h2p'))
    api.add_resource(Pinyin2Hanzi, furl('/nlp/p2h'))
    api.add_resource(S2T, furl('/nlp/s2t'))
    api.add_resource(T2S, furl('/nlp/t2s'))


class Params(object):
    """
    参数
    """
    def __init__(self):
        self.rqp = reqparse.RequestParser()
        self.rqp.add_argument('txt', type=str, required=True, trim=True, help='parameter [txt] is required!')
        self.rqp.add_argument('impl', type=str, required=False, trim=True, help='parameter [impl] is invalid!')
        self.rqp.add_argument('revise', type=boolean, required=False, help='parameter [revise] is a bool param')
        self.rqp.add_argument('norm', type=boolean, required=False, help='parameter [norm] is a bool param')
        self.rqp.add_argument('max_len', type=int, required=False, help='parameter [max_len] type is int')
        self.rqp.add_argument('vocabid', type=str, required=False, help='parameter [vocabid] is required')

        self.args = None

    def get_param(self, name, default_value=None):
        if self.args is None:
            self.args = self.rqp.parse_args()
        if self.args[name] is not None:
            return self.args[name]
        return default_value


class Ssplit(Resource):
    """
    分句
    """
    def __init__(self):
        self.rqp = reqparse.RequestParser()
        self.rqp.add_argument('txt', type=str, required=True, trim=True, help='parameter [txt] is required!')
        self.rqp.add_argument('impl', type=str, required=False, trim=True, help='parameter [impl] is invalid!')
        self.rqp.add_argument('pattern', type=str, required=False, default='[\s,，.。:：!！?？、]', help='parameter [pattern]')

    def post(self):
        args = self.rqp.parse_args()
        txt = args['txt']
        impl = args['impl']
        pattern = args['pattern']
        return ssplit(txt, impl=impl, pattern=pattern)


class Tokenize(Resource):
    """
    分词
    """
    def __init__(self):
        self.rqp = reqparse.RequestParser()
        self.rqp.add_argument('txt', type=str, required=True, trim=True, help='parameter [txt] is required!')
        self.rqp.add_argument('impl', type=str, required=False, default="ltp", trim=True, help='parameter [impl] is invalid!')
        self.rqp.add_argument('vocabid', type=str, required=False, default=DEFAULT_VOCAB, help='parameter [vocabid] is required')
        self.rqp.add_argument('max_len', type=int, required=False, default=4, help='parameter [max_len] type is int')
        self.rqp.add_argument('update_cache', type=boolean, required=False, help='parameter [update_cache] type is !')

    def post(self):
        args = self.rqp.parse_args()
        txt = args['txt']
        impl = args['impl']
        max_len = args['max_len']
        vocabid = args['vocabid']
        update_cache = args['update_cache']

        vocab = get_vocab(vocabid, update_cache)

        xtokenize = get_tokenize(impl, dictionary=vocab, max_len=max_len)
        return [t.to_json() for t in xtokenize(txt)]


class Pos(Resource, Params):
    """
    词性标注
    """
    def post(self):
        txt = self.get_param('txt')
        impl = self.get_param('impl', 'ltp')
        revise = self.get_param('revise', False)
        norm = self.get_param('norm', False)
        return [t.to_json() for t in pos(txt, impl, revise, norm)]


class Ner(Resource, Params):
    """
    命名实体识别
    """
    def post(self):
        txt = self.get_param('txt')
        impl = self.get_param('impl', 'ltp')
        tags = pos(txt, impl='ltp')
        return [{'token': tp[0].word, 'tag': tp[0].tag, 'ner': tp[1]} for tp in zip(tags, ner(txt, impl))]


class Parse(Resource, Params):
    """
    句法解析
    """
    def post(self):
        txt = self.get_param('txt')
        impl = self.get_param('impl', 'ltp')
        return [r.to_json() for r in parse(txt, impl)]


class Hanzi2Pinyin(Resource, Params):
    """
    汉字转拼音
    """
    def post(self):
        txt = self.get_param('txt')
        impl = self.get_param('impl', 'Pinyin2Hanzi')
        return to_pinyin(txt, impl)


class Pinyin2Hanzi(Resource, Params):
    """
    汉字转拼音
    拼音用空格分隔
    """
    def post(self):
        txt = self.get_param('txt')
        impl = self.get_param('impl', 'Pinyin2Hanzi')
        return to_hanzi(txt.split(), impl)


class S2T(Resource, Params):
    """
    简体转繁体
    """
    def post(self):
        txt = self.get_param('txt')
        impl = self.get_param('impl', 'zhconv')
        return to_traditional(txt, impl)


class T2S(Resource, Params):
    """
    繁体转简体
    """
    def post(self):
        txt = self.get_param('txt')
        impl = self.get_param('impl', 'zhconv')
        return to_simplified(txt, impl)
