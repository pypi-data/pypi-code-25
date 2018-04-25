import os
import unittest
from selenium.webdriver.remote.webdriver import WebDriver


class BrowserTestCase(unittest.TestCase):
    """ Custom TestCase wrapper.
        Needed to support the browser and url paramters.
    """

    browser = None
    url = None

    def __init__(
            self, methodName, browser: WebDriver, url: str,
            extra_args={}):
        super().__init__(methodName)
        self.browser = browser
        self.url = url
        self.extra_args = extra_args

    @classmethod
    def my_tests(cls):
        """ Helper method used to fetch the available tests for a TestSuite
        """
        return unittest.defaultTestLoader.getTestCaseNames(cls)

    def screenshot(self, suffix: str=''):
        """ Capture a screeenshot.
            Uses `suffix` if given or the current browser url.
        """
        suffix = suffix or self._get_screenshot_suffix()
        name = '{}/screenshot_{}.png'.format(os.getcwd(), suffix)
        self.browser.save_screenshot(name)

    def _get_screenshot_suffix(self) -> str:
        return '_'.join(self.browser.current_url.split('#')[0].split('/')[2:])


class BrowserTestResult(unittest.runner.TextTestResult):
    """ Custom TestResult. Saves screenshots of failed tests.
    """
    def addFailure(self, test: BrowserTestCase, err):
        test.screenshot()
        super().addFailure(test, err)

    def addError(self, test: BrowserTestCase, err):
        test.screenshot()
        super().addError(test, err)

    def getDescription(self, test: BrowserTestCase):
        """ Include url in the test description.
        """
        text = super().getDescription(test)
        return '[{}] {}'.format(test.url, text)
