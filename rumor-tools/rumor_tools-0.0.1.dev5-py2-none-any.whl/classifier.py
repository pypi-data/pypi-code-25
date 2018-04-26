#!/usr/bin/env python
# encoding: utf-8


"""
A GBT classifier for classification.
"""
import json
import logging
import os
import pickle
import re
import xml

import xgboost as xgb
from keras import Input, Model
from keras.layers import Embedding, Conv1D, Dropout, Flatten, Dense, LSTM, Add
from keras.models import load_model
from keras.preprocessing import sequence
from sklearn import metrics
import numpy as np
import tensorflow as tf
from gensim.models import word2vec
from xgboost import plot_tree

from rumor_tools import save_model
from rumor_tools.preprocess import cut_words, cut_sub_sentences
from rumor_tools.quantifier import ContentQuantifier

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class XGBoostModel(object):

    def __init__(self):
        self.model = xgb.Booster()

    def train(self, params, train_data=None, eval_data=None):
        self.model = xgb.train(params=params, dtrain=train_data, evals=eval_data, num_boost_round=5)

    def predict(self, data, **kargs):
        return self.model.predict(data, **kargs)

    def save(self, path):
        self.model.save_model(os.path.join(path, "boost.mdl"))

    def load(self, path):
        self.model = self.model.load_model(os.path.join(path, "boost.mdl"))

    @staticmethod
    def load_data(path):
        train_data = xgb.DMatrix(os.path.join(path, "train.csv"))
        test_data = xgb.DMatrix(os.path.join(path, "test.csv"))

        return train_data, test_data


class EmotionHandler(xml.sax.ContentHandler):

    def __init__(self):
        self.CurrentData = ""
        self.id = ""
        self.category = ""
        self.clauses = []
        self.causes = []
        self.keywords = []

        self.emotions = []

    # 元素开始事件处理
    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "emotionml":
            self.clauses = []
            self.causes = []
            self.keywords = []
            # print("*****Emotion*****")
        elif tag == "category":
            self.category = attributes['name']
        elif tag == "clause":
            self.causes.append(0 if attributes['cause'] == "N" else 1)

    # 元素结束事件处理
    def endElement(self, tag):
        if tag == "category":
            # print("Category:", self.category)
            pass
        elif tag == "emotion":
            self.emotions.append({
                'id': self.id,
                'clauses': [str(clause.encode("utf-8")).strip(" ") for clause in self.clauses if
                            len(str(clause.encode("utf-8")).strip(" ")) > 1],
                'keywords': [str(keyword.encode("utf-8")).strip(" ") for keyword in self.keywords if
                             len(str(keyword.encode("utf-8")).strip(" ")) > 1],
                'causes': self.causes,
                'category': self.category
            })
        self.CurrentData = ""

    # 内容事件处理
    def characters(self, content):
        if self.CurrentData == "text":
            self.clauses.append(content)
        elif self.CurrentData == "keywords":
            self.keywords.append(content)


