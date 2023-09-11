import { test } from "@jest/globals";
import { driver } from "./setup.js";

test("find and click", async () => {
  const searchSelector = await driver.$("~Click me");
  await searchSelector.waitForDisplayed({ timeout: 30_000 });
  await searchSelector.click();
}, 10_000);

test("insert text", async () => {
  const insertTextSelector = await driver.$("~Enter Text");
  await insertTextSelector.waitForDisplayed({ timeout: 30_000 });
  await insertTextSelector.addValue("Hello dogu!");
  await driver.pause(5_000);
}, 10_000);
