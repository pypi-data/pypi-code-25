"""schema testers"""
import copy
import datetime
import enum
import json
import logging
import pathlib
import warnings

import deepdiff
import genson
import jsonschema
import pymongo
import semantic_version
from plumbum import cli

from . import _version
from . import exceptions
import prosper.common.prosper_cli as p_cli


with open(str(pathlib.Path(__file__).parent / 'root_schema.schema'), 'r') as schema_fh:
    ROOT_SCHEMA = json.load(schema_fh)

__all__ = [
    'MongoContextManager',
    'Update',
    'schema_helper',
]


class Update(enum.Enum):
    """enum for classifying what kind of update is required"""
    first_run = 'first_run'
    major = 'major'
    minor = 'minor'
    no_update = 'no_update'


class MongoContextManager:
    """context manager for mongo connections

    Notes:
        connection_str requires {username}, {password} format strings

    Args:
        config (:obj:`prosper.common.prosper_config.ProsperConfig`): configparser-like object
        _testmode (bool): use a localdb rather than a prod one
        _testmode_filepath (str): path to localdb

    """

    def __init__(
            self,
            config,
            _testmode=False,
            _testmode_filepath=pathlib.Path(__file__).parent,
    ):
        self.username = config.get_option('MONGO', 'username')
        self.password = config.get_option('MONGO', 'password')
        self.database = config.get_option('MONGO', 'database')
        self.connection_string = config.get_option('MONGO', 'connection_string')
        self._testmode = _testmode
        self._testmode_filepath = _testmode_filepath
        # TODO: validate {} in connection_str

    def __get_connector(self):
        """switches between testmode/prod connectors

        Returns:
            pymongo.MongoCollection: connection to mongodb

        """
        if self._testmode:
            import tinymongo
            return tinymongo.TinyMongoClient(foldername=str(self._testmode_filepath))

        return pymongo.MongoClient(
            self.connection_string.format(
                username=self.username,
                password=self.password,
            )
        )

    def __enter__(self):
        """with MongoContextManager() entrypoint"""
        self.connection = self.__get_connector()
        return self.connection[self.database]

    def __exit__(self, *exc):
        """with MongoContextManager() exitpoint"""
        self.connection.close()

def generate_first_run_metadata(
        schema_name,
        schema_group,
        version='1.0.0',
):
    """generate basic metadata frame for first_run case.  Broken out as test-helper

    Args:
        schema_name (str): name of data source
        schema_group (str): group for data source
        version (str): semantic version of init data

    Returns:
        dict: "blank" metadata object for first_run case

    """
    return dict(
        schema_group=schema_group,
        schema_name=schema_name,
        update='',
        version=version,
        schema={},
    )

def generate_schema_from_data(
        raw_data,
        data_source='',
):
    """generate jsonschema from raw dict with genson.  Broken out as test-helper

    Args:
        raw_data (dict): raw json data from source
        data_source (str): source of data being jsonschema'd

    Returns:
        dict: jsonschema

    """
    builder = genson.SchemaBuilder(data_source)
    builder.add_object(raw_data)
    return builder.to_schema()

def fetch_latest_schema(
        schema_name,
        schema_group,
        mongo_collection,
):
    """find latest schema in database

    Args:
        schema_name (str): data source name
        schema_group (str): datas source group
        mongo_collection (:obj:`pymongo.collection`): db connection handle

    Returns:
        dict: jsonschema object with latest version

    """
    schema_list = list(mongo_collection.find({
        '$and':[
            {'schema_name': schema_name},
            {'schema_group': schema_group},
        ],
    }))
    if not schema_list:
        warnings.warn(
            '{}.{} schema not in database -- creating fresh entry'.format(
                schema_group, schema_name),
            exceptions.FirstRunWarning
        )
        return generate_first_run_metadata(schema_name, schema_group)

    data = max(
        schema_list, key=lambda x: semantic_version.Version(x['version'])
    )
    data.pop('_id', None)  # remove Mongo $_id from working frame
    return data

def compare_schemas(
        sample_schema,
        current_schema,
):
    """compare 2 jsonschemas and look for changes.  Checks required[] keys

    Notes:
        Update.minor: added required keys, but did not remove anything
        Update.major: removed required keys or otherwise changed structure
        Update.no_update: schemas are identical

    Args:
        sample_schema (dict): incomming schema to validate
        current_schema (dict): current schema from database

    Returns:
        Update: update status of comparison

    """
    logger = logging.getLogger(_version.__library_name__)
    if not sample_schema:
        return Update.first_run

    diff = deepdiff.DeepDiff(sample_schema, current_schema)
    logger.debug(diff)
    is_minor = any([
        'dictionary_item_added' in diff,
        'iterable_item_added' in diff,
    ])
    is_major = any([
        'dictionary_item_removed' in diff,
        # 'values_changed' in diff,
        'type_changes' in diff,  # is minor?
        'iterable_item_removed' in diff
    ])

    if is_major:
        return Update.major
    if is_minor:
        return Update.minor
    if diff:
        raise exceptions.UnhandledDiff(str(diff.keys()))

    return Update.no_update

