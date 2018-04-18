

import os
import sys
import copy
import time
import pprint
import signal

import threading       as mt
import radical.utils   as ru

from ..          import constants      as rpc
from ..          import states         as rps

from .misc       import hostip

from .queue      import Queue          as rpu_Queue
from .queue      import QUEUE_OUTPUT   as rpu_QUEUE_OUTPUT
from .queue      import QUEUE_INPUT    as rpu_QUEUE_INPUT
from .queue      import QUEUE_BRIDGE   as rpu_QUEUE_BRIDGE

from .pubsub     import Pubsub         as rpu_Pubsub
from .pubsub     import PUBSUB_PUB     as rpu_PUBSUB_PUB
from .pubsub     import PUBSUB_SUB     as rpu_PUBSUB_SUB
from .pubsub     import PUBSUB_BRIDGE  as rpu_PUBSUB_BRIDGE


# ==============================================================================
#
class Controller(object):
    """
    A Controller is an entity which creates, manages and destroys Bridges and
    Components, according to some configuration.
    """

    # --------------------------------------------------------------------------
    #
    def __init__(self, cfg, session):
        """
        The given configuration is inspected for a 'bridges' and a 'components'
        entry.  Under bridges, we expect either a dictionary of the form:

           {
             'bridge_name_a' : {},
             'bridge_name_b' : {},
             'bridge_name_c' : {'in'  : 'address',
                                'out' : 'address'},
             'bridge_name_d' : {'in'  : 'address',
                                'out' : 'address'},
             ...
           }

        where bridges with unspecified addresses will be started by the
        controller, on initialization.  The controller will need at least
        a 'control_pubsub' bridge, either as address or to start, for component
        coordination (see below).

        The components field is expected to have entries of the form:

           {
             'component_a' : 1,
             'component_b' : 3
             ...
           }

        where the respective number of component instances will be created.
        The controller creation will stall until all components are started,
        which is done via a barrier on respective 'alive' messages on the
        'control_pubsub'.

        Components and Bridges will get passed a copy of the config on creation.
        Components will also get passed a copy of the bridge addresses dict.

        The controller has one additional method, `stop()`, which will destroy
        all components and bridges (in this order).  Stop is not called on
        `__del__()`, and thus must be invoked explicitly.
        """

        assert(cfg['owner']), 'controller config always needs an "owner"'

        self._session = session

        # we use a uid to uniquely identify message to and from bridges and
        # components, and for logging/profiling.
        self._uid   = '%s.ctrl' % cfg['owner']
        self._owner = cfg['owner']

        # get debugging, logging, profiling set up
        self._debug = cfg.get('debug')
        self._dh    = ru.DebugHelper(name=self.uid)
        self._log   = self._session._get_logger(self._owner, level=self._debug)

        # we keep a copy of the cfg around, so that we can pass it on when
        # creating components.
        self._cfg = copy.deepcopy(cfg)

        # Dig any releavnt information from the cfg.  That most importantly
        # contains bridge addresses.
        self._ctrl_cfg = {
                'bridges' : copy.deepcopy(cfg.get('bridges'))
        }
        # we also ceep the component information around, in case we need to
        # start any
        self._comp_cfg = copy.deepcopy(cfg.get('components', {}))

        self._log.info('initialize %s', self.uid)

        # keep handles to bridges and components started by us, but also to
        # other things handed to us via 'add_watchables()' (such as sub-agents)
        self._bridges_to_watch    = list()
        self._components_to_watch = list()

        # we will later subscribe to the ctrl pubsub -- keep a handle
        self._ctrl_sub = None

        # control thread activities
        self._term       = mt.Event()  # signal termination
        self._term_cause = list()      # record termination causes

        # We keep a static typemap for component startup. If we ever want to
        # become reeeealy fancy, we can derive that typemap from rp module
        # inspection.
        #
        # NOTE:  I'd rather have this as class data than as instance data, but
        #        python stumbles over circular imports at that point :/

        from .. import worker as rpw
        from .. import pmgr   as rppm
        from .. import umgr   as rpum
        from .. import agent  as rpa

        self._typemap = {rpc.UPDATE_WORKER                  : rpw.Update,

                         rpc.PMGR_LAUNCHING_COMPONENT       : rppm.Launching,

                         rpc.UMGR_STAGING_INPUT_COMPONENT   : rpum.Input,
                         rpc.UMGR_SCHEDULING_COMPONENT      : rpum.Scheduler,
                         rpc.UMGR_STAGING_OUTPUT_COMPONENT  : rpum.Output,

                         rpc.AGENT_STAGING_INPUT_COMPONENT  : rpa.Input,
                         rpc.AGENT_SCHEDULING_COMPONENT     : rpa.Scheduler,
                         rpc.AGENT_EXECUTING_COMPONENT      : rpa.Executing,
                         rpc.AGENT_STAGING_OUTPUT_COMPONENT : rpa.Output
                         }

        # complete the setup with bridge and component creation
        self._start_bridges()
        self._start_components()
        
    # --------------------------------------------------------------------------
    # 
    def is_alive(self):

        # A controller can become unusable due to three distinct conditions: 
        #
        #   - it is terminated, 
        #   - it detects a failing component or bridge 
        #   - it meets an unrecoverable internal error condition
        # 
        # In all three cases, it will attempt to terminate the (remaining)
        # managed componens and bridges, and will then terminate: while the
        # controller instance remains valid, any method call with result in
        # a `RuntimeError` exception.  We do *not* attempt to actively signal
        # the owner about the termination, dut to the known signaling and
        # exception problems.  Instead we rely on this polling mechanism to
        # check controller health now and then.  
        #
        # `is_alive()` is used internally to perform the respective health check
        # on each method call, but is also exposed as API call, and any owner of
        # a `Controller` instance is well advised to frequently call this method
        # to poll for error conditions.
        if self._term.is_set():
            raise RuntimeError('Controller terminated.  Cause: %s' % self._term_cause)


    # --------------------------------------------------------------------------
    #
    @property
    def uid(self):
        return self._uid


    # --------------------------------------------------------------------------
    #
    @property
    def ctrl_cfg(self):

        return copy.deepcopy(self._ctrl_cfg)


    # --------------------------------------------------------------------------
    #
    def stop(self):

      # ru.print_stacktrace()

        # avoid races with watcher thread
        self._term.set()

        self._log.debug('%s stopped', self.uid)

        # we first stop all components (and sub-agents), and only then tear down
        # the communication bridges.  That way, the bridges will be available
        # during shutdown.

        for to_stop_list in [self._components_to_watch, self._bridges_to_watch]:

            for t in to_stop_list:
                self._log.debug('%s stop    %s', self.uid, t.name)
                t.stop()
                self._log.debug('%s stopped %s', self.uid, t.name)

            for t in to_stop_list:
                self._log.debug('%s join    %s', self.uid, t.name)
                if not ru.is_this_thread():
                    t.join()
                self._log.debug('%s joined  %s', self.uid, t.name)

        self._log.debug('%s stopped', self.uid)

        if not ru.is_main_thread():
            # only the main thread should survive
            self._log.debug('%s exit thread', self.uid)
            sys.exit()


    # --------------------------------------------------------------------------
    #
    def _start_bridges(self):
        """
        Helper method to start a given list of bridges.  The type of bridge
        (queue or pubsub) is derived from the name.  The bridge addresses are
        kept in self._ctrl_cfg.

        If new components are later started via self._start_components, then the
        address map is passed on as part of the component config,
        """

        # we *always* need bridges defined in the config, at least the should be
        # the addresses for the control and log bridges (or we start them)
        assert(self._ctrl_cfg['bridges'])
        assert(self._ctrl_cfg['bridges'][rpc.LOG_PUBSUB])
        assert(self._ctrl_cfg['bridges'][rpc.CONTROL_PUBSUB])

        # start all bridges which don't yet have an address
        bridges = list()
        for bname,bcfg in self._ctrl_cfg['bridges'].iteritems():

            addr_in  = bcfg.get('addr_in')
            addr_out = bcfg.get('addr_out')

            if addr_in:
                # bridge is running
                assert(addr_out)

            else:
                # bridge needs starting
                self._log.info('create bridge %s', bname)
            
                if bname.endswith('queue'):
                    bridge = rpu_Queue(self._session, bname, rpu_QUEUE_BRIDGE, bcfg)
                elif bname.endswith('pubsub'):
                    bridge = rpu_Pubsub(self._session, bname, rpu_PUBSUB_BRIDGE, bcfg)
                else:
                    raise ValueError('unknown bridge type for %s' % bname)

                # FIXME: check if bridge is up and running
                # we keep a handle to the bridge for later shutdown
                bridges.append(bridge)

                addr_in  = ru.Url(bridge.bridge_in)
                addr_out = ru.Url(bridge.bridge_out)

                # we just started the bridge -- use the local hostip for 
                # the address!
                # FIXME: this should be done in the bridge already
                addr_in.host  = hostip()
                addr_out.host = hostip()

                self._ctrl_cfg['bridges'][bname]['addr_in']  = str(addr_in)
                self._ctrl_cfg['bridges'][bname]['addr_out'] = str(addr_out)

                self._log.info('created bridge %s (%s)', bname, bridge.name)


        # make sure the bridges are watched:
        self._bridges_to_watch += bridges

        # before we go on to start components, we also register for alive
        # messages, otherwise those messages can arrive before we are able to
        # get them.
        addr = self._ctrl_cfg['bridges'][rpc.CONTROL_PUBSUB]['addr_out']
        self._ctrl_sub = rpu_Pubsub(self._session, rpc.CONTROL_PUBSUB, rpu_PUBSUB_SUB, 
                                    self._ctrl_cfg, addr=addr)
        self._ctrl_sub.subscribe(rpc.CONTROL_PUBSUB)

        self._log.debug('start_bridges done')


    # --------------------------------------------------------------------------
    #
    def _start_components(self):

        # at this point we know that bridges have been started, and we can use
        # the control pubsub for alive messages.

        self._log.debug('start comps: %s', self._comp_cfg)
      # print 'start comps: %s' % self._comp_cfg

        if not self._comp_cfg:
            return

        assert(self._ctrl_sub)
        assert('bridges' in self._ctrl_cfg )

        assert(rpc.LOG_PUBSUB     in self._ctrl_cfg['bridges'])
        assert(self._ctrl_cfg['bridges'][rpc.LOG_PUBSUB].get('addr_in'))
        assert(self._ctrl_cfg['bridges'][rpc.LOG_PUBSUB].get('addr_out'))

        assert(rpc.CONTROL_PUBSUB in self._ctrl_cfg['bridges'])
        assert(self._ctrl_cfg['bridges'][rpc.CONTROL_PUBSUB].get('addr_in'))
        assert(self._ctrl_cfg['bridges'][rpc.CONTROL_PUBSUB].get('addr_out'))

        # start components
        comps = list()
        for cname,cnum in self._comp_cfg.iteritems():

            self._log.debug('start %s component(s) %s', cnum, cname)

            ctype = self._typemap.get(cname)
            if not ctype:
                raise ValueError('unknown component type (%s)' % cname)

            for i in range(cnum):

                # for components, we pass on the original cfg (or rather a copy
                # of that) -- but we'll overwrite any relevant settings from our
                # ctrl_cfg, such as bridge addresses.
                ccfg = copy.deepcopy(self._cfg)
                ccfg['components'] = dict()  # avoid recursion
                ccfg['cname']      = cname
                ccfg['number']     = i
                ccfg['owner']      = self._owner

                ru.dict_merge(ccfg, self._ctrl_cfg, ru.OVERWRITE)

                comp = ctype.create(ccfg, self._session)
                comp.start()

                comps.append(comp)

        # components are started -- we now will trigger the startup syncing (to
        # get alive messages from them), and then get them added to the watcher
        self.add_watchables(comps)


    # --------------------------------------------------------------------------
    #
    def add_watchables(self, things, owner=None):
        """
        This method allows to inject objects into the set of things this
        controller is watching.  Only those object types can be added which
            - issue 'alive' notifications
            - expose pull(), stop() and join() methods.
        Such objects would be components and sub-agents -- but not communication
        bridges (no alive notifications).
        """
        
        # for a given set of things, we check the control channel for 'alive'
        # messages from these things (addressed to the owner (or us), and from
        # thing.name.  Once that is received within timeout (10sec), we add the
        # thing to the list of watch items, which will be automatically be
        # picked up by the watcher thread (which we start also, once).
        #
        # Anything being added here needs: a 'name' property, a 'poll' method
        # (for the watcher to check state), and a 'stop' method (to shut the
        # thing down on termination).
        #
        # Once control is passed to this controller, the callee is not supposed
        # to handle the goven things anymore

        if not owner:
            owner = self._owner

        if not isinstance(things, list):
            things = [things]

        for thing in things:

            assert(thing.name)
            assert(thing.is_alive)
            assert(thing.stop)

        # the things are assumed started at this point -- we just want to
        # make sure that they are up and running, and thus wait for alive
        # messages on the control pubsub, for a certain time.  If we don't hear
        # back from them in time, we consider startup to have failed, and shut
        # down.
        timeout = 60
        start   = time.time()

      # # we register 'alive' messages earlier.  Whenever an 'alive' message
      # # arrives, we check if a subcomponent spawned by us is the origin.  If
      # # that is the case, we record the component as 'alive'.  Whenever we see
      # # all current components as 'alive', we unlock the barrier.
      # alive = {t.name: False for t in things}
      # while True:
      #
      #     topic, msgs = self._ctrl_sub.get_nowait(1000) # timout in ms
      #     self._log.debug('got msg (alive?): %s' % msgs)
      #
      #     if not msgs:
      #         # this will happen on timeout
      #         msgs = []
      #
      #     if not isinstance(msgs, list):
      #         msgs = [msgs]
      #
      #     for msg in msgs:
      #
      #         self._log.debug('msg [%s] : %s', owner, pprint.pformat(msg))
      #
      #         cmd = msg['cmd']
      #         arg = msg['arg']
      #
      #         # only look at alive messages
      #         if cmd not in ['alive']:
      #             # nothing to do
      #             break
      #
      #         # only look at interesting messages
      #         if not arg['owner'] == owner:
      #             self._log.debug('unusable alive msg for %s (%s)', arg['owner'], owner)
      #             break
      #
      #         sender = arg['sender']
      #
      #         # alive messages usually come from child processes
      #         if sender.endswith('.child'):
      #             sender = sender[:-6]
      #
      #         # we only look for messages from known things
      #         if sender not in alive:
      #             self._log.debug('invalid alive msg from %s' % sender)
      #             break
      #
      #         # record thing only once
      #         if alive[sender]:
      #             self._log.error('duplicated alive msg from %s' % sender)
      #             break
      #
      #         # thing is known and alive - record
      #         alive[sender] = True
      #
      #     # we can stop waiting is all things are alive:
      #     living = alive.values().count(True)
      #     if living == len(alive):
      #         self._log.debug('barrier %s complete (%s)', self.uid, len(alive))
      #         break
      #
      #     self._log.debug('barrier %s incomplete %s/%s',
      #                     self.uid, living, len(alive))
      #
      #     # check if we have still time to wait:
      #
      #     now = time.time()
      #     self._log.debug('barrier %s check %s : %s : %s' % (self.uid, start, timeout, now))
      #     if (now - start) > timeout:
      #         self._log.error('barrier %s failed %s/%s',
      #                         self.uid, living, len(alive))
      #         self._log.error('waited  for %s', alive.keys())
      #         self._log.error('missing for %s', [t for t in alive if not alive[t]])
      #         raise RuntimeError('startup barrier failed: %s' % alive)
      #       # self.stop()

            # incomplete, but still have time: just try again (no sleep
            # needed, the get_nowait will idle when waiting for messages)

        # make sure the watcher picks up the right things
        self._components_to_watch += things

        self._log.debug('controller startup completed')


# ------------------------------------------------------------------------------

