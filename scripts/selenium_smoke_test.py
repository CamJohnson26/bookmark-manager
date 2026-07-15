import os
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

from bookmark_library.page_crawler.firefox_binary import get_firefox_binary


driver_path = os.getenv("GECKODRIVER_PATH", "/usr/local/bin/geckodriver")
options = Options()
options.binary_location = get_firefox_binary()
options.add_argument("-headless")
service = Service(executable_path=driver_path, log_output=sys.stderr)
browser = None

try:
    browser = webdriver.Firefox(service=service, options=options)
    print(browser.capabilities["browserVersion"])
finally:
    if browser is not None:
        browser.quit()
    else:
        service.stop()
