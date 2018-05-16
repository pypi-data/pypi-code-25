#!/usr/bin/python
# Filename: munki.py

import re
import urllib
import macman


managedinstalls_plist = '/Library/Preferences/ManagedInstalls.plist'
remotedesktop_plist = '/Library/Preferences/com.apple.RemoteDesktop.plist'


def getClientIdentifier():
    """ Return Munki ClientIdentifier """

    return macman.plists.readPlist(managedinstalls_plist, 'ClientIdentifier')


def setClientIdentifier(client_id):
    """ Set Munki ClientIdentifier and Text2 field of Remote Desktop """

    plist = {managedinstalls_plist: {'ClientIdentifier': client_id}}
    macman.plists.checkPlist(plist)

    plist = {remotedesktop_plist: {'Text2': client_id}}
    macman.plists.checkPlist(plist)


def getSoftwareRepoURL():
    """ Return Munki ClientIdentifier """

    return macman.plists.readPlist(managedinstalls_plist, 'SoftwareRepoURL')


def availableManifests():
    """ Return list of manifests available from the SoftwareRepoURL"""

    # get SoftwareRepoURL path
    software_url = getSoftwareRepoURL()

    # read html file
    try:
        htmlFile = urllib.urlopen('%s/manifests/' % software_url)
        html = htmlFile.read()
    except IOError:
        return None

    available_manifests = []
    for line in html.split():

        # search for text containted with href=" and >
        link = re.search('href="(.+?)" *>', line)

        if link is not None:

            # remove entries containg non-alphanumeric characters
            manifest = re.match('^[\w-]+$', link.group(1))

            # append to available manifests list
            if manifest is not None:
                available_manifests.append(manifest.group(0))

    return available_manifests