class EmotionCause(object):
    __instance = None
    __init_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, max_words=40000, max_len=400, batch_size=32, embedding_dims=300,
                 filters=250, kernel_size=3, epochs=2, word2vec=None):

        np.random.seed(12345)

        if EmotionCause.__init_flag is False:
            # set parameters:
            self.max_words = max_words
            self.max_len = max_len
            self.batch_size = batch_size
            self.embedding_dims = embedding_dims
            self.__filters = filters
            self.__kernel_size = kernel_size
            self.__epochs = epochs

            self.word2idx = {}
            self.idx2word = {}
            self.word2vec_model = None
            self.vocab = None
            self.model = None

            self.word2vec_model = word2vec
            self.vocab = self.word2vec_model.wv.vocab

            self.graph = tf.get_default_graph()

            for i, word in enumerate(self.vocab):
                self.word2idx[word] = i
                self.idx2word[i] = word

            EmotionCause.__init_flag = True

    def load_model(self, other_parameters_file, model_file):

        with open(other_parameters_file, "rb") as f:
            self.max_words, self.max_len, self.batch_size, self.embedding_dims, self.__filters, self.__kernel_size, self.__epochs, self.word2idx, self.idx2word = pickle.load(f)

        self.model = load_model(model_file)

    def save_model(self, other_parameters_file, model_file):

        with open(other_parameters_file, "wb+") as f:
            pickle.dump((self.max_words, self.max_len, self.batch_size, self.embedding_dims, self.__filters, self.__kernel_size, self.__epochs, self.word2idx, self.idx2word), f, 2)

        self.model.save(model_file)

    def load_data(self, path=""):
        (X_train, y_train), (X_test, y_test) = self._load(path=path, num_words=self.max_words)
        X_train = sequence.pad_sequences(X_train, maxlen=self.max_len)
        X_test = sequence.pad_sequences(X_test, maxlen=self.max_len)
        return X_train, y_train, X_test, y_test

    def build_model(self):

        num_words = max(self.max_words, len(self.vocab))
        embedding_matrix = np.zeros((num_words, self.embedding_dims))
        for i, word in enumerate(self.vocab):
            if i >= self.max_words:
                continue
            embedding_vector = self.word2vec_model.wv[word]
            if embedding_vector is not None:
                embedding_matrix[i] = embedding_vector

        # _load pre-trained word embeddings into an Embedding layer
        # note that we set trainable = False so as to keep the embeddings fixed

        data_input_right = Input(shape=(400,), dtype='int32', )
        embed_right = Embedding(num_words,
                                self.embedding_dims,
                                weights=[embedding_matrix],
                                input_length=self.max_len,
                                trainable=False)(data_input_right)

        conv = Conv1D(filters=10, kernel_size=self.__kernel_size, activation="relu", padding="valid", strides=1)(
            embed_right)
        dropout = Dropout(0.25)(conv)
        flatten = Flatten()(dropout)
        output_right = Dense(128)(flatten)

        data_input_left = Input(shape=(400,), dtype='int32', )
        embed_left = Embedding(num_words,
                               self.embedding_dims,
                               weights=[embedding_matrix],
                               input_length=self.max_len,
                               trainable=False)(data_input_left)
        output_left = LSTM(128, dropout=0.2, return_sequences=False, recurrent_dropout=0.2)(embed_left)

        merged = Add()([output_right, output_left])
        final_output = Dense(1, activation='sigmoid')(merged)

        self.model = Model(inputs=[data_input_right, data_input_left], outputs=final_output)

    def train(self, X_train, y_train, X_test, y_test):

        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.model.fit([X_train, X_train], y_train)
        score, acc = self.model.evaluate([X_test, X_test], y_test, batch_size=self.batch_size)

        logger.info('Test score: {0}'.format(score))
        logger.info('Test accuracy: {1}'.format(acc))

        from keras.utils.vis_utils import plot_model

        plot_model(self.model, to_file='model8.png', show_shapes=True)

    def predict(self, corpus,  num_words=None, skip_top=0, maxlen=None, start_char=1, oov_char=2, index_from=3):

        x = []

        for i in range(len(corpus)):
            for j in range(len(corpus[i]['clauses'])):
                # print corpus[i]['causes'][j], list(jieba.cut(corpus[i]['clauses'][j]))
                temp = [self.word2idx[w] if w in self.word2idx.keys() else -5 for w in
                        list(cut_words(corpus[i]['clauses'][j]))]
                x.append(temp)

        x_train = x[:]
        # x_test = x[int(len(x) * 0.5):]
        #
        # np.random.shuffle(x_train)
        # np.random.shuffle(x_test)
        #
        # x_train.extend(x_test)
        xs = x_train

        if start_char is not None:
            xs = [[start_char] + [w + index_from for w in x] for x in xs]
        elif index_from:
            xs = [[w + index_from for w in x] for x in xs]

        if maxlen:
            new_xs = []
            new_labels = []
            for x in xs:
                if len(x) < maxlen:
                    new_xs.append(x)
            xs = new_xs
            labels = new_labels
            if not xs:
                raise ValueError('After filtering for sequences shorter than maxlen=' +
                                 str(maxlen) + ', no sequence was kept. '
                                               'Increase maxlen.')
        if not num_words:
            num_words = max([max(x) for x in xs])

        # by convention, use 2 as OOV word
        # reserve 'index_from' (=3 by default) characters:
        # 0 (padding), 1 (start), 2 (OOV)
        if oov_char is not None:
            xs = [[oov_char if (w >= num_words or w < skip_top) else w for w in x] for x in xs]
        else:
            new_xs = []
            for x in xs:
                nx = []
                for w in x:
                    if skip_top <= w < num_words:
                        nx.append(w)
                new_xs.append(nx)
            xs = new_xs

        x_train = np.array(xs)

        x_train = sequence.pad_sequences(x_train, maxlen=self.max_len)

        result = []

        with self.graph.as_default():

            result = [(i, x) for i, x in enumerate(self.model.predict([x_train, x_train]))]

        return result

    def _load(self, path, num_words=None, skip_top=0, maxlen=None, seed=113, start_char=1, oov_char=2, index_from=3):

        # 创建一个 XMLReader
        parser = xml.sax.make_parser()
        # turn off namepsaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)

        # 重写 ContextHandler
        Handler = EmotionHandler()
        parser.setContentHandler(Handler)

        parser.parse(path)

        corpus = Handler.emotions

        clauses = []
        causes = []

        for emotion in corpus:

            if len(emotion['causes']) != len(emotion['clauses']):
                # print("~" * 100)
                for clause in emotion['clauses']:
                    clauses.append(clause)
                causes.extend(emotion['causes'])
                corpus.remove(emotion)
                continue

            for i in range(len(emotion['clauses'])):
                clauses.append(emotion['clauses'][i])
                causes.extend([emotion['causes'][i]])

        y = []
        x = []

        for i in range(len(corpus)):
            for j in range(len(corpus[i]['clauses'])):
                # print corpus[i]['causes'][j], list(jieba.cut(corpus[i]['clauses'][j]))
                temp = [self.word2idx[w] if w in self.word2idx.keys() else -5 for w in list(cut_words(corpus[i]['clauses'][j]))]
                x.append(temp)
                y.append(corpus[i]['causes'][j])

        x_train = x[:int(len(x)*0.9)]
        labels_train = y[:int(len(y)*0.9)]
        x_test = x[int(len(x)*0.9):]
        labels_test = y[int(len(y)*0.9):]

        np.random.seed(seed)
        np.random.shuffle(x_train)
        np.random.seed(seed)
        np.random.shuffle(labels_train)

        np.random.seed(seed * 2)
        np.random.shuffle(x_test)
        np.random.seed(seed * 2)
        np.random.shuffle(labels_test)

        # print len(x_train), len(x_train[0]),
        # print len(x_test), len(x_test[0])

        # labels_train.extend(labels_test)
        xs = x_train + x_test
        labels = labels_train + labels_test

        if start_char is not None:
            xs = [[start_char] + [w + index_from for w in x] for x in xs]
        elif index_from:
            xs = [[w + index_from for w in x] for x in xs]

        if maxlen:
            new_xs = []
            new_labels = []
            for x, y in zip(xs, labels):
                if len(x) < maxlen:
                    new_xs.append(x)
                    new_labels.append(y)
            xs = new_xs
            labels = new_labels
            if not xs:
                raise ValueError('After filtering for sequences shorter than maxlen=' +
                                 str(maxlen) + ', no sequence was kept. '
                                 'Increase maxlen.')
        if not num_words:
            num_words = max([max(x) for x in xs])

        # by convention, use 2 as OOV word
        # reserve 'index_from' (=3 by default) characters:
        # 0 (padding), 1 (start), 2 (OOV)
        if oov_char is not None:
            xs = [[oov_char if (w >= num_words or w < skip_top) else w for w in x] for x in xs]
        else:
            new_xs = []
            for x in xs:
                nx = []
                for w in x:
                    if skip_top <= w < num_words:
                        nx.append(w)
                new_xs.append(nx)
            xs = new_xs

        x_train = np.array(xs[:len(x_train)])
        y_train = np.array(labels[:len(x_train)])

        x_test = np.array(xs[len(x_train):])
        y_test = np.array(labels[len(x_train):])

        return (x_train, y_train), (x_test, y_test)


