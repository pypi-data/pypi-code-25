import os
import pkg_resources
import platform
import logging

import pyautogui

from osk_mapper.exceptions import *

"""
On-Screen Keyboard (OSK) Mapper
Author: Jonathon Carlyon (JonathonCarlyon@gmail.com)
Maps the positions of the keys on the virtual keyboard
Currently OSK's height must be minimized for all keys to be detected.
"""


class KeyLocations:
    def __init__(self):
        logging.basicConfig(
            format='%(asctime)s %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
            level=logging.INFO
        )
        os_version = ' '.join(
            platform.platform().split('-')[:2]
        )
        osk_resources = pkg_resources.resource_filename(
            __name__,
            f'resources/osk/{os_version}'
        )
        osk_icon = self.detect_osk_icon(
            os.path.join(osk_resources, 'OSK_ICON.png')
        )
        self.osk_region = self.set_osk_region(osk_icon)
        logging.warning(f'OSK Region set {self.osk_region}'
                        f'\nDO NOT MOVE THE OSK')
        logging.info('Starting key mapping')
        self.Q = self.map_using_image(
            os.path.join(osk_resources, 'Q.png')
        )
        self.W = self.map_using_image(os.path.join(
            osk_resources, 'W.png')
        )
        self.pixel_space = (self.W[0] - self.Q[0])
        self.E = self.map_using_pixel_difference(self.W, self.Q)
        self.R = self.map_using_pixel_difference(self.E, self.Q)
        self.T = self.map_using_pixel_difference(self.R, self.Q)
        self.Y = self.map_using_pixel_difference(self.T, self.Q)
        self.U = self.map_using_pixel_difference(self.Y, self.Q)
        self.I = self.map_using_pixel_difference(self.U, self.Q)
        self.O = self.map_using_pixel_difference(self.I, self.Q)
        self.P = self.map_using_pixel_difference(self.O, self.Q)
        #
        self.A = self.map_using_image(os.path.join(
            osk_resources, 'A.png')
        )
        self.S = self.map_using_pixel_difference(self.A, self.A)
        self.D = self.map_using_pixel_difference(self.S, self.A)
        self.F = self.map_using_pixel_difference(self.D, self.A)
        self.G = self.map_using_pixel_difference(self.F, self.A)
        self.H = self.map_using_pixel_difference(self.G, self.A)
        self.J = self.map_using_pixel_difference(self.H, self.A)
        self.K = self.map_using_pixel_difference(self.J, self.A)
        self.L = self.map_using_pixel_difference(self.K, self.A)
        #
        self.Z = self.map_using_image(
            os.path.join(osk_resources, 'Z.png')
        )
        self.X = self.map_using_pixel_difference(self.Z, self.Z)
        self.C = self.map_using_pixel_difference(self.X, self.Z)
        self.V = self.map_using_pixel_difference(self.C, self.Z)
        self.B = self.map_using_pixel_difference(self.V, self.Z)
        self.N = self.map_using_pixel_difference(self.B, self.Z)
        self.M = self.map_using_pixel_difference(self.N, self.Z)
        #
        self.ESC = self.map_using_image(
            os.path.join(osk_resources, 'ESC.png')
        )
        # Starting from Tilda for Windows 7 compatibility.
        self.TILDA = self.map_using_image(
            os.path.join(osk_resources, 'TILDA.png'),
        )
        self.ONE = self.map_using_pixel_difference(self.TILDA, self.ESC)
        self.TWO = self.map_using_pixel_difference(self.ONE, self.ESC)
        self.THREE = self.map_using_pixel_difference(self.TWO, self.ESC)
        self.FOUR = self.map_using_pixel_difference(self.THREE, self.ESC)
        self.FIVE = self.map_using_pixel_difference(self.FOUR, self.ESC)
        self.SIX = self.map_using_pixel_difference(self.FIVE, self.ESC)
        self.SEVEN = self.map_using_pixel_difference(self.SIX, self.ESC)
        self.EIGHT = self.map_using_pixel_difference(self.SEVEN, self.ESC)
        self.NINE = self.map_using_pixel_difference(self.EIGHT, self.ESC)
        self.ZERO = self.map_using_pixel_difference(self.NINE, self.ESC)
        #
        self.ALT = self.map_using_image(
            os.path.join(osk_resources, 'ALT.png')
        )
        self.CTRL = self.map_using_image(os.path.join(
            osk_resources, 'CTRL.png')
        )
        self.SHIFT = self.map_using_image(
            os.path.join(osk_resources, 'SHIFT.png')
        )
        self.CAPS = self.map_using_image(
            os.path.join(osk_resources, 'CAPS.png')
        )
        self.TAB = self.map_using_image(
            os.path.join(osk_resources, 'TAB.png')
        )
        self.ALT = self.map_using_image(
            os.path.join(osk_resources, 'ALT.png')
        )
        #
        self.LEFT = self.map_using_image(
            os.path.join(osk_resources, 'LEFT.png')
        )
        self.RIGHT = self.map_using_image(
            os.path.join(osk_resources, 'RIGHT.png')
        )
        self.UP = self.map_using_image(
            os.path.join(osk_resources, 'UP.png')
        )
        self.DOWN = self.map_using_image(
            os.path.join(osk_resources, 'DOWN.png')
        )
        logging.info('Done matching')

    @staticmethod
    def set_osk_region(icon):
        region_top_padding = 25
        region_top = icon[0] - region_top_padding
        region_left = icon[1]
        region_width = 1000
        region_height = 800
        return (region_top,
                region_left,
                region_width,
                region_height)

    @staticmethod
    def detect_osk_icon(image):
        """
        Searches for the OSK icon and sets it if it exists
        otherwise an exception will be thrown
        :param image: String image containing OSK's icon
        :return: Tuple containing screen coordinates to key
        """
        logging.info("Looking for On-Screen Keyboard")
        osk_icon = pyautogui.locateCenterOnScreen(
            image,
            grayscale=True
        )
        if not osk_icon:
            raise UnableToDetectOnScreenKeyboard(
                UnableToDetectOnScreenKeyboard.__doc__
            )
        logging.info(f"On-Screen keyboard detected. {osk_icon}")
        return osk_icon

    def map_using_image(self, image):
        """
        Use pyautogui to set map the location of the key to the OSK
        :param image: String path to image of a key
        :return: Tuple containing screen coordinates to key
        """
        key_location = pyautogui.locateCenterOnScreen(
            image,
            region=self.osk_region,
            grayscale=True
        )
        if key_location is None:
            raise UnableToDetectKey(
                UnableToDetectKey.__doc__.format(image)
            )
        return key_location

    def map_using_pixel_difference(self, key1, key2):
        """
        Sets key coordinates by using pixel difference of other keys
        instead of doing additional costly image recognition
        :param key1: Tuple containing coordinates to a key on the OSK
        :param key2: Tuple containing coordinates to a key on the OSK
        :return: Tuple containing screen coordinates to key
        """
        return key1[0] + self.pixel_space, key2[1]
