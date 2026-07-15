import atexit
import os
from threading import Lock

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from bookmark_library.page_crawler.wsj_login import (
    is_wsj_url,
    login_if_needed,
    reset_login_state,
)

PAGE_LOAD_TIMEOUT = int(os.getenv("SELENIUM_PAGE_LOAD_TIMEOUT", "60"))
PROFILE_DIR = os.getenv(
    "SELENIUM_PROFILE_DIR",
    os.path.join(os.getcwd(), ".selenium-profile"),
)

_browser = None
_browser_lock = Lock()


def _wait_for_page(browser):
    """Wait for the browser's load event and for a usable document body."""
    wait = WebDriverWait(browser, PAGE_LOAD_TIMEOUT)
    wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))


def _get_browser():
    global _browser
    if _browser is not None:
        return _browser

    os.makedirs(PROFILE_DIR, exist_ok=True)
    options = Options()
    options.binary_location = "/usr/bin/firefox"
    options.page_load_strategy = "normal"
    options.profile = PROFILE_DIR
    _browser = webdriver.Firefox(options=options)
    _browser.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return _browser


def _close_browser():
    if _browser is not None:
        _browser.quit()


atexit.register(_close_browser)


def get_html_selenium(url):
    global _browser

    with _browser_lock:
        try:
            browser = _get_browser()
            browser.get(url)
            _wait_for_page(browser)
            if is_wsj_url(url):
                login_if_needed(browser, _wait_for_page, PAGE_LOAD_TIMEOUT)
                if browser.current_url != url:
                    browser.get(url)
                    _wait_for_page(browser)
            return browser.page_source.replace("\x00", "")
        except Exception:
            if _browser is not None:
                _browser.quit()
            _browser = None
            reset_login_state()
            raise
