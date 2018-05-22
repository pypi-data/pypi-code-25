"""
References:
    keras.datasets.imdb

"""
import json
import numpy as np

DATA_PATH = r"D:\OneDrive\workspace\data\nlp\imdb\imdb.npz"
WORD_PATH = r"D:\OneDrive\workspace\data\nlp\imdb\imdb_word_index.json"


def load_data(npz_path=DATA_PATH, num_words=None, skip_top=0,
              maxlen=None, seed=113, start_char=1, oov_char=2, index_from=3):
    """Loads the IMDB dataset.

    Args:
        npz_path(str):
        num_words(int):
            词表规模，按频率降序
        skip_top(int):
            跳过频率最高的几个词（通常是停用词）
        maxlen(int):
            序列最大长度，超过该长度的序列将被过滤
        seed(int):
            随机数种子
        start_char(int):
            序列开始标记，默认值为 1
        oov_char(int):
            如果某些词因为 num_words 或 skip_top 参数被跳过了，则用 oov_char 代替
        index_from(int):
            因为设置了 start_char 和 oov_char，所以真实的词需要往后顺延，默认为 3
            比如，原词典中 {the: 1}，但 the 实际上是 `1+index_from=4`（index_from 默认为 3）

    Returns:
        (x_train, y_train), (x_test, y_test)
            x: array(list[1, ...], list[1, ...])
            y: array([1, 0, ...])

    Raises:
        ValueError: maxlen 设置的太小，导致所有数据都被过滤了

    Notes:
        Note that the 'out of vocabulary' character is only used for
        words that were present in the training set but are not included
        because they're not making the `num_words` cut here.
        Words that were not seen in the training set but are in the test set
        have simply been skipped.

    References:
        keras.datasets.imdb
    """
    with np.load(npz_path) as f:
        x_train, labels_train = f['x_train'], f['y_train']
        x_test, labels_test = f['x_test'], f['y_test']

    np.random.seed(seed)
    indices = np.arange(len(x_train))
    np.random.shuffle(indices)
    x_train = x_train[indices]
    labels_train = labels_train[indices]

    indices = np.arange(len(x_test))
    np.random.shuffle(indices)
    x_test = x_test[indices]
    labels_test = labels_test[indices]

    xs = np.concatenate([x_train, x_test])
    labels = np.concatenate([labels_train, labels_test])

    if start_char is not None:
        xs = [[start_char] + [w + index_from for w in x] for x in xs]
    elif index_from:
        xs = [[w + index_from for w in x] for x in xs]

    if maxlen:
        xs, labels = _remove_long_seq(maxlen, xs, labels)
        if not xs:
            raise ValueError('`maxlen=' + str(maxlen) + '` is so short that no sequence was kept.')
    if not num_words:
        num_words = max([max(x) for x in xs])

    # by convention, use 2 as OOV word
    # reserve 'index_from' (=3 by default) characters:
    # 0 (padding), 1 (start), 2 (OOV)
    if oov_char is not None:
        xs = [[w if (skip_top <= w < num_words) else oov_char for w in x] for x in xs]
    else:
        xs = [[w for w in x if skip_top <= w < num_words] for x in xs]

    idx = len(x_train)
    x_train, y_train = np.array(xs[:idx]), np.array(labels[:idx])
    x_test, y_test = np.array(xs[idx:]), np.array(labels[idx:])

    return (x_train, y_train), (x_test, y_test)


def get_word_index(path=WORD_PATH):
    """获取 word2index
        {"the": 1, "and": 2, ...}
    """
    with open(path) as f:
        return json.load(f)


def _remove_long_seq(maxlen, seq, label):
    new_seq, new_label = [], []
    for x, y in zip(seq, label):
        if len(x) < maxlen:
            new_seq.append(x)
            new_label.append(y)
    return new_seq, new_label

