import pymongo
from pymongo import MongoClient

import time
import json
import os
import io
import jsonschema
from jsonschema.exceptions import ValidationError

from . import Config
from .exceptions import IncidentNotFoundException,\
    DuplicateIncidentException, InvalidIncidentFormatException,\
    IncidentStorageLostException, InvalidQueryException, EventNotFoundException, IncidentStorageException
from pymongo.collection import ReturnDocument


def retry_auto_reconnect(func):
    """
    This is a decorator for functions that utilize some external storage driver.
    Any exception that reflects a connection error triggers an automatic
    retry of the given function. Those exceptions are defined in
    :func:`BasicOperationStorage.get_retry_exceptions`

    :param func: the function that will obtain retry feature
    :type func: function handle
    """

    def f_retry(self, *args, **kwargs):
        num_tries = Config.get("operation_storage", "retry_policy", "num", 3)
        wait_in_ms = Config.get("operation_storage", "retry_policy", "wait_in_ms", 0)
        exceptions = self.get_retry_exceptions()
        last_exception = None
        for i in range(num_tries):  # @UnusedVariable
            try:
                return func(self, *args, **kwargs)
            except exceptions as e:
                last_exception = e
                if wait_in_ms > 0:
                    time.sleep(wait_in_ms / 1000)
                continue
        raise IncidentStorageLostException(last_exception)
    return f_retry


class MongoDBStorage():
    """
    Store with MongoDB using the default json document definition

    On creating an instance the mongodb client is setup and all
    necessary databases and collections are created.
    """

    def get_retry_exceptions(self):
        """
        :func:`retry_auto_reconnect` decorator will act on these exceptions and trigger retry
        """
        return (pymongo.errors.AutoReconnect,
                pymongo.errors.ServerSelectionTimeoutError,)

    @retry_auto_reconnect
    def __init__(self, mongodb_config, purge=False):
        """
        This is a generic MongoDB instantiator
        :param mongodb_config:
        :type mongodb_config:
        :param purge:
        :type purge:
        """
        super(MongoDBStorage, self).__init__()

        if not mongodb_config:
            raise Exception("No mongo db configuration provided!")
        self._mongodb_config = mongodb_config

        self._mongodb_client = MongoClient(host=mongodb_config["seeds"])

        self._default_db = None
        if len(mongodb_config["databases"].keys()) == 1:
            self._default_db = list(mongodb_config["databases"].keys())[0]

        for database in mongodb_config["databases"].keys():
            database_object = self._mongodb_client[database]

            for collection in mongodb_config["databases"][database]["collections"].keys():
                if collection in\
                        database_object.collection_names(include_system_collections=False) and purge:
                    database_object[collection].drop()

                # if collections doesnt exist, create it
                if collection not in\
                        database_object.collection_names(include_system_collections=False):
                    collection_config = {"name": collection}
                    try:
                        collection_config.update(mongodb_config["databases"][database]["collections"][collection])
                    except TypeError:
                        pass
                    self._create_collection(database_object, collection_config)

            if self._default_db and len(mongodb_config["databases"][database]["collections"].keys()) == 1:
                self._default_collection = list(mongodb_config["databases"][database]["collections"].keys())[0]

    def _get_db(self, database_name=None):
        if not database_name and self._default_db:
            database_name = self._default_db
        return self._mongodb_client[database_name]

    def _get_collection(self, database_name=None, collection_name=None):
        if not collection_name and self._default_collection:
            collection_name = self._default_collection
        return self._get_db(database_name)[collection_name]

    def _create_collection(self, database_object, collection_config):
        database_object.create_collection(
            collection_config["name"]
        )
        if collection_config.get("unique") is not None:
            list_of_tuples = []
            for key in collection_config.get("unique"):
                list_of_tuples.append((key, pymongo.ASCENDING))
            database_object[collection_config["name"]].create_index(
                list_of_tuples,
                unique=True)

        if collection_config.get("indices") is not None:
            for index in collection_config.get("indices"):
                if type(index) == str:
                    index = [index]

                list_of_tuples = []
                for key in index:
                    list_of_tuples.append((key, pymongo.ASCENDING))
                database_object[collection_config["name"]].create_index(
                    list_of_tuples,
                    unique=False)


