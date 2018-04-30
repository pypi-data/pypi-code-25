"""API to interface with Humble Bundle servers."""
# TODO: Download asmjs?

import collections
import csv
import hashlib
import json
import os
from pathlib import Path, PurePath
from typing import List, Mapping, NamedTuple, Optional

import requests


HUMBLE_API_ROOT = 'https://www.humblebundle.com/api/v1'
HUMBLE_LOGIN_URL = 'https://www.humblebundle.com/processlogin'
HUMBLE_ORDERS_URL = f'{HUMBLE_API_ROOT}/user/order'
DOWNLOAD_CHUNK_SIZE = 1024 * 4


# Data structure definitions
#############################
Download = collections.namedtuple('Download', [
    'android_app_only', 'download_identifier', 'download_struct',
    'download_version_number', 'machine_name', 'options_dict', 'platform'])
Subproduct = collections.namedtuple('Subproduct', [
    'custom_download_page_box_html', 'downloads', 'human_name', 'icon',
    'machine_name', 'library_family_name', 'payee', 'url'])


class Product(NamedTuple):
    """Data structure for product JSON."""
    automated_empty_tpkds: dict
    category: str
    human_name: str
    machine_name: str
    partial_gift_enabled: bool
    post_purchase_text: str
    supports_canonical: bool
    # Optional fields
    subscription_credits: Optional[int] = None


class Purchase(NamedTuple):
    """Data structure for purchase JSON."""
    amount_spent: int
    claimed: bool
    created: str
    currency: str
    gamekey: str
    is_giftee: bool
    missed_credit: None
    path_ids: list
    product: Product
    subproducts: List[Subproduct]
    total: int
    uid: str
    # Optional fields
    all_coupon_data: Optional[list] = None


class DownloadStructUrl(NamedTuple):
    """Data structure for download_struct's urls JSON."""
    web: str
    # Optional fields
    bittorrent: Optional[str] = None


class DownloadStruct(NamedTuple):
    """Data structure for download_struct JSON."""
    human_size: str
    # Optional fields
    arch: Optional[str] = None
    asm_config: Optional[dict] = None
    asm_manifest: Optional[dict] = None
    external_link: Optional[str] = None
    file_size: Optional[int] = None
    force_download: Optional[bool] = None  # noqa
    hd_stream_url: Optional[str] = None
    kindle_friendly: Optional[bool] = None
    md5: Optional[str] = None
    name: Optional[str] = None
    sd_stream_url: Optional[str] = None
    sha1: Optional[str] = None
    small: Optional[int] = None
    timestamp: Optional[int] = None
    uploaded_at: Optional[str] = None
    url: Optional[DownloadStructUrl] = None
    uses_kindle_sender: Optional[bool] = None

    @property
    def file_name(self):
        """Extract the file name from the URL."""
        if self.url:
            return self.url.web.split('/')[-1].split('?', 1)[0]
        else:
            raise ValueError('No downloads available for this struct')


# Main interface
#################

