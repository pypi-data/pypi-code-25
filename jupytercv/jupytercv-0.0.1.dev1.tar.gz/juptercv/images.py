from PIL import Image
import numpy as np


def pil2np(pil_img):
    return np.asarray(pil_img, dtype=np.uint8)


def np2pil(np_img):
    return Image.fromarray(np_img)
