# -*- coding: utf-8 -*-
import logging
import weakref


__author__ = 'Horacio Hoyos'
__copyright__ = 'Copyright , Kinori Technologies'


class Scoop:

    def __init__(self, type=None):
        """
        A Scoop encapsulates the information the Snithcer wants to send. It should define a type so that agents can
        easily identify scoops from different snitchers/applications.

        A Scoop can be chained with other scoops to queue notifications and dispatch them as a burst. The chain can be
        created by invoking the add method and the head Scoop can be iterated to retrieve the chain.

        :param type: The type of the Scoop
        """
        self.type = type
        self.next = None
        self.logger = logging.getLogger(__name__)

    def __iter__(self):
        yield self
        up_next = self.next
        while up_next is not None:
            yield up_next
            up_next = up_next.next

    def __repr__(self):
        return 'Scoop({!r})'.format(self.type)

    def s_add(self, scoop):
        if self.next is None:
            self.next = scoop
        else:
            self.next.s_add(scoop)


class Snitcher:

    def __init__(self, *args, **kwargs):
        """
        A source of information. Agents can register with the snitcher to receive scoops from the snitcher.
        """
        self._agents = weakref.WeakKeyDictionary()
        self.s_chatty = True
        self.logger = logging.getLogger(__name__)

    def __repr__(self):
        return 'Snitcher(){{chatty: {!r}, agents: {!r}}}'.format(self.s_chatty, self._agents)

    def s_register_agent(self, agent, callback=None):
        """
        Register an agent to receive information from the snitcher. By default the snitcher will use the
        'notify' method of the agent. Optionally, the agent can provide a different method.

        The agents 'notify' method should as a minimum have a 'scoop' keyword argument.

        :param agent: The agent listening to the snitcher
        :param callback: The preferred method name to inform the agent. If *None*, will use the default.
        :raises AttributeError: If the agent does not have an 'notify' method an no preferred method is supplied
        """
        if callback is None:
            try:
                callback = getattr(agent, 'notify')
            except AttributeError as e:
                self.logger.error('Register Agent: %s - No notify attribute found', agent)
                raise e
        self.logger.info('Register Agent: %s - callback:  %r', agent, callback)
        self._agents[agent] = callback

    def s_unregister_agent(self, agent):
        """
        Un register an agent to receive information from the snitcher. The agent will no longer receive sccops from the
        Snitcher.

        :param agent: The agent to unregister
        """
        try:
            self.logger.info('Unregister Agent: %r', agent)
            self._agents.pop(agent)
        except KeyError:
            self.logger.warning('Unregister Agent: %r - Agent not registered', agent)

    def s_unregister_all(self):
        """
        Un register all agents receiving information from the snitcher. The agents will no longer receive information
        from the snitcher.
        """
        self.logger.info('Unregistered all agents')
        self._agents.clear()

    def s_agents(self):
        """
        Get the set of agents listening to this snitcher. The returned value is a view object of the internal agents
        dictionary. It provides a dynamic view on the dictionary’s entries, which means that when the dictionary
        changes, the view reflects these changes.
        :return: A set (view) of the agents listening to this snitcher.
        """
        return self._agents.keys()

    def s_inform(self, *args, **kwargs):
        """
        Notifies a change in the state of this snitcher as described by the args and kwargs parameters, iif the snithcer
        is talking. The information will be relayed to the agents via Agent.notify(), unless the agent has registered a
        different method.

        :param args:  Positional arguments passed to the callback method registered by the agent
        :param kwargs: Keyword arguments passed to the callback method registered by the agent
        :raises TypeError: If the callback is not callable
        """
        if self.s_chatty:
            for agent, callback in self._agents.items():
                try:
                    self.logger.info('Talking to agent: %r', agent)
                    callback(*args, **kwargs)
                except TypeError as e:
                    self.logger.error('Talking to agent: %r - Callback failed', agent, exc_info=True)
                    raise e
        else:
            self.logger.info('Snitcher not talking')

    @classmethod
    def __sing(cls):
        print('Informer, You know say Daddy Snow me, I\'m gonna blame. A licky boom-boom down')
