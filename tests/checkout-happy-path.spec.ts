import { test, expect } from "@playwright/test";

/**
 * Critical E2E: Login → add product → checkout → verify completion.
 *
 * Selectors prefer data-test attributes (stable on SauceDemo) over CSS/XPath.
 * Assertions check outcomes (URL, visible confirmation, cleared cart badge),
 * not just that buttons were clicked.
 */
test.describe("SauceDemo purchase flow", () => {
  test.beforeEach(async ({ page }) => {
    // Isolation: each test starts logged out with a clean origin storage state.
    await page.goto("/");
    await page.context().clearCookies();
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.goto("/");
  });

  test("standard_user can buy a product and complete checkout", async ({
    page,
  }) => {
    // --- Login ---
    await page.getByPlaceholder("Username").fill("standard_user");
    await page.getByPlaceholder("Password").fill("secret_sauce");
    await page.getByRole("button", { name: "Login" }).click();

    await expect(page).toHaveURL(/inventory\.html/);
    await expect(page.getByText("Products")).toBeVisible();

    // --- Select product & add to cart ---
    const backpack = page.getByTestId("add-to-cart-sauce-labs-backpack");
    await backpack.click();
    await expect(page.getByTestId("remove-sauce-labs-backpack")).toBeVisible();
    await expect(page.getByTestId("shopping-cart-badge")).toHaveText("1");

    // --- Cart ---
    await page.getByTestId("shopping-cart-link").click();
    await expect(page).toHaveURL(/cart\.html/);
    await expect(page.getByTestId("inventory-item-name")).toHaveText(
      "Sauce Labs Backpack",
    );
    await expect(page.getByTestId("inventory-item-price")).toHaveText(
      "$29.99",
    );

    // --- Checkout step one ---
    await page.getByTestId("checkout").click();
    await expect(page).toHaveURL(/checkout-step-one\.html/);
    await page.getByTestId("firstName").fill("Ada");
    await page.getByTestId("lastName").fill("Lovelace");
    await page.getByTestId("postalCode").fill("90210");
    await page.getByTestId("continue").click();

    // --- Overview: meaningful price assertions ---
    await expect(page).toHaveURL(/checkout-step-two\.html/);
    await expect(page.getByTestId("inventory-item-name")).toHaveText(
      "Sauce Labs Backpack",
    );
    await expect(page.getByTestId("subtotal-label")).toContainText("29.99");
    await expect(page.getByTestId("tax-label")).toContainText("2.40");
    await expect(page.getByTestId("total-label")).toContainText("32.39");

    // --- Finish ---
    await page.getByTestId("finish").click();
    await expect(page).toHaveURL(/checkout-complete\.html/);
    await expect(page.getByTestId("complete-header")).toHaveText(
      "Thank you for your order!",
    );
    await expect(page.getByTestId("complete-text")).toBeVisible();

    // Cart should be cleared after a successful order
    await expect(page.getByTestId("shopping-cart-badge")).toHaveCount(0);
  });
});
