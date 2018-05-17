# -*- coding: utf-8 -*-
import random
import warnings
import numpy as np
from sklearn.model_selection import StratifiedKFold


# region实用工具
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


# 计算不同样本之间的距离，输入：[m,n]，输出[m,m]，其中dist[i,j]为x[i]到x[j]的距离
def calculate_distance(x):
    # x:样本矩阵
    m = x.shape[0]
    distance = np.zeros([m, m])
    for i in range(m):
        for j in range(m - 1, i, -1):
            distance[i][j] = np.linalg.norm(x[i] - x[j], 2)
            distance[j][i] = distance[i][j]
    return distance


# endregion

# region评价指标
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


# endregion

# region距离度量
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


# 相关系数
def correlation_coefficient(a, b):
    # a：向量1
    # b：向量2
    a = np.array(a).squeeze()
    b = np.array(b).squeeze()
    if len(a.shape) != 1 or len(b.shape) != 1:
        warnings.warn('数据维度不为1，不执行操作！')
        return None
    return ((a - a.mean()) * (b - b.mean())).mean() / (a.std() * b.std())


# 相关距离
def correlation_distance(a, b):
    # a：向量1
    # b：向量2
    return 1 - correlation_coefficient(a, b)


# 马氏距离
def mahalanobis_distance(x):
    # x:样本
    x = np.array(x)
    if len(x.shape) != 2:
        warnings.warn('数据维度不为2，不执行操作！')
        return None
    m, n = x.shape
    S_inv = np.linalg.pinv(np.cov(x))
    D = np.zeros([m, m])
    for i in range(m):
        for j in range(i + 1, m):
            D[i, j] = np.sqrt((x[i] - x[j]).reshape(1, n).dot(S_inv).dot((x[i] - x[j]).reshape(n, 1)))
            D[j, i] = D[i, j]
    return D


# endregion

# region机器学习

# 主成分分析
def PCA(x, feature_num=None, svd=False):
    # x：样本
    # feature_num：保留的特征数
    x = np.array(x, np.float)
    if len(x.shape) != 1 and len(x.shape) != 2:
        warnings.warn('数据维度不正确，不执行操作！')
        return None
    if len(x.shape) == 1:
        x = np.expand_dims(x, 0)
    if feature_num is None:
        feature_num = x.shape[1]
    x -= x.mean(0, keepdims=True)
    if svd:
        U, S, VT = np.linalg.svd(x)
        index_sort = np.argsort(S)  # 对奇异值进行排序
        index = index_sort[-1:-(feature_num + 1):-1]
        return x.dot(VT.transpose()[:, index])  # 乘上最大的feature_num个特征组成的特征向量
    else:
        eigval, eigvec = np.linalg.eig(x.transpose().dot(x) / x.shape[0])
        index_sort = np.argsort(eigval)  # 对特征值进行排序
        index = index_sort[-1:-(feature_num + 1):-1]
        return x.dot(eigvec[:, index])  # 乘上最大的feature_num个特征组成的特征向量

# endregion
