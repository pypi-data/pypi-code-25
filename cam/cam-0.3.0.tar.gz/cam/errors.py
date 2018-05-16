# Copyright 2018 Mingyi Zhang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
import traceback


class FatalError( Exception ):

    trace = None

    def __init__(self, msg, trace = None):
        if isinstance(msg,FatalError):
            trace = msg.trace
            msg = msg.msg
        elif isinstance(msg,Exception):
            msg = msg.msg
        self.msg = msg
        if trace is None:
            #etype, value, tb = sys.exc_info()
            #return ''.join(format_exception(etype, value, tb, limit))
            self.trace = traceback.format_exc()
        else:
            self.trace = trace

class NotImplemented(FatalError):
    pass