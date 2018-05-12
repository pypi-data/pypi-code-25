# -*- coding: utf-8 -*-
#
#   Copyright © 2015 - 2018 Stephan Zevenhuizen
#   debugger_MATE_for_Dummies, (10-05-2018).
#

# You must open an experiment in MATRIX with an I(t) channel first.

import mate4dummies.objects as mo

def read_prop(obj, prop):
    out = getattr(obj, prop)()
    print(prop + ':', out)

channel_props = ['Enable']
clock_props = ['Enable', 'Period', 'Samples']
experiment_props = ['Bricklet_Written', 'Name', 'Result_File_Name',
                    'Result_File_Path', 'State']
gap_voltage_control_props = ['Preamp_Range', 'Voltage']
regulator_props = ['Enable_Z_Offset_Slew_Rate', 'Feedback_Loop_Enabled',
                   'Loop_Gain_1_I', 'Loop_Gain_2_I', 'Preamp_Range_1',
                   'Preamp_Range_2', 'Setpoint_1', 'Setpoint_2', 'Z_Offset',
                   'Z_Offset_Slew_Rate', 'Z_Out']
view_props = ['Cycle_Count', 'Data_Size', 'Deliver_Data', 'Run_Count']
xy_scanner_props = ['Angle', 'Area', 'Enable_Drift_Compensation', 'Lines',
                    'Offset', 'Plane_X_Slope', 'Plane_Y_Slope', 'Points',
                    'Raster_Time', 'Return_To_Stored_Position',
                    'Store_Current_Position', 'Target_Position',
                    'Trigger_Execute_At_Target_Position', 'XY_Position_Report',
                    'X_Drift', 'X_Retrace', 'X_Retrace_Trigger',
                    'X_Trace_Trigger', 'Y_Drift', 'Y_Retrace',
                    'Y_Retrace_Trigger', 'Y_Trace_Trigger']
obj_names = ['channel', 'clock', 'experiment', 'gap_voltage_control',
             'regulator', 'view', 'xy_scanner']
mo.mate.testmode = False
mo.mate.connect()
if mo.mate.online:
    mo.channel_name = 'I_t'
    mo.get_clock_name(mo.channel_name)
    for obj_name in obj_names:
        obj = getattr(mo, obj_name)
        print()
        print('Object ' + obj_name + ':')
        print('--------------------------------------------------------------')
        for prop in eval(obj_name + '_props'):
            read_prop(obj, prop)
    mo.mate.disconnect()
