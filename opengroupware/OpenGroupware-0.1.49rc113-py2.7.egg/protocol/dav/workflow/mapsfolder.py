# Copyright (c) 2010, 2014, 2015, 2017
#   Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import json
from coils.core import BundleManager
from coils.logic.workflow import ActionMapper, WorkflowMap
from coils.net import DAVFolder, StaticObject
from mapobject import MapObject
from coils.logic.workflow.maps import MapFactory

"""
NOTE: Maps are not implemented, not used anyhwere.  This is a feature
which originally was hoped would come over from BIE - that has not happened
and does not seem likely.  OIE transforms and formats almost match, and in
some ways superceed, the funcionality of BIE maps.
"""


class MapsFolder(DAVFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def supports_PUT(self):
        return True

    def _load_contents(self):
        for name in WorkflowMap.List():
            m = MapFactory.Marshall(
                context=self.context, name=name,
            )
            self.insert_child('{0}.yaml'.format(name, ), m, alias=None)
        return True

    def _render_key_macros(
        self, name, auto_load_enabled=True, is_webdav=False,
    ):
        result = []
        for name in ActionMapper.list_macros():
            command = BundleManager.get_command(
                ActionMapper.get_macro(name)
            )
            result.append(command.descriptor)
        return StaticObject(
            self, '.macros',
            context=self.context,
            request=self.request,
            payload=json.dumps(result),
            mimetype='application/json'
        )

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):

        tmp = self.render_dot_key(
            name, auto_load_enabled=auto_load_enabled, is_webdav=is_webdav,
        )
        if tmp:
            return tmp

        maps = WorkflowMap.List()

        if name[:-5] in maps:
            tmp = MapObject(
                self, name,
                entity=MapFactory.Marshall(self.context, name, ),
                context=self.context,
                request=self.request,
            )
            print tmp
            return tmp

        self.no_such_path()
