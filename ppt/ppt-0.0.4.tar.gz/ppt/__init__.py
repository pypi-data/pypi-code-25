#!/usr/bin/env python3

from .profiler import Profiler, SessionsProfiler
from .plotter import Plotter
from .cuda import block_cuda, noblock_cuda

_PPT_PROFILER = SessionsProfiler()
_PPT_PLOTTER = Plotter()

time = _PPT_PROFILER.time
start = _PPT_PROFILER.start
stop = _PPT_PROFILER.stop
stats = _PPT_PROFILER.stats
summary = _PPT_PROFILER.summary

plot = _PPT_PLOTTER.plot
close = _PPT_PLOTTER.close
