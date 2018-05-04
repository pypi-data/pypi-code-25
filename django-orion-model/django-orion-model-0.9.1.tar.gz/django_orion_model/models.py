from collections.__init__ import defaultdict
from datetime import timedelta

from django.conf import settings
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models

# Create your models here.
from django.utils.timezone import now
from pyfiware import OrionManager
from logging import getLogger

logger = getLogger(__name__)


def _expire_time():
    return now() + timedelta(seconds=settings.ORION_EXPIRATION)


def _orion_get(self, item):
    _get = super().__getattribute__
    if item in _get('_orion_fields'):
        self.refresh_orion()
    return _get(item)


def _orion_set(self, key, value):
    if key in self._orion_fields:
        self.updated.append(key)
        self.save_to_orion()
    super().__setattr__(key, value)


def retrieve_orion(manager, broker, scope):
    try:
        return manager[broker][scope]
    except KeyError:
        manager[broker][scope] = OrionManager(host=broker, scopes=scope)
        return manager[broker][scope]


class Scope(models.Model):
    name = models.CharField(max_length=1011, unique=True)
    path = models.URLField()


class Broker(models.Model):
    name = models.CharField(max_length=1011, unique=True)
    url = models.URLField()


class OrionEntity(models.Model):
    ORION_TYPE = "Entity"
    ORION_SUB_TYPE = None

    # Created and awaiting to be pushed to Orion
    STATUS_CREATING = "CREATING"
    # Created and awaiting to be populated from Orion
    STATUS_CREATED = "CREATED"
    # The mention is currently writing from orion
    STATUS_PENDING_WRITING = "WRITING"
    # The mention is currently reading from orion
    STATUS_PENDING_READING = "READING"
    # The Entity does not need to write or read from Orion
    STATUS_OK = "OK"
    # The mention awaits for repeat a writing
    STATUS_AWAIT_REWRITING = "REWRITING"
    # The mention awaits for repeat a reading
    STATUS_AWAIT_REFRESH = "REFRESH"
    # The entity is not connected to Orion
    STATUS_OFFLINE = "OFFLINE"
    # The mention does not have a reflect in Orion
    STATUS_MISSING = "MISSING"

    STATUS_OPTIONS = [
        (STATUS_CREATING, "Creating"),
        (STATUS_CREATED, "Created"),
        (STATUS_PENDING_WRITING, "Pending writing"),
        (STATUS_PENDING_READING, "Pending reading"),
        (STATUS_OK, "Ok"),
        (STATUS_AWAIT_REFRESH, "Await refresh"),
        (STATUS_AWAIT_REWRITING, "Await rewrite"),
        (STATUS_OFFLINE, "Offline"),
        (STATUS_MISSING, "Missing"),
    ]

    STATUS_CREATION = [
        (STATUS_CREATING, "Creating"),
        (STATUS_CREATED, "Created"),
        (STATUS_OK, "Ok"),
        (STATUS_OFFLINE, "Offline"),
    ]
    broker = models.ForeignKey(Broker, models.CASCADE)
    scope = models.ForeignKey(Scope, models.CASCADE)

    orion_id = models.CharField(unique=True, max_length=1011)
    type = models.CharField(max_length=1011)
    data = JSONField(blank=True, default=dict)

    updated = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    expiration = models.DateTimeField(default=_expire_time)
    status = models.CharField(blank=True, default="created", max_length=50, choices=STATUS_OPTIONS)
    error = models.TextField(blank=True)
    _orion = defaultdict(dict)

    @property
    def orion(self):
        return retrieve_orion(self._orion, self.broker, self.scope)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.type = kwargs.get("orion_type", getattr(self, "ORION_TYPE", None))
        if self.type is None:
            raise Exception("Set entity type as orion_type parameter or orion_type_default class attribute")

        self._orion_fields = set(f.attname for f in self._meta.fields if issubclass(type(f), OrionField))
        self.__getattribute__ = _orion_get
        self.__setattr__ = _orion_set

    @property
    def history_cache(self):
        return self._history_cache

    @history_cache.setter
    def history_cache(self, value):
        self._history_cache = value

    def history(self, time_slice):
        if type(time_slice) is list:
            return [[key, self.history_cache.get(key, None)] for key in time_slice]
        return self.history_cache.fromkeys(time_slice)

    @classmethod
    def from_db(cls, db, field_names, values):
        """Override model save methods """
        orion_object = super().from_db(db, field_names, values)
        orion_object.update_from_orion()
        return orion_object

    def save(self, *args, **kwargs):
        """Override model save methods """
        self.save_to_orion()
        super().save(*args, **kwargs)

    # Orion Connectivity
    def refresh_orion(self):
        reload = self.expiration > now()
        if self.status == self.STATUS_CREATED:
            logger.warning("Lecture of %s while unset", self.orion_id)
            reload = True
        elif self.status == self.STATUS_PENDING_WRITING:
            logger.warning("Lecture of %s while transition status %s", self.orion_id, self.status)
        elif self.status == self.STATUS_PENDING_READING:
            logger.warning("Lecture of %s while transition status %s", self.orion_id, self.status)
            reload = True
        elif self.status == self.STATUS_AWAIT_REFRESH:
            reload = True
        if reload:
            self.update_from_orion()
        for key in self.data:
            try:
                super().__setattr__(key, self.data[key])
            except KeyError:
                pass

    def save_to_orion(self):
        """ Saves the object to Orion context broker.

        If an error occurs object is marked as STATUS_AWAIT_REWRITING and keeps update flags.
        If everything goes correctly update flags are resets and a reading is launched.

        :return: Nothing
        """
        if self.status == self.STATUS_OFFLINE:
            return

        if self.status == self.STATUS_CREATING:
            attributes = self.data
            for field in self._orion_fields:
                attributes[field] = super().__getattribute__(field)
            try:
                self.orion.create(element_id=self.orion_id, element_type=self.type, **attributes)
                self.update_from_orion()
                self.updated = ""
            except Exception as ex:
                self.error = "Error creating: {0}".format(ex)
                self.status = self.STATUS_AWAIT_REWRITING
            return

        self.status = self.STATUS_PENDING_WRITING
        try:
            if self.updated:
                update_json = {}
                for field in self.updated.split(","):
                    update_json[field] = self.data[field]
                self.orion.patch(element_id=self.orion_id, **update_json)
                self.updated = ""
            self.update_from_orion()
        except Exception as ex:
            self.error = str(ex)
            self.status = self.STATUS_AWAIT_REWRITING

    def update_from_orion(self):
        """ The object data is updated from the Orion context broker.

        If an error occurs object is marked as STATUS_AWAIT_REFRESH and awaits keeps old data
        If everything goes correctly data is stored, expiration mark is set and object is marked as STATUS_OK.

        :return: Nothing
        """
        if self.status == self.STATUS_OFFLINE:
            return

        self.status = self.STATUS_PENDING_READING
        try:
            response = self.orion.get(entity_id=self.orion_id, silent=True)
            if response:
                self.data = response
                self.expiration = _expire_time()
                self.type = self.data.get("type")
                for field in self._orion_fields:
                    if field is OrionField:
                        field.update_from_json()
                self.status = self.STATUS_OK
            else:
                self.status = self.STATUS_MISSING
        except Exception as ex:
            self.error = str(ex)
            self.expiration = now()
            self.status = self.STATUS_AWAIT_REFRESH

    @classmethod
    def search(cls, entity_type=None, id_pattern=None, query=None,
               broker=settings.ORION_URL, scope=settings.ORION_SCOPE):
        """Find suitable entities from Orion"""
        orion = retrieve_orion(cls._orion, broker, scope)
        response = orion.search(entity_type=entity_type, id_pattern=id_pattern, query=query)
        return [entity for entity in response]

    @classmethod
    def remove_form_orion(cls, orion_id, entity_type, broker=settings.ORION_URL, scope=settings.ORION_SCOPE):
        """ Ask Orion to remove a entity"""
        orion = retrieve_orion(cls._orion, broker, scope)
        orion.delete(entity_id=orion_id, entity_type=entity_type)


class OrionField:
    orion_field = True


class OrionCharField(models.CharField, OrionField):
    pass


class OrionTextField(models.TextField, OrionField):
    pass


class OrionFloatField(models.FloatField, OrionField):
    pass


class OrionDateTimeField(models.DateTimeField, OrionField):
    pass