def build_metadata(
        schema,
        current_metadata,
        update_type,
):
    """build updated schema

    Args:
        schema (dict): jsonschema for data source
        current_metadata (dict): current table entry frame
        update_type (enum): what kind of update to perform

    Returns:
        dict: updated current_metadata

    """
    updated_metadata = copy.deepcopy(current_metadata)
    if any([
            update_type == Update.first_run,
            update_type == Update.minor,
            update_type == Update.major,
    ]):
        updated_metadata['schema'] = schema
        updated_metadata['update'] = datetime.datetime.utcnow().isoformat()

    current_version = semantic_version.Version(current_metadata['version'])
    if update_type == Update.minor:
        updated_metadata['version'] = str(current_version.next_patch())
    elif update_type == Update.major:
        updated_metadata['version'] = str(current_version.next_minor())

    jsonschema.validate(updated_metadata, ROOT_SCHEMA)

    return updated_metadata

def dump_major_update(
        metadata,
        filepath,
):
    """dump major update to a local file for humans to review/update

    Args:
        metadata (dict): proposed new entry
        filepath (:obj:`pathlib.Path`): path to dump file

    Returns:
        str: path to dump file

    """
    if not filepath.exists():
        collection = []
    else:
        with open(str(filepath), 'r') as coll_fh:
            collection = json.load(coll_fh)

    collection.append(metadata)

    with open(str(filepath), 'w') as coll_fh:
        json.dump(collection, coll_fh)

    return str(filepath)

MAJOR_UPDATE_FILEPATH = 'prosper-schema-update_{}.json'.format(
    datetime.datetime.utcnow().isoformat())
def schema_helper(
        data,
        data_source,
        schema_name,
        schema_group,
        config,
        _collection_name='prosper_schemas',
        _testmode=False,
        _dump_filepath='',
):
    """test helper: generates schemas from data and checks them against a mongoDB.
        Updates for minor changes (adding keys)
        Raises errors for major changes


    Args:
        data (dict): data to generate jsonschema from (raw data)
        data_source (str): link to source
        schema_name (str): name of resource for tracking
        schema_group (str): group (project name) for grouping
        config (:obj:`prosper.common.ProsperConfig`): config object with [MONGO] credentials
        _testmode (bool): run on local database with TinyMongo
        _dump_filepath (str): path to dump files to

    Returns:
        ???

    """
    logger = logging.getLogger(_version.__library_name__)

    logger.info('Parsing data into jsonschema')
    schema = generate_schema_from_data(data, data_source)
    logger.debug(schema)

    mongo_context = MongoContextManager(
        config, _testmode_filepath=_dump_filepath, _testmode=_testmode
    )
    with mongo_context as mongo:
        logger.info(
            'Fetching current schema from database: `%s.%s.%s`',
            _collection_name, schema_group, schema_name
        )
        current_metadata = fetch_latest_schema(
            schema_name, schema_group, mongo[_collection_name]
        )
        logger.debug(current_metadata['schema'])

        logger.info('Comparing schemas')
        update_status = compare_schemas(
            current_metadata['schema'], schema
        )
        logger.debug(update_status)

        logger.info('Generating updated metadata')
        metadata = build_metadata(
            schema, current_metadata, update_status,
        )
        logger.debug(metadata)

        if any([
                update_status == Update.minor,
                update_status == Update.first_run,
        ]):
            logger.info('Updating database')
            _id = mongo[_collection_name].insert_one(metadata)

        elif update_status == Update.major:
            logger.error(
                'Major update -- Please run `update-prosper-schemas %s` to update db',
                MAJOR_UPDATE_FILEPATH
            )
            dump_file = dump_major_update(
                metadata, pathlib.Path(_dump_filepath) / MAJOR_UPDATE_FILEPATH)
            raise exceptions.MajorSchemaUpdate(dump_file)
        else:
            logger.info('No updates applied to database')


class UpdateProsperSchemas(p_cli.ProsperApplication):  # pragma: no cover
    """cli utility for writing major updates to mongoDB"""
    PROGNAME = 'update-prosper-schemas'
    VERSION = _version.__version__

    config_path = str(pathlib.Path(__file__).parent / 'app.cfg')

    HERE = cli.SwitchAttr(
        '--local-dir',
        cli.ExistingDirectory,
        help='local working directory for scripty stuff',
        default=str(pathlib.Path('')),
    )
    schema_collection = cli.SwitchAttr(
        '--collection',
        str,
        help='Mongo collection to write to',
        default='ProsperSchemas',
    )

    def main(self, update_file):
        """main do stuff"""
        self.logger.info('Loading update file: %s', update_file)
        with open(update_file, 'r') as update_fh:
            update_recipe = json.load(update_fh)

        mongo_context = MongoContextManager(
            self.config,
            _testmode_filepath=self.HERE,
            _testmode=self.debug,
        )

        self.logger.info('connecting to Mongo')
        with mongo_context as mongo:
            for update in update_recipe:
                self.logger.info(
                    'writing update for %s.%s', update['schema_group'], update['schema_name']
                )
                receipt = mongo[self.schema_collection].insert_one(update)
                self.logger.debug(receipt)

        self.logger.info('updated remote collection')


def run_plumbum():  # pragma: no cover
    """entrypoint hook for running CLI"""
    UpdateProsperSchemas.run()

if __name__ == '__main__':  # pragma: no cover
    run_plumbum()
