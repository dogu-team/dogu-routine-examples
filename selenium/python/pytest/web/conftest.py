import pytest
import os
from pathlib import Path
from dogu.device.device_client import DeviceClient
from dogu.device.device_host_client import DeviceHostClient, EnsureBrowserAndDriverOptions, EnsureBrowserAndDriverResult
from dogu.device.appium_server import AppiumServerContext
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.safari.service import Service as SafariService

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

pytest_plugins = ["pytest_dogu_sdk"]


@pytest.fixture(scope="session")
def device():
    device_client = DeviceClient(localhost, device_server_port, 30)
    yield device_client


@pytest.fixture(scope="session")
def host():
    host_client = DeviceHostClient(localhost, device_server_port, 10 * 60)
    yield host_client


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
def driver(ensure_browser_result: EnsureBrowserAndDriverResult):
    print("setup driver")

    if ensure_browser_result.browserName == 'chrome':
        options = webdriver.ChromeOptions()
        options.binary_location = ensure_browser_result.browserPath
        service = ChromeService(executable_path=ensure_browser_result.browserDriverPath)
        driver = webdriver.Chrome(options=options, service=service)
    elif ensure_browser_result.browserName == 'firefox':
        options = webdriver.FirefoxOptions()
        options.binary_location = ensure_browser_result.browserPath
        service = FirefoxService(executable_path=ensure_browser_result.browserDriverPath)
        driver = webdriver.Firefox(options=options, service=service)
    elif ensure_browser_result.browserName == 'edge':
        options = webdriver.EdgeOptions()
        options.binary_location = ensure_browser_result.browserPath
        service = EdgeService(executable_path=ensure_browser_result.browserDriverPath)
        driver = webdriver.Edge(options=options, service=service)
    elif ensure_browser_result.browserName == 'safari':
        options = SafariOptions()
        options.binary_location = ensure_browser_result.browserPath
        service = SafariService(executable_path=ensure_browser_result.browserDriverPath)
        driver = webdriver.Safari(options=options, service=service)
    else:
        raise Exception(f"Unsupported browser name: {ensure_browser_result.browserName}")
    
    yield driver

    print("teardown driver")
    driver.quit()
