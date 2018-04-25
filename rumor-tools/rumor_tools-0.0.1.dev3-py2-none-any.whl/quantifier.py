#!/usr/bin/env python
# encoding: utf-8


"""
A high level quantifier library for text analysis.
"""
import logging
import math
import os
import re
from itertools import chain
from pprint import pprint

import gensim
import keras
import numpy as np
import yaml
from gensim.models import Word2Vec, LdaMulticore, Doc2Vec
from keras import Sequential
from keras.layers import Embedding, LSTM, Dropout, Dense, Activation, Bidirectional
from keras.models import model_from_yaml
from keras.preprocessing import sequence
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn.cluster import MiniBatchKMeans
from smart_open import smart_open

from rumor_tools import save_model, load_model, timing
from rumor_tools.preprocess import cut_words, extract_entities, pmi_multi_query, KeywordDetector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SentimentClassifier(object):

    __instance = None
    __init_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, max_len=100, batch_size=32, n_epoch=5, logger=None):
        """
        A word2vec based LSTM model for sentiment classification.

        :param max_len: Maximum length of the input sequence, longer sequence will be truncated.

        :param batch_size: Batch size of training or testing data.

        :param n_epoch: Epoch number for training.

        :param logger: Logger object.

        """
        if not SentimentClassifier.__init_flag:
            self.logger = logger
            self.max_len = max_len
            self.word2idx = {}
            self.idx2word = {}
            self.word2vec = None
            self.model = None
            self.vocab_size = None
            self.batch_size = batch_size
            self.epoch = n_epoch

            SentimentClassifier.__init_flag = True

    @staticmethod
    def load_data(dir_path):
        pos = open(os.path.join(dir_path, "pos.csv")).readlines()
        neg = open(os.path.join(dir_path, "neg.csv")).readlines()
        neu = open(os.path.join(dir_path, "neu.csv")).readlines()

        x = pos + neu + neg
        y = np.concatenate((np.zeros(len(pos), dtype=int), np.ones(len(neu), dtype=int), 1 + np.ones(len(neg), dtype=int)))
        return x, y

    def load_dictionaries(self, w2v_file):
        self.word2vec = Word2Vec.load(w2v_file)
        self.word2idx = {w: i+2 for i, w in enumerate(self.word2vec.vocab)}     # We need to add two more dummy words
        self.word2idx["UNK"] = 0
        self.word2idx["PAD"] = 1
        self.idx2word = {i: w for i, w in self.word2idx.items()}

    def prepare_data(self, x, y):
        x = [[self.word2idx.get(w, self.word2idx["UNK"]) for w in cut_words(d)] for d in x]
        x = sequence.pad_sequences(x, maxlen=self.max_len, value=self.word2idx["PAD"])
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)
        y_train = keras.utils.to_categorical(y_train, num_classes=3)
        y_test = keras.utils.to_categorical(y_test, num_classes=3)

        return x_train, x_test, y_train, y_test

    def get_embedding_layer(self):

        self.vocab_size = len(self.word2idx)
        embeddings = np.zeros((self.vocab_size, 300)) # Use pre-trained embeddings with 300-dim
        for word, index, in self.word2idx.items():
            if word in self.word2vec.vocab:
                embeddings[index, :] = self.word2vec[word]
        return embeddings

    def build(self, embeddings):
        self.model = Sequential()
        self.model.add(Embedding(output_dim=300,
                                 input_dim=self.vocab_size,
                                 mask_zero=True,
                                 weights=[embeddings],
                                 trainable=False,
                                 input_length=self.max_len))

        self.model.add(Bidirectional(LSTM(units=100, activation="tanh"), merge_mode='concat', weights=None))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(3, activation="softmax"))
        self.model.add(Activation("softmax"))

        self.model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

    def train(self, x_train, y_train):
        self.model.fit(x_train, y_train, batch_size=self.batch_size, nb_epoch=self.epoch, verbose=1)

    def test(self, x_test, y_test):
        score = self.model.evaluate(x_test, y_test, batch_size=self.batch_size)
        print("Final Test Score:{0}".format(score))

    def save(self, path):
        yaml_string = self.model.to_yaml()
        with open(os.path.join(path, "lstm.yml"), "w") as f:
            f.write(yaml.dump(yaml_string, default_flow_style=True))
        self.model.save_weights(os.path.join(path, "lstm.h5"))

    def load(self, path):
        with open(os.path.join(path, "lstm.yml"), "r") as f:
            yaml_string = yaml.load(f.read())
        self.model = model_from_yaml(yaml_string=yaml_string)

        self.model.load_weights(os.path.join(path, "lstm.h5"))
        self.model.compile(loss='categorical_crossentropy',
                           optimizer='adam', metrics=['accuracy'])

    def predict(self, data):
        data = [[self.word2idx.get(w, 0) for w in cut_words(d)] for d in data]
        data = sequence.pad_sequences(data, maxlen=self.max_len)
        result = self.model.predict_classes(data)
        return result


