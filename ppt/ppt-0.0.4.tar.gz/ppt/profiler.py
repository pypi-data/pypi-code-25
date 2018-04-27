#!/usr/bin/env python3

from __future__ import print_function

import cProfile
import pstats


class Profiler(object):

    def __init__(self):
        self.profiler = cProfile.Profile()

    def start(self):
        self.profiler.enable()

    def stop(self):
        self.profiler.disable()

    def stats(self):
        ps = pstats.Stats(self.profiler).sort_stats('cumulative')
        ps.print_stats()

    def summary(self):
        ps = pstats.Stats(self.profiler).sort_stats('cumulative')
        fn_calls = sum([ps.stats[s][0] for s in ps.stats])
        cumtime = sum([ps.stats[s][2] for s in ps.stats])
        print(fn_calls, 'function calls in', "%0.3f" % cumtime, 'seconds')


class SessionsProfiler(object):

    def __init__(self):
        self.sessions = {}
        self.current_session = None

    def _get_session(self, name):
        if name not in self.sessions:
            self.sessions[name] = Profiler()
        return self.sessions[name]

    def time(self, name=None):
        if self.current_session is not None:
            self.current_session.stop()
        session = self._get_session(name)
        self.current_session = session
        session.start()

    def start(self, name=None):
        session = self._get_session(name)
        session.start()

    def stop(self, name=None):
        if self.current_session is not None:
            self.current_session.stop()
            self.current_session = None
        if name in self.sessions:
            self.sessions[name].stop()

    def stats(self, name=None):
        if name is not None:
            self.sessions[name].stats()
        else:
            for name in self.sessions:
                print('*' * 10, name, '*' * 10)
                self.sessions[name].stats()

    def summary(self, name=None):
        if name is not None:
            print(name, end=': ')
            self.sessions[name].summary()
        else:
            for name in self.sessions:
                print(name, end=': ')
                self.sessions[name].summary()
