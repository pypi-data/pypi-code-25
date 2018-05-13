# -*- coding: utf-8 -*-
import numpy as np
import random
import warnings
from sklearn.model_selection import StratifiedKFold


# 生成迭代器
def data_iter(data, label, batch_size):
    # data:样本数据
    # label：样本标签
    # batch_size：批大小
    data, label = np.array(data), np.array(label)
    n_samples = data.shape[0]
    idx = list(range(n_samples))
    random.shuffle(idx)
    for i in range(0, n_samples, batch_size):
        j = np.array(idx[i:min(i + batch_size, n_samples)])
        yield np.take(data, j, 0), np.take(label, j, 0)


# 准确率
def accuracy_score(prediction, label):
    # prediction：预测类别或one-hot编码
    # label：实际类别或one-hot编码
    prediction, label = np.array(prediction), np.array(label)
    assert len(prediction.shape) == 1 or len(prediction.shape) == 2
    assert len(label.shape) == 1 or len(label.shape) == 2
    if len(prediction.shape) == 2:
        if prediction.shape[1] == 1:
            prediction = prediction.squeeze()
        else:
            prediction = np.argmax(prediction, 1)
    if len(label.shape) == 2:
        if label.shape[1] == 1:
            label = label.squeeze()
        else:
            label = np.argmax(label, 1)
    return np.mean(np.equal(prediction, label))


# label转one-hot
def to_categorical(label, num_classes=None):
    # label：样本标签
    # num_calsses：总共的类别数
    label = np.array(label, dtype='int')
    if num_classes is not None:
        assert num_classes < label.max()  # 类别数量错误
    num_classes = label.max() + 1
    if len(label.shape) == 1:
        y = np.eye(num_classes)[label]
        return y
    else:
        warnings.warn('Warning: one_hot_to_label do not work')
        return label


# one-hot转label
def one_hot_to_label(y):
    # y：one-hot编码
    y = np.array(y)
    if len(y.shape) == 2 and y.max() == 1 and y.sum(1).mean() == 1:
        return y.argmax(1)
    else:
        warnings.warn('Warning: one_hot_to_label do not work')
        return y


# 均方误差
def MSE(prediction, y, feature_importance=None):
    # prediction：预测值
    # y:真实值
    # feature_importance：特征重要性权重
    prediction, y = np.array(prediction).squeeze(), np.array(y).squeeze()
    assert len(prediction.shape) == 1 and len(y.shape) == 1
    if feature_importance is None:
        return np.mean(np.square(prediction - y))
    else:
        feature_importance = np.array(feature_importance)
        assert feature_importance.shape[0] == prediction.shape[0]
        return np.mean(feature_importance * np.square(prediction - y))


# 均方根误差
def RMSE(prediction, y, feature_importance=None):
    # prediction：预测值
    # y:真实值
    # feature_importance：特征重要性权重
    prediction, y = np.array(prediction).squeeze(), np.array(y).squeeze()
    assert len(prediction.shape) == 1 and len(y.shape) == 1
    if feature_importance is None:
        return np.sqrt(np.mean(np.square(prediction - y)))
    else:
        feature_importance = np.array(feature_importance)
        assert feature_importance.shape[0] == prediction.shape[0]
        return np.sqrt(np.mean(feature_importance * np.square(prediction - y)))


# 平均绝对误差
def MAE(prediction, y, feature_importance=None):
    # prediction：预测值
    # y:真实值
    # feature_importance：特征重要性权重
    prediction, y = np.array(prediction).squeeze(), np.array(y).squeeze()
    assert len(prediction.shape) == 1 and len(y.shape) == 1
    if feature_importance is None:
        return np.mean(np.abs(prediction - y))
    else:
        feature_importance = np.array(feature_importance)
        assert feature_importance.shape[0] == prediction.shape[0]
        return np.mean(feature_importance * np.abs(prediction - y))


# 误差平方和
def SSE(prediction, y, feature_importance=None):
    # prediction：预测值
    # y:真实值
    # feature_importance：特征重要性权重
    prediction, y = np.array(prediction).squeeze(), np.array(y).squeeze()
    assert len(prediction.shape) == 1 and len(y.shape) == 1
    if feature_importance is None:
        return np.sum(np.square(prediction - y))
    else:
        feature_importance = np.array(feature_importance)
        assert feature_importance.shape[0] == prediction.shape[0]
        return np.sum(feature_importance * np.square(prediction - y))


