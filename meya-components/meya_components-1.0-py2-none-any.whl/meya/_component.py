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

import importlib
import json
from meya.db import MeyaDB
from meya.cms import MeyaCMS


class Component(object):
    COMPONENT_REGISTRY = 'registry.json'
    COMPONENT_ROOT = 'components.'

    def __init__(self, bot_id, user_id, request_id, properties):
        self.db = MeyaDB(bot_id, user_id, request_id)
        self.cms = MeyaCMS(bot_id, user_id, request_id)
        self.properties = properties or {}

    def log(self, context, status="info", type="misc"):
        ''' Simple logging interface that causes log publishes
            after completion. TODO consider letting users log
            directly.'''
        data = {"context": context, "status": status, "type": type}
        # Special print statement
        # Parsed as a separate event publish by the Meya platform
        print "event({data})".format(
            data=json.dumps(data)
        )

    def create_message(self, text=None, card=None, entities=None, speech=None):
        if not text and not card:
            raise Exception("Either text or card is required.")
        if card:
            if not text:
                text = card.as_text()

        msg = {'text': text}
        if card:
            msg['card'] = card.payload
        if entities:
            msg['entities'] = entities
        if speech:
            msg['speech'] = speech
        return msg

    def respond(self, action=None, message=None, messages=[], data=None):
        if message:
            messages = [message]

        return {
            'action': action,
            'messages': messages,
            'data': data
        }

    @staticmethod
    def create(component, method, bot_id, user_id, request_id, properties,
               **kwargs):
        with open(Component.COMPONENT_REGISTRY) as data_file:
            data = json.load(data_file)

        """ get the component path from the name
        ie. hipmunk.joke -> hipmunk_joke.ChuckNorrisJoke
        """
        path = data.get(component)
        if path:
            # prepend the module root
            path = "{}{}".format(Component.COMPONENT_ROOT, path)
            module_name, class_name = path.rsplit(".", 1)
            klass = getattr(
                importlib.import_module(module_name), class_name)
            return klass(bot_id, user_id, request_id, properties)

        # default return none
        return None
