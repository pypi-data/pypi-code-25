# Copyright 2018 Locl Interactive Inc. (d/b/a Meya.ai). All Rights Reserved.
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

from meya import Component


def do(event, context):
    method = event.get('method')
    component_name = event.get('component')

    # instantiate the component
    component = Component.create(**event)

    if component is None:
        raise Exception("Couldn't find component: {}".format(
            component_name))
    elif method == 'start':
        # run the component
        return component.start()
    elif method:
        # TODO find and execute transition
        raise Exception("Only method=start is allowed.")
    else:
        raise Exception("No method specified.")
