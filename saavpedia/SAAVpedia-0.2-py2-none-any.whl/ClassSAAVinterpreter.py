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

class SAAVinterpreter(object) :
    def __init__(self):
        self.__itsKeys = set()
        pass

    def addKey(self, theKey):
        self.__itsKeys.add(theKey)

    def getKeySet(self):
        return self.__itsKeys

    def has(self, theKey):
        return theKey in self.getKeySet()

    pass



if __name__ == '__main__':
    pass

