from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
import time


def test_go_to_dogutech_io(driver: WebDriver):
    driver.get("https://dogutech.io/")

def test_find_element_dogu(driver: WebDriver):
    elems = driver.find_elements(AppiumBy.XPATH, "//*[contains(text(),'Dogu')]")
    assert len(elems) > 0

def test_scolls(driver: WebDriver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(3)

    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(3)
