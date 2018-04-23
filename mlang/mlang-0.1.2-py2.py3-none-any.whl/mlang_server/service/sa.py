# coding: utf-8

from flask_restful import reqparse
from flask_restful import Resource
from flask_restful.inputs import boolean

from mlang.res.vocab import Vocab
from mlang.res.vocab import DefaultSentimentVocab

from mlang.ie.sa.sentiment import SentimentAnalyzer
from mlang.ie.sa.extract_term import extract as extract_terms
from mlang.ie.sa.extract_opinion import extract as extract_opinions

from mlang_server.service.vocab import get_vocab
from mlang_server.service.vocab import DEFAULT_VOCAB_SENTIMENT
from mlang_server.service.corpus import get_corpus


def init(api, furl):
    api.add_resource(Score, furl('/sa/score'))
    api.add_resource(Subjective, furl('/sa/subjective'))
    api.add_resource(ExtractTerms, furl('/sa/terms'))
    api.add_resource(ExtractOpinion, furl('/sa/opinions'))


class Score(Resource):
    """
    计算文本情感分值
    """

    def __init__(self):
        self.rqp = reqparse.RequestParser()
        self.rqp.add_argument('txt', type=str, required=True, trim=True, help='parameter [txt] is required!')
        self.rqp.add_argument('positive_vocabid', required=False, type=str, default=DEFAULT_VOCAB_SENTIMENT,
                              help='positive words vocab id')
        self.rqp.add_argument('negative_vocabid', required=False, type=str, default=DEFAULT_VOCAB_SENTIMENT,
                              help='negative words vocab id')
        self.rqp.add_argument('update_cache', required=False, type=boolean, default=False, help='update cache')

    def post(self):
        args = self.rqp.parse_args()

        txt = args['txt']
        pvocabid = args['positive_vocabid']
        nvocabid = args['negative_vocabid']
        update_cache = args['update_cache']

        pvocab = get_vocab(pvocabid, update_cache)
        nvocab = get_vocab(nvocabid, update_cache)

        if isinstance(pvocab, DefaultSentimentVocab):
            positives = pvocab.positives()
        else:
            positives = pvocab.words()

        if isinstance(nvocab, DefaultSentimentVocab):
            negatives = nvocab.negatives()
        else:
            negatives = nvocab.words()

        analyzer = SentimentAnalyzer(positives=positives, negatives=negatives)
        return analyzer.score(txt)


class Subjective(Resource):
    """
    判断文本是否是主观
    """
    def __init__(self):
        self.rqp = reqparse.RequestParser()
        self.rqp.add_argument('txt', type=str, required=True, trim=True, help='parameter [txt] is required!')
        self.rqp.add_argument('positive_vocabid', required=False, type=str, default=DEFAULT_VOCAB_SENTIMENT,
                              help='positive words vocab id')
        self.rqp.add_argument('negative_vocabid', required=False, type=str, default=DEFAULT_VOCAB_SENTIMENT,
                              help='negative words vocab id')
        self.rqp.add_argument('update_cache', required=False, type=boolean, default=False, help='update cache')

    def post(self):
        args = self.rqp.parse_args()

        txt = args['txt']
        pvocabid = args['positive_vocabid']
        nvocabid = args['negative_vocabid']
        update_cache = args['update_cache']

        pvocab = get_vocab(pvocabid, update_cache)
        nvocab = get_vocab(nvocabid, update_cache)

        if isinstance(pvocab, DefaultSentimentVocab):
            positives = pvocab.positives()
        else:
            positives = pvocab.words()

        if isinstance(nvocab, DefaultSentimentVocab):
            negatives = nvocab.negatives()
        else:
            negatives = nvocab.words()

        analyzer = SentimentAnalyzer(positives=positives, negatives=negatives)
        return analyzer.is_subjective(txt)


class ExtractTerms(Resource):
    """
    从语料中提取情感词、特征词
    """
    def __init__(self):
        self.rqp = reqparse.RequestParser()
        self.rqp.add_argument('corpusid', type=str, required=True, help='corpus id')
        self.rqp.add_argument('s_seed', type=str, required=False, default=['好', '漂亮', '不错', '差'], help='sentiment seed set.', action='append')
        self.rqp.add_argument('top_n', type=int, required=False, default=3000, help='top n words.')

    def get(self):
        args = self.rqp.parse_args()
        corpusid = args['corpusid']
        s_seed = set(args['s_seed'])
        top_n = args['top_n']

        corpus = get_corpus(corpusid)
        G, S = extract_terms(s_seed, corpus, top_n)
        return {
            'targets': G,
            'sentiments': S
        }

    def post(self):
        return self.get()


class ExtractOpinion(Resource):
    """
    从文本中提取观点
    """
    def post(self):
        """
        情感词/特征词从vocab中读取
        :return:
        """
        rqp = reqparse.RequestParser()
        rqp.add_argument('txt', type=str, required=True, help='txt.')
        rqp.add_argument('target_vocabid', type=str, required=True, help='target vocab id')
        rqp.add_argument('sentiment_vocabid', type=str, required=False, default=DEFAULT_VOCAB_SENTIMENT, help='sentiment vocab id')
        rqp.add_argument('positive_vocabid', type=str, required=False, help='positive vocab id')
        rqp.add_argument('negative_vocabid', type=str, required=False, help='negative vocab id')
        rqp.add_argument('update_cache', type=boolean, required=False, help='update cache, boolean', default=False)
        args = rqp.parse_args()

        txt = args['txt']
        update_cache = args['update_cache']
        target_vocabid = args['target_vocabid']
        sentiment_vocabid = args['sentiment_vocabid']

        gwords = get_vocab(target_vocabid, update_cache)
        swords = get_vocab(sentiment_vocabid, update_cache)

        positive_vocabid = args['positive_vocabid']
        negative_vocabid = args['negative_vocabid']

        if positive_vocabid:
            p_vocab = get_vocab(positive_vocabid, update_cache)
        else:
            p_vocab = Vocab()

        if negative_vocabid:
            n_vocab = get_vocab(negative_vocabid, update_cache)
        else:
            n_vocab = Vocab()

        # 提取出评价观点
        opinions = extract_opinions(txt, gwords, swords)

        # 使用用户配置的正面/负面词库进行情感倾向判定
        specific_analyzer = SentimentAnalyzer(positives=p_vocab.words(), negatives=n_vocab.words())
        for opinion in opinions:
            opinion.orientation = specific_analyzer.calc_score(opinion.sentiment, opinion.smodifiers)

        # 使用通用情感词库进行情感倾向判定
        for opinion in opinions:
            if opinion.orientation == 0:
                general_analyzer = SentimentAnalyzer()
                opinion.orientation = general_analyzer.calc_score(opinion.sentiment, opinion.smodifiers)

        return [o.to_json() for o in opinions]

    # def post(self):
    #     """
    #     情感词/特征词从请求参数中读取
    #     :return:
    #     """
    #     rqp = reqparse.RequestParser()
    #     rqp.add_argument('txt', type=str, required=True, help='txt.')
    #     rqp.add_argument('targets', type=str, required=True, help='target vocab id', action='append')
    #     rqp.add_argument('sentiments', type=str, required=True, help='sentiment vocab id', action='append')
    #     args = rqp.parse_args()
    #
    #     txt = args['txt']
    #     targets = args['targets']
    #     sentiments = args['sentiments']
    #
    #     return [o.to_json() for o in extract_opinions(txt, targets, sentiments)]
