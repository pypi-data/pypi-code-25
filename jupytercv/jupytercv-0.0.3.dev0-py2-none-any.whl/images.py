from io import BytesIO

from PIL import Image
import numpy as np
import cv2
import requests


class UImage(np.ndarray):
    def __new__(cls, img_path=None, img_url=None, *args, **kwargs):
        if img_path:
            img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        if img_url:
            res = requests.get(img_url)
            image_data = BytesIO(res.content).read()

            # Decode image
            img = cv2.imdecode(np.fromstring(image_data, np.uint8), cv2.IMREAD_COLOR)

        kwargs.update(shape=img.shape, dtype=img.dtype, buffer=img)
        obj = super(UImage, cls).__new__(cls, *args, **kwargs)

        obj._cspace = 'BGR'

        return obj

    def ascolor(self, cspace):
        if self._cspace == cspace:
            return self

        color_conversion = getattr(cv2, 'COLOR_{}2{}'.format(self._cspace, cspace), None)
        obj = cv2.cvtColor(self, color_conversion).view(UImage)
        obj._cspace = cspace

        return obj

    @property
    def pil_img(self):
        return Image.fromarray(self.ascolor('RGB'))
