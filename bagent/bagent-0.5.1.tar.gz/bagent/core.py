# -*- coding: utf-8 -*-
# This file is part of bagent
#
# Copyright (C) 2018-present Jeremies Pérez Morata
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.


import asyncio
import logging
from contextlib import ContextDecorator
from bagent.messages import MessageContext

logger = logging.getLogger(__name__)

class AgentMixin(object):
    def __init__(self, loop, debug):
        self.next_pid = 1
        self.parent_ctx = None
        self.parent = None
        self.parent_pid = '0'
        self.agents = {}
        self.loop = loop
        self.debug = debug
        self.pid = '0'

        self.messages = asyncio.Queue(loop=loop)
        self.fn = None
        self.args = None
        self.kwargs = None

    def create_agent(self, agent_fn, *args, **kwargs):
        agent = AgentContext(self.loop, debug=self.debug)

        pid = '{0}-{1}'.format(self.pid, self.next_pid)
        agent.pid = pid
        agent.parent = self
        agent.parent_pid = self.pid
        agent.fn = agent_fn
        agent.args = args
        agent.kwargs = kwargs
        agent.parent_ctx = self

        self.agents[pid] = agent
        self.next_pid += 1

        logger.debug("Agent created: {0}".format(pid))

        return pid

    async def recv(self):
        logger.debug("{0} waiting for message...".format(self.pid))
        return await self.messages.get()

    def get_message(self):
        return MessageContext(self)

    async def send(self, pid, msg, sender=None):
        if not sender:
            sender = self.pid

        logger.debug("From {0}, sending {1} to {2}".format(sender, str(msg), pid))

        if self.pid == pid:
            await self.messages.put((sender, msg))
        else:
            agent = self._find_child_path(pid)
            if agent:
                await agent.send(pid, msg, sender=sender)
            else:
                if self.pid == 0:
                    logger.warning("PID {0} not FOUND".format(pid))
                else:
                    await self.parent.send(pid, msg, sender=sender)

    def _find_child_path(self, pid):
        for apid, agent in self.agents.items():
            if apid.startswith(pid):
                return agent
        return None


class AgentContext(AgentMixin):
    def __init__(self, loop, debug=False):
        AgentMixin.__init__(self, loop, debug)
        self.running_agents = 0

    def _decr_children_count(self, fn):
        async def func(*args, **kwargs):
            await fn(*args, **kwargs)
            self.running_agents -= 1
            logger.debug("Agent terminated: {0}".format(self.pid))
        return func

    async def start(self, agent_fn, *args, **kwargs):
        agent_fn = self._decr_children_count(agent_fn)

        pid = self.create_agent(agent_fn, *args, **kwargs)

        agent = self.agents[pid]
        asyncio.ensure_future(agent.execute())

        self.running_agents += 1

        return pid

    def _wait_children(self, fn):
        async def func(*args, **kwargs):
            await fn(*args, **kwargs)
            while self.running_agents > 0:
                await asyncio.sleep(1)
        return func

    async def execute(self):
        logger.debug("Starting agent: {0}".format(self.pid))
        self.fn = self._wait_children(self.fn)
        await self.fn(self, *self.args, **self.kwargs)


class RootContext(ContextDecorator, AgentMixin):
    def __init__(self, loop, debug=False):
        ContextDecorator.__init__(self)
        AgentMixin.__init__(self, loop, debug)

        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.ERROR)

    def start(self, agent_fn, *args, **kwargs):
        pid = self.create_agent(agent_fn, *args, **kwargs)
        return pid

    def send(self):
        raise Exception("Not implemented")

    def recv(self):
        raise Exception("Not implemented")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        tasks = [agent.execute() for agent in self.agents.values()]
        self.loop.run_until_complete(asyncio.wait(tasks))
        self.loop.close()
        return False
