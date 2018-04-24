# coding=utf-8


import time
import json
from airtest_hunter import AirtestHunter, open_platform
from poco.drivers.netease.internal import NeteasePoco

from pocounit.case import PocoTestCase
from airtest.core.api import connect_device, device as current_device
from poco.drivers.android.uiautomation import AndroidUiautomationPoco


class Case(PocoTestCase):
    @classmethod
    def setUpClass(cls):
        super(Case, cls).setUpClass()
        if not current_device():
            connect_device('Android:///')

    def runTest(self):
        from poco.drivers.cocosjs import CocosJsPoco
        poco = CocosJsPoco()
        for n in poco():
            print(n.get_name())


# if __name__ == '__main__':
#     import pocounit
#     pocounit.main()


# from hunter_cli import Hunter, open_platform
# from poco.drivers.netease.internal import NeteasePoco
#
# tokenid = open_platform.get_api_token('test')
# hunter = Hunter(tokenid, 'xy2', 'xy2_at_408d5c116536')
# poco = NeteasePoco('xy2', hunter)
#
# print poco('npc_conversation').offspring('list_options').offspring('Widget')[0].offspring('txt_content').nodes[0].node.data

from airtest.core.api import connect_device
from poco.utils.track import track_sampling, MotionTrack, MotionTrackBatch
from poco.utils.airtest.input import AirtestInput



# mt = MotionTrack(speed=0.1)
# mt1 = MotionTrack()
# mt2 = MotionTrack()
# mt.start([0.5, 0.5]).move([0.2, 0.5]).move([0.5, 0.5])
# mt1.start([0.5, 0.6]).move([0.2, 0.6]).hold(1).move([0.5, 0.6])



connect_device('Android:///')
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

poco(text='设置').start_gesture().hold(1).to(poco(text='图库')).hold(1).up()

#
#
# # poco.apply_motion_tracks([mt1, mt])
# ui = poco('android:id/content')
# print(ui.get_bounds())
#
# t0 = time.time()
# ui.focus([0.5, 0.8]).pinch(percent=0.2)
# t1 = time.time()
#
# time.sleep(1)
# t2 = time.time()
# ui.pinch('out')
# t3 = time.time()
# print(t1 - t0, t3 - t2)
#
time.sleep(4)

