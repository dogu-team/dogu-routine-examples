import { test, expect } from "@jest/globals";
import { driver } from "./setup.js";

test(
  "go to dogutech.io",
  async () => {
    await driver.get("https://dogutech.io");
  },
  5 * 60_000
);

test("find Dogu elements", async () => {
  const doguElements = await driver.findElements({
    xpath: "//*[contains(text(), 'Dogu')]",
  });
  expect(doguElements.length).toBeGreaterThan(0);
});

test("scroll pages", async () => {
  await driver.executeScript("window.scrollTo(0, document.body.scrollHeight)");
  await driver.sleep(3000);

  await driver.executeScript("window.scrollTo(0, 0)");
  await driver.sleep(3000);
});
