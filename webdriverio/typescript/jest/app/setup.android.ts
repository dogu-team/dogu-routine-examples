import { beforeAll, afterAll } from "@jest/globals";
import { DeviceClient, AppiumServerContext } from "dogu-device-client";
import { remote, RemoteOptions } from "webdriverio";

const isCi = process.env["CI"] === "true";
export const serial =
  process.env["DOGU_DEVICE_SERIAL"] ?? "YOUR_LOCAL_DEVICE_SERIAL";
const deviceServerPort = parseInt(
  process.env["DOGU_DEVICE_SERVER_PORT"] ?? "5001"
);

declare global {
  var driver: WebdriverIO.Browser;
}

let server: AppiumServerContext | undefined;

beforeAll(async () => {
  const device = new DeviceClient({ port: deviceServerPort });
  server = await device.runAppiumServer(serial);
  const caps = await device.getAppiumCapabilities(serial);
  if (!isCi) {
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

  const driver = await remote(options);
  global.driver = driver;
});

afterAll(async () => {
  const driver = global.driver;
  Reflect.deleteProperty(global, "driver");
  await driver.deleteSession();
  await server?.close();
});
