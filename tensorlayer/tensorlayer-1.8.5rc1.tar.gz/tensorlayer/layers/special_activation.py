# -*- coding: utf-8 -*-

import tensorflow as tf

from .. import _logging as logging
from .core import *

from ..deprecation import deprecated_alias

__all__ = [
    'PReluLayer',
]


class PReluLayer(Layer):
    """
    The :class:`PReluLayer` class is Parametric Rectified Linear layer.

    Parameters
    ----------
    prev_layer : :class:`Layer`
        Previous layer。
    channel_shared : boolean
        If True, single weight is shared by all channels.
    a_init : initializer
        The initializer for initializing the alpha(s).
    a_init_args : dictionary
        The arguments for initializing the alpha(s).
    name : str
        A unique layer name.

    References
    -----------
    - `Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification <http://arxiv.org/pdf/1502.01852v1.pdf>`__

    """

    @deprecated_alias(layer='prev_layer', end_support_version=1.9)  # TODO remove this line for the 1.9 release
    def __init__(
            self,
            prev_layer,
            channel_shared=False,
            a_init=tf.constant_initializer(value=0.0),
            a_init_args=None,
            # restore = True,
            name="prelu_layer"):

        if a_init_args is None:
            a_init_args = {}

        super(PReluLayer, self).__init__(prev_layer=prev_layer, name=name)
        logging.info("PReluLayer %s: channel_shared:%s" % (name, channel_shared))

        self.inputs = prev_layer.outputs

        if channel_shared:
            w_shape = (1, )
        else:
            w_shape = int(self.inputs.get_shape()[-1])

        # with tf.name_scope(name) as scope:
        with tf.variable_scope(name):
            alphas = tf.get_variable(name='alphas', shape=w_shape, initializer=a_init, dtype=LayersConfig.tf_dtype, **a_init_args)
            try:  # TF 1.0
                self.outputs = tf.nn.relu(self.inputs) + tf.multiply(alphas, (self.inputs - tf.abs(self.inputs))) * 0.5
            except Exception:  # TF 0.12
                self.outputs = tf.nn.relu(self.inputs) + tf.mul(alphas, (self.inputs - tf.abs(self.inputs))) * 0.5

        # self.all_layers = list(layer.all_layers)
        # self.all_params = list(layer.all_params)
        # self.all_drop = dict(layer.all_drop)

        self.all_layers.append(self.outputs)
        self.all_params.extend([alphas])
