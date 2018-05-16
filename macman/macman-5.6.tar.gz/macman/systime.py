#!/usr/bin/python
# Filename: systime.py

from subprocess import PIPE, Popen
import macman

def ntpStatus():
    """ Return NTP status On if running, status Off if not """

    output = macman.misc.systemsetup('-getusingnetworktime')
    if 'ON' in output.strip().split()[-1]:
        return 'ON'
    return 'OFF'


def getTimezone():
    """ Return timezone used """

    output = macman.misc.systemsetup('-gettimezone')

    return output.strip().split()[-1]


def setTimezone(timezone):
    """ Set timezone """

    macman.logs.writeLog('Setting time zone to "%s"' % timezone)
    macman.misc.systemsetup('-settimezone', "%s" % timezone)


def getNtpServer():
    """ Return ntp server used """

    output = macman.misc.systemsetup('-getnetworktimeserver')
    return output.strip().split()[-1]


def setNtpServer(ntp_server):
    """ Set NTP server """

    macman.logs.writeLog('Setting NTP server to "%s"' % ntp_server)
    macman.misc.systemsetup('-setnetworktimeserver', '"%s"' % ntp_server)


def ntpStart():
    """ Start NTP client """

    macman.logs.writeLog('Starting NTP client')
    macman.misc.systemsetup('-setusingnetworktime', 'on')


def ntpStop():
    """ Stop NTP client """

    macman.logs.writeLog('Stopping NTP client')
    macman.misc.systemsetup('-setusingnetworktime', 'off')
