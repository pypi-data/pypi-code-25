import io
import requests
from PIL import Image, ImageColor, ImageDraw

from verifai_sdk.version import VERSION

ID_FRONT = 'F'
ID_BACK = 'B'


class VerifaiService:
    api_token = None
    clasifier_urls = []
    base_api_url = 'https://dashboard.verifai.com/api/'
    ssl_verify = True

    def __init__(self, token=None):
        self.__clasifier_roundrobin = 0
        self.api_token = token

    def add_clasifier_url(self, url, skip_unreachable=False):
        try:
            self.__check_clasifier_url(url)
            self.clasifier_urls.append(url)
            return True
        except AssertionError:
            if not skip_unreachable:
                raise ValueError('No server available at that URL')
            return False

    def get_model_data(self, id_uuid):
        data = self.__get_from_api('id-models', params={'uuid': id_uuid})
        if data:
            return data[0]  # Get first result because a unique key is queried
        return None

    def mask_image_with_uuid(self, image, id_uuid):
        pass

    def mask_image_with_coords(self, image, coords):
        pass

    def classify_image(self, image):
        r = requests.post(
            self.__get_clasifier_url(),
            files={'file': image}
        )
        response = r.json()
        if response['status'] == 'SUCCESS':
            return VerifaiDocument(response, image, self)
        return None

    def classify_image_path(self, image_path):
        f = open(image_path, 'rb')
        i = f.read()
        return self.classify_image(i)

    def __get_clasifier_url(self):
        index = self.__clasifier_roundrobin
        if self.clasifier_urls[index]:
            if index + 1 >= len(self.clasifier_urls):
                self.__clasifier_roundrobin = 0
            else:
                self.__clasifier_roundrobin = index + 1
            return self.clasifier_urls[index]
        raise ValueError("No clasifier URLs. Set one first with add_clasifier_url(url)")

    def __get_from_api(self, path, params):
        headers = {
            'Authorization': 'Token ' + self.api_token
        }
        r = requests.get(self.base_api_url + path, headers=headers, params=params, verify=self.ssl_verify)
        if r.status_code == 200:
            return r.json()
        return None

    def __check_clasifier_url(self, url):
        try:
            r = requests.options(url)
        except requests.exceptions.ConnectionError:
            raise AssertionError('No connection possible')

        assert (r.headers['allow'] == 'POST, OPTIONS')
        return True


class VerifaiDocument:
    service = None
    id_uuid = None
    id_side = None
    coords = None

    zones = None

    image = None
    cropped_image = None

    def __init__(self, response, b_jpeg_image, service):
        self.service = service
        self.id_uuid = response['uuid']
        self.id_side = response['side']
        self.coords = response['coords']
        self.load_image(b_jpeg_image)
        self.__model_data = None

    @property
    def model(self):
        return self.get_model_data()['model']

    @property
    def country(self):
        return self.get_model_data()['country']

    @property
    def position_in_image(self):
        return self.coords

    def load_image(self, b_jpeg_image):
        f = io.BytesIO(b_jpeg_image)
        self.image = Image.open(f)

    def get_cropped_image(self):
        if self.cropped_image is not None:
            return self.cropped_image
        px_coords = self.get_bounding_box_pixelcoords(self.coords)
        px_coords = self.__coords_list(px_coords)
        self.cropped_image = self.image.crop(px_coords)
        return self.cropped_image

    def get_part_of_card_image(self, coords, tolerance=0):
        i = self.get_cropped_image()
        if tolerance > 0:
            coords = self.inflate_coords(coords, tolerance)
        px_coords = self.get_bounding_box_pixelcoords(coords, i.width, i.height)
        px_coords = self.__coords_list(px_coords)
        return i.crop(px_coords)

    def inflate_coords(self, coords, factor):
        new_coords = {
            'xmin': coords['xmin'] - factor,
            'ymin': coords['ymin'] - factor,
            'xmax': coords['xmax'] + factor,
            'ymax': coords['ymax'] + factor,
        }
        for key, value in new_coords.items():
            if value < 0:
                new_coords[key] = 0
            if value > 1:
                new_coords[key] = 1
        return new_coords


    def get_bounding_box_pixelcoords(self, float_coords, im_width=None, im_height=None):
        """
        Get the pixel coords based on the image and the inference
        result.

        :return: dict with the bounding box in pixels
        :rtype: dict
        """
        if im_width is None and im_height is None:
            im_width = self.image.width
            im_height = self.image.height

        response = {
            'xmin': int(im_width * float_coords['xmin']),
            'ymin': int(im_height * float_coords['ymin']),
            'xmax': int(im_width * float_coords['xmax']),
            'ymax': int(im_height * float_coords['ymax'])
        }
        return response

    def get_zones(self):
        if self.zones is None:
            data = self.get_model_data()
            self.zones = []
            for zone_data in data['zones']:
                self.zones.append(VerifaiDocumentZone(self, zone_data))
        return self.zones

    def get_actual_size_mm(self):
        data = self.get_model_data()
        return float(data['width_mm']), float(data['height_mm'])

    def get_model_data(self):
        if not self.__model_data:
            self.__model_data = self.service.get_model_data(self.id_uuid)
        return self.__model_data

    def mask_zones(self, zones, image=None, filter_sides=True):
        if image is None:
            image = self.get_cropped_image()
        c = ImageColor.getrgb('#000000')
        drawer = ImageDraw.Draw(image)
        for zone in zones:
            if filter_sides and zone.side != self.id_side:
                continue
            px_coords = self.get_bounding_box_pixelcoords(zone.coords, image.width, image.height)
            px_coords = self.__coords_list(px_coords)
            drawer.rectangle(px_coords, c)

        return image


    def __coords_list(self, coords):
        """
        Helper to make a PIL coordnates list

        :param coords: xmin-max ymin-max coords
        :type coords: dict
        :return: tuple of coords
        :rtype: tuple
        """
        return (coords['xmin'], coords['ymin'],
                coords['xmax'], coords['ymax'])

class VerifaiDocumentZone:
    document = None
    title = None
    side = None
    coords = None

    def __init__(self, document, zone_data):
        self.document = document
        self.title = zone_data['title']
        self.set_side(zone_data['side'])
        self.set_coords(zone_data['x'], zone_data['y'], zone_data['width'], zone_data['height'])

    def set_side(self, side):
        self.side = side[:1]

    def set_coords(self, xmin, ymin, width, height):
        width_mm, height_mm = self.document.get_actual_size_mm()

        mm_xmin = xmin * width_mm
        mm_ymin = ymin * height_mm

        mm_xmax = mm_xmin + (width_mm * width)
        mm_ymax = mm_ymin + (height_mm * height)

        xmax = mm_xmax / width_mm
        ymax = mm_ymax / height_mm

        self.coords = {
            'xmin': xmin,
            'ymin': ymin,
            'xmax': xmax,
            'ymax': ymax
        }

