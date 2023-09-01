import { test, expect, describe } from "@jest/globals";

describe("android", () => {
  test("find and click wikipedia", async () => {
    const searchSelector = await global.driver.$("~Search Wikipedia");
    await searchSelector.waitForDisplayed({ timeout: 30_000 });
    await searchSelector.click();
  }, 10_000);

  test("find insert text", async () => {
    const insertTextSelector = await global.driver.$(
      'android=new UiSelector().resourceId("org.wikipedia.alpha:id/search_src_text")'
    );
    await insertTextSelector.waitForDisplayed({ timeout: 30_000 });
    await insertTextSelector.addValue("Wikipedia");
    await global.driver.pause(5_000);
  }, 10_000);

  test('expect to find "Wikipedia"', async () => {
    const allProductsName = await global.driver.$$(`android.widget.TextView`);
    expect(allProductsName.length).toBeGreaterThan(0);
  });
});
