#!/usr/bin/env python
# encoding: utf-8


"""
A GBT classifier for classification.
"""
import os

import xgboost as xgb
from sklearn import metrics
from xgboost import plot_tree

from rumor_tools import save_model
from rumor_tools.quantifier import ContentQuantifier


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


if __name__ == '__main__':

    ############
    # XGBooost #
    ############

    model = XGBoostModel()
    params = {
        'booster': 'gbtree',
        'gamma': 0.1,  # 用于控制是否后剪枝的参数,越大越保守，一般0.1、0.2这样子。
        'max_depth': 6,  # 构建树的深度，越大越容易过拟合
        'lambda': 2,  # 控制模型复杂度的权重值的L2正则化项参数，参数越大，模型越不容易过拟合。
        'subsample': 0.7,  # 随机采样训练样本
        'colsample_bytree': 0.7,  # 生成树时进行的列采样
        'min_child_weight': 5,
        # 这个参数默认是 1，是每个叶子里面 h 的和至少是多少，对正负样本不均衡时的 0-1 分类而言
        # ，假设 h 在 0.01 附近，min_child_weight 为 1 意味着叶子节点中最少需要包含 100 个样本。
        # 这个参数非常影响结果，控制叶子节点中二阶导的和的最小值，该参数值越小，越容易 overfitting。
        'silent': 0,  # 设置成1则没有运行信息输出，最好是设置为0.
        'eta': 0.7,  # 如同学习率
        'seed': 1000,
        'nthread': 8,  # cpu 线程数
    }

    train, test = model.load_data("/home/maxen/Documents/Code/PycharmProjects/Detection/Classifier")
    model.train(params, train, eval_data=[(test, "eval")])
    y_pred = model.predict(test)

    # leaf = model.predict(test, pred_leaf=True)
    # plot_tree(model.model)

    # fig = plt.gcf()
    # fig.set_size_inches(50, 50)
    # fig.savefig('tree.png')

    y_pred = [1 if r >= 0.5 else 0 for r in y_pred]
    test_y = test.get_label()

    print('AUC: %.4f' % metrics.roc_auc_score(test_y, y_pred))
    print('ACC: %.4f' % metrics.accuracy_score(test_y, y_pred))
    print('Recall: %.4f' % metrics.recall_score(test_y, y_pred))
    print('F1-score: %.4f' % metrics.f1_score(test_y, y_pred))
    print('Precesion: %.4f' % metrics.precision_score(test_y, y_pred))

    save_model(model, "./", "xgboost.ml")