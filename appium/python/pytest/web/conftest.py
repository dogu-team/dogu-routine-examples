import pytest
import os
from pathlib import Path
from appium.webdriver import Remote
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from dogu.device.device_client import DeviceClient
from dogu.device.device_host_client import DeviceHostClient, EnsureBrowserAndDriverOptions, EnsureBrowserAndDriverResult
from dogu.device.appium_server import AppiumServerContext
from dotenv import load_dotenv

load_dotenv(str(Path(__file__).parent.parent / '.env.local'))

localhost = "127.0.0.1"
device_serial = os.environ.get("DOGU_DEVICE_SERIAL")
device_platform = os.environ.get("DOGU_DEVICE_PLATFORM")
device_server_port = int(os.environ.get("DOGU_DEVICE_SERVER_PORT", 5001))
browser_name = os.environ.get("DOGU_BROWSER_NAME")
browser_version = os.environ.get("DOGU_BROWSER_VERSION", "latest")

if device_serial is None:
    raise Exception("DOGU_DEVICE_SERIAL is not set")
if browser_name is None:
    raise Exception("DOGU_BROWSER_NAME is not set")

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
    appium_server = device.run_appium_server(device_serial)

    yield appium_server

    print("teardown appium_server")
    appium_server.close()


@pytest.fixture(scope="session")
def ensure_browser_result(host: DeviceHostClient):
    ensure_browser_options = EnsureBrowserAndDriverOptions(
        browserName=browser_name,
        browserPlatform=device_platform,
        browserVersion=browser_version,
        deviceSerial=device_serial)
    print("ensure browser with options", ensure_browser_options)
    ensure_browser_result = host.ensure_browser_and_driver(ensure_browser_options)
    print("ensure browser done with result", ensure_browser_result)
    yield ensure_browser_result


@pytest.fixture(scope="session")
def driver(appium_server: AppiumServerContext, device: DeviceClient, ensure_browser_result: EnsureBrowserAndDriverResult):
    print("setup driver")
    capabilites = device.get_appium_capabilities(device_serial)

    if ensure_browser_result.browserName == "chrome":
        options = AppiumOptions().load_capabilities(
            {
                **capabilites,
                "appium:appPackage": "com.android.chrome",
                "appium:appActivity": "com.google.android.apps.chrome.Main",
                "appium:chromedriverExecutable": ensure_browser_result.browserDriverPath,
                "appium:showChromedriverLog": True,
                "appium:chromeOptions": {
                    "args": ["--disable-fre", "--no-default-browser-check", "--no-first-run"]
                },
                "goog:chromeOptions": {
                    "args": ["--disable-fre", "--no-default-browser-check", "--no-first-run"]
                }
            }
        )
    else:
        raise Exception(f"unsupported browser {ensure_browser_result.browserName}")

    driver = Remote(f"http://{localhost}:{appium_server.port}", options=options)

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

    if ensure_browser_result.browserName == "chrome":
        context = driver.context
        driver.switch_to.context("NATIVE_APP")
        terms_accepts = driver.find_elements(AppiumBy.ID, "com.android.chrome:id/terms_accept")
        if len(terms_accepts) > 0:
            terms_accepts[0].click()
        negative_buttons = driver.find_elements(AppiumBy.ID, "com.android.chrome:id/negative_button")
        if len(negative_buttons) > 0:
            negative_buttons[0].click()
        driver.switch_to.context(context)

    yield driver

    print("teardown driver")
    driver.quit()