class IncidentStorage(MongoDBStorage):
    """
    TODO move everything generic into MongoDBStorage
    """

    INCIDENT_SCHEMA = None

    def validate_incident(self, incident):
        """
            Validates the given reformatted operation against the json schema given by
            :file:`operation_schema.json`

            :param operation: operation formatted as returned by :func:`decode_operation`
            :type operation:
        """
        if not IncidentStorage.INCIDENT_SCHEMA:
            schema_file = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "incident-schema.json"
            )
            IncidentStorage.INCIDENT_SCHEMA = json.loads(io.open(schema_file).read())
        try:
            # to validate date format against zulu time, rfc import is needed
            jsonschema.validate(incident,
                                IncidentStorage.INCIDENT_SCHEMA,
                                format_checker=jsonschema.FormatChecker())
        except ValidationError:
            raise InvalidIncidentFormatException()

    def _debug_print(self, operation):
        from pprint import pprint
        pprint(operation)

    @retry_auto_reconnect
    def get_status(self):
        status = self._get_collection(collection_name="status").find_one()
        if status:
            status.pop("_id")
        return status

    @retry_auto_reconnect
    def set_status(self, status):
        self._get_collection(collection_name="status").find_one_and_replace(
            {},
            status,
            upsert=True)

    def _unique_key(self, incident):
        try:
            return {"unique_string": incident["unique_string"],
                    "provider_info.name": incident["provider_info"]["name"]}
        except KeyError:
            raise InvalidIncidentFormatException()

    def _id_to_string(self, id_dict):
        if id_dict.get("id"):
            id_dict = id_dict["id"]
        try:
            return id_dict["start_time"] \
                + '-' + id_dict["sport"] \
                + '-' + id_dict["event_group_name"] \
                + '-' + id_dict["home"] \
                + '-' + id_dict["away"]
        except KeyError:
            raise InvalidIncidentFormatException()

    @retry_auto_reconnect
    def insert_incident(self, incident, keep_id=False):
        if not incident.get("id_string"):
            incident["id_string"] = self._id_to_string(incident)

        self.validate_incident(incident)

        try:
            self._get_collection(collection_name="incident").insert_one(
                incident
            )
            if not keep_id:
                incident.pop("_id")
        except pymongo.errors.DuplicateKeyError:
            raise DuplicateIncidentException()

    @retry_auto_reconnect
    def delete_incident(self, incident_or_primary_key):
        # do basics
        if type(incident_or_primary_key) == str:
            result = self._get_collection(collection_name="incident").delete_many(
                {"unique_string": incident_or_primary_key}
            )
        else:
            result = self._get_collection(collection_name="incident").delete_one(
                {"unique_string": incident_or_primary_key["unique_string"],
                 "provider_info.name": incident_or_primary_key["provider_info"]["name"]})
        if result.deleted_count == 0:
            raise IncidentNotFoundException()
        return result.deleted_count

    @retry_auto_reconnect
    def delete_incidents_by_id(self, incident_or_id_dict):
        if incident_or_id_dict is None:
            raise InvalidQueryException()
        filter_dict = {
            "id_string": self._id_to_string(incident_or_id_dict)
        }
        result = self._get_collection(collection_name="incident").delete_many(
            filter_dict
        )
        if result.deleted_count == 0:
            raise IncidentNotFoundException()
        return result.deleted_count

    @retry_auto_reconnect
    def get_incident(self, incident):
        incident = self._get_collection(collection_name="incident").find_one(
            self._unique_key(incident),
            {'_id': False}
        )
        if not incident:
            raise IncidentNotFoundException()
        return incident

    @retry_auto_reconnect
    def get_incidents(self, filter_dict=None):
        incident = self._get_collection(collection_name="incident").find(
            filter_dict,
            {'_id': False})
        return incident

    @retry_auto_reconnect
    def get_incidents_by_id(self, incident_or_id_dict=None, call=None):
        if incident_or_id_dict is None:
            raise InvalidQueryException()
        filter_dict = {
            "id_string": self._id_to_string(incident_or_id_dict)
        }
        if call is not None:
            filter_dict.update({
                "call": call
            })

        return self.get_incidents(
            filter_dict
        )

    @retry_auto_reconnect
    def incident_exists(self, incident):
        operation = self._get_collection(collection_name="incident").find_one(
            self._unique_key(incident),
            {"$exists": True}
        )
        if not operation:
            return False
        return True

    @retry_auto_reconnect
    def incident_exists_by_id(self, incident_or_id_dict=None, call=None):
        if incident_or_id_dict is None:
            raise InvalidQueryException()
        filter_dict = {
            "id_string": self._id_to_string(incident_or_id_dict)
        }
        if call is not None:
            filter_dict.update({
                "call": call
            })
        operation = self._get_collection(collection_name="incident").find_one(
            filter_dict,
            {"$exists": True}
        )
        if not operation:
            return False
        return True

    @retry_auto_reconnect
    def get_incidents_count(self):
        return self._get_collection(collection_name="incident").find().count()

