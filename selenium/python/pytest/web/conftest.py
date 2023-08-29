import os

import pytest
from selenium import webdriver

pytest_plugins = ["pytest_dogu_report"]

browser_name = os.environ.get("DOGU_BROWSER_NAME", "chrome")
browser_version = os.environ.get("DOGU_BROWSER_VERSION", "")
browser_major_version = os.environ.get("DOGU_BROWSER_MAJOR_VERSION", "")
browser_path = os.environ.get("DOGU_BROWSER_PATH", "")
browser_driver_path = os.environ.get("DOGU_BROWSER_DRIVER_PATH", "")
browser_package_name = os.environ.get("DOGU_BROWSER_PACKAGE_NAME", "")

@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    if browser_path:
        options.binary_location = browser_path
    driver = webdriver.Chrome(executable_path=browser_driver_path, options=options)
    yield driver
    driver.quit()
