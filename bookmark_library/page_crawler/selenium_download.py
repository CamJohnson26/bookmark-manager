from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time
import os

# start web browser
# options.binary_location = '/usr/bin/firefox'


def get_html_selenium(url):
    binary = FirefoxBinary('/usr/bin/firefox')
    browser = webdriver.Firefox(firefox_binary=binary)
    # get source code
    browser.get(url)
    time.sleep(5)
    browser.execute_script("window.scrollTo(0,5000)")
    time.sleep(10)
    html = browser.page_source
    browser.close()

    return html