class TFIDFModel(object):
    __instance = None
    __init_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if not TFIDFModel.__init_flag:
            self.model = TfidfVectorizer(min_df=2, smooth_idf=True)
            TFIDFModel.__init_flag = True

    def fit(self, decoded_corpus):
        """
        Train the model based on the feed corpus

        :param decoded_corpus: A list of decoded segmented strings(separated by space)

        :return: Transformed corpus
        """

        self.model.fit(decoded_corpus)

    def save(self, path):
        from sklearn.externals import joblib
        joblib.dump(self.model, os.path.join(path, "tf_idf.ml"))

    def load(self, path):
        from sklearn.externals import joblib
        self.model = joblib.load(os.path.join(path, "tf_idf.ml"))

    def predict(self, decoded_corpus):
        """
        Transform the decoded corpus into tfidf vector.

        :param decoded_corpus: Decoded segmented string text

        :return: None
        """

        x_tfidf = self.model.transform(decoded_corpus)
        return x_tfidf.toarray()

    @staticmethod
    def load_file(path):

        with open(path, "r") as input_file:
            for line in input_file:
                yield line.decode("utf-8")


class NBModel(object):
    __instance = None
    __init_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if not NBModel.__init_flag:
            self.model = MultinomialNB()
            NBModel.__init_flag = True

    def train(self, x, y):
        self.model.fit(x, y)

    def predict(self, x):
        return self.model.predict(x)

    def save(self, path, name):
        save_model(self.model, path, name)

    def load(self, path, name):
        self.model = load_model(path, name)


class LDAModel(object):

    __instance = None
    __init_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if not LDAModel.__init_flag:
            self.model = None
            self.dictionary = None
            LDAModel.__init_flag = True

    def load_data(self, raw_segmented_corpus, dictionary=None):
        self.dictionary = dictionary if dictionary else gensim.corpora.Dictionary(raw_segmented_corpus)
        corpus = [self.dictionary.doc2bow(d) for d in raw_segmented_corpus]
        return corpus

    def prepare_data(self, raw_segmented_corpus):
        return [self.dictionary.doc2bow(d) for d in raw_segmented_corpus]

    def train(self, corpus, topics=5):
        self.model = LdaMulticore(corpus, id2word=self.dictionary, num_topics=topics)

    def update(self, corpus):
        self.model.update(corpus)

    def predict(self, document):
        return sorted(self.model.get_document_topics(document, minimum_probability=0.0), key=lambda x:x[1], reverse=True)

    def save(self, path):
        self.model.save(os.path.join(path, "lda.ml"))
        import pickle
        pickle.dump(self.dictionary, open(os.path.join(path, "lda.dict"), "wb"))

    def load(self, path):
        self.model = LdaMulticore.load(os.path.join(path, "lda.ml"), mmap="r")
        import pickle
        self.dictionary = pickle.load(open(os.path.join(path, "lda.dict"), "rb"))


