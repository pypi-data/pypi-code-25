# -*- coding: utf-8 -*-
#
#   Copyright © 2015 - 2018 Stephan Zevenhuizen
#   start_MATE_for_Dummies_2, (10-05-2018).
#

# You need the Python packages numpy and matplotlib.
# Run this script from within the MS Windows Command Prompt (console),
# by pressing the keyboard Esc key you can stop the 'wait for event' loop.

import mate4dummies.objects as mo
import numpy as np
import matplotlib.pyplot as plt

def view_data():
    global view_count, x_data, y_data
    view_count += 1
    _ = mo.clock.Enable(False)
    data_size = mo.view.Data_Size()
    period = mo.clock.Period()
    x_data = np.linspace(0, (data_size - 1) * period, data_size)
    y_data = mo.sample_data(data_size)
    run_count = mo.view.Run_Count()
    cycle_count = mo.view.Cycle_Count()
    print('Run count:', run_count)
    print('Cycle count:', cycle_count)
    _ = mo.clock.Enable(True)

x_data = np.array([0, 1], float)
y_data = np.array([0, 1], float)
samples = 50
raster_time = 5.0
mo.mate.testmode = False
mo.mate.connect()
if mo.mate.online:
    mo.channel_name = 'Df_t'
    mo.get_clock_name(mo.channel_name)
    if mo.channel.Enable():
        _ = mo.clock.Enable(False)
        _ = mo.clock.Period(raster_time / samples)
        _ = mo.clock.Samples(samples)
        mo.view.Data(view_data)
        _ = mo.view.Deliver_Data(True)
        mo.allocate_sample_memory(samples)
        _ = mo.clock.Enable(True)
        view_count = 0
        mo.esc = False
        while view_count < 1 and (mo.mate.rc == mo.mate.rcs['RMT_SUCCESS'] or
                                  mo.mate.testmode) and not mo.esc:
            mo.wait_for_event()
        _ = mo.clock.Enable(False)
        _ = mo.view.Deliver_Data(False)
        mo.view.Data()
    else:
        mo.log.AppendText('Channel not enabled, measurement cancelled.\n')
    mo.mate.disconnect()
print('Mean and standard deviation y_data:', np.mean(y_data), np.std(y_data))
plt.plot(x_data, y_data)
plt.show()
