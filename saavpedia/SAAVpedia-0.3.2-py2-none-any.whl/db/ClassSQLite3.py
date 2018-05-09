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
import urllib2, math

class SQLite3(object) :

    def __init__(self):
        self.__itsCursor = None
        self.__itsVersionList = [
            {'date':'2018.05.04', 'size':10753868800, 'folder':'2018.05.04.sqlite.split', 'unit_size':10485760 }
        ]
        pass

    def __load(self, theCount = 0):
        theBasePath = os.path.dirname(os.path.realpath(__file__))
        theDBFilePath = theBasePath + '/saavpedia.db'
        if os.path.exists(theDBFilePath):
            if os.path.isfile(theDBFilePath) and os.path.getsize(theDBFilePath) == self.__itsVersionList[-1]['size']:
                self.__itsConnection = sqlite3.connect(theDBFilePath)
                self.__itsCursor = self.__itsConnection.cursor()
                print 'Local SAAVpedia DB is loaded.'
                return False
            pass
        if theCount == 0:
            self.__saveDB(theDBFilePath)
            return self.__load(theCount+1)
        self.__itsCursor = None
        return True

    def __saveDB(self, theDBFilePath):
        theLastVersionInfo = self.__itsVersionList[-1]
        theNumOfSplitFiles = int(math.ceil(theLastVersionInfo['size'] / (theLastVersionInfo['unit_size'] * 1.0)))
        theWriter = open(theDBFilePath, 'w')
        for idx in range(theNumOfSplitFiles):
            theURL = 'https://github.com/saavpedia/python/blob/master/SAAVpedia/db/{0}/SAAVpediaData.sqlite.db.{1}.kbsi?raw=true'.format(theLastVersionInfo['folder'], idx)
            print 'Downloading SAAVpediaData.sqlite.{0}.db - {1:.2f}%'.format(idx, (idx+1.0)/theNumOfSplitFiles*100.0)
            theData = urllib2.urlopen(theURL).read()
            theWriter.write(theData)
        print 'Download is completed.'
        theWriter.close()

    def load(self):
        try:
            self.__load()
            return False
        except Exception as e:
            print e.message()
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
    theSQLite = SQLite3()
    theSQLite.load()
    pass

