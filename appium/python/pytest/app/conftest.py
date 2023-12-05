import pytest
import os
from pathlib import Path
from appium.webdriver import Remote
from appium.options.common import AppiumOptions
from dogu.device.device_client import DeviceClient
from dogu.device.device_host_client import DeviceHostClient
from dogu.device.appium_server import AppiumServerContext
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv(str(Path(__file__).parent.parent / '.env.local'))

serial = os.environ.get("DOGU_DEVICE_SERIAL")
token = os.environ.get("DOGU_DEVICE_TOKEN")
app_path = os.environ.get("DOGU_APP_PATH")
device_server_url = os.environ.get("DOGU_DEVICE_SERVER_URL", "http://127.0.0.1:5001")
device_gamium_server_port = 50061

if serial is None:
    raise Exception("DOGU_DEVICE_SERIAL is not set")
if app_path is None:
    raise Exception("DOGU_APP_PATH is not set")

pytest_plugins = ["pytest_dogu_sdk"]

@pytest.fixture(scope="session")
def device():
    device_client = DeviceClient(device_server_url, token=token, timeout=30)
    yield device_client


@pytest.fixture(scope="session")
def host():
    host_client = DeviceHostClient(device_server_url, token=token, timeout=30)
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
            "appium:app": app_path
        }
    )
    parsed = urlparse(device_server_url)
    driver = Remote(f"{parsed.scheme}://{parsed.hostname}:{appium_server.port}", options=options)

    try:
        alert = driver.switch_to.alert
        alert.dismiss()
    except:
        pass
    try:
        alert = driver.switch_to.alert
        alert.accept()
    except:
        pass
    driver.switch_to.context("NATIVE_APP")

    yield driver

    print("teardown driver")
    driver.quit()

