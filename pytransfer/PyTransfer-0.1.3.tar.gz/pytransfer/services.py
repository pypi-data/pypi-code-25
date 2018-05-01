import mimetypes
import random
import string
import requests
import re

from .uploader import FileStreamUploader
from .settings import providers


class TransferSh(FileStreamUploader):
    boundary: str

    def __init__(self, *args, **kwargs):
        self.url = providers['transfer.sh']['url']

        super(TransferSh, self).__init__(*args, **kwargs)

    def queue_http_start(self):
        self.boundary = ''.join(random.choice(string.digits + string.ascii_letters) for i in range(30))
        start = bytes('--' + self.boundary + '\r\n', 'utf-8')
        start += bytes('Content-Disposition: form-data; name="file"; filename="' + self.filename + '"' + '\r\n', 'utf-8')
        start += bytes('Content-Type: ' + str(mimetypes.guess_type(self.filename)[0]) + '\r\n', 'utf-8')
        start += bytes('\r\n', 'utf-8')
        self.queue.append(start)

    def queue_file(self):
        self.queue.append(open(self.filename, 'rb'))

    def queue_http_end(self):
        self.queue.append(bytes('\r\n--' + self.boundary + '--\r\n', 'utf-8'))

    def upload_file(self):
        r = requests.post(self.url, data=self, headers={
            'Content-Type': 'multipart/form-data; boundary=' + self.boundary
        })

        return r.text

    @staticmethod
    def parse_file_identifier_from_url(url):
        return re.search(r'[^/]+\/[^/]+$', url).group(0)

    @staticmethod
    def parse_host_from_url(url):
        return re.search(r'(http|https)\:\/\/[^\/]+', url).group(0)

    @staticmethod
    def print_post_upload_message(uploaded_files):
        if len(uploaded_files) > 1:
            file_identifiers = []
            for url in uploaded_files:
                file_identifiers.append(TransferSh.parse_file_identifier_from_url(url))

            base_url = TransferSh.parse_host_from_url(uploaded_files[0]) + '/'

            base_archive_url = base_url + '(' + ','.join([fragment for fragment in file_identifiers]) + ')'
            print('ZIP:', base_archive_url + '.zip')
            print()
            print('TAR.GZ:', base_archive_url + '.tar.gz')
