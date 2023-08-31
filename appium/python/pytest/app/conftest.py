import pytest
import os
from appium.webdriver import Remote
from appium.options.common import AppiumOptions
from dogu.device.device_client import DeviceClient
from dogu.device.device_host_client import DeviceHostClient
from dogu.device.appium_server import AppiumServerContext

localhost = "127.0.0.1"
is_ci = os.environ.get("CI", "false") == "true"
serial = os.environ.get("DOGU_DEVICE_SERIAL", "YOUR_LOCAL_DEVICE_SERIAL")
device_server_port = int(os.environ.get("DOGU_DEVICE_SERVER_PORT", 5001))
device_gamium_server_port = 50061

pytest_plugins = ["pytest_dogu_report"]

@pytest.fixture(scope="session")
def device():
    device_client = DeviceClient(localhost, device_server_port, 30)
    yield device_client


@pytest.fixture(scope="session")
def host():
    host_client = DeviceHostClient(localhost, device_server_port, 30)
    yield host_client


@pytest.fixture(scope="session")
def appium_server(device: DeviceClient):
    print("setup appium_server")
    appium_server = device.run_appium_server(serial)

    yield appium_server

    print("teardown appium_server")
    appium_server.close()


@pytest.fixture(scope="session")
def driver(appium_server: AppiumServerContext, device: DeviceClient):
    print("setup driver")
    capabilites = device.get_appium_capabilities(serial)
    options = AppiumOptions().load_capabilities(
        {
            **capabilites,
            "appium:newCommandTimeout": 1800,
        }
    )
    if not is_ci:
        options.set_capability("app", "YOUR_LOCAL_APP_PATH")
    driver = Remote(f"http://{localhost}:{appium_server.port}", options=options)

    yield driver

    print("teardown driver")
    driver.quit()

