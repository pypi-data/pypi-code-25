import pyautogui

from osk_mapper.mapper import KeyLocations


class TestClass(KeyLocations):
    def __init__(self):
        print('here we go')
        super().__init__()
        print('woohoo')


a = TestClass()
pyautogui.moveTo(a.A)