class ContentQuantifier(object):

    __instance = None
    __init_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, tfidf, lda, sentiment, word_detector, nb):
        if not ContentQuantifier.__init_flag:
            self.tfidf_model = tfidf
            self.lda_model = lda
            self.sentiment_model = sentiment
            self.keyword_model = word_detector
            self.nb_model = nb

            self.url_re = re.compile("(http://t\.cn/[a-zA-Z]*)")
            self.hashtag_re = re.compile("(#.*?#)")
            self.mention_re = re.compile("(@.*?) ")
            self.telephone_re = re.compile("1[34578][0-9]{9}")

            ContentQuantifier.__init_flag = True

    @timing
    def quantify(self, encoded_raw_text):
        """
        Transform the raw text(string) into predefined vector representation.

        :param encoded_raw_text: String text

        :return: Numpy array
        """

        results = []

        tfidf_score = self.tfidf_model.predict([" ".join(cut_words(encoded_raw_text.decode("utf-8")))])[0]
        nb_score = self.nb_model.model.predict_proba(tfidf_score.reshape(1, -1)).tolist()
        results.append(nb_score[0][1])

        topic_score = self.lda_model.predict(self.lda_model.prepare_data([cut_words(encoded_raw_text.decode("utf-8"))]))[0][0][0]
        sentiment_score = self.sentiment_model.predict([encoded_raw_text.decode("utf-8")])[0]
        results.append(topic_score)
        results.append(sentiment_score)

        entities = list(chain(*extract_entities(encoded_raw_text.decode("utf-8")).values()))
        target_score = np.average(np.asarray(pmi_multi_query(entities)), axis=0)
        target_score = target_score if not np.isnan(np.average(np.asarray(pmi_multi_query(entities)), axis=0)) else 0.0
        results.append(target_score)

        keyword_score = float(len(self.keyword_model.find(encoded_raw_text)) / (len(cut_words(encoded_raw_text)) + 1))
        results.append(keyword_score)

        url_score = len(self.url_re.findall(encoded_raw_text))
        hashtag_score = len(self.hashtag_re.findall(encoded_raw_text))
        mention_score = len(self.mention_re.findall(encoded_raw_text))
        telephone_score = len(self.telephone_re.findall(encoded_raw_text))

        results.extend([url_score, hashtag_score, mention_score, telephone_score])

        return results


class KmeansModel(object):
    __instance = None
    __init_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, random_state=10):

        if not KmeansModel.__init_flag:
            self.n_clusters = None
            self.random_state = random_state
            self.km_model = None
            self.score = None
            KmeansModel.__init_flag = True

    def train(self, x, search=(10, 50)):
        k_range = range(*search)
        models = []
        for k in k_range:
            model = MiniBatchKMeans(n_clusters=k, random_state=self.random_state)
            model.fit(x)
            score = model.score(x)
            models.append((k, score))
            logger.info("KMeansModel selection: k - {0} with score {1}".format(k, score))
        self.n_clusters, self.score = sorted(models, key=lambda x:x[-1], reverse=True)[0]
        self.km_model = MiniBatchKMeans(n_clusters=self.n_clusters, random_state=self.random_state)
        self.km_model.fit(x)
        logger.info("Best KMeansModel: k - {0} with score {1}".format(self.n_clusters, self.score))

    def update(self, x):
        self.km_model.partial_fit(x)

    def predict(self, x):

        return self.km_model.predict(x)

    def get_similar(self, x, target):

        predictions = self.predict(x)
        target_prediction = self.predict(target)

        return [x[i] for i in [j for j, v in enumerate(predictions) if v == target_prediction[0]]]

    def save(self, path, name):
        save_model(self.km_model, path, name)

    def load(self, path, name):
        self.km_model = load_model(path, name)


class Doc2VecModel(object):
    __instance = None
    __init_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):

        if not Doc2VecModel.__init_flag:

            self.doc2vec_model = None

            Doc2VecModel.__init_flag = True

    def train(self, documents, emb_size=100, window=8, min_count=2, workers=4):
        self.doc2vec_model = Doc2Vec(documents, size=emb_size, window=window, min_count=min_count, workers=workers)

    def save(self, path, name):
        self.doc2vec_model.save(os.path.join(path, name))

    def load(self, path, name):
        self.doc2vec_model = Doc2Vec.load(os.path.join(path, name))

    @staticmethod
    def load_data(documents, tokens_only=False, limit=10000):
        """
        Generate documents from raw documents.

        :param limit: Maximum number of lines.

        :param documents: Raw documents.

        :param tokens_only: Whether the document is tagged(for training) or not

        :return: A document at a time.

        """

        for i, line in enumerate(documents):
            if i > limit:
                break
            if tokens_only:
                yield gensim.utils.simple_preprocess(line)
            else:
                yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), [i])

    def predict(self, x):
        """
        Infer vectors given documents.

        :param x: A list of documents, each document is a list of words.

        :return: A list of vectors.
        """
        return [self.doc2vec_model.infer_vector(y) for y in x]


def similarity(target, reference, model=None, scaled=False):
    """
    Calculate the similarity between target and reference text using method.

    :param scaled: Scale the result to [0, 1, 2, 3] for front-web use.

    :param target: Target text, encoded.

    :param reference: Reference text, encoded.

    :param model: One of tfidf model or doc2vec model.

    :return: A float number in [0, 1] scale.
    """

    result = 0.0

    if model:
        vectors = np.asarray(model.predict([target.decode("utf-8"), reference.decode("utf-8")]))
        result = cosine_similarity(vectors[0].reshape(1, -1), vectors[1].reshape(1, -1))[0][0]

    if not scaled:
        return result
    else:
        return int(math.floor(abs(result)/0.25))


