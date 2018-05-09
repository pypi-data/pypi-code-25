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
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')

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
