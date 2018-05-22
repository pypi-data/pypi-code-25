"""

References:
    tl.layers
"""
import tensorflow as tf
import tensorlayer as tl


def embedding(inputs,
              vocabulary_size=80000,
              embedding_size=100,
              E_init=tf.random_uniform_initializer(-0.1, 0.1),
              E_init_args=None,
              name='embedding'):
    """
    最简单的 embedding 层，不使用预训练的参数

    Args:
        inputs:
        vocabulary_size:
        embedding_size:
        E_init:
        E_init_args:
        name:

    Returns:

    """
    with tf.variable_scope(name):
        embeddings = tf.get_variable('embeddings', shape=(vocabulary_size, embedding_size), dtype=tf.float32,
                                     initializer=E_init,
                                     **(E_init_args or {}))
        embed = tf.nn.embedding_lookup(embeddings, inputs)

    return embed, embeddings


def embedding_pre_trained(inputs,
                          name='embedding'):
    """
    使用预训练的词向量
        因为 tf 无法创建超过 2G 的变量，所以正确的做法是使用 placeholder

    Args:
        inputs:

    Returns:

    """
    with tf.variable_scope(name):
        embeddings = tf.placeholder(tf.float32, shape=[None, None], name="embeddings")
        embed = tf.nn.embedding_lookup(embeddings, inputs)

    return embed, embeddings


def embedding_average():
    """"""
