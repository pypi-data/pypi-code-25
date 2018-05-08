import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urljoin
from codecs import open
from json.decoder import JSONDecodeError

from requests.exceptions import RequestException
import requests

logger = logging.getLogger(__name__)


class BrickFTPError(Exception):
    pass


class BrickFTP:

    def __init__(self, *, username, password, subdomain):
        self._username = username
        self._password = password
        self._subdomain = subdomain
        self._session_id = None
        self._logged_in = False

    def _login(self):
        start_session_resp = self._post(
            '/api/rest/v1/sessions.json',
            json={'username': self._username, 'password': self._password}
        )
        self._session_id = start_session_resp['id']
        self._logged_in = True

    def _path(self, path):
        return str(path).lstrip('/')

    def dir(self, remote_path):
        if not self._logged_in:
            self._login()
        return self._get(f'/api/rest/v1/folders/{self._path(remote_path)}')

    def mkdir(self, remote_path):
        if not self._logged_in:
            self._login()
        return self._post(f'/api/rest/v1/folders/{self._path(remote_path)}')

    def upload(self, *, upload_path, local_path, encoding='utf-8'):
        # NOTE: can currently only upload upto 5MB size files
        # https://developers.brickftp.com/#requesting-additional-upload-urls
        if not self._logged_in:
            self._login()
        upload_control_url = f'/api/rest/v1/files/{self._path(upload_path)}'
        # Start upload
        start_upload_resp_json = self._post(
            upload_control_url,
            json={'action': 'put'},
        )
        # Upload parts
        ref = start_upload_resp_json['ref']
        upload_uri = start_upload_resp_json['upload_uri']
        with open(local_path, encoding=encoding) as input_file:
            resp = requests.put(upload_uri, data=input_file.read())
            if not resp.ok:
                raise BrickFTPError(
                    f'Failed to upload part. Resp: {resp.text}'
                )
        # End upload
        self._post(upload_control_url, json={'action': 'end', 'ref': ref})

    def download_file(self, *, remote_path, local_path=None):
        if not self._logged_in:
            self._login()
        if local_path is None:
            remote_path = Path(remote_path)
            local_path = NamedTemporaryFile(
                delete=False,
                prefix=f'{remote_path.stem}_',
                suffix=remote_path.suffix,
            ).name
        dl_info = self._get(f'/api/rest/v1/files/{self._path(remote_path)}')
        resp = requests.get(dl_info['download_uri'])
        resp.raise_for_status()
        file_bytes = resp.content
        with open(local_path, 'wb') as file_:
            file_.write(file_bytes)
        return local_path

    def delete(self, remote_path):
        if not self._logged_in:
            self._login()
        self._delete(
            f'/api/rest/v1/files/{self._path(remote_path)}',
            headers={'Depth': 'infinity'}
        )

    def _post(self, path, **kwargs):
        return self._request(path=path, method='post', **kwargs)

    def _get(self, path):
        return self._request(path=path, method='get')

    def _delete(self, path, **kwargs):
        return self._request(path=path, method='delete', **kwargs)

    def _request(self, *, path, method, **kwargs):
        url = urljoin(f'https://{self._subdomain}.brickftp.com/', path)
        try:
            resp = getattr(requests, method)(
                url, **{**self._default_request_kwargs, **kwargs}
            )
        except RequestException as exc:
            raise BrickFTPError(exc) from exc
        try:
            resp_json = resp.json()
        except JSONDecodeError:
            raise BrickFTPError(f'Non-valid JSON response: {resp.text}')
        if not resp.ok:
            error = resp_json['error']
            raise BrickFTPError(error)
        return resp_json

    @property
    def _default_request_kwargs(self):
        if self._logged_in:
            return {'cookies': {'BrickAPI': self._session_id}}
        elif not self._logged_in and self._session_id:
            return {'auth': (self._session_id, 'x')}
        else:
            return {}
