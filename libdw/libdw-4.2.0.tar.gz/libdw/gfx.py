from . import util
from soar.io import io
from . import colors
import time

import sys
from imp import reload

from . import gw
from . import dw
reload(dw)
from . import tk
# this file is for integrating graphics with soar, so we know tk has
# been inited.
tk.setInited()

import traceback

class PlotJob():
    def __init__(self, xname, yname, connect_points,
                 xfunc=None, yfunc=None, 
                 xbounds='auto', ybounds='auto'):
        self.xname = xname
        self.xfunc = xfunc
        self.xbounds = xbounds
        self.yname = yname
        self.yfunc = yfunc
        self.ybounds = ybounds
        self.connect_points = connect_points
    def call_func(self, func, inp):
        if func.__code__.co_argcount == 0:
            return func()
        elif func.__code__.co_argcount == 1:
            return func(inp)
        else:
            sys.stderr.write('Static plot function takes too many arguments')
            return 0.0

class RobotGraphics():
    connect_points_def = False
    def __init__(self, draw_slime_trail=False, sonar_monitor=False):
        """
        :param draw_slime_trail: whether or not to draw slime trail when
        robot is stopped.  Setting draw_slime_trail='Cheat' will use
        actual rather than sensed pose in the simulator.  Default is
        False.  :param sonar_monitor: whether or not to enable the
        sonar monitor.  Default is False.
        """
        self.tick = 0
        self.draw_slime_trail = draw_slime_trail
        self.slime_data = []
        self.slime_window = None
        self.plot_jobs = []
        self.plot_windows = []
        self.plot_window_idx = 0
        self.file_tasks = []
        self.plot_data = {}
        self.plot_data['clocktime'] = []
        self.plot_data['step'] = []
        self.trace_tasks = []
        self.window_size = 500
        self.step = 0
        io.register_user_function('shutdown', self.reset)
        io.register_user_function('step', self.step_plotting)
        io.register_user_function('brain_stop', self.plot)
        if sonar_monitor:
            self.enable_sonar_monitor()

    def __del__(self):
        if (self.slime_window): self.slime_window.destroy()
        self.close_plot_windows()

    def clear_plot_data(self):
        # Added by lpk
        self.step = 0
        print('clearing plot data')
        for k in list(self.plot_data.keys()):
            print(('   key', k, len(self.plot_data[k])))
            self.plot_data[k] = []

    def close_plot_windows(self):
        for w in self.plot_windows:
            w.destroy()
        self.plot_windows = []
    
    def tasks(self):
        return self.trace_tasks

    def enable_sonar_monitor(self):
        io.sonar_monitor(True)

    def add_static_plot_function(self, x=('step', None), y=('step', None),
                              connect_points = connect_points_def):
        """
        :param x: function to call for x-axis of static plot 
        :param y: function to call for y-axis of static plot 
        :param connect_points: Boolean, whether or not to draw lines
         between the points.  Default is False.
        """
        (xname, xfunc)= x
        (yname, yfunc)= y
        if yname in self.plot_data: yfunc = None
        if xname in self.plot_data: xfunc = None
        if xfunc or yfunc:
            self.plot_jobs.append(PlotJob(xname, yname, 
                                         connect_points, 
                                         xfunc, yfunc))
        if yfunc: self.plot_data[yname] = []
        if xfunc: self.plot_data[xname] = []

    def add_dynamic_plot_function(self, y=('step', None)):
        """
        :param y: function to call for y-axis of dynamic plot
        """
        (name, func) = y
        io.add_scope_probe_function(name, func)

    def add_static_plot_SM_probe(self, x=('step', None, None, None),
                             y=('step', None, None, None), 
                             connect_points = connect_points_def):
        """
        :param x: probe for x-axis of static plot
        :param y: probe for y-axis of static plot
        :param connect_points: Boolean; whether or not to draw lines
         between the points.  Default is False.
        """
        (yname, ymachine, ymode, yvaluefun) = y
        (xname, xmachine, xmode, xvaluefun) = x
        if ymachine: self.add_probe(y)
        if xmachine: self.add_probe(x)
        self.plot_jobs.append(PlotJob(xname, yname, connect_points))
                                         
    def add_dynamic_plot_SM_probe(self, y=('step', None, None, None),
                              connect_points = connect_points_def):
        """
        :param y: probe for y-axis of dynamic plot
        """
        (yname, ymachine, ymode, yvaluefun) = y
        if ymachine: self.add_probe(y)
        io.add_scope_probe_function(yname, lambda: self.recent_pt(yname))

    def recent_pt(self, name):
        try:
            if len(self.plot_data[name]) > 0:
                return self.plot_data[name][len(self.plot_data[name])-1]
            else:
                return 0.0
        except KeyError:
            sys.stderr.write("Name not defined in gfx object: "+name)


    def reset(self):
        self.slime_data = []
        self.plot_data.clear()
        self.plot_data['clocktime'] = []
        self.plot_data['step'] = []
        io.sonar_monitor(False)
        io.clear_scope()

    def make_trace_fun(self, machine_name, mode, value_fun, stream):
        def trace_fun(x):
            stream.append(value_fun(x))
        return trace_fun

    def set_up_plotting(self, data_probes, plot_tasks):
        for p in data_probes:
            self.add_probe(p)
        for (xname, xbounds, yname, ybounds) in data_tasks:
            self.plot_jobs.append(PlotJob(xname, yname, connect_points,
                                         xbounds=xbounds,
                                         ybounds=ybounds))

    def add_probe(self, probe):
        (stream_name, machine_name, mode, value_fun) = probe
        stream = []
        if stream_name not in self.plot_data:
            self.plot_data[stream_name] = stream
        else:
            sys.stderr.write("Trying to add multiple probes w/ name:"+\
                                 stream_name)
        self.trace_tasks.append((machine_name, mode,
                                self.make_trace_fun(machine_name, mode,
                                                  value_fun, stream)))

    def step_plotting(self):
        if self.draw_slime_trail:
            odo = io.SensorInput(self.draw_slime_trail=='Cheat').odometry
            self.slime_data.append(odo.xyt_tuple())
        self.plot_data['clocktime'].append(time.time())
        self.plot_data['step'].append(self.step)
        self.step += 1
        inp = io.SensorInput()
        for j in self.plot_jobs:
            if j.xfunc: self.plot_data[j.xname].append(j.call_func(j.xfunc, inp))
            if j.yfunc: self.plot_data[j.yname].append(j.call_func(j.yfunc, inp))
                 
    def plot(self):
        if self.draw_slime_trail:
            self.plot_slime()
        self.do_data_plot_jobs()

    def do_data_plot_jobs(self):
        self.time_data = self.plot_data['clocktime'][:]
        self.step_data = self.plot_data['step'][:]
        if len(self.step_data) == 0: return
        self.plot_window_idx = 0
        for j in self.plot_jobs:
            xdata = self.plot_data[j.xname]
            ydata = self.plot_data[j.yname]
            self.plot_data_versus_data(xdata, j.xbounds, ydata, j.ybounds,
                                    j.yname+' versus '+j.xname, j.connect_points)
        for j in self.plot_jobs:
            self.plot_data[j.xname] = []

    def plot_data_versus_data(self, x_data, x_bounds, y_data, y_bounds, name,
                           connect_points, window_size = None):
        if not window_size: window_size = self.window_size
        if len(x_data) == 0:
            print(('X Data stream', name, 'empty:  skipping plot'))
            return
        if len(y_data) == 0:
            print(('Y Data stream', name, 'empty:  skipping plot'))
            return

        (x_lower, x_upper) = self.get_bounds(x_data, x_bounds)
        (y_lower, y_upper) = self.get_bounds(y_data, y_bounds)
        