if __name__ == '__main__':

    ############
    # XGBooost #
    ############

    # model = XGBoostModel()
    # params = {
    #     'booster': 'gbtree',
    #     'gamma': 0.1,  # 用于控制是否后剪枝的参数,越大越保守，一般0.1、0.2这样子。
    #     'max_depth': 6,  # 构建树的深度，越大越容易过拟合
    #     'lambda': 2,  # 控制模型复杂度的权重值的L2正则化项参数，参数越大，模型越不容易过拟合。
    #     'subsample': 0.7,  # 随机采样训练样本
    #     'colsample_bytree': 0.7,  # 生成树时进行的列采样
    #     'min_child_weight': 5,
    #     # 这个参数默认是 1，是每个叶子里面 h 的和至少是多少，对正负样本不均衡时的 0-1 分类而言
    #     # ，假设 h 在 0.01 附近，min_child_weight 为 1 意味着叶子节点中最少需要包含 100 个样本。
    #     # 这个参数非常影响结果，控制叶子节点中二阶导的和的最小值，该参数值越小，越容易 overfitting。
    #     'silent': 0,  # 设置成1则没有运行信息输出，最好是设置为0.
    #     'eta': 0.7,  # 如同学习率
    #     'seed': 1000,
    #     'nthread': 8,  # cpu 线程数
    # }
    #
    # train, test = model.load_data("/home/maxen/Documents/Code/PycharmProjects/Detection/Classifier")
    # model.train(params, train, eval_data=[(test, "eval")])
    # y_pred = model.predict(test)
    #
    # # leaf = model.predict(test, pred_leaf=True)
    # # plot_tree(model.model)
    #
    # # fig = plt.gcf()
    # # fig.set_size_inches(50, 50)
    # # fig.savefig('tree.png')
    #
    # y_pred = [1 if r >= 0.5 else 0 for r in y_pred]
    # test_y = test.get_label()
    #
    # print('AUC: %.4f' % metrics.roc_auc_score(test_y, y_pred))
    # print('ACC: %.4f' % metrics.accuracy_score(test_y, y_pred))
    # print('Recall: %.4f' % metrics.recall_score(test_y, y_pred))
    # print('F1-score: %.4f' % metrics.f1_score(test_y, y_pred))
    # print('Precesion: %.4f' % metrics.precision_score(test_y, y_pred))
    #
    # save_model(model, "./", "xgboost.ml")



    ######################
    # Emotion Cause Test #
    ######################

    PROJECT_PATH = "/home/maxen/Documents/Code/PycharmProjects/MyWeb/MyWeb/web/rumor"
    EMOTION_CAUSE_MODEL = "data/emotion_causes/emotion_model/model_file/model.h5"

    word2vec_model = word2vec.Word2Vec.load("/home/maxen/Documents/Code/PycharmProjects/MyWeb/MyWeb/web/rumor/data/word2vec/zh/zh.bin")

    # emotion_cause = EmotionCause(word2vec=word2vec_model)
    # X_train, y_train, X_test, y_test = emotion_cause.load_data(path="/home/maxen/Documents/Code/PycharmProjects/MyWeb/MyWeb/web/rumor/data/emotion_causes/HLTEmotionml.eml")
    #
    # emotion_cause.build_model()
    # emotion_cause.train(X_train, y_train, X_test, y_test)
    #
    # corpus = [s for s in cut_sub_sentences("上海城管暴力执法，同学的舅妈被打死了，报警了可是公安只说等回复，太可怕了，城管为什么可以这么嚣张？", with_punctuations=False)]
    # ranks = emotion_cause.predict([{'clauses': corpus}])
    # for rank in ranks:
    #     print corpus[rank[0]]
    #
    # emotion_cause.save_model(
    #     os.path.join(PROJECT_PATH, "data/emotion_causes/emotion_model/model_file/parameters.ec"),
    #     os.path.join(PROJECT_PATH, EMOTION_CAUSE_MODEL),
    # )

    # text = "当日凌晨3点左右，达州市达川区大树镇建军村1组肖治兰家民房发生火灾事故，致使房屋垮塌，造成一家6口不幸遇难。其中包括户主肖某、妻子石某，及其两名女儿和两名儿子，年龄最大者为45岁，最小为9岁。"
    #
    # emotion_cause = EmotionCause(word2vec=word2vec_model)
    # emotion_cause.build_model()
    # emotion_cause.load_model(
    #     os.path.join(PROJECT_PATH, "data/emotion_causes/emotion_model/model_file/parameters.ec"),
    #     os.path.join(PROJECT_PATH, EMOTION_CAUSE_MODEL))
    #
    # corpus = [s for s in cut_sub_sentences(text.decode("utf-8"), with_punctuations=False)]
    # print(json.dumps(corpus, ensure_ascii=False))
    # ranks = emotion_cause.predict([{'clauses': corpus}])
    #
    # with open("visualization.html", "w") as html_file:
    #     html_file.write("<head>")
    #     html_file.write("<meta http-equiv=\"Content-Type\" content=\"text/html;charset=utf-8\">")
    #     html_file.write("</head>")
    #     html_file.write("<body>")
    #     alphas = [rank[1] for rank in ranks]
    #     for word, alpha in zip([corpus[rank[0]] + "," for rank in ranks], [alpha/max(alphas) for alpha in alphas]):
    #         html_file.write('<font style="background: rgba(255, 255, 0, %f)">%s</font>\n' % (alpha, word))
    #     html_file.write("</body>")
    #
    #
    # pass

