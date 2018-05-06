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
        prediction = np.argmax(prediction, 1)
    if len(label.shape) == 2:
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