"""

"""
import tensorflow as tf
import tensorlayer as tl

# from .cnn import *
# from .rnn import *
from .attention import *
from .embedding import *

logging = tf.logging


def dense(inputs, n_units,
          activation=tf.nn.relu,
          use_bias=True,
          W_init=tf.truncated_normal_initializer(stddev=0.1),
          W_init_args=None,
          b_init=tf.constant_initializer(value=0.0),
          b_init_args=None,
          name="dense",
          reuse=None):
    """全连接层

    input_shape: [batch_size, n_features]
    output_shape: [batch_size, n_units]

    References:
        tf.layers.Dense
        tl.layers.DenseLayer
    """
    W_init_args = {} if W_init_args is None else W_init_args
    b_init_args = {} if b_init_args is None else b_init_args

    logging.info("DenseLayer: %s - n_units: %d activation: %s" % (name, n_units, activation.__name__))

    # n_inputs = int(tf.convert_to_tensor(inputs).get_shape()[-1])
    inputs = tf.convert_to_tensor(inputs)
    n_inputs = inputs.get_shape()[-1].value

    with tf.variable_scope(name, reuse=reuse):
        W = tf.get_variable('W', shape=[n_inputs, n_units], initializer=W_init, dtype=tf.float32,
                            **W_init_args)
        if use_bias:
            b = tf.get_variable('b', shape=[n_units], initializer=b_init, dtype=tf.float32,
                                **b_init_args)
            # outputs = act(tf.matmul(inputs, W) + b)
            outputs = activation(tf.nn.xw_plus_b(inputs, W, b))
        else:
            outputs = activation(tf.matmul(inputs, W))

    return outputs
