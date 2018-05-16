#!/usr/bin/python
# Filename: remoteaccess.py

from subprocess import PIPE, Popen
import macman


def ardStatus():
    """ Return ARD status of On or Off """
    p = Popen(['/usr/sbin/netstat', '-atp', 'tcp'], stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    if err: macman.logs.writeLog('Error: %s' % err)
    if 'RFB' in output.upper():
        return 'On'
    return 'Off'

def ardStop():
    """ Disable ARD """

    macman.logs.writeLog('Stopping ARD agent')
    macman.misc.kickstart('-deactivate', '-configure', '-access', '-off')


def ardStart():
    """ Enable ARD """

    macman.logs.writeLog('Starting ARD agent')
    macman.misc.kickstart('-activate', '-restart', '-agent')


def ardCheckAdmins(ard_admins):
    """ Ensure that only approved admins are allowed ARD access """

    admins_present = []

    # if list of admins provided (no munki manifest specified, will apply to all)
    if not isinstance(ard_admins, dict):
        for username in ard_admins:
            # check that user exists
            if macman.users.getUserID(username):
                admins_present.append(username)

    # if dictionary provided, assume munki manifest keys with lists of admins values
    else:

        # get munki manifest
        client_id = macman.munki.getClientIdentifier()

        # use site_default if current munki manifest not included in dictionary
        if client_id not in ard_admins:
            client_id = 'site_default'

        # check which approved admin accounts exist on computer
        for munki_manifest, admins_list in ard_admins.iteritems():
            if client_id == munki_manifest:
                for username in admins_list:
                    # check that user exists
                    if macman.users.getUserID(username):
                        admins_present.append(username)

    # get current user accounts with remote management permissions
    output = macman.misc.dscl('list', '/Local/Default/Users', 'naprivs')
    try:
        admins_current = [i.split()[0] for i in output.strip().split('\n')]
        
        # sort lists for comparison
        admins_current = sorted(admins_current)
        admins_present = sorted(admins_present)
    except IndexError:
        admins_current = ''

    if not admins_current == admins_present:
        macman.logs.writeLog('Current ARD admins: %s' % str(admins_current))
        macman.logs.writeLog('Correct ARD admins: %s' % str(admins_present))
        macman.logs.writeLog('ARD admin settings inconsistent, fixing')

        ardStop()

        # remove access to all current ard admins (necessary to reset permissions)
        for user in admins_current:
            macman.misc.dscl('delete', '/Local/Default/Users/%s' % user, 'naprivs')

        # allow access to only specific users
        macman.misc.kickstart('-configure', '-allowAccessFor', '-specifiedUsers')

        # allow access to present approved ard admins
        for user in admins_present:
            macman.misc.kickstart('-configure', '-users', '%s' % user, '-access', '-on', '-privs', '-all')

        ardStart()


def sshStatus():
    """ Return SSH status of On or Off """

    output = macman.misc.systemsetup('-getremotelogin')

    return output.strip().split()[2]


def sshStart():
    """ Sets remote login (SSH) to On """

    macman.misc.systemsetup('-setremotelogin', 'on')


def sshStop():
    """ Sets remote login (SSH) to Off """

    macman.misc.systemsetup('-setremotelogin', '-f', 'off')
