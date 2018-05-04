# -*- coding: utf-8 -*-
"""
Provide a wrapper and helpers for OPEN_STACK  library.
See https://pypi.python.org/pypi/openstacksdk for API details

"""
from __future__ import absolute_import

import logging
import os
import re

import openstack
from openstack.profile import Profile

import toil.provider.base

logger = logging.getLogger(__name__)


class OpenStackLib(toil.provider.base.BaseProvider):
    """
    library for OPEN_STACK functionality.
    """

    def __init__(self, toil, config):
        super(OpenStackLib, self).__init__(toil, config)

    def session(self, profile='default'):
        """
        Create an OPEN_STACK session.

        Args:
          profile (): the profile defined in config to use

        Returns:
          3.session.Session
        """
        if profile in self.config:
            self.configure_proxy()
            # create a session
            return OpenStackSession(self._toil, profile, self.config[profile])
        else:
            raise toil.CloudException(
                "profile '{profile}' not defined in config {config}".format(profile=profile, config=self.config))


class OpenStackSession(object):
    """
    provide open stack api access
    """

    def __init__(self, toil, profile, config):
        self._profile = profile
        self._config = config
        self._toil = toil

    def connect(self):
        prof = openstack.profile.Profile()
        prof.set_region(openstack.profile.Profile.ALL, self._config['region'])

        return openstack.connection.Connection(
            profile=prof,
            user_agent='toil',
            auth_url=self._config['auth_url'],
            project_name=self._config['project'],
            project_domain_name=self._config['domain'],
            user_domain_name=self._config['domain'],
            username=self._config['user'],
            password=self._config['password']
        )

    def upload_to_container(self, container, local_path, prefix=None):
        """
        Upload a local directory to Openstack swift container.  Uses the cloud helper process_dir and passes a function handler.

        Args:
          container (): container name
          local_path (): local directory path
          prefix (): prefix for openstack

        Returns:
          Nothing
        """
        connection = self.connect()
        self._toil.traverse_dir(local_path, self._openstack_file_upload_handler, container=container,
                                local_path=local_path, prefix=prefix, remove_from_key=local_path, connection=connection)

    def _openstack_file_upload_handler(self, real_file_path, file_path, file_name, **kwargs):
        """
        A helper method to upload a file to openstack .
        This method is private and should only be used withing this class.

        Args:
          real_file_path (): path to local file
          file_path (): the path to use in aws
          file_name (): the local file name
          **kwargs ():

        Returns:
          Nothing
        """

        container = kwargs.get('container', None)
        connection = kwargs.get('connection', None)

        if container is None:
            raise TypeError('container argument is required')

        if connection is None:
            raise TypeError('connection argument is required')

        object_key = (os.path.relpath(file_path, '/') + '/' + file_name).replace('\\', '/')
        if not object_key.startswith('/'):
            object_key = '/' + object_key

        remove_from_key = kwargs.get('remove_from_key', None)
        if remove_from_key is not None:
            object_key = object_key.replace(remove_from_key, '')

        prefix = kwargs.get('prefix', '')
        if prefix is None:
            prefix = ''
        if prefix != '' and not prefix.endswith('/'):
            prefix += '/'

        object_key = prefix + object_key

        real_file_path = real_file_path.replace('\\', '/')
        self._upload_file_to_container(container, object_key, real_file_path, connection)

    def _upload_file_to_container(self, container, object_key, file_path, connection):
        """
        Upload a file to container
        This method is private and should only be used withing this class.

        Args:
          bucket_name (): the container the file is going to
          object_key (): the key path for the file
          file_path (): the path for the local file to upload

        Returns:
          Nothing.
        """
        data = open(file_path, 'rb')
        logger.debug('upload {file_path} to {container} {object_key}'.format(file_path=file_path, container=container,
                                                                             object_key=object_key))

        result = connection.object_store.upload_object(container=container,
                                                       name=object_key,
                                                       data=open(file_path, 'r'))

        logger.debug(result)

    def download_from_container(self, container, key=None, local_path=''):
        """
        Download a file from openstack container.

        Args:
          container (): container name
          key (): the key to file in openstack
          file_path (): local file path and name

        Returns:
          Nothing
        """
        connection = self.connect()
        result = connection.object_store.objects(container)

        for obj in result:
            if (key is None) or (key and obj.name.startswith(key)):
                local_key = obj.name
                local_key = re.sub('[:]', "_colon_", local_key)
                if local_path.endswith('/'):
                    download_path = local_path + local_key
                else:
                    download_path = local_path + '/' + local_key
                local_dir_name = os.path.dirname(download_path)

                try:
                    if not os.path.exists(local_dir_name):
                        os.makedirs(local_dir_name)

                    logger.debug(
                        'download {container}[{object_key}] to {download_path}'.format(download_path=download_path,
                                                                                       container=container,
                                                                                       object_key=obj.name))
                    if not (download_path.endswith('/')):
                        connection.object_store.download_object(obj, path=download_path)

                except Exception as ex:
                    logging.error(ex)
