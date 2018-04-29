#
# Copyright 2017 The E2C Authors. All Rights Reserved.
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
# ==============================================================================

from typing import Dict

from graphviz import Digraph

from e2c.contracts.actor import Actor
from e2c.contracts.const import *
from e2c.contracts.errors import *


# ======================================================= #
# VISUALIZER
# ======================================================= #

class Visualizer(object):
    """
    The class to visualize actors and relations.
    """

    def __init__(self, actors: Dict[str, Actor]):
        """
        The class to visualize actors and relations.

        :type actors: :class:`Dict[str, Actor]`
        :param actors: The actors to analyse.
        """
        self._actors = actors
        self._extends = {}

    def run(self, folder: str, **config):
        """
        Starts the visualizing.

        :type folder: str
        :param folder: The folder to store the output.

        :rtype: None
        """
        any_actor, actors = False, []
        graph_attr = {'label': config.get(LABEL, ''), 'labeljust': 'r', 'fontcolor': 'gray30',
                      'rankdir': config.get(DIR, 'LR'), }  #'splines': 'ortho',}# 'actorsep':'1'}
        edge_attr = {'color': 'gray', 'fontcolor': 'gray30', 'penwidth': '2.0',
                     'arrowtail': 'dot', 'arrowhead': 'normal', 'dir': 'both'}
        node_attr = {'color': 'gray', 'fontcolor': 'gray30', 'shape': 'box',
                     'style': 'rounded', 'penwidth': '2.0'}

        format = config.get('format', 'png')
        dot = Digraph(graph_attr=graph_attr, node_attr=node_attr,
                      edge_attr=edge_attr, format=format)

        for left_actor_name, left_actor in self._actors.items():
            for left_param, right_actors in left_actor.actors.items():

                any_actor = True
                if left_actor_name == SELF:
                    dot.node(left_actor_name, None, {'color': 'orange'})

                for relation_actor in right_actors:
                    if relation_actor.name == OUT:
                        dot.node(relation_actor.name, None, {'color': 'orange'})

                    edge_attr = {}
                    if left_param == ERR:
                        edge_attr = {'color': 'red', 'fontcolor': 'red'}
                    elif left_param == TRC:
                        edge_attr = {'color': 'darkorchid1', 'fontcolor': 'darkorchid1'}

                    if left_actor_name not in actors:
                        actors.append(left_actor_name)
                    if relation_actor.name not in actors:
                        actors.append(relation_actor.name)

                    dot.edge(left_actor_name, relation_actor.name,
                             label=left_param, _attributes=edge_attr)

                    if relation_actor.doc:
                        comment_node_name = relation_actor.name + '_comment'
                        node_attr = {'shape': 'note', 'color': 'gray', 'fontcolor': 'gray30'}
                        edge_attr = {'color': 'gray', 'style': 'dashed', 'arrowtail': 'none'}
                        dot.node(comment_node_name, relation_actor.doc, _attributes=node_attr)
                        dot.edge(comment_node_name, relation_actor.name, _attributes=edge_attr)

        if not any_actor:
            raise E2CVisualizeError('Graph is empty!')

        dot.render(config.get(NAME, DEFAULT), folder, cleanup=True)
        # dot.save(name, directory=os.path.join(folder or '', 'dot'))
