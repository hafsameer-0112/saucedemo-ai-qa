import { defineConfig, devices } from "@playwright/test";

/**
 * SauceDemo E2E — keeps defaults lean for a single critical purchase flow.
 * No unnecessary hard-coded waits; Playwright auto-waiting + expect() timeouts.
 */
export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  timeout: 60_000,
  expect: { timeout: 10_000 },
  use: {
    baseURL: "https://www.saucedemo.com",
    // SauceDemo exposes stable locators as data-test (not data-testid).
    testIdAttribute: "data-test",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    ...devices["Desktop Chrome"],
  },
});

