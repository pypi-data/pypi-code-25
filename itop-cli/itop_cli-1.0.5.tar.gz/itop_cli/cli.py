#!/usr/bin/env python
"""
  Usage:
    itop.py delete <class> <query> (--env=<env>|--config=<config>)
    itop.py export <class> [<query>] (--env=<env>|--config=<config>) [--pretty]
    itop.py import <class> --input=<input_file> [--search_keys=<search_keys>] (--env=<env>|--config=<config>)
    itop.py create <class> [FIELDS]... (--env=<env>|--config=<config>)
    itop.py update <class> <search> [FIELDS]... (--env=<env>|--config=<config>)
    itop.py -h | --help | --version

  Arguments:
    FIELDS                         Key value pairs. Ex : "description=Ceci est une description". If not overridden, the script will use the org_id of the config file
    <query>                        OQL query.
    <search>                       Simple search element. "key=value" format

  Options:
    -e <env> --env=<env>                            Will search ~/.itop/<venv>.json as configuration file
    -c <config> --config=<config>                   Path to config file
    -s <search_keys> --search_keys=<search_keys>    Key(s) to search objects, comma separated [default: name]
    -i <input_file> --input=<input_file>            File to use for data input
    -p --pretty                                     Prettify JSON output

  Examples:
    itop delete Person 'SELECT Person WHERE status="inactive"' --env=dev
    itop export SynchroDataSource --env=dev
    itop export Server "SELECT Server WHERE name LIKE 'SRVTEST'" --env=dev
    itop import SynchroDataSource --input=/tmp/out.json --search_keys=database_table_name
    itop create Server "name=SRVTEST" "description=Serveur de test" --env=dev
    itop update Server "name=SRVTEST" "description=Serveur de prod" --env=dev
    itop update Server "name=SRVTEST" "description=Serveur de prod" "brand_id=SELECT Brand WHERE name='Altiris'" --env=dev
"""

from os.path import join, expanduser

from json import load, dumps
from docopt import docopt

import itopy

from . import import_data, export_data, delete, create, update

def org_id(itop, org_name):
    """
    Search the id of an organization
    :param itop: itop connection
    :param org_name: name of the organization to search
    :return:
    """
    response = itop.get('Organization', 'SELECT Organization WHERE name = "%s"' % org_name)
    if "code" not in response:
        raise BaseException(response)
    if response['code'] != 0 and response['message'] != 'Found: 1':
        exit("Organization '{}' not found".format(org_name))
    code = list(response['objects'].values())[0]['key']
    return code


def main_itop():
    ARGUMENTS = docopt(__doc__, version='0.1')

    if ARGUMENTS["--config"] is not None:
        CONF_PATH = ARGUMENTS["<config>"]

    if ARGUMENTS["--env"] is not None:
        CONF_PATH = join(expanduser('~'), ".itop", ARGUMENTS["--env"] + ".json")

    try:
        CONF = load(open(CONF_PATH, "r"))
    except IOError as exception:
        exit(str(exception))

    if ("url" not in CONF) \
            or ("version" not in CONF) \
            or ("user" not in CONF)\
            or ("password" not in CONF)\
            or ("org_name" not in CONF):
        exit("Wrong config file format")

    ITOP = itopy.Api()
    ITOP.connect(CONF["url"], CONF["version"], CONF["user"], CONF["password"])

    # Connection test. This value will also be used for creations
    try:
        ORG_ID = org_id(ITOP, CONF["org_name"])
    except BaseException as exception:
        exit(str(exception))

    try:
        if ARGUMENTS["delete"]:
            delete(ITOP, ARGUMENTS["<class>"], ARGUMENTS["<query>"], )

        if ARGUMENTS["export"]:
            EXPORT = export_data(ITOP, ARGUMENTS["<class>"], ARGUMENTS["<query>"])
            if ARGUMENTS["--pretty"]:
                print(dumps(EXPORT, sort_keys=True, indent=4, separators=(',', ': ')))
            else:
                print(dumps(EXPORT))

        if ARGUMENTS["import"]:
            DATA = open(ARGUMENTS["--input"], "r")
            import_data(ITOP, ARGUMENTS["<class>"], DATA, ARGUMENTS["--search_keys"])

        if ARGUMENTS["create"]:
            FIELDS = ARGUMENTS["FIELDS"]
            if "org_id" not in FIELDS:
                FIELDS.append("org_id=%s" % ORG_ID)
            create(ITOP, ARGUMENTS["<class>"], ARGUMENTS["FIELDS"])

        if ARGUMENTS["update"]:
            FIELDS = ARGUMENTS["FIELDS"]
            update(ITOP, ARGUMENTS["<class>"], ARGUMENTS["<search>"], ARGUMENTS["FIELDS"])

    except Exception as exception:
        exit("{} : {}".format(type(exception), str(exception)))
