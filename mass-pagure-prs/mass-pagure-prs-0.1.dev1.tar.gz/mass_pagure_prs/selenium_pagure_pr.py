"""
This module contains selenium functions to create and merge
a PR on Pagure.

The function to create a PR `create_pull_request` should be
replaced with an API call when Pagure 4.0.0 is out.

There is a Pagure API call to merge the PR, but no clear way
to check if there are any conflicts in the PR. So the
fnction `merge_pull_request` is a better alternative
(for me) to use.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_pull_request(url, title, description,
                        fas_user, fas_password):
    """Create a pull request from a fork to upstream.

    Pagure API does not allow this yet, so selenium it is.
    """
    driver = webdriver.Firefox()
    driver.get(url)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'bodycontent'))
    )
    # Sometimes when the user is "kinited", the login page does not open,
    # and you go directly to the PR page.
    if driver.title == 'Login':
        if not fas_user or not fas_password:
            raise Exception('Please provide both FAS username and password')

        login_elem = driver.find_element_by_name('login_name')
        login_elem.clear()
        login_elem.send_keys(fas_user)

        password_elem = driver.find_element_by_name('login_password')
        password_elem.clear()
        password_elem.send_keys(fas_password)

        login_button = driver.find_element_by_id('loginbutton')
        login_button.click()

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.NAME, 'title'))
    )

    pr_title = driver.find_element_by_name('title')
    pr_title_value = pr_title.get_attribute('value')

    if pr_title_value != title:
        # This means the PR either contains more commits or is wrong.
        # Needs to be checked manually.
        raise Exception(
            'Opening the PR did not go well. '
            f'The PR title: {pr_title_value}')

    pr_init_comment = driver.find_element_by_id('initial_comment')
    pr_init_comment.clear()
    pr_init_comment.send_keys(description)

    create_button = driver.find_element_by_xpath(
        "//input[@type='submit'][@value='Create']")
    create_button.click()

    # TODO: check the page if it was a success.
    driver.close()


def merge_pull_request(url, fas_user, fas_password):
    driver = webdriver.Firefox()
    driver.get(url)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'bodycontent'))
    )
    # Sometimes when the user is "kinited", the login page does not open,
    # and you go directly to the PR page.
    login = driver.find_elements_by_xpath("//a[contains(text(), 'Log In')]")
    if login:
        login_url = login[0].get_attribute('href')
        driver.get(login_url)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'bodycontent'))
    )

    if driver.title == 'Login':
        if not fas_user or not fas_password:
            raise Exception('Please provide both FAS username and password')

        login_elem = driver.find_element_by_name('login_name')
        login_elem.clear()
        login_elem.send_keys(fas_user)

        password_elem = driver.find_element_by_name('login_password')
        password_elem.clear()
        password_elem.send_keys(fas_password)

        login_button = driver.find_element_by_id('loginbutton')
        login_button.click()

    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, 'merge_btn'))
    )

    pr_message = driver.find_element_by_id('merge-alert-message')
    if pr_message.text != 'The pull-request can be merged and fast-forwarded':
        raise Exception(
            'Failed to merge: conflicts maybe')

    merge_button = driver.find_element_by_id("merge_btn")
    merge_button.click()

    WebDriverWait(driver, 30).until(EC.alert_is_present(), 'Waiting for alert timed out')

    alert = driver.switch_to_alert()
    alert.accept()
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'bodycontent'))
    )

    # TODO: check the page if it was a success.
    driver.close()
