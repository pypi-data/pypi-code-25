# Copyright (c) 2016 Intel, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from flask import request
import flask_restful
from six.moves import http_client

from valence.common import utils
from valence.controller import racks

LOG = logging.getLogger(__name__)


class RackList(flask_restful.Resource):

    def get(self):
        req = request.get_json()
        filters = request.args.to_dict()

        return utils.make_response(
            http_client.OK,
            racks.Rack(req['podm_id']).list_racks(req, filters))


class Rack(flask_restful.Resource):

    def get(self, rack_id):
        req = request.get_json()
        return utils.make_response(
            http_client.OK,
            racks.Rack(req['podm_id']).show_rack(rack_id))
