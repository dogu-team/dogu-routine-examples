import { beforeAll, afterAll } from "@jest/globals";
import {
  DeviceClient,
  AppiumServerContext,
  DeviceCloser,
  DeviceHostClient,
} from "dogu-device-client";
import { remote, RemoteOptions } from "webdriverio";
import { GamiumClient, NodeGamiumService, UI } from "gamium";

import { config } from "dotenv";

config({ path: ".env.local" });

const Localhost = "127.0.0.1";
const Serial = process.env["DOGU_DEVICE_SERIAL"];
const AppPath = process.env["DOGU_APP_PATH"];
const DeviceServerPort = parseInt(
  process.env["DOGU_DEVICE_SERVER_PORT"] ?? "5001"
);
const DeviceGamiumServerPort = 50061;

if (!Serial) {
  throw new Error("DOGU_DEVICE_SERIAL is not specified");
}

if (!AppPath) {
  throw new Error("DOGU_APP_PATH is not specified");
}

export let driver: WebdriverIO.Browser;
export let gamium: GamiumClient;
export let ui: UI;
let server: AppiumServerContext | undefined;
let forwardClosable: DeviceCloser | undefined;

beforeAll(async () => {
  const device = new DeviceClient({ port: DeviceServerPort });
  server = await device.runAppiumServer(Serial);
  const caps = await device.getAppiumCapabilities(Serial);
  caps["appium:app"] = AppPath;

  const options: RemoteOptions = {
    logLevel: "debug",
    protocol: "http",
    hostname: Localhost,
    port: server.port,
    path: "/",
    connectionRetryCount: 0,
    capabilities: caps,
  };

  driver = await remote(options);
  await driver.dismissAlert().catch(() => {});
  await driver.acceptAlert().catch(() => {});

  const host = new DeviceHostClient({ port: DeviceServerPort });
  const gamiumHostPort = await host.getFreePort();
  forwardClosable = await device.forward(
    Serial,
    gamiumHostPort,
    DeviceGamiumServerPort
  );

  const service = new NodeGamiumService(Localhost, gamiumHostPort);
  gamium = new GamiumClient(service);
  await gamium.connect();

  ui = gamium.ui();
}, 300_000);

afterAll(async () => {
  await gamium.sleep(5000);
  await gamium.actions().appQuit().perform();
  await forwardClosable?.close();
  await driver.deleteSession();
  await server?.close();
}, 300_000);
