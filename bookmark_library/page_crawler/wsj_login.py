import os
from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


_login_checked = False


def is_wsj_url(url):
    hostname = (urlparse(url).hostname or "").lower()
    return hostname == "wsj.com" or hostname.endswith(".wsj.com")


def login_if_needed(browser, wait_for_page, timeout):
    global _login_checked

    if _login_checked or not is_wsj_url(browser.current_url):
        return

    username = os.getenv("WSJ_USERNAME")
    password = os.getenv("WSJ_PASSWORD")
    if not username or not password:
        _login_checked = True
        return

    browser.get("https://www.wsj.com/login")
    wait_for_page(browser)
    if "login" not in browser.current_url.lower():
        # The persistent profile is already authenticated.
        _login_checked = True
        return

    try:
        username_field = WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username'], input[type='email']"))
        )
    except TimeoutException:
        # The persistent profile may already contain a valid WSJ session.
        _login_checked = True
        return

    password_field = WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password'], input[type='password']"))
    )
    username_field.clear()
    username_field.send_keys(username)
    password_field.clear()
    password_field.send_keys(password)
    WebDriverWait(browser, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"))
    ).click()
    wait_for_page(browser)
    _login_checked = True


def reset_login_state():
    global _login_checked
    _login_checked = False
