#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# stream_monitor                                                               #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program monitors a specified set of data streams (files) for changes.   #
# If a file is not changed in a specified time, an alert is sent.              #
#                                                                              #
# copyright (C) 2018 Will Breaden Madden, wbm@protonmail.ch                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

usage:
    program [options]

options:
    -h, --help                display help message
    --version                 display version and exit

    --configuration=FILEPATH  filepath of configuration    [default: stream_monitor_configuration.json]
    --alarms=BOOL             enable alarms                [default: true]
    --interval=INT            checking interval in seconds [default: 300]
    --verbose=BOOL            enable verbosity             [default: true]
"""

import datetime
import docopt
import logging
import os
import sys
import time

import lock
import propyte
import technicolor
import tonescale

name    = "stream_monitor"
version = "2018-04-19T2211Z"

def main(options = docopt.docopt(__doc__)):
    filepath_configuration =     options["--configuration"]
    alarms                 =     options["--alarms"].lower() == "true"
    interval               = int(options["--interval"])
    verbose                =     options["--verbose"].lower() == "true"
    global log
    log = logging.getLogger(name)
    log.addHandler(technicolor.ColorisingStreamHandler())
    if verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    if options["--version"]:
        log.info(version)
        exit()
    if not exist_filepaths(filepaths = [filepath_configuration]): sys.exit()
    while True:
        configuration = lock.load_JSON(filepath_configuration)
        log.info("\n" + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S Z"))
        for stream, characteristics in (configuration["streams"].items()):
            if exist_filepaths(filepaths = [stream]):
                characteristics["last_modification_time"] = os.stat(os.path.expanduser(stream)).st_mtime
                current_time = (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(0)).total_seconds()
                if verbose:
                    log.info("{stream} last modification time: {last_modification_time}".format(
                        stream                 = stream.ljust(40),
                        last_modification_time = datetime.datetime.fromtimestamp(int(characteristics["last_modification_time"])).strftime("%Y-%m-%d %H:%M:%S")
                    ))
                if current_time - characteristics["last_modification_time"] > characteristics["update_time"]:
                    alert(text = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ") + " {stream} has not updated within its expected update time of {update_time} s".format(
                        stream      = stream,
                        update_time = characteristics["update_time"]
                    ))
                    if alarms: play_alarm()
        time.sleep(interval)

def alert(text = "alert"):
    log.info(text)
    try:
        propyte.start_messaging_Pushbullet()
        propyte.send_message_Pushbullet(text = text)
    except:
        pass

def play_alarm():
    try:
        sound = tonescale.access_sound(name = "DynamicLoad_BSPNostromo_Ripley.023")
        sound.repeat(number = 1)
        sound.play(background = True)
    except:
        pass

def exist_filepaths(filepaths = None):
    if not filepaths:
        log.error("no filepaths specified")
        return False
    status = {}
    for filepath in filepaths:
        status[filepath] = os.path.isfile(filepath)
    filepaths_nonexistent = [k for k, v in list(status.items()) if not v]
    for filepath in filepaths_nonexistent:
        log.warning("{filepath} not found".format(filepath = filepath))
    if filepaths_nonexistent:
        return False
    else:
        return True

if __name__ == "__main__":
    main()

