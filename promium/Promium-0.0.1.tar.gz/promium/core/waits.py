# -*- coding: utf-8 -*-

import logging
import requests
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    WebDriverException,
    TimeoutException
)


log = logging.getLogger(__name__)

JQUERY_LOAD_TIME = 20
AJAX_LOAD_TIME = 20
ANIMATION_LOAD_TIME = 20


def enable_jquery(driver):
    """Enables jquery"""
    driver.execute_script(
        """
        jqueryUrl =
        'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js';
        if (typeof jQuery == 'undefined') {
            var script = document.createElement('script');
            var head = document.getElementsByTagName('head')[0];
            var done = false;
            script.onload = script.onreadystatechange = (function() {
                if (!done && (!this.readyState || this.readyState == 'loaded'
                        || this.readyState == 'complete')) {
                    done = true;
                    script.onload = script.onreadystatechange = null;
                    head.removeChild(script);

                }
            });
            script.src = jqueryUrl;
            head.appendChild(script);
        };
        """
    )


def wait_for_ajax(driver):
    """Waits for execution ajax"""
    try:
        enable_jquery(driver)
        WebDriverWait(driver, JQUERY_LOAD_TIME).until(
            lambda driver: driver.execute_script(
                'return typeof jQuery != "undefined"'
            ),
            'jQuery undefined (waiting time: %s sec)' % JQUERY_LOAD_TIME
        )
        WebDriverWait(driver, AJAX_LOAD_TIME).until(
            lambda driver: driver.execute_script('return jQuery.active == 0;'),
            'Ajax timeout (waiting time: %s sec)' % AJAX_LOAD_TIME
        )

    except TimeoutException:
        raise


def wait_for_animation(driver):
    """Waits for execution animation"""
    enable_jquery(driver)
    WebDriverWait(driver, ANIMATION_LOAD_TIME).until(
        lambda driver: driver.execute_script(
            'return jQuery(":animated").length == 0;'
        ),
        'Animation timeout (waiting time: %s sec)' % ANIMATION_LOAD_TIME
    )


def wait_for_page_loaded(driver):
    """Waits for page loaded"""
    try:
        wait_for_ajax(driver)
        wait_for_animation(driver)
    # TODO need fix, don't understand
    except UnexpectedAlertPresentException as e:
        alert_is_present = EC.alert_is_present()
        if alert_is_present(driver):
            driver.switch_to_alert()
            alert = driver.switch_to_alert()
            e.alert_text = alert.text
            if e.alert_text == u"Stop downloading new page?":
                pass
            else:
                alert.dismiss()
                raise e


def wait(driver, seconds=10):
    """Waits in seconds"""
    return WebDriverWait(
        driver, seconds, ignored_exceptions=[WebDriverException]
    )


def wait_until(driver, expression, seconds=10, msg=None):
    """Waits until expression execution"""
    try:
        return wait(driver, seconds).until(expression, msg)
    except TimeoutException:
        # TODO validate console errors
        raise


def wait_until_not(driver, expression, seconds=10, msg=None):
    """Waits until not expression execution"""
    try:
        return wait(driver, seconds).until_not(expression, msg)
    except TimeoutException:
        # TODO validate console errors
        raise


def wait_for_alert(driver):
    """Wait for alert"""
    return wait_until(
        driver=driver,
        expression=EC.alert_is_present(),
        seconds=10,
        msg=u"Alert is not present."
    )


def wait_until_with_reload(driver, expression, trying=5, seconds=2, msg=''):
    """Waits until expression execution with reload page"""
    for t in iter(range(trying)):
        try:
            driver.refresh()
            if wait_until(driver, expression, seconds=seconds):
                return
        except TimeoutException:
            log.info(u"Waiting attempt number %s" % (t + 1))
    raise AssertionError(
        u'The values in expression not return true after {} tries\n'
        u'{}'.format(trying, msg)
    )


def wait_until_not_with_reload(
    driver,
    expression,
    trying=5,
    seconds=2,
    msg=u''
):
    """Waits until not expression execution with reload page"""
    for t in iter(range(trying)):
        try:
            driver.refresh()
            if not wait_until_not(driver, expression, seconds=seconds):
                return
        except TimeoutException:
            log.info(u"Waiting attempt number %s" % (t + 1))
    raise AssertionError(
        u'The values in expression not return false after {} tries\n'
        u'{}'.format(trying, msg)
    )


def wait_for_status_code(url, status_code=200):
    """Waits for status code"""
    for _ in range(20):
        status = requests.get(url, verify=False).status_code
        if status == status_code:
            break
        time.sleep(1)


def wait_until_new_window_is_opened(driver, original_window):
    """Waits until new window is opened"""
    # TODO need testing
    wait_until(
        driver,
        EC.new_window_is_opened(driver.window_handles),
        msg=u"New window didn't open"
    )
    window_handles = driver.window_handles
    window_handles.remove(original_window)
    return window_handles[0]
