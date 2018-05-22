"""

References:
    tf.layers
    tl.layers
"""
import tensorflow as tf

logging = tf.logging


def conv1d(inputs, kernel_size, out_channels,
           stride=1,
           activation=tf.nn.relu,
           use_bias=True,
           padding="VALID",
           W_init=tf.truncated_normal_initializer(stddev=0.02),
           W_init_args=None,
           b_init=tf.constant_initializer(value=0.0),
           b_init_args=None,
           data_format="NWC",
           name="conv1d",
           reuse=None):
    """
    1D 卷积

    Args:
        inputs: A 3D tensor with shape `[batch_size, max_length, in_channels]`
        kernel_size: An integer or a tuple/list with one element
        out_channels:
        stride(int):
        activation: default to use `tf.nn.relu`
        use_bias(bool):
        padding(str):
        W_init:
        W_init_args(dict):
        b_init:
        b_init_args(dict):
        data_format(str):
        name(str):
        reuse(bool):

    Returns:
        A 3D tensor with shape `[batch_size, max_length/strides, out_channels]`

    """
    # W_init_args = {} if W_init_args is None else W_init_args
    # b_init_args = {} if b_init_args is None else b_init_args

    inputs = tf.convert_to_tensor(inputs)
    in_channels = inputs.get_shape()[-1].value

    if isinstance(kernel_size, int):
        kernel_size = (kernel_size,)
    kernel_shape = kernel_size + (in_channels, out_channels)

    assert isinstance(stride, int), "stride must be an integer."

    logging.info("Conv1dLayer: %s - kernel_shape: %s strides: %s padding: %s activation: %s" % (
        name, str(kernel_shape), str(stride), padding, activation.__name__))

    with tf.variable_scope(name, reuse=reuse):
        W = tf.get_variable(name='W', shape=kernel_shape, initializer=W_init, dtype=tf.float32,
                            **(W_init_args or {}))
        if use_bias:
            b = tf.get_variable(name='b', shape=kernel_shape[-1:], initializer=b_init, dtype=tf.float32,
                                **(b_init_args or {}))
            outputs = activation(
                tf.nn.bias_add(
                    tf.nn.conv1d(inputs, W, stride=stride, padding=padding, data_format=data_format), b))
        else:
            outputs = activation(
                tf.nn.conv1d(inputs, W, strides=stride, padding=padding, data_format=data_format))

    return outputs


def conv2d(inputs, kernel_size, out_channels,
           strides=(1, 1, 1, 1),
           activation=tf.nn.relu,
           use_bias=True,
           padding="VALID",
           W_init=tf.truncated_normal_initializer(stddev=0.02),
           W_init_args=None,
           b_init=tf.constant_initializer(value=0.0),
           b_init_args=None,
           data_format="NHWC",
           name="conv2d",
           reuse=None):
    """
    2D 卷积

    Args:
        inputs: A 4D tensor with shape `[batch_size, in_height, in_width, in_channels]`
        kernel_size: An integer or a tuple/list with (k_height, k_width)
            特别的，当应用在 NLP 中时，一般置 kernel_size=(n_gram, embedding_size)
        out_channels(int): The number of the out channels
        strides: An integer or a tuple/list of length 4
        activation: default to use `tf.nn.relu`
        use_bias(bool):
        padding(str):
        W_init:
        W_init_args(dict):
        b_init:
        b_init_args(dict):
        data_format(str):
        name(str):
        reuse(bool):

    Returns:
        A 4D `Tensor` with shape `[batch_size, in_height/strides[1], in_width/strides[2], out_channels]`
    """
    inputs = tf.convert_to_tensor(inputs)
    in_channels = inputs.get_shape()[-1].value

    if isinstance(kernel_size, int):
        kernel_size = (kernel_size,) * 2
    kernel_shape = kernel_size + (in_channels, out_channels)  # [kernel_h, kernel_w, in_channels, out_channels]

    if isinstance(strides, int):
        strides = (1,) + (strides,) * 2 + (1,)
    assert len(strides) == 4, "strides must be an integer or a tuple of length 4"

    logging.info("Conv2dLayer: %s - kernel_shape: %s strides: %s padding: %s activation: %s" % (
        name, str(kernel_shape), str(strides), padding, activation.__name__))

    with tf.variable_scope(name, reuse=reuse):
        W = tf.get_variable(name='W', shape=kernel_shape, initializer=W_init, dtype=tf.float32,
                            **(W_init_args or {}))
        if use_bias:
            b = tf.get_variable(name='b', shape=kernel_shape[-1:], initializer=b_init, dtype=tf.float32,
                                **(b_init_args or {}))
            outputs = activation(
                tf.nn.bias_add(
                    tf.nn.conv2d(inputs, W, strides=strides, padding=padding, data_format=data_format), b))
        else:
            outputs = activation(
                tf.nn.conv2d(inputs, W, strides=strides, padding=padding, data_format=data_format))

    return outputs


def conv3d(inputs, kernel_size, out_channels,
           strides=(1, 1, 1, 1, 1),
           activation=tf.nn.relu,
           use_bias=True,
           padding="VALID",
           W_init=tf.truncated_normal_initializer(stddev=0.02),
           W_init_args=None,
           b_init=tf.constant_initializer(value=0.0),
           b_init_args=None,
           data_format="NDHWC",
           name="conv3d",
           reuse=None):
    """
    3D 卷积

    Args:
        inputs: A 5D tensor with shape `[batch_size, in_depth, in_height, in_width, in_channels]`
        kernel_size: An integer or a tuple/list with (k_depth, k_height, k_width)
        out_channels:
        strides: An integer or a tuple/list of length 5
        activation: default to use `tf.nn.relu`
        use_bias:
        padding:
        W_init:
        W_init_args:
        b_init:
        b_init_args:
        data_format:
        name:
        reuse:

    Returns:

    """
    inputs = tf.convert_to_tensor(inputs)
    in_channels = inputs.get_shape()[-1].value

    if isinstance(kernel_size, int):
        kernel_size = (kernel_size,) * 3
    kernel_shape = kernel_size + (in_channels, out_channels)

    if isinstance(strides, int):
        strides = (1,) + (strides,) * 3 + (1,)
    assert len(strides) == 5, "strides must be an integer or a tuple of length 5"

    logging.info("Conv2dLayer: %s - kernel_shape: %s strides: %s padding: %s activation: %s" % (
        name, str(kernel_shape), str(strides), padding, activation.__name__))

    with tf.variable_scope(name, reuse=reuse):
        W = tf.get_variable(name='W', shape=kernel_shape, initializer=W_init, dtype=tf.float32,
                            **(W_init_args or {}))
        if use_bias:
            b = tf.get_variable(name='b', shape=kernel_shape[-1:], initializer=b_init, dtype=tf.float32,
                                **(b_init_args or {}))
            outputs = activation(
                tf.nn.bias_add(
                    tf.nn.conv3d(inputs, W, strides=strides, padding=padding, data_format=data_format), b))
        else:
            outputs = activation(
                tf.nn.conv3d(inputs, W, strides=strides, padding=padding, data_format=data_format))

    return outputs
