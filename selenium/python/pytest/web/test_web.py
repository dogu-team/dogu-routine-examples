from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By


def test_go_to_dogutech_io(driver: WebDriver):
    driver.get("https://dogutech.io/")


def test_search_for_dogu(driver: WebDriver):
    global dogu_elements
    driver.find_elements(By.XPATH, '//*[contains(text(), "dogu")]')


def test_check_for_dogu():
    assert len(dogu_elements) > 0
