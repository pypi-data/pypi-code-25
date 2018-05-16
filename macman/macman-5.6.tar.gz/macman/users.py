#!/usr/bin/python
# Filename: users.py

import pwd
from subprocess import Popen, PIPE
import shutil
import grp
import os
import macman


def getUserID(username):
    """ Get a user id. Return None is user does not exist """

    output = macman.misc.dscl('-read', '/Local/Default/Users/%s' % username, 'UniqueID')

    try:
        return output.strip().split()[1]
    except:
        return None


def deleteUser(username):
    """ Delete user if it exists """

    # check if user exists
    if getUserID(username) is not None:

        # see if user is currently logged in, force logout
        if getCurrentUser() == username:
            macman.misc.killAll('loginwindow')
            macman.logs.writeLog('User "%s" currently logged in. Forcing logout.' % username)

        # get list of groups user belongs to
        groups = [g.gr_name for g in grp.getgrall() if username in g.gr_mem]
        gid = pwd.getpwnam(username).pw_gid
        groups.append(grp.getgrgid(gid).gr_name)

        # get user home directory
        userhome = getUserHome(username)

        shadow_file = '/var/db/dslocal/nodes/Default/users/%s' % username

        # delete user from groups
        macman.logs.writeLog('Removing user "%s" from groups: %s' % (username, str(groups)))
        for group in groups:
            macman.misc.dscl('-delete', '/Local/Default/Groups/%s' % group, 'GroupMembership', '%s' % username)

        # delete user account
        macman.logs.writeLog('Deleting user "%s"' % username)
        macman.misc.dscl('-delete', '/Local/Default/Users/%s' % username)

        # delete user home folder
        if os.path.exists(userhome):
            macman.logs.writeLog('Deleting home directory "%s"' % userhome)
            shutil.rmtree(userhome)
        else:
            macman.logs.writeLog('User "%s" has no home directory to delete.' % username)

        # delete user shadow hash file
        if os.path.exists(shadow_file):
            macman.logs.writeLog('Deleting user shadow file "%s"' % userhome)
            shutil.rmtree(shadow_file)
        else:
            macman.logs.writeLog('User "%s" has no shadow file to delete.' % username)


def createUser(username, password, user_id, primary_group, user_picture_path=None):
    """ Create a new local user """

    # if home folder already exists, add number to the path until unique found
    home_folder = '/Users/%s' % username
    i = 0
    while os.path.exists(home_folder):
        home_folder = '/Users/%s%s' % (username, str(i))
        i += 1

    macman.logs.writeLog('Creating user "%s.' % username)
    macman.misc.dscl('-create', '/Local/Default/Users/%s' % username)
    macman.misc.dscl('-create', '/Local/Default/Users/%s' % username, 'UserShell', '/bin/bash')
    macman.misc.dscl('-create', '/Local/Default/Users/%s' % username, 'RealName', username)
    macman.misc.dscl('-create', '/Local/Default/Users/%s' % username, 'PrimaryGroupID', str(primary_group))
    macman.misc.dscl('-passwd', '/Local/Default/Users/%s' % username, password)
    macman.misc.dscl('-create', '/Local/Default/Users/%s' % username, 'NFSHomeDirectory', home_folder)

    if not user_id:
        # get unique uid for new user
        output = macman.misc.dscl('-list', '/Local/Default/Users', 'UniqueID')
        uids = []
        for i in output.strip().split('\n'):
            uids.append(int(i.strip().split()[1]))
        user_id = max(uids) + 1
    macman.misc.dscl('-create', '/Local/Default/Users/%s' % username, 'UniqueID', str(user_id))

    if user_picture_path and os.path.exists(user_picture_path):
        macman.misc.dscl('-create', '/Local/Default/Users/%s' % username, 'Picture', user_picture_path)



def getCurrentUser():
    """ Return current logged in user """

    p = Popen('ls -l /dev/console', shell=True, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    macman.logs.writeLog(err)

    return output.split()[2]


def getUserHome(username):
    """ Return path to user home """

    home_folder = os.path.expanduser('~%s' % username)

    # if returns a string starting with tilde, user home does not exist
    if not home_folder.startswith('~'):
        return home_folder
    return None


def getUserPasswordHash(username):
    """ Return password hash for a user """

    output = macman.misc.defaults('read', '/var/db/dslocal/nodes/Default/users/%s' % username, 'ShadowHashData')

    return output.strip().replace('\n    ', '').replace('\n', '')


def setUserPasswordHash(username, password_hash):
    """ Return password hash for a user """

    macman.misc.defaults('write', '/var/db/dslocal/nodes/Default/users/%s' % username, 'ShadowHashData', password_hash)


def getAdminUsers():
    """ Return list of local admin users """
    output = macman.misc.dscl('-read', '/Local/Default/Groups/admin')
    for line in output.split('\n'):
        if 'GroupMembership' in line:
            return line.split(':')[1].strip().split()
    return None


def refreshUser():

    # setup logging
    log_file = '{file_name}.log'
    macman.logs.setupLogging(log_file)

    username = '{username}'
    primary_group = {primary_group}
    password = '{password}'
    user_picture_path = '{user_picture_path}'

    current_user = macman.users.getCurrentUser()
    admin_users = macman.users.getAdminUsers()

    # if current user is not an admin user error prompt
    if current_user not in admin_users:

        # setup error dialog
        title = 'Error: Unauthorized user'
        informative_text = 'User "%s" does not have the authority to perform this task.' % current_user
        body_text = 'Please try again with an admin user'
        macman.dialog.infoMsgBox(title, informative_text, body_text)

    # if current user is an admin user
    else:

        # if username does not exist
        if not macman.users.getUserID(username):
            title = 'Error:'
            body_text = 'Error: User account "%s" does not exist on this machine.' % username
            informative_text = 'Do you wish to create it?'
            dialog_return = macman.dialog.okMsgBox(title, informative_text, body_text)

            if dialog_return == 'OK':
                macman.users.createUser(username, password, primary_group, user_picture_path)

        elif current_user is username:
            title = 'Error:'
            body_text = 'Error: User "%s" is currently logged in. Please log in as another user before installing this application.' % username
            informative_text = 'Terminating installation.'
            macman.dialog.infoMsgBox(title, informative_text, body_text)
            exit()

        else:
            title = '!!! WARNING !!!'
            body_text = 'Warning: This program will remove all data from account: "%s"' % username
            informative_text = 'Do you wish to continue?'
            dialog_return = macman.dialog.okMsgBox(title, informative_text, body_text)

            if dialog_return == 'OK':
                macman.users.deleteUser(username)
                macman.users.createUser(username, password, primary_group, user_picture_path)
