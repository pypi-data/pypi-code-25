# -*- coding: utf-8 -*-
#
#   Copyright © 2015 - 2018 Stephan Zevenhuizen
#   start_MATE_for_Dummies, (10-05-2018).
#

# Run this script from within the MS Windows Command Prompt (console),
# by pressing the keyboard Esc key you can stop the 'wait for event' loop.

import mate4dummies.objects as mo

def test(text):
    global retraces
    retraces += 1
    print(text)
    print('Retraces:', retraces)
    mo.xy_scanner.resume()

mo.mate.testmode = False
mo.mate.connect()
if mo.mate.online:
    reset_value = mo.xy_scanner.X_Retrace_Trigger()
    _ = mo.xy_scanner.X_Retrace_Trigger(True)
    mo.xy_scanner.X_Retrace_Done(test, 'Testing...')
    retraces = 0
    mo.experiment.start()
    mo.esc = False
    while retraces < 300 and (mo.mate.rc == mo.mate.rcs['RMT_SUCCESS'] or
                              mo.mate.testmode) and not mo.esc:
        mo.wait_for_event()
    mo.experiment.stop()
    mo.xy_scanner.X_Retrace_Done()
    _ = mo.xy_scanner.X_Retrace_Trigger(reset_value)
    mo.mate.disconnect()
