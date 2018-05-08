# -*- coding: utf-8 -*-
"""
Provide a wrapper and helpers for AWS boto library.
See https://boto3.readthedocs.io/en/latest/ for API details
"""
import logging
import os
import boto3
import re
import toil.provider.base
import toil
from botocore.client import Config

logger = logging.getLogger(__name__)


class AwsLib(toil.provider.base.BaseProvider):
    """
    library for AWS functionality.
    """

    def __init__(self, toil, config):
        super(AwsLib, self).__init__(toil, config)

    def session(self, profile='default'):
        """
        Create an AWS session.

        Args:
          profile (): the profile defined in config to use

        Returns:
          boto3.session.Session
        """
        if profile in self.config:
            self.configure_proxy()
            # create a session
            return AwsSession(self._toil, profile, self.config[profile])
        else:
            raise toil.CloudException(
                "profile '{profile}' not defined in config {config}".format(profile=profile, config=self.config))


class AwsSession(object):
    """
    provide aws api access
    """

    def __init__(self, toil, profile, config):
        # self._profile = profile
        self._config = config
        self._toil = toil

    def sts_client(self):
        """
        Create an aws sts client

        Args:
          session (): an aws session

        Returns:
          boto3.session.client
        """
        session = boto3.session.Session(
            region_name=self._config['region'],
            aws_access_key_id=self._config['access_key_id'],
            aws_secret_access_key=self._config['secret_access_key'],
        )

        return session.client(service_name='sts')

    def assume_role(self, sts_client, **kwargs):
        """
        Use sts to assume an AWS role.

        Returns a set of temporary security credentials (consisting of an access key ID, a secret access key, and a
        security token) that you can use to access AWS resources.

        Args:
          sts_client (): an aws sts client
          profile (): the profile defined in config to use

        Returns: dict
       """
        sts_credentials = sts_client.assume_role(
            RoleArn=self._config['role_arn'],
            RoleSessionName=self._config['role_session_name']
            , **kwargs)
        return sts_credentials

    def client(self, client_type, **kwargs):
        """
        Create a client.

        Args:
          client_type (): the type of aws service
          self._profile (): the self._profile defined in config to use

        Returns:
          A low-level client representing an AWS service.  Uses sts as defined in the config self._profile.
        """
        session = boto3.session.Session(
            region_name=self._config['region'],
            aws_access_key_id=self._config['access_key_id'],
            aws_secret_access_key=self._config['secret_access_key'],
        )

        if 'role_arn' in self._config and self._config['role_arn'] != "":
            sts_client = self.sts_client()
            sts_credentials = self.assume_role(sts_client)
            return session.client(client_type,
                                  aws_access_key_id=sts_credentials['Credentials']['AccessKeyId'],
                                  aws_secret_access_key=sts_credentials['Credentials']['SecretAccessKey'],
                                  aws_session_token=sts_credentials['Credentials']['SessionToken'],
                                  config=Config(signature_version='s3v4'),
                                  **kwargs
                                  )
        else:
            return session.client(client_type, **kwargs)

    def resource(self, resource_type, **kwargs):
        """
        Create a resource.

        Args:
          resource_type (): the type of aws resource
          profile (): the profile defined in config to use

        Returns:
          A low-level client representing an AWS service.  Uses sts as defined in the config profile.
        """

        session = boto3.session.Session(
            region_name=self._config['region'],
            aws_access_key_id=self._config['access_key_id'],
            aws_secret_access_key=self._config['secret_access_key'],
        )

        if 'role_arn' in self._config and self._config['role_arn'] != "":
            sts_client = self.sts_client()
            sts_credentials = self.assume_role(sts_client)
            return session.resource(resource_type,
                                    aws_access_key_id=sts_credentials['Credentials']['AccessKeyId'],
                                    aws_secret_access_key=sts_credentials['Credentials']['SecretAccessKey'],
                                    aws_session_token=sts_credentials['Credentials']['SessionToken'],
                                    config=Config(signature_version='s3v4'),
                                    **kwargs
                                    )
        else:
            session.resource(resource_type, **kwargs)

    def _upload_file_to_s3(self, resource, bucket_name, object_key, file_path, ssekms_key_id=None):
        """
        Upload a file to s3
        This method is private and should only be used withing this class.

        Args:
          resource (): aws resource
          bucket_name (): the bucket the file is going to
          object_key (): the key path for the file
          file_path (): the path for the local file to upload
          ssekms_key_id (): the server side encryption key

        Returns:
          Nothing.
        """
        if ssekms_key_id is not None:
            data = open(file_path, 'rb')
            logger.debug(
                'upload {file_path} to {bucketName}{objectKey} using {ssekms_key_id}'.format(file_path=file_path,
                                                                                             bucketName=bucket_name,
                                                                                             objectKey=object_key,
                                                                                             ssekms_key_id=ssekms_key_id))
            result = resource.Bucket(bucket_name).put_object(ServerSideEncryption='aws:kms', Key=object_key, Body=data,
                                                             SSEKMSKeyId=ssekms_key_id)
            logger.debug(result)
        else:
            data = open(file_path, 'rb')
            logger.debug(
                'upload {file_path} to {bucketName}{objectKey} using {ssekms_key_id}'.format(file_path=file_path,
                                                                                             bucketName=bucket_name,
                                                                                             objectKey=object_key,
                                                                                             ssekms_key_id=ssekms_key_id))
            result = resource.Bucket(bucket_name).put_object(Key=object_key, Body=data)
            logger.debug(result)
            # logger.debug('upload {file_path} to {bucketName}{objectKey}'.format(file_path=file_path, bucketName=bucket_name, objectKey=object_key))
            # result = resource.Bucket(bucket_name).upload_file(Filename=file_path, Key=object_key)
            # logger.debug(result)

    def _aws_file_upload_handler(self, real_file_path, file_path, file_name, **kwargs):
        """
        A helper method to upload a file to aws.
        This method is private and should only be used withing this class.

        Args:
          real_file_path (): path to local file
          file_path (): the path to use in aws
          file_name (): the local file name
          **kwargs ():

        Returns:
          Nothing
        """

        bucket = kwargs.get('bucket', None)
        if bucket is None:
            raise TypeError('bucket argument is required')

        resource = kwargs.get('resource', None)
        if resource is None:
            raise TypeError('resource argument is required')

        ssekms_key_id = kwargs.get('ssekms_key_id', None)

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

        # object_key = prefix + (file_name).replace('\\', '/')
        real_file_path = real_file_path.replace('\\', '/')
        self._upload_file_to_s3(resource, bucket, object_key, real_file_path, ssekms_key_id)

    def upload_to_s3(self, bucket, local_path, prefix=None, ssekms_key_id=None):
        """
        Upload a local directory to AWS.  Uses the cloud helper process_dir and passes a function handler.

        Args:
          bucket (): aws bucket name
          local_path (): local directory path
          prefix (): prefix for aws
          ssekms_key_id (): aws encryption key
          profile (): the profile to use defined in config.

        Returns:
          Nothing
        """
        resource = self.resource('s3', verify=False)
        self._toil.traverse_dir(local_path, self._aws_file_upload_handler, resource=resource, bucket=bucket,
                                local_path=local_path, prefix=prefix, ssekms_key_id=ssekms_key_id,
                                remove_from_key=local_path)

    def download_from_s3(self, bucket_name, key, file_path, ssekms_key_id=None):
        """
        Download a file from aws s3.

        Args:
          bucket_name (): aws bucket name
          key (): the key to file in aws
          file_path (): local file path and name
          ssekms_key_id (): aws encryption key
          profile (): the profile to use defined in config

        Returns:
          Nothing
        """
        resource = self.resource('s3', verify=False)
        result = resource.Bucket(bucket_name).objects.filter(Prefix=key)
        for s3_obj in result:
            # resource.Bucket(bucket_name).download_file
            logger.debug(s3_obj.key)

            local_key = s3_obj.key
            local_key = re.sub('[:]', "_colon_", local_key)
            # local_key = re.sub('[^a-zA-Z0-9\n\._-]', "", local_key)
            local_path = file_path + '/' + local_key
            local_dir_name = os.path.dirname(local_path)

            try:
                if not os.path.exists(local_dir_name):
                    os.makedirs(local_dir_name)

                if not (local_path.endswith('/')):
                    resource.Bucket(bucket_name).download_file(s3_obj.key, local_path)

            except Exception as ex:
                logging.error(ex)
