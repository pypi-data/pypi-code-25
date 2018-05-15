import asyncio
import concurrent
import uuid
from typing import List
from uuid import uuid1

import networkx as nx

from serpentarium.engine.CompositionNode import CompositionNode
from serpentarium.engine.ModContext import ModContext
from serpentarium.monitoring.Monitor import Monitor
from serpentarium.util.helpers import get_class


class ExecutionContext(ModContext):
    """
    An execution context of the system.
    Encapsulates Mod composition graph, event loop and thread pool for blocking tasks.
    """

    def __init__(self, mods: List[dict], monitor: Monitor, monitor_polling: int) -> None:
        """
        Builds an execution graph, creates eent loop and thread pool.
        :param mods: mod configuration
        :param monitor: execution monitor
        """
        self.monitor_polling = monitor_polling
        self._monitor = monitor
        self._graph = nx.MultiDiGraph()
        self._mods_instances = {}
        self._loop = asyncio.get_event_loop()
        self._exec = concurrent.futures.ThreadPoolExecutor(max_workers=3)

        mod_map = {}

        for mod in mods:
            mod_class = get_class(mod['class'])
            instance_id = uuid1()
            mod_instance = mod_class(name=mod['name'], id=instance_id, settings=mod['settings'], context=self)

            execution_node = ExecutionContext.map_mod_instance(mod, instance_id)
            self._mods_instances[instance_id] = (mod_instance, execution_node)
            mod_map[mod['name']] = execution_node

        self._graph.add_nodes_from(mod_map.values())

        for (name, mod) in mod_map.items():
            for connector in mod.connectors:
                connect_with = mod_map[connector['name']]
                self._graph.add_edge(connect_with, mod)

    def start(self) -> None:
        """
        Starts the mods and monitoring coroutine.
        """
        for (instance, node) in self._mods_instances.values():
            instance.on_start()
        if self.monitor_polling > 0:
            asyncio.ensure_future(self.async_monitor(self.monitor_polling), loop=self._loop)
        self._loop.run_forever()

    def shutdown(self) -> None:
        """
        Shuts down the event loop and thread pool.
        """
        self._loop.stop()
        self._exec.shutdown()

    def emit(self, id: uuid, message: dict) -> None:
        """
        Creates a coroutine to pass the message downstraem.
        :param id: unique mod id
        :param message: message to pass
        """
        asyncio.ensure_future(self.async_emit(id, message), loop=self._loop)

    def execute_blocking(self, callback, *args) -> None:
        """
        Executes a piece of blocking code in a thread pool
        :param callback: function to execute
        :param args: parameters to pass
        """
        self._loop.run_in_executor(self._exec, callback, *args)

    def draw(self, label: str, path_to_save: str) -> None:
        """
        Draws a visualisation of the execution graph
        :param label: description to add to the image
        :param path_to_save: path to save file
        :return:
        """
        pydot = nx.drawing.nx_pydot.to_pydot(self._graph)
        pydot.write_png(path_to_save)

    async def async_emit(self, id: uuid, message: dict):
        """
        Finds a neighbours of current mod and passes a copy of the message to them.
        :param id: unique mod id
        :param message: message to pass
        """
        (instance, execution_node) = self._mods_instances[id]
        neighbours = list(self._graph.neighbors(execution_node))
        for neighbour in neighbours:
            (neighbour_instance, neighbour_composition) = self._mods_instances[neighbour.id]
            await neighbour_instance.on_message(message.copy())

    async def async_monitor(self, polling_interval: int):
        """
        A coroutine which collects metrics periodically
        """
        while True:
            await asyncio.sleep(polling_interval)
            for (instance, node) in self._mods_instances.values():
                instance.on_stats(self._monitor)

    @staticmethod
    def map_mod_instance(mod: dict, id: uuid) -> CompositionNode:
        """
        Creates a composition node object from mod
        :param mod: mod
        :param id: mod id
        :return:
        """
        if 'connectors' in mod:
            return CompositionNode(name=mod['name'], id=id, connectors=mod['connectors'])
        else:
            return CompositionNode(name=mod['name'], id=id)
