from typing import Optional
from urllib.parse import urlparse
import pytest
import os
from pathlib import Path
from appium.webdriver import Remote
from appium.webdriver.webdriver import WebDriver
from appium.options.common import AppiumOptions
from dogu.device.device_client import DeviceClient
from dogu.device.device_host_client import DeviceHostClient
from dogu.device.appium_server import AppiumServerContext
from gamium import *
from dotenv import load_dotenv

print(os.environ)

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


@pytest.fixture(scope="session")
def gamium_host_port(host: DeviceHostClient, device: DeviceClient):
    print("setup gamium_host_port")
    host_port = host.get_free_port()
    forward_closer = device.forward(serial, host_port, device_gamium_server_port)

    yield host_port

    print("teardown gamium_host_port")
    forward_closer.close()


@pytest.fixture(scope="session")
def gamium(driver: WebDriver, gamium_host_port: int):
    print("setup gamium")
    parsed = urlparse(device_server_url)
    host = parsed.hostname
    service = TcpGamiumService(parsed.hostname, gamium_host_port, 30)
    gamium = GamiumClient(service)
    gamium.connect()
    stop_gamium_profile = start_gamium_profile(host, gamium_host_port)

    yield gamium

    print("teardown gamium")
    stop_gamium_profile()
    gamium.sleep(4000)
    gamium.actions().app_quit().perform()


def start_gamium_profile(host: str, gamium_host_port: int):
    from datetime import datetime, timezone
    import requests
    import threading
    import time

    def utc_now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec='microseconds')

    def parse_platform() -> Optional[int]:
        dogu_device_platform = os.environ.get("DOGU_DEVICE_PLATFORM")
        if dogu_device_platform == 'linux':
            return 1
        elif dogu_device_platform == 'macos':
            return 10
        elif dogu_device_platform == 'windows':
            return 20
        elif dogu_device_platform == 'android':
            return 30
        elif dogu_device_platform == 'ios':
            return 40
        else:
            return 0

    def profile_main(stop_event: threading.Event, gamium: GamiumClient):
        service = TcpGamiumService(host, gamium_host_port, 30)
        gamium = GamiumClient(service)
        gamium.connect()

        while not stop_event.is_set():
            try:
                if not gamium.is_connected():
                    print("gamium is not connected. skip profile loop")
                    break

                fps = gamium.profile().fps

                dogu_api_base_url = os.environ.get("DOGU_API_BASE_URL")
                if dogu_api_base_url is None:
                    print("DOGU_API_BASE_URL is not set. skip profile loop")
                    break

                dogu_organization_id = os.environ.get("DOGU_ORGANIZATION_ID")
                if dogu_organization_id is None:
                    print("DOGU_ORGANIZATION_ID is not set. skip profile loop")
                    break

                dogu_device_id = os.environ.get("DOGU_DEVICE_ID")
                if dogu_device_id is None:
                    print("DOGU_DEVICE_ID is not set. skip profile loop")
                    break

                dogu_host_token = os.environ.get("DOGU_HOST_TOKEN")
                if dogu_host_token is None:
                    print("DOGU_HOST_TOKEN is not set. skip profile loop")
                    break

                platform = parse_platform()
                if platform is None:
                    print("DOGU_DEVICE_PLATFORM is not set. skip profile loop")
                    break

                response = requests.post(f"{dogu_api_base_url}/public/organizations/{dogu_organization_id}/devices/{dogu_device_id}/game-runtime-infos", json={
                        "gameRuntimeInfos": [{
                            "platform": platform,
                            "fps": fps,
                            "localTimeStamp": utc_now(),
                        }]
                    },
                    headers={
                        "Authorization": f"Bearer {dogu_host_token}"
                    })
                response.raise_for_status()
            except Exception as e:
                print(f"gamium profile loop error {e}")
            finally:
                time.sleep(5)

    print("start gamium profiler")
    stop_event = threading.Event()
    thread = threading.Thread(target=profile_main, args=(stop_event, gamium))
    thread.start()

    def stop_gamium_profile():
        print("stop gamium profiler")
        stop_event.set()
        thread.join()

    return stop_gamium_profile


@pytest.fixture(scope="session")
def ui(gamium: GamiumClient):
    return gamium.ui()
