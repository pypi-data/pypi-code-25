import hashlib
import io
import json

import boto3
from botocore.exceptions import ClientError

from generator.caches.base import SVGCache


class S3Cache(SVGCache):
    def __init__(self, aws_access_key, aws_secret_key, s3_bucket_name):
        self._session = boto3.session.Session(aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
        self._s3 = self._session.resource('s3')
        self._bucket = self._s3.Bucket(s3_bucket_name)

    @staticmethod
    def _make_key(parameters):
        parameters_as_str = json.dumps(parameters, sort_keys=True)
        hash = hashlib.md5()
        hash.update(parameters_as_str.encode('utf-8'))
        return f'{hash.hexdigest()}.b64'

    def get(self, parameters):
        key = self._make_key(parameters)
        bytes = io.BytesIO()

        try:
            self._bucket.download_fileobj(key, bytes)
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return None
            else:
                raise

        return bytes.getvalue()

    def add(self, parameters, png_bytes):
        key = self._make_key(parameters)
        self._bucket.upload_fileobj(io.BytesIO(png_bytes), key)