#        if len(self.plot_windows) > self.plot_window_idx:
#            w = self.plot_windows[self.plot_window_idx]
#            w.reopenWindow(window_size, window_size, 
#                           x_lower, x_upper, y_lower, y_upper, name)
#            self.plot_window_idx += 1
#        else:
        w = gw.GraphingWindow(window_size, window_size, 
                              x_lower, x_upper, y_lower, y_upper, name)
        self.plot_windows.append(w)
        if connect_points:
            w.graph_continuous_set(x_data, y_data)
        else:
            w.graph_point_set(x_data, y_data)

    def plot_slime(self):
        max_t = len(self.slime_data)
        if max_t == 0:
            print('No slime to plot')
            return

        slime_x = [p[0] for p in self.slime_data]
        slime_y = [p[1] for p in self.slime_data]

        (x_lower, x_upper, y_lower, y_upper) = self.get_equally_scaled_bounds(slime_x, 
                                                                       slime_y)
        x_range = x_upper - x_lower
        y_range = y_upper - y_lower

        if util.within(x_range, 0, 0.001):
            return

        if self.slime_window:
            self.slime_window.destroy()
        self.slime_window = dw.DrawingWindow(\
            self.window_size, self.window_size, x_lower, x_upper, y_lower, y_upper,
            'slime')
        # Draw dimensions
        self.slime_window.draw_text(x_lower + 0.1 * x_range, y_lower + 0.05 * y_range,
                                  util.pretty_string(x_lower), color = "black")
        self.slime_window.draw_text(x_upper - 0.1 * x_range, y_lower + 0.05 * y_range,
                                  util.pretty_string(x_upper), color = "black")
        self.slime_window.draw_text(x_lower + 0.05 * x_range, y_lower + 0.1 * y_range,
                                  util.pretty_string(y_lower), color = "black")
        self.slime_window.draw_text(x_lower + 0.05 * x_range, y_upper - 0.1 * y_range,
                                  util.pretty_string(y_upper), color = "black")
        # Draw axes
        x_min = min(slime_x)
        x_max = max(slime_x)
        y_min = min(slime_y)
        y_max = max(slime_y)

        self.slime_window.draw_line_seg(x_min, y_min, x_upper - 0.1 * x_range, y_min, 
                                     'gray')
        self.slime_window.draw_line_seg(x_min, y_min, x_min, y_upper - 0.1 * y_range, 
                                     'gray')

        # Draw slime
        for i in range(max_t):
            self.slime_window.draw_robot(slime_x[i], slime_y[i], 
                                       slime_x[i], slime_y[i],
                                       colors.RGBToPyColor(colors.HSVtoRGB(i*360.0/max_t, 1.0, 1.0)),
                                  2)

    def get_bounds(self, data, bounds):
        if bounds == 'auto':
            upper = max(data)
            lower = min(data)
            if util.within(upper, lower, 0.0001):
                upper = 2*lower + 0.0001
            bound_margin = util.clip((upper - lower) * 0.1, 1, 100)
            return ((lower - bound_margin) , (upper + bound_margin))
        else:
            return bounds

    def get_equally_scaled_bounds(self, x_data, y_data):
        x_max = max(x_data)
        x_min = min(x_data)
        y_max = max(y_data)
        y_min = min(y_data)
        x_range = x_max - x_min
        y_range = y_max - y_min
        if x_range > y_range:
            y_max = y_min + x_range
        else:
            x_max = x_min + y_range
        
        bound_margin = (x_max - x_min) * 0.1
        return (x_min - bound_margin , x_max + bound_margin,
                y_min - bound_margin, y_max + bound_margin)
