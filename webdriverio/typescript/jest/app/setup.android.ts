import { beforeAll, afterAll } from "@jest/globals";
import { DeviceClient, AppiumServerContext } from "dogu-device-client";
import { remote, RemoteOptions } from "webdriverio";
import { config } from "dotenv";

config({ path: ".env.local" });

const Serial = process.env["DOGU_DEVICE_SERIAL"];
const AppPath = process.env["DOGU_APP_PATH"];
const DeviceServerPort = parseInt(
  process.env["DOGU_DEVICE_SERVER_PORT"] ?? "5001"
);

if (!Serial) {
  throw new Error("DOGU_DEVICE_SERIAL is not specified");
}

if (!AppPath) {
  throw new Error("DOGU_APP_PATH is not specified");
}

export let driver: WebdriverIO.Browser;
let server: AppiumServerContext | undefined;

beforeAll(async () => {
  const device = new DeviceClient({ port: DeviceServerPort });
  server = await device.runAppiumServer(Serial);
  const caps = await device.getAppiumCapabilities(Serial);
  caps["appium:app"] = AppPath;

  const options: RemoteOptions = {
    logLevel: "debug",
    protocol: "http",
    hostname: "127.0.0.1",
    port: server.port,
    path: "/",
    connectionRetryCount: 0,
    capabilities: caps,
  };

  driver = await remote(options);
  await driver.dismissAlert().catch(() => {});
  await driver.acceptAlert().catch(() => {});
});

afterAll(async () => {
  await driver.deleteSession();
  await server?.close();
});
