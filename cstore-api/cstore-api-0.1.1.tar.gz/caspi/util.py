from selenium.webdriver import Chrome, ChromeOptions
import re

"""
    module for 
    utility classes & functions
"""


class HeadlessChrome(Chrome):
    def __init__(self):
        """
            initialize chrome driver instance
            with headless options ('--headless', '--disable-gpu')
        """

        # chrome options for headless chrome
        options = ChromeOptions()

        # add optional arguments for headless
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        # set window size desktop fullscreen (1920 x 1080)
        options.add_argument('--window-size=1920,1080')

        # initialize chrome driver
        super(HeadlessChrome, self).__init__(chrome_options=options)

    def __enter__(self):
        """
            return self instance
            for with ~ as statement

            Return:
                HeadlessChrome: self instance for with ~ as statement
        """

        # return instance to with statement
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
            close all resource in web driver
            for after with ~ as statement
        """

        # close browser
        self.close()


def escape_unit_suffix(src):
    """
        escape unit suffix like '~원' by regex

        Args:
            src (str) : text would you want to convert

        Return:
            str: text which escaped unit suffix
    """

    return re.sub(r'([,원])', '', src)


def pick_address_string(src):
    """
        get address string from input string with regex

        Args:
            src (str) : text would you like get address

        Return:
            str: address what you picked
    """

    match = re.match(r'.*?[로(지하)?|길동리]\s?(\d+-*)+\s?((번*길)\s?(\d+-*)+)?', src)
    return match.group() if match else None
