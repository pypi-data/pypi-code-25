from __future__ import division
import os
import re
import logging
import numpy
import tensorflow as tf
from bob.ip.color import gray_to_rgb
from bob.io.image import to_matplotlib
from . import download_file
from bob.extension import rc
from bob.extension.rc_config import _saverc


logger = logging.getLogger(__name__)


def prewhiten(img):
    mean = numpy.mean(img)
    std = numpy.std(img)
    std_adj = numpy.maximum(std, 1.0 / numpy.sqrt(img.size))
    y = numpy.multiply(numpy.subtract(img, mean), 1 / std_adj)
    return y


def get_model_filenames(model_dir):
    # code from https://github.com/davidsandberg/facenet
    files = os.listdir(model_dir)
    meta_files = [s for s in files if s.endswith('.meta')]
    if len(meta_files) == 0:
        raise ValueError(
            'No meta file found in the model directory (%s)' % model_dir)
    elif len(meta_files) > 1:
        raise ValueError(
            'There should not be more than one meta file in the model '
            'directory (%s)' % model_dir)
    meta_file = meta_files[0]
    max_step = -1
    for f in files:
        step_str = re.match(r'(^model-[\w\- ]+.ckpt-(\d+))', f)
        if step_str is not None and len(step_str.groups()) >= 2:
            step = int(step_str.groups()[1])
            if step > max_step:
                max_step = step
                ckpt_file = step_str.groups()[0]
    return meta_file, ckpt_file


class FaceNet(object):
    """Wrapper for the free FaceNet variant:
    https://github.com/davidsandberg/facenet

    To use this class as a bob.bio.base extractor::

        from bob.bio.base.extractor import Extractor
        class FaceNetExtractor(FaceNet, Extractor):
            pass
        extractor = FaceNetExtractor()

    And for a preprocessor you can use::

        from bob.bio.face.preprocessor import FaceCrop
        # This is the size of the image that this model expects
        CROPPED_IMAGE_HEIGHT = 160
        CROPPED_IMAGE_WIDTH = 160
        # eye positions for frontal images
        RIGHT_EYE_POS = (46, 53)
        LEFT_EYE_POS = (46, 107)
        # Crops the face using eye annotations
        preprocessor = FaceCrop(
            cropped_image_size=(CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
            cropped_positions={'leye': LEFT_EYE_POS, 'reye': RIGHT_EYE_POS},
            color_channel='rgb'
        )

    """

    def __init__(self,
                 model_path=rc["bob.ip.tensorflow_extractor.facenet_modelpath"],
                 image_size=160,
                 **kwargs):
        super(FaceNet, self).__init__()
        self.model_path = model_path
        self.image_size = image_size
        self.session = None
        self.embeddings = None

    def _check_feature(self, img):
        img = numpy.ascontiguousarray(img)
        if img.ndim == 2:
            img = gray_to_rgb(img)
        assert img.shape[-1] == self.image_size
        assert img.shape[-2] == self.image_size
        img = to_matplotlib(img)
        img = prewhiten(img)
        return img[None, ...]

    def load_model(self):
        if self.model_path is None:
            self.model_path = self.get_modelpath()
        if not os.path.exists(self.model_path):
            self.download_model()
        # code from https://github.com/davidsandberg/facenet
        model_exp = os.path.expanduser(self.model_path)
        if (os.path.isfile(model_exp)):
            logger.info('Model filename: %s' % model_exp)
            with tf.gfile.FastGFile(model_exp, 'rb') as f:
                graph_def = tf.GraphDef()
                graph_def.ParseFromString(f.read())
                tf.import_graph_def(graph_def, name='')
        else:
            logger.info('Model directory: %s' % model_exp)
            meta_file, ckpt_file = get_model_filenames(model_exp)

            logger.info('Metagraph file: %s' % meta_file)
            logger.info('Checkpoint file: %s' % ckpt_file)

            saver = tf.train.import_meta_graph(
                os.path.join(model_exp, meta_file))
            saver.restore(tf.get_default_session(),
                          os.path.join(model_exp, ckpt_file))
        # Get input and output tensors
        self.images_placeholder = self.graph.get_tensor_by_name("input:0")
        self.embeddings = self.graph.get_tensor_by_name("embeddings:0")
        self.phase_train_placeholder = self.graph.get_tensor_by_name(
            "phase_train:0")
        logger.info("Successfully loaded the model.")

    def __call__(self, img):
        images = self._check_feature(img)
        if self.session is None:
            self.session = tf.InteractiveSession()
            self.graph = tf.get_default_graph()
        if self.embeddings is None:
            self.load_model()
        feed_dict = {self.images_placeholder: images,
                     self.phase_train_placeholder: False}
        features = self.session.run(
            self.embeddings, feed_dict=feed_dict)
        return features.flatten()

    def __del__(self):
        tf.reset_default_graph()

    @staticmethod
    def get_rcvariable():
        return "bob.ip.tensorflow_extractor.facenet_modelpath"

    @staticmethod
    def get_modelpath():
        
        # Priority to the RC path
        model_path = rc[FaceNet.get_rcvariable()]

        if model_path is None:
            import pkg_resources
            model_path = pkg_resources.resource_filename(__name__,
                                                         'data/FaceNet/20170512-110547')

        return model_path


    @staticmethod
    def download_model():
        """
        Download and extract the FaceNet files in bob/ip/tensorflow_extractor
        """
        import zipfile
        zip_file = os.path.join(FaceNet.get_modelpath(),
                                "20170512-110547.zip")
        urls = [
            # This is a private link at Idiap to save bandwidth.
            "http://beatubulatest.lab.idiap.ch/private/wheels/gitlab/"
            "facenet_model2_20170512-110547.zip",
            # this works for everybody
            "https://drive.google.com/uc?export=download&id="
            "0B5MzpY9kBtDVZ2RpVDYwWmxoSUk",
        ]

        for url in urls:
            try:
                logger.info(
                    "Downloading the FaceNet model from "
                    "{} ...".format(url))
                download_file(url, zip_file)
                break
            except Exception:
                logger.warning(
                    "Could not download from the %s url", url, exc_info=True)
        else:  # else is for the for loop
            if not os.path.isfile(zip_file):
                raise RuntimeError("Could not download the zip file.")

        # Unzip
        logger.info("Unziping in {0}".format(FaceNet.get_modelpath()))
        with zipfile.ZipFile(zip_file) as myzip:
            myzip.extractall(os.path.dirname(FaceNet.get_modelpath()))

        logger.info("Saving the path `{0}` in the ~.bobrc file".format(FaceNet.get_modelpath()))
        rc[FaceNet.get_rcvariable()] = FaceNet.get_modelpath()
        _saverc(rc)

        # delete extra files
        os.unlink(zip_file)
