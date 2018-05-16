#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: plists.py

import os
import plistlib
from subprocess import Popen, PIPE
from xml.parsers.expat import ExpatError
import macman


def checkPlist(plists):
    """ Compare values in a plist to values in a dictionary. If values do not match the dictionary
    values will be used. Dictionary format is nested, with the plist path as root key. Secondary nested
    dictionaries are assumed to contain a munki manifest and value.

    Will require write permission for plist.

    Example dictionary:

    plists = {'/Library/Preferences/com.apple.loginwindow.plist': {                 << plist path
                'affected_services': 'SomeService SomeOtherService',                << list of affected services
                'RestartDisabledWhileLoggedIn': False,                              << key and values
                'HideMobileAccounts': False,
                'HideLocalUsers': False,
                'LoginwindowText': {                                                << secondary nested dictionary
                        'site_default': 'Welcome to the Home of the Mighty Lynx.',  << munki manifest key and value
                        'student': 'Welcome to the 2016-2017 school year!',
                        'staff': 'Welcome NCPS Staff!'
                }
            }
    }

    """
    # Get munki manifest set on computer
    client_id = macman.munki.getClientIdentifier()

    for plist_path, plist_content in plists.iteritems():
        to_write = False
        services = None

        # replace tilde with user home path
        if plist_path.startswith('~'):
            plist_path = macman.misc.tildeToPath(macman.users.getCurrentUser(), plist_path)

        # read current plist contents into dictionary
        current_plist = readPlist(plist_path)

        for key, value in plist_content.iteritems():

            # get list of services to restart if plist is changed
            if key == 'affected_services':
                services = value

            # if value is not a dictionary
            elif not isinstance(value, dict):

                # compare current plist contents to scripted plist contents
                try:
                    if current_plist[key] != value:
                        to_write = True
                        current_plist[key] = value
                        macman.logs.writeLog('%s "%s" incorrect, setting value to: "%s"' % (plist_path, key, str(value)))

                # if scripted key doesn't exist in current plist
                except (KeyError, TypeError):
                    to_write = True
                    current_plist[key] = value
                    macman.logs.writeLog('%s "%s" does not exist, setting value to: "%s"' % (plist_path, key, str(value)))

            else:

                # if value is a dictionary, assume its keys are munki manifests
                try:

                    # if client_id doesn't match one of the scripted manifests, use generic settings
                    if client_id not in value:
                        macman.logs.writeLog('Munki manifest "%s" not found in dictionary. Using "site_default"' % str(client_id))
                        client_id = 'site_default'

                    # compare current plist contents to correct plist contents, based on client_id
                    for dict_key, dict_value in value.iteritems():
                        if client_id == dict_key and current_plist[key] != value[client_id]:
                            to_write = True
                            current_plist[key] = value[client_id]
                            macman.logs.writeLog('%s "%s" incorrect, setting value to: "%s"' % (plist_path, key,
                                                                                                str(value[client_id])))
                            break

                # if key doesn't exist
                except (KeyError, TypeError):
                    for dict_key, dict_value in value.iteritems():
                        if client_id == dict_key:
                            to_write = True
                            current_plist[key] = dict_value
                            macman.logs.writeLog('%s "%s" does not exist, setting value to: "%s"' % (plist_path, key,
                                                                                                     str(dict_value)))

        # Write dictionary to plist
        if to_write:
            writePlist(plist_path, current_plist, services)


def readPlist(plist_path, key=None):
    """ Return plist data. If key is given, return only value of that key """

    # replace tilde with current user home path
    if plist_path.startswith('~'):
        plist_path = macman.misc.tildeToPath(macman.users.getCurrentUser(), plist_path)

    # if file exists read contents into dictionary
    if os.path.isfile(plist_path):

        # if no key provided
        if not key:

            # return entire plist
            try:
                current_plist = plistlib.readPlist(plist_path)

            # when plist format is binary it must be converted to xml before reading
            except ExpatError:
                # convert to xml
                plist_string = macman.misc.plutil('-convert', 'xml1', '-o', '-', plist_path)
                current_plist = plistlib.readPlistFromString(plist_string)

        # if key provided
        else:

            # return only value of key
            try:
                current_plist = plistlib.readPlist(plist_path)[key]

            # when plist format is binary it must be converted to xml before reading
            except ExpatError:
                # convert to xml
                plist_string = macman.misc.plutil('-convert', 'xml1', '-o', '-', plist_path)
                try:
                    current_plist = plistlib.readPlistFromString(plist_string)[key]

                # if key doesn't exist, return empty dictionary
                except KeyError:
                    current_plist = {}

            # if key doesn't exist, return empty dictionary
            except KeyError:
                current_plist = {}

    # if file does not exist, return empty dictionary
    else:
        current_plist = {}

    return current_plist


def writePlist(plist_path, plist_dict, services=None):
    """ Write dictionary to plist. Will require write permission for plist. """

    output = None

    # replace tilde with user home path
    if plist_path.startswith('~'):
        plist_path = macman.misc.tildeToPath(macman.users.getCurrentUser(), plist_path)

    if os.path.isfile(plist_path):

        # if file not read/write able
        if not os.access(plist_path, os.W_OK):
            # attempt to change permissions.
            macman.files.setPathPermissions(plist_path, '0774')

        # check if plist is in xml or binary format
        p = Popen('file "%s"' % plist_path, shell=True, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        macman.logs.writeLog(err); macman.logs.writeLog(output)

    # retrieve current plist file uid, gid, and permissions
    plist_permissions = macman.files.getPathPermissions(plist_path)

    # if no permissions returned (file doesn't exist) set owner to current user, staff group, and 664 oct permissions
    uid = plist_permissions['uid'] if plist_permissions['uid'] else macman.users.getUserID(macman.users.getCurrentUser())
    gid = plist_permissions['gid'] if plist_permissions['gid'] else 20
    mode = plist_permissions['mode'] if plist_permissions['mode'] else 0664

    # write new plist
    plistlib.writePlist(plist_dict, plist_path)

    # convert plist to binary if necessary
    if output and 'BINARY' in output.upper():
        macman.misc.plutil('-convert', 'binary1', '"%s"' % plist_path)

    # restore plist file permissions
    macman.files.setPathPermissions(plist_path, mode)
    macman.files.setPathUidGid(plist_path, uid, gid)

    # kill all affected services
    if services:
        macman.misc.killAll(services)


def binaryToXml(plist_path):
    """ Convert a binary formatted plist to xml format. Write permissions required. """

    return macman.misc.plutil('-convert', 'xml1', '%s' % plist_path)


def xmlToBinary(plist_path):
    """ convert a xml formatted plist to binary. Write permissions required. """

    return macman.misc.plutil('-convert', 'binary1', '%s' % plist_path)
