class UnableToDetectOnScreenKeyboard(Exception):
    """OSK Icon could not be found on the screen."""


class UnableToDetectKey(Exception):
    """There was no match found on the OSK for the following image: {}"""
