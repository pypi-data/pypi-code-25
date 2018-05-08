# -*- coding: utf-8 -*-
"""
Provide a wrapper and helpers for SCALR library.
See https://api-explorer.scalr.com/ for API details
"""
import base64
import datetime
import hashlib
import hmac
import logging
import urllib
import urlparse

import requests

import toil.provider.base
import toil
import toil.util.decorator

logger = logging.getLogger(__name__)


class ScalrLib(toil.provider.base.BaseProvider):
    """
    Class for Scalr functionality.

    Properties :
      config: dict with configuration data
    """

    def __init__(self, toil, config):
        super(ScalrLib, self).__init__(toil, config)

    def session(self, profile='default'):
        """
        Create a Scalr session.

        Args:
          profile (): the profile defined in config to use

        Returns:
          ScalrApiSession
        """
        if profile in self.config:
            self.configure_proxy()
            session = ScalrApiSession(self,
                                      api_url=self.config[profile]['api_url'],
                                      api_key_id=self.config[profile]['api_key_id'],
                                      api_key_secret=self.config[profile]['api_key_secret']
                                      )
            return session
        else:
            raise toil.CloudException(
                "profile '{profile}' not defined in config {config}".format(profile=profile, config=self.config))


class ScalrApiSession(requests.Session):
    """
    uses the requests library for an http session
    """

    def __init__(self, client, api_url, api_key_id, api_key_secret):
        self.client = client
        self.api_url = api_url
        self.api_key_id = api_key_id
        self.api_key_secret = api_key_secret
        super(ScalrApiSession, self).__init__()

    def prepare_request(self, request):
        """
        Ensures the url includes the config api.
        Implements Scalr signing requirements.
        Args:
          request (str):

        Returns: request
        """
        if not request.url.startswith(self.api_url):
            request.url = "".join([self.api_url, request.url])
        request = super(ScalrApiSession, self).prepare_request(request)
        now = datetime.datetime.utcnow()
        date_header = now.isoformat()
        url = urlparse.urlparse(request.url)

        if url.query:
            pairs = urlparse.parse_qsl(url.query, keep_blank_values=True, strict_parsing=True)
            pairs = [map(urllib.quote, pair) for pair in pairs]
            # TODO - Spec isn't clear on whether the sorting should happen prior or after encoding
            pairs.sort(key=lambda pair: pair[0])
            canon_qs = "&".join("=".join(pair) for pair in pairs)
        else:
            canon_qs = ""

        # Authorize
        sts = "\n".join([
            request.method,
            date_header,
            url.path,
            canon_qs,
            request.body if request.body is not None else ""
        ])

        sig = " ".join([
            "V1-HMAC-SHA256",
            base64.b64encode(hmac.new(str(self.api_key_secret), sts, hashlib.sha256).digest())
        ])

        request.headers.update({
            "X-Scalr-Key-Id": self.api_key_id,
            "X-Scalr-Signature": sig,
            "X-Scalr-Date": date_header,
            "X-Scalr-Debug": "1",
            "Content-Type": 'application/json'
        })

        logger.debug("URL: %s", request.url)
        logger.debug("StringToSign: %s", repr(sts))
        logger.debug("Signature: %s", repr(sig))

        return request

    def request(self, *args, **kwargs):
        """
        request data from scalr, converts response to json
        Args:
          *args ():
          **kwargs ():

        Returns: requests.Response
        """
        res = super(ScalrApiSession, self).request(*args, **kwargs)
        logger.debug("%s - %s", " ".join(args), res.status_code)
        try:
            errors = res.json().get("errors", None)
            if errors is not None:
                for error in errors:
                    logger.warning("API Error (%s): %s", error["code"], error["message"])
        except ValueError:
            logger.error("Received non-JSON response from API!")
        res.raise_for_status()
        logger.debug("Received response: %s", res.text)
        return res

    def list(self, path, **kwargs):
        """
        call the service until all data is collected
        Args:
          path (str):
          **kwargs ():

        Returns: List
        """
        data = []
        while path is not None:
            body = self.get(path, **kwargs).json()
            if body is not None:
                if type(body) is dict:
                    if 'data' in body.keys():
                        data.extend(body["data"])
                    else:
                        data.append((''.join('{}{}'.format(key, val) for key, val in body.items())))
                if "pagination" in body:
                    path = body["pagination"]["next"]
                else:
                    path = None
            else:
                path = None
        return data

    def create(self, *args, **kwargs):
        self._fuzz_ids(kwargs.get("json", {}))
        return self.post(*args, **kwargs).json().get("data")

    def fetch(self, *args, **kwargs):
        return self.get(*args, **kwargs).json()["data"]

    def delete(self, *args, **kwargs):
        self.delete(*args, **kwargs)

    def post(self, *args, **kwargs):
        return super(ScalrApiSession, self).post(*args, **kwargs).json()["data"]

    def patch(self, *args, **kwargs):
        return super(ScalrApiSession, self).patch(*args, **kwargs).json()["data"]

    @toil.util.decorator.retry(3, requests.exceptions.RequestException)
    def get(self, url, **kwargs):
        """
        uses a decorator to retry when a request exception occurs
        Args:
          url (str):
          **kwargs ():

        Returns: requests.Response
        """
        return super(ScalrApiSession, self).get(url, **kwargs)
