import time
import logging

from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase, CreateError

from botocore.exceptions import ClientError
import boto3
from boto3.dynamodb.conditions import Attr as DynamoConditionAttr
from botocore.config import Config
import os
from django.utils import timezone
from datetime import timedelta


TABLE_NAME = getattr(
    settings, 'DYNAMODB_SESSIONS_TABLE_NAME', 'sessions')
HASH_ATTRIB_NAME = getattr(
    settings, 'DYNAMODB_SESSIONS_TABLE_HASH_ATTRIB_NAME', 'session_key')
ALWAYS_CONSISTENT = getattr(
    settings, 'DYNAMODB_SESSIONS_ALWAYS_CONSISTENT', True)

USE_LOCAL_DYNAMODB_SERVER = getattr(
    settings, 'USE_LOCAL_DYNAMODB_SERVER', False)
BOTO_CORE_CONFIG = getattr(
    settings, 'BOTO_CORE_CONFIG', None)

READ_CAPACITY_UNITS = getattr(
    settings, 'DYNAMODB_READ_CAPACITY_UNITS', 123
)
WRITE_CAPACITY_UNITS = getattr(
    settings, 'DYNAMODB_WRITE_CAPACITY_UNITS', 123
)

# defensive programming if config has been defined
# make sure it's the correct format.
if BOTO_CORE_CONFIG:
    assert isinstance(BOTO_CORE_CONFIG, Config)


# We'll find some better way to do this.
_DYNAMODB_CONN = None
_DYNAMODB_TABLE = None

logger = logging.getLogger(__name__)
dynamo_kwargs = dict(
    service_name='dynamodb',
    config=BOTO_CORE_CONFIG
)

if USE_LOCAL_DYNAMODB_SERVER:
    local_dynamodb_server = 'LOCAL_DYNAMODB_SERVER'
    assert os.environ.get(local_dynamodb_server), \
        "If USE_LOCAL_DYNAMODB_SERVER is set to true define " \
        "LOCAL_DYNAMODB_SERVER in the environment"
    dynamo_kwargs['endpoint_url'] = os.environ[local_dynamodb_server]


def dynamodb_connection_factory(low_level=False):
    """
    Since SessionStore is called for every single page view, we'd be
    establishing new connections so frequently that performance would be
    hugely impacted. We'll lazy-load this here on a per-worker basis. Since
    boto3.resource.('dynamodb')objects are state-less (aside from security
    tokens), we're not too concerned about thread safety issues.
    """

    if low_level:
        return boto3.client(**dynamo_kwargs)

    global _DYNAMODB_CONN

    if not _DYNAMODB_CONN:
        logger.debug("Creating a DynamoDB connection.")
        _DYNAMODB_CONN = boto3.resource(**dynamo_kwargs)
    return _DYNAMODB_CONN


def dynamodb_table():
    global _DYNAMODB_TABLE

    if not _DYNAMODB_TABLE:
        _DYNAMODB_TABLE = dynamodb_connection_factory().Table(TABLE_NAME)
    return _DYNAMODB_TABLE


class SessionStore(SessionBase):
    """
    Implements DynamoDB session store.
    """

    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)

    @property
    def table(self):
        return dynamodb_table()

    def load(self):
        """
        Loads session data from DynamoDB, runs it through the session
        data de-coder (base64->dict), sets ``self.session``.

        :rtype: dict
        :returns: The de-coded session data, as a dict.
        """

        if self.session_key is not None:
            response = self.table.get_item(
                Key={'session_key': self.session_key},
                ConsistentRead=ALWAYS_CONSISTENT)
            if 'Item' in response:
                session_data = self.decode(response['Item']['data'])
                time_now = timezone.now()
                time_ten_sec_ahead = time_now + timedelta(seconds=60)
                if time_now < session_data.get('_session_expiry',
                                               time_ten_sec_ahead):
                    return session_data

        self._session_key = None
        return {}

    def exists(self, session_key):
        """
        Checks to see if a session currently exists in DynamoDB.

        :rtype: bool
        :returns: ``True`` if a session with the given key exists in the DB,
            ``False`` if not.
        """
        if session_key is None:
            return False

        response = self.table.get_item(
            Key={'session_key': session_key},
            ConsistentRead=ALWAYS_CONSISTENT)
        if 'Item' in response:
            return True
        else:
            return False

    def create(self):
        """
        Creates a new entry in DynamoDB. This may or may not actually
        have anything in it.
        """

        while True:
            self._session_key = self._get_new_session_key()
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        """
        Saves the current session data to the database.

        :keyword bool must_create: If ``True``, a ``CreateError`` exception
            will be raised if the saving operation doesn't create a *new* entry
            (as opposed to possibly updating an existing entry).
        :raises: ``CreateError`` if ``must_create`` is ``True`` and a session
            with the current session key already exists.
        """

        if self.session_key is None:
            return self.create()

        update_kwargs = {
            'Key': {'session_key': self.session_key},
        }

        attribute_names = {'#data': 'data', '#ttl': 'ttl'}
        attribute_values = {
            ':data': self.encode(self._get_session(no_load=must_create)),
            ':ttl': int(time.time() + self.get_expiry_age())
        }
        set_updates = ['#data = :data', '#ttl = :ttl']
        if must_create:
            # Set condition to ensure session with same key doesnt exist
            update_kwargs['ConditionExpression'] = \
                DynamoConditionAttr('session_key').not_exists()
            attribute_values[':created'] = int(time.time())
            set_updates.append('created = :created')

        update_kwargs['UpdateExpression'] = 'SET ' + ','.join(set_updates)
        update_kwargs['ExpressionAttributeValues'] = attribute_values
        update_kwargs['ExpressionAttributeNames'] = attribute_names
        try:
            self.table.update_item(**update_kwargs)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ConditionalCheckFailedException':
                raise CreateError
            raise

    def delete(self, session_key=None):
        """
        Deletes the current session, or the one specified in ``session_key``.

        :keyword str session_key: Optionally, override the session key
            to delete.
        """

        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key

        self.table.delete_item(Key={'session_key': session_key})

    @classmethod
    def clear_expired(cls):
        # Todo figure out a way of filtering with timezone
        pass
