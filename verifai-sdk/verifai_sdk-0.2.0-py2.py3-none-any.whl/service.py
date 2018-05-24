import io
import requests

from PIL import Image

from verifai_sdk.document import VerifaiDocument


class VerifaiService:
    """
    The VerifaiService is your main component to use. It communicates
    with various backend systems and handles all the privacy sensitive
    data internally.

    To use the service you need to initialize it first with a API token
    and the URL to the classifier service, and optional to the OCR
    service.

    See https://docs.verifai.com/server_docs/python-sdk-latest.html
    """
    api_token = None
    server_urls = {'classifier': [], 'ocr': []}
    base_api_url = 'https://dashboard.verifai.com/api/'
    ssl_verify = True

    def __init__(self, token=None):
        """
        Initialize the VerifaiService with a token. A token is mandatory
        to communicate with the Verifai backend services.

        :param token: API token, can be found in the Verifai Dashboard.
        :type token: str
        """
        self.__url_roundrobin = {'classifier': 0, 'ocr': 0}
        self.api_token = token

    def add_clasifier_url(self, url, skip_unreachable=False):
        """
        To add the URL to your local running Verifai Classifier service.
        Please not that you need to provide the full path to the api
        endpoint.

        For example: http://localhost:5000/api/classify/

        You can add multiple servers to scale up operations.

        :param url: The full path to the classifier API
        :type url: str
        :param skip_unreachable: Ignore errors in connecting to it.
        :type skip_unreachable: bool
        :return: True if add is successful, False if it doesn't.
        :rtype: bool
        """
        return self.__add_server_url(url, skip_unreachable, 'classifier')

    def add_ocr_url(self, url, skip_unreachable=False):
        """
        To add the URL to your local running Verifai OCR service.
        Please not that you need to provide the full path to the api
        endpoint.

        For example: http://localhost:5001/api/ocr/

        You can add multiple servers to scale up operations.
        :param url: The full path to the classifier API
        :type url: str
        :param skip_unreachable: Ignore errors in connecting to it.
        :type skip_unreachable: bool
        :return: True if add is successful, False if it doesn't.
        :rtype: bool
        """
        return self.__add_server_url(url, skip_unreachable, 'ocr')

    def get_model_data(self, id_uuid):
        """
        Fetch the raw data from the API for further processing.

        Note: Since it is not a public API it is subject to changes.

        :param id_uuid: The UUID you got form the classifier
        :type id_uuid: str
        :return: dict with the results found in the Verifai Backend
        :rtype: dict or None
        """
        data = self.__get_from_api('id-models', params={'uuid': id_uuid})
        if data:
            return data[0]  # Get first result because a unique key is queried
        return None

    def get_ocr_data(self, mrz_image):
        """
        Sends the mrz_image (Image) to the Verifai OCR service, and
        returns the raw response.

        :param mrz_image: MRZ cutout of the document
        :type mrz_image: Image
        :return: dict with raw response or None of not response
        :rtype: dict or None
        """
        bytes_io = io.BytesIO()
        mrz_image.save(bytes_io, 'JPEG')
        r = requests.post(
            self.__get_url('ocr'),
            files={'file': bytes_io.getvalue()},
            verify=self.ssl_verify
        )
        response = r.json()
        return response

    def classify_image(self, image):
        """
        Send a image to the Verifai Classifier and get a VerifaiDocument
        in return. If it fails to classify it will return None.

        :param image: file contents of a JPEG image
        :type image: str
        :return: Initialized VerifaiDocument
        :rtype: VerifaiDocument or None
        """
        r = requests.post(
            self.__get_url('classifier'),
            files={'file': image},
            verify=self.ssl_verify
        )
        response = r.json()
        if response['status'] == 'SUCCESS':
            return VerifaiDocument(response, image, self)

        return None

    def classify_image_path(self, image_path):
        """
        Send a image to the Verifai Classifier and get a VerifaiDocument
        in return. If it fails to classify it will return None.

        :param image_path: Path to the image
        :type image_path: str
        :return: Initialized VerifaiDocument
        :rtype: VerifaiDocument or None
        """
        f = open(image_path, 'rb')
        i = f.read()
        return self.classify_image(i)

    def __add_server_url(self, url, skip_unreachable, type):
        try:
            self.__check_server_url(url)

            if type == 'classifier':
                self.server_urls[type].append(url)
            else:
                self.server_urls[type].append(url)
            return True
        except AssertionError:
            if not skip_unreachable:
                raise ValueError('No server available at that URL ({0})'.format(url))
            return False

    def __get_url(self, type):
        index = self.__url_roundrobin[type]
        if self.server_urls[type][index]:
            if index + 1 >= len(self.server_urls[type]):
                self.__url_roundrobin[type] = 0
            else:
                self.__url_roundrobin[type] = index + 1
            return self.server_urls[type][index]
        raise ValueError("No clasifier URLs. Set one first with add_clasifier_url(url)")

    def __get_from_api(self, path, params):
        headers = {
            'Authorization': 'Token ' + self.api_token
        }
        r = requests.get(self.base_api_url + path, headers=headers, params=params, verify=self.ssl_verify)
        if r.status_code == 200:
            return r.json()
        r.raise_for_status()

    def __check_server_url(self, url):
        try:
            r = requests.options(url, verify=self.ssl_verify)
        except requests.exceptions.ConnectionError:
            raise AssertionError('No connection possible for ' + url)
        if not r.status_code == 200:
            raise AssertionError('Got a {0} for {1}'.format(r.status_code, url))
        methods = r.headers['allow'].split(',')
        methods.sort()
        methods = [item.strip() for item in methods]

        assert methods == ['POST', 'OPTIONS']
        return True