# 总平方和
def SST(y, feature_importance=None):
    # y:真实值
    # feature_importance：特征重要性权重
    y = np.array(y)
    assert len(y.shape) == 1
    if feature_importance is None:
        return np.sum(np.square(y - np.mean(y)))
    else:
        feature_importance = np.array(feature_importance)
        assert feature_importance.shape[0] == y.shape[0]
        return np.sum(feature_importance * np.square(y - np.mean(y)))


# 回归平方和
def SSR(prediction, y, feature_importance=None):
    # prediction：预测值
    # y:真实值
    # feature_importance：特征重要性权重
    prediction, y = np.array(prediction).squeeze(), np.array(y).squeeze()
    assert len(prediction.shape) == 1 and len(y.shape) == 1
    assert len(y.shape) == 1
    if feature_importance is None:
        return np.sum(np.square(prediction - np.mean(y)))  # Total sum of squares
    else:
        feature_importance = np.array(feature_importance)
        assert feature_importance.shape[0] == prediction.shape[0]
        return np.sum(feature_importance * np.square(prediction - np.mean(y)))


# 确定系数
def R_square(prediction, y, feature_importance=None):
    # prediction：预测值
    # y:真实值
    # feature_importance：特征重要性权重
    return 1 - SSE(prediction, y, feature_importance) / SST(y, feature_importance)


# K折交叉验证
def cross_val_score(estimator, x, y, k=10, verbose=True):
    # estimator：待评价的模型
    # x：样本数据
    # y：样本标签
    folder = StratifiedKFold(k, True, 0)
    scores = []
    for i, (train_index, test_index) in enumerate(folder.split(x, y)):
        estimator.fit(x[train_index], y[train_index])
        score = estimator.score(x[test_index], y[test_index])
        scores.append(score)
        if verbose:
            print('第%d次交叉验证完成，得分为%.4f' % (i + 1, score))
    scores = np.array(scores)
    return scores


# 闵可夫斯基距离
def minkowski_distance(a, b, p):
    # a：向量1
    # b：向量2
    # p：参数（阶数）
    a = np.array(a).squeeze()
    b = np.array(b).squeeze()
    if len(a.shape) != 1 or len(b.shape) != 1:
        warnings.warn('数据维度不为1，不执行操作！')
        return None
    return np.power(np.sum(np.power(np.abs(a - b), p)), 1 / p)


# l1范数
def l1_distance(a, b):
    # a：向量1
    # b：向量2
    return minkowski_distance(a, b, 1)


# 曼哈顿距离
def manhattan_distance(a, b):
    # a：向量1
    # b：向量2
    return minkowski_distance(a, b, 1)


# l2范数
def l2_distance(a, b):
    # a：向量1
    # b：向量2
    return minkowski_distance(a, b, 2)


# 欧拉距离
def euclidean_distance(a, b):
    # a：向量1
    # b：向量2
    return minkowski_distance(a, b, 2)


# 切比雪夫距离
def chebyshev_distance(a, b):
    # a：向量1
    # b：向量2
    a = np.array(a).squeeze()
    b = np.array(b).squeeze()
    if len(a.shape) != 1 or len(b.shape) != 1:
        warnings.warn('数据维度不为1，不执行操作！')
        return None
    return np.max(np.abs(a - b))


# 夹角余弦
def cosine(a, b):
    # a：向量1
    # b：向量2
    a = np.array(a).squeeze()
    b = np.array(b).squeeze()
    if len(a.shape) != 1 or len(b.shape) != 1:
        warnings.warn('数据维度不为1，不执行操作！')
        return None
    return a.dot(b) / (np.linalg.norm(a, 2) * np.linalg.norm(b, 2))


# 汉明距离
def hamming_distance(a, b):
    # a：向量1
    # b：向量2
    a = np.array(a, np.str).squeeze()
    b = np.array(b, np.str).squeeze()
    if len(a.shape) != 1 or len(b.shape) != 1:
        warnings.warn('数据维度不为1，不执行操作！')
        return None
    return np.sum(a != b)


# 杰拉德相似系数
def jaccard_similarity_coefficient(a, b):
    # a：向量1
    # b：向量2
    a = set(a)
    b = set(b)
    return len(a.intersection(b)) / len(a.union(b))


# 杰拉德距离
def jaccard_distance(a, b):
    # a：向量1
    # b：向量2
    return 1 - jaccard_similarity_coefficient(a, b)