class HumbleDownloader:
    """API interface for Humble Bundle purchases."""
    def __init__(self,
                 session_key: Optional[str] = None,
                 cache_dir: Optional[os.PathLike] = None):
        self.session = requests.Session()
        # No official API, we're pretending to be the Android app
        self.session.headers.update({
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "Keep-Alive": "true",
            "X-Requested-By": "hb_android_app",
            "User-Agent": "Apache-HttpClient/UNAVAILABLE (java 1.4)"
        })
        if session_key:
            self.set_session(session_key)

        self.cache_dir = cache_dir
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_dir.joinpath('orders').mkdir(exist_ok=True)

    def login(self, username: str, password: str):
        """Authenticate with Humble API."""
        # NOTE: NOT CURRENTLY WORKING
        # TODO: Figure out how to handle CAPTCHA and fix this method
        login_details = {'username': username, 'password': password}
        self.session.post(HUMBLE_LOGIN_URL, data=login_details,
                          params={"ajax": "true"})

    def set_session(self, session_key: str):
        """Set the session key to use."""
        self.session.cookies['_simpleauth_sess'] = session_key

    def get_purchase_list(self) -> List[str]:
        """Get all purchase keys from Humble Bundle."""
        r = self.session.get(HUMBLE_ORDERS_URL)
        return [k['gamekey'] for k in r.json()]

    def get_purchase(self, key: str) -> Purchase:
        """Retrieve data on a specific purchase."""
        purchase_data = self._load_purchase_json(key)
        return self._convert_purchase_data(purchase_data)

    def _load_purchase_json(self, key: str):
        """Get JSON for purchase from cache if possible, otherwise download"""
        json_cache_file = self._create_order_cache_path(key)
        if self.cache_dir and json_cache_file.exists():
            json_cache_file = self._create_order_cache_path(key)
            # TODO: Error handling
            # TODO: logging
            with json_cache_file.open() as order_file:
                purchase_data = json.load(order_file)
        else:
            r = self.session.get(f'{HUMBLE_API_ROOT}/order/{key}')
            purchase_data = r.json()
            # Cache purchase JSON
            if self.cache_dir:
                # json_cache_file = self._create_order_cache_path(key)
                with json_cache_file.open('w', ) as order_file:
                    order_file.write(r.text)
        return purchase_data

    def _create_order_cache_path(self, key: str) -> Path:
        """Generate a path to store order JSON cache data.

        If a cache dire has not been set, use NullPath to return a virtual
        path object.
        """
        filename = key + '.json'
        # Generate a fake path if caching disabled
        if not self.cache_dir:
            return NullPath('NULLPATH') / filename
        return self.cache_dir / 'orders' / filename

    def _convert_purchase_data(self, purchase_data: Mapping) -> Purchase:
        """Convert JSON to internal data structures."""
        purchase_data['product'] = namedtuple_filter(Product,
                                                     purchase_data['product'])
        fixed_subproducts = []
        for subproduct in purchase_data['subproducts']:
            fixed_downloads = []
            for download in subproduct['downloads']:
                fixed_structs = []
                for struct in download['download_struct']:
                    # Some download_structs have no downloads (e.g. streaming)
                    if 'url' in struct:
                        fixed_download_urls = namedtuple_filter(
                            DownloadStructUrl, struct['url'])
                        struct['url'] = fixed_download_urls
                    # At least one bundle has this typo (androidbundle4)
                    if 'timetstamp' in struct:
                        struct['timestamp'] = struct['timetstamp']
                        del struct['timetstamp']
                    # At least one bundle has this typo (hib14)
                    if 'timestmap' in struct:
                        # It already has a timestamp field with a higher value
                        # so I guess just ditch the old one?
                        del struct['timestmap']
                    # At least one bundle has this typo (booktrope_bookbundle)
                    if 'kindle-friendly' in struct:
                        struct['kindle_friendly'] = struct['kindle-friendly']
                        del struct['kindle-friendly']
                    fixed_struct = namedtuple_filter(DownloadStruct, struct)
                    fixed_structs.append(fixed_struct)
                download['download_struct'] = fixed_structs
                fixed_downloads.append(download)
            subproduct['downloads'] = list(map(
                lambda d: namedtuple_filter(Download, d), fixed_downloads))
            fixed_subproducts.append(subproduct)
        purchase_data['subproducts'] = list(map(
            lambda s: namedtuple_filter(Subproduct, s),
            fixed_subproducts))

        return namedtuple_filter(Purchase, purchase_data)

    def find_key_from_name(self, machine_name: str) -> Optional[str]:
        """Givin a machine name, search the bundles for its key."""
        if self.cache_dir:
            keynames = self._load_keyname_cache()
        else:
            keynames = {}

        if machine_name in keynames:
            return keynames[machine_name]

        keys = self.get_purchase_list()
        machine_name_key = None
        for key in keys:
            purchase = self.get_purchase(key)
            keynames[key] = purchase.product.machine_name
            if purchase.product.machine_name == machine_name:
                machine_name_key = key
                break
        if self.cache_dir:
            self._save_keyname_cache(keynames)
        return machine_name_key

    def _load_keyname_cache(self) -> Mapping:
        """Load keynames from CSV cache file."""
        keyname_cache = self.cache_dir / 'keynames.csv'
        if keyname_cache.exists():
            with keyname_cache.open(newline='') as csvfile:
                keyname_dicts = list(csv.DictReader(csvfile))
                keynames = {key_dict['machine_name']: key_dict['key'] for
                            key_dict in keyname_dicts}
            return keynames

        return {}

    def _save_keyname_cache(self, keynames: Mapping):
        """Write out keynames to a CSV cache file."""
        keyname_cache = self.cache_dir / 'keynames.csv'
        with keyname_cache.open('w', newline='') as csvfile:
            keyname_writer = csv.DictWriter(csvfile,
                                            ('machine_name', 'key'))
            keyname_pairs = [{'machine_name': k, 'key': n} for n, k in
                             keynames.items()]
            keyname_writer.writeheader()
            keyname_writer.writerows(keyname_pairs)


# Utility functions
####################

def download_file(download_struct: DownloadStruct,
                  output_path: os.PathLike,
                  progress_callback=lambda _: None):
    """Download file described by a download_struct to disk."""
    download_url = download_struct.url.web
    r = requests.get(download_url, stream=True)
    # TODO: Open temp file and write to that before renaming
    with output_path.open('wb') as f:
        # TODO: Check for 0 length (bad/expired gamekey in URL)
        for chunk in r.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
            # Filter keep-alive packets
            if chunk:
                f.write(chunk)
                progress_callback(len(chunk))


def verify_download(download_struct: DownloadStruct,
                    path: os.PathLike) -> bool:
    """Use the information in the download stuct to check file path."""
    # Check file size
    file_size = path.lstat().st_size
    if file_size != download_struct.file_size:
        return False

    # File is correct size, so let's check contents
    # Using MD5 as not all downloads have a SHA1 available
    file_hash = hashlib.md5()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(file_hash.block_size * 32), b''):
            file_hash.update(chunk)
    return file_hash.hexdigest() == download_struct.md5


def namedtuple_filter(namedtuple_class: collections.namedtuple,
                      data: Mapping) -> collections.namedtuple:
    """Remove unknown fields from a dict before creating namedtuple.

    Used to prevent crash if nonbreaking fields are added to HB's API."""
    # TODO: Debugging flag to not ignore unknown fields
    filtered_data = {k: data[k] for k in data if k in namedtuple_class._fields}
    return namedtuple_class(**filtered_data)


# TODO: implement remaining Path methods
# Ugly hack to allow subclassing Path/PurePath
# https://stackoverflow.com/a/34116756
class NullPath(type(PurePath())):
    """Emulates a Path object that does not perform filesystem operations."""

    @staticmethod
    def exists() -> bool:
        """Null paths do not exist, always return False."""
        return False
