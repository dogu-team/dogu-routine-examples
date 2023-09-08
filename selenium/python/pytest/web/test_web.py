from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By


def test_go_to_dogutech_io(driver: WebDriver):
    driver.get("https://dogutech.io/")


def test_find_element_dogu(driver: WebDriver):
    elems = driver.find_elements(By.XPATH, "//*[contains(text(),'Dogu')]")
    assert len(elems) > 0