if __name__ == '__main__':

    #################
    # SentimentTest #
    #################


    #################
    # Train Test    #
    #################

    # sentiment = SentimentClassifier(n_epoch=20)
    # x, y = sentiment.load_data("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/TrainSet/zh_SA_DATA")
    # sentiment.load_dictionaries("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_EMB/zh.bin")
    # embedding = sentiment.get_embedding_layer()
    # x_train, x_test, y_train, y_test = sentiment.prepare_data(x, y)
    #
    # sentiment.build(embedding)
    # sentiment.train(x_train, y_train)
    # sentiment.test(x_test, y_test)
    #
    # sentiment.save("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_SA")
    # sentiment.load("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_SA")
    # sentiment.test(x_test, y_test)
    # sentiment.predict(["这套书太乱，女儿一点看的兴趣都没有。买来就束之高阁了。".decode("utf-8")])

    #################
    # Load Test     #
    #################

    # sentiment = SentimentClassifier()
    # sentiment.load_dictionaries("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_EMB/zh.bin")
    # sentiment.load("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_SA")
    # result = sentiment.predict(["这本书写的不怎么样,好像是杜拉拉在写日记一样，很多内容没有实质的励志性信息，就跟普通的一般公司职员的情况差不多，只是在强调杜拉拉是怎样一步步发展的，有点像是在炫耀自己的能力。".decode("utf-8")])
    # print(result)

    #################
    # TFIDF Test    #
    #################

    # test = ["『 中共 的 另一面 令 所有 敌人 胆寒 ！ （ 深度 好文 ） 』 O 中共 的 另一面 令 所有 敌人 胆寒 ！ （ 深度 好文 ）  ".decode("utf-8")]
    #
    # model = TFIDFModel()
    # corpus = TFIDFModel.load_file('/home/maxen/Documents/Code/PycharmProjects/PrepareData/weibos.txt')
    # model.fit(corpus)
    # corpus_fitted = model.predict(test)
    #
    # model.save("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_TFIDF")
    # model.load("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_TFIDF")
    # corpus_pred = model.predict(test)
    #
    # print(corpus_pred)

    #################
    # NB Test       #
    #################

    # tfidf_model = TFIDFModel()
    # tfidf_model.load("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_TFIDF")
    #
    # tfidf_neg_corpus = tfidf_model.predict(
    #     TFIDFModel.load_file('/home/maxen/Documents/Code/PycharmProjects/PrepareData/weibos.txt'))
    # tfidf_neg_tags = [0] * len(tfidf_neg_corpus)
    #
    # tfidf_pos_corpus = tfidf_model.predict(
    #     TFIDFModel.load_file('/home/maxen/Documents/Code/PycharmProjects/PrepareData/rumors.txt'))
    # tfidf_pos_tags = [1] * len(tfidf_pos_corpus)
    #
    # x = np.concatenate((tfidf_pos_corpus, tfidf_neg_corpus))
    # y = tfidf_pos_tags + tfidf_neg_tags
    #
    # x_train, x_test, y_train, test_y = train_test_split(x, y, test_size=0.1, random_state=42)
    #
    # nb = NBModel()
    # nb.train(x_train, y_train)
    # y_pred = nb.predict(x_test)
    #
    # print('AUC: %.4f' % metrics.roc_auc_score(test_y, y_pred))
    # print('ACC: %.4f' % metrics.accuracy_score(test_y, y_pred))
    # print('Recall: %.4f' % metrics.recall_score(test_y, y_pred))
    # print('Precision: %.4f' % metrics.precision_score(test_y, y_pred))
    # print('F1-score: %.4f' % metrics.f1_score(test_y, y_pred))
    #
    # nb.save("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_NB", "nb.ml")

    ##############
    # LDA Model  #
    ##############

    # lda_model = LDAModel()
    # corpus = [a.split() for a in
    #           open('/home/maxen/Documents/Code/PycharmProjects/PrepareData/all.txt', "r").readlines()]
    # corpus = lda_model.load_data(corpus)
    #
    # lda_model.train(corpus, 30)
    # lda_model.predict(corpus)
    #
    # lda_model.save("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_LDA")
    # lda_model.load("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_LDA")
    #
    # result = lda_model.predict(corpus[1])
    #
    # print(corpus[1])
    # print(result)

    ################
    # Content Test #
    ################

    # test = "这本书写的不怎么样,好像是杜拉拉在写日记一样，很多内容没有实质的励志性信息，就跟普通的一般公司职员的情况差不多，只是在强调杜拉拉是怎样一步步发展的，有点像是在炫耀自己的能力。"
    #
    # lda_model = LDAModel()
    # lda_model.load("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_LDA")
    #
    # nb = NBModel()
    # nb.load("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_NB", "nb.ml")
    #
    # tfidf_model = TFIDFModel()
    # tfidf_model.load("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_TFIDF")
    #
    # sentiment = SentimentClassifier(n_epoch=20)
    # sentiment.load("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_SA")
    #
    # keyword_detector = KeywordDetector()
    # keyword_detector.load_keywords_from_dir("/home/maxen/Documents/Code/PycharmProjects/rumor_tools/test_data_dir")
    #
    # c_quantifier = ContentQuantifier(tfidf_model, lda_model, sentiment, keyword_detector, nb)
    # result = c_quantifier.quantify(test)
    #
    # print(result)

    ################
    #  KmeansModel #
    ################

    # kmeans = KmeansModel()
    #
    # tfidf_model = TFIDFModel()
    # tfidf_model.load("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_TFIDF")
    #
    # corpus = tfidf_model.predict(TFIDFModel.load_file('/home/maxen/Documents/Code/PycharmProjects/PrepareData/weibos.txt'))
    #
    # kmeans.train(corpus, (165, 166))
    #
    # kmeans.save("/home/maxen/Documents/Code/PycharmProjects/MyWeb/MyWeb/web/rumor/data/kmeans", "kmeans.pkl")


    ################
    # Doc2Vec Test #
    ################

    # doc2vec = Doc2VecModel()
    # documents = open("/home/maxen/Documents/Code/PycharmProjects/PrepareData/weibos.txt").readlines()
    # documents = doc2vec.load_data(documents, limit=100000)
    # doc2vec.train(documents, workers=8)
    # doc2vec.save("/home/maxen/Documents/Code/PycharmProjects/MyWeb/MyWeb/web/rumor/data/doc2vec_model/model_file",
    #              "model.doc2vec")

    ###################
    # Similarity Test #
    ###################

    # test = ["毕业 以来 陪伴 你 的 第二个 年头 ， 在 学校 的 时候 没 办法 跟 你 一起 飞 ， 一 毕业 就 立马 飞奔 到 你 的 城市 ， 距离 上 一次 生日 见面会 是 370 天 ， 虽然 每次 都 "
    #         "是 排队 3 小时 ， 签名 三十秒 ， 每次 都 被 人 讲 都 这么 大 了 还 追星 ， 还 经常 被 嫌弃 ， 可是 我 喜欢 啊 哈哈哈 ， 又 有 什么 办法 呢 ， 对 了 ， 你 比 上 一次 "
    #         "见到 好像 又 瘦 了 ， 刚好 我 也 是 新书 大卖 大卖 @ 吳大偉 DvWooooo @ 吳大偉 DvWooooo   @ 梁上 進 henderson   | 广州 · 天河 ...",
    #         "毕业 以后 陪伴 你 的 第三个 年头 ， 在 学校 的 时候 没 办法 跟 你 一起 飞 ， 一 毕业 就 立马 飞奔 到 你 的 家乡 ， 距离 上 一次 生日 见面会 是 370 天 ， 虽然 每次 都 "
    #         "是 排队 3 小时 ， 签名 三十秒 ， 每次 都 被 人 讲 都 这么 大 了 还 追星 ， 还 经常 被 嫌弃 ， 可是 我 喜欢 啊 哈哈哈 ， 又 有 什么 办法 呢 ， 对 了 ， 你 比 上 一次 "
    #         "见到 好像 又 瘦 了 ， 刚好 我 也 是 新书 大卖 大卖 @ 吳大偉 DvWooooo @ 吳大偉 DvWooooo   @ 梁上 進 henderson   | 广州 · 天河 ..."]
    #
    # tfidf_model = TFIDFModel()
    # tfidf_model.load("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/Models/zh_TFIDF")
    #
    # doc2vec = Doc2VecModel()
    # doc2vec.load("/home/maxen/Documents/Code/PycharmProjects/MyWeb/MyWeb/web/rumor/data/doc2vec_model/model_file", "model.doc2vec")
    #
    # print(similarity(test[0].decode("utf-8"), test[1].decode("utf-8"), tfidf_model, scaled=True))
    # print(similarity(test[0], test[1], doc2vec, scaled=True))

    pass


