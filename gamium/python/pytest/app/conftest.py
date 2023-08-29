import pytest
import os
from appium.webdriver import Remote
from appium.webdriver.webdriver import WebDriver
from appium.options.common import AppiumOptions
from dogu.device import DeviceClient, DeviceHostClient
from gamium import *

localhost = "127.0.0.1"
serial = os.environ.get("DOGU_DEVICE_SERIAL", "LOCAL_DEVICE_SERIAL")
device_server_port = int(os.environ.get("DOGU_DEVICE_SERVER_PORT", 5001))
device_gamium_server_port = 50061

platform = os.environ.get("DOGU_DEVICE_PLATFORM", "android")
is_ci = os.environ.get("CI", "false") == "true"
automationName = platform == "android" and "UiAutomator2" or "XCUITest"


@pytest.fixture(scope="session")
def device():
    device_client = DeviceClient(localhost, device_server_port, 30)
    yield device_client


@pytest.fixture(scope="session")
def host():
    host_client = DeviceHostClient(localhost, device_server_port, 30)
    yield host_client


@pytest.fixture(scope="session")
def driver(device: DeviceClient):
    print("setup driver")
    appium_server = device.run_appium_server(serial)

    options = AppiumOptions().load_capabilities(
        {
            "platformName": platform,
            "deviceName": serial,
            "automationName": "UiAutomator2",
            "newCommandTimeout": 1800,
        }
    )
    if not is_ci:
        options.set_capability("app", "LOCAL_APP_PATH")

    driver = Remote(f"http://{localhost}:{appium_server.port}", options=options)
    yield driver

    print("teardown driver")
    driver.quit()
    appium_server.close()


@pytest.fixture(scope="session")
def gamium(driver: WebDriver, host: DeviceHostClient, device: DeviceClient):
    print("setup gamium")

    host_port = host.get_free_port()
    forward_closer = device.forward(serial, host_port, device_gamium_server_port)
    service = TcpGamiumService(localhost, host_port, 10000)
    gamium = GamiumClient(service)
    gamium.connect()

    yield gamium

    print("teardown gamium")

    forward_closer.close()


@pytest.fixture(scope="session")
def ui(gamium: GamiumClient):
    return gamium.ui()
