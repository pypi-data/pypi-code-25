import os
import tensorflow as tf
from huaytools.utils.bunch import Bunch


class TFConfig(Bunch):
    """"""

    def __init__(self, name=None):
        super(TFConfig, self).__init__()

        self.name = name
        self.out_dir = './out_' + self.name
        os.makedirs(self.out_dir, exist_ok=True)

        self.ckpt_dir = os.path.join(self.out_dir, 'ckpt_' + self.name)

        # config for `tf.Session`, ref: `tf.ConfigProto`
        # more params ref: https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/protobuf/config.proto
        self.sess_config = tf.ConfigProto()
        self.sess_config.allow_soft_placement = True
        self.sess_config.log_device_placement = True  # 主要用来观察平行的情况
        self.sess_config.gpu_options.per_process_gpu_memory_fraction = 0.5
        self.sess_config.gpu_options.allow_growth = True
