#!/usr/bin/env python

################################################################################
# Copyright 2018 Young-Mook Kang <ymkang@thylove.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import os
import sqlite3

class SQLite3(object) :

    def __init__(self):
        self.__itsCursor = None
        pass

    def __load(self):
        theBasePath = os.path.dirname(os.path.realpath(__file__))
        theDBFilePath = theBasePath + '/saavpedia.db'
        if os.path.exists(theDBFilePath) and os.path.isfile(theDBFilePath):
            self.__itsConnection = sqlite3.connect(theDBFilePath)
            self.__itsCursor = self.__itsConnection.cursor()
        else:
            self.__itsCursor = None
            print 'There is no a SAAVpedia DB file in the SAAVpedia library folder.'
        pass

    def load(self):
        try:
            self.__load()
            return False
        except:
            return True

    def open(self, theDBFilePath):
        try:
            self.__itsConnection = sqlite3.connect(theDBFilePath)
            self.__itsCursor = self.__itsConnection.cursor()
            return False
        except:
            return True

    def close(self):
        if not self.__itsCursor == None:
            self.__itsCursor.close()
        self.__itsCursor = None
        pass

    def execute(self, theCommand):
        if not self.__itsCursor == None:
            return self.__itsCursor.execute(theCommand)
        return None


if __name__ == '__main__':
    pass