#     @retry_auto_reconnect
#     def get_operations_in_progress(self, filter_by=None):
#         filter_dict = {"status": "in_progress"}
#         filter_dict.update(self._parse_filter(filter_by))
#         return list(self._operations_storage.find(filter_dict))


class EventStorage(IncidentStorage):

    @retry_auto_reconnect
    def get_event_by_id(self, incident_or_id_dict=None, resolve=True):
        if incident_or_id_dict is None:
            raise InvalidQueryException()
        filter_dict = {
            "id_string": self._id_to_string(incident_or_id_dict)
        }
        event = self._get_collection(collection_name="event").find_one(
            filter_dict
        )
        if resolve:
            def replace_with_incident(call_dict):
                if call_dict is None:
                    return
                for idx, incident_id in enumerate(call_dict["incidents"]):
                    incident = self._get_collection(collection_name="incident").find_one(
                        {"_id": incident_id},
                        {'_id': False}
                    )
                    if not incident:
                        raise IncidentNotFoundException()
                    incident.pop("id")
                    incident.pop("call")
                    call_dict["incidents"][idx] = incident
            replace_with_incident(event.get("create", None))
            replace_with_incident(event.get("in_progress", None))
            replace_with_incident(event.get("result", None))
            replace_with_incident(event.get("finish", None))
        if not event:
            raise EventNotFoundException()
        return event

    @retry_auto_reconnect
    def insert_incident(self, incident):
        super(EventStorage, self).insert_incident(incident, keep_id=True)

        if incident.get("_id", None) is None:
            raise IncidentStorageException("Something unknown went wrong")

        self._insert_or_update_event(incident)

        incident.pop("_id")

    @retry_auto_reconnect
    def _insert_or_update_event(self, incident):
        # check if it exists
        try:
            event = self.get_event_by_id(incident, resolve=False)
        except EventNotFoundException:
            event = {
                "id_string": self._id_to_string(incident)
            }
        if event.get(incident["call"], None) is None:
            event[incident["call"]] = {
                "incidents": [incident["_id"]],
                "status": {"name": "unknown"}
            }
        else:
            event[incident["call"]]["incidents"].append(incident["_id"])
        return self._get_collection(collection_name="event").find_one_and_replace(
            {"id_string": event["id_string"]},
            event,
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

    def update_event_status_by_id(self, incident_or_id_dict=None, call=None, status=None):
        if incident_or_id_dict is None or call is None or status is None:
            raise InvalidQueryException()
        return self._get_collection(collection_name="event").find_one_and_update(
            {"id_string": self._id_to_string(incident_or_id_dict)},
            {'$set': {call + ".status": status}},
            return_document=ReturnDocument.AFTER
        )
