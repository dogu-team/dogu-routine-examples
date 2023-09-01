import { beforeAll, afterAll } from "@jest/globals";
import { DeviceClient, AppiumServerContext } from "dogu-device-client";
import { remote, RemoteOptions } from "webdriverio";

const IsCI = process.env["CI"] === "true";
const Serial = process.env["DOGU_DEVICE_SERIAL"] ?? "YOUR_LOCAL_DEVICE_SERIAL";
const DeviceServerPort = parseInt(
  process.env["DOGU_DEVICE_SERVER_PORT"] ?? "5001"
);

export let driver: WebdriverIO.Browser;
let server: AppiumServerContext | undefined;

beforeAll(async () => {
  const device = new DeviceClient({ port: DeviceServerPort });
  server = await device.runAppiumServer(Serial);
  const caps = await device.getAppiumCapabilities(Serial);
  if (!IsCI) {
    caps["appium:app"] = "YOUR_LOCAL_APP_PATH";
  }

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
});

afterAll(async () => {
  await driver.deleteSession();
  await server?.close();
});
