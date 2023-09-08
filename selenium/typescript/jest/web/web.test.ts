import { test, expect } from "@jest/globals";
import { driver } from "./setup.js";

test("go to dogutech.io", async () => {
  await driver.get("https://dogutech.io");
});

test("find Dogu elements", async () => {
  const doguElements = await driver.findElements({
    xpath: "//*[contains(text(), 'Dogu')]",
  });
  expect(doguElements.length).toBeGreaterThan(0);
});
