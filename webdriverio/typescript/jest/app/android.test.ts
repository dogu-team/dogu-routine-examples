import { test, expect } from "@jest/globals";
import { driver } from "./setup.js";

test("find and click wikipedia", async () => {
  const searchSelector = await driver.$("~Search Wikipedia");
  await searchSelector.waitForDisplayed({ timeout: 30_000 });
  await searchSelector.click();
}, 10_000);

test("find insert text", async () => {
  const insertTextSelector = await driver.$(
    'android=new UiSelector().resourceId("org.wikipedia.alpha:id/search_src_text")'
  );
  await insertTextSelector.waitForDisplayed({ timeout: 30_000 });
  await insertTextSelector.addValue("Wikipedia");
  await driver.pause(5_000);
}, 10_000);

test('expect to find "Wikipedia"', async () => {
  const allProductsName = await driver.$$(`android.widget.TextView`);
  expect(allProductsName.length).toBeGreaterThan(0);
});
