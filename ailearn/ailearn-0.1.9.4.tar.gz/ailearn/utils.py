# -*- coding: utf-8 -*-
import numpy as np
import random
import warnings


# 生成迭代器
def data_iter(data, label, batch_size):
    data, label = np.array(data), np.array(label)
    n_samples = data.shape[0]
    idx = list(range(n_samples))
    random.shuffle(idx)
    for i in range(0, n_samples, batch_size):
        j = np.array(idx[i:min(i + batch_size, n_samples)])
        yield np.take(data, j, 0), np.take(label, j, 0)


# 准确率
def accuracy_score(prediction, label):
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
    y = np.array(y)
    if len(y.shape) == 2 and y.max() == 1 and y.sum(1).mean() == 1:
        return y.argmax(1)
    else:
        warnings.warn('Warning: one_hot_to_label do not work')
        return y


# 均方误差
def MSE(prediction, y, feature_importance=None):
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
    return 1 - SSE(prediction, y, feature_importance) / SST(y, feature_importance)
