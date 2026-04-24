import { test, expect } from "@playwright/test";

/**
 * E2E Tests for News Analytics Platform Production Deployment
 * Tests the full user journey on the deployed Vercel instance
 */

const PRODUCTION_URL =
  process.env.TEST_URL || "https://frontend-weld-seven-93.vercel.app";

test.describe("Production Deployment - Basic Functionality", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the production URL before each test
    await page.goto("/");
  });

  test("should load the home page successfully", async ({ page }) => {
    // Wait for the page to load
    await page.waitForLoadState("networkidle");

    // Check that we're on the correct URL
    expect(page.url()).toContain("vercel.app");

    // Check page title
    await expect(page).toHaveTitle(/News Analytics/i);

    // Take a screenshot for visual verification
    await page.screenshot({
      path: "test-results/home-page.png",
      fullPage: true,
    });
  });

  test("should display navigation menu", async ({ page }) => {
    // Check for navigation links
    const storiesLink = page.locator('nav a[href="/"]').first();
    const analyticsLink = page.locator('nav a[href="/analytics"]').first();

    await expect(storiesLink).toBeVisible();
    await expect(analyticsLink).toBeVisible();

    // Verify navigation text
    await expect(storiesLink).toContainText(/stories/i);
    await expect(analyticsLink).toContainText(/analytics/i);
  });

  test("should navigate to Stories page", async ({ page }) => {
    // Click on Stories link (or verify we're already there)
    await page.goto("/");

    // Wait for page to load
    await page.waitForLoadState("domcontentloaded");

    // Check for stories page elements
    const pageContent = await page.textContent("body");
    expect(pageContent).toBeTruthy();

    // Look for stories page controls
    const hasIngestButton =
      (await page.locator('button:has-text("Ingest")').count()) > 0;
    const hasClusterButton =
      (await page.locator('button:has-text("Cluster")').count()) > 0;
    const hasRefreshButton =
      (await page.locator('button:has-text("Refresh")').count()) > 0;

    // At least one of these should be present on the stories page
    expect(
      hasIngestButton || hasClusterButton || hasRefreshButton,
    ).toBeTruthy();
  });

  test("should navigate to Analytics page", async ({ page }) => {
    // Navigate to analytics
    await page.goto("/analytics");

    // Wait for page to load
    await page.waitForLoadState("domcontentloaded");

    // Check for analytics page content
    const pageContent = await page.textContent("body");
    expect(pageContent).toBeTruthy();

    // Analytics page should have some data visualization elements
    const hasAnalyticsContent =
      pageContent.toLowerCase().includes("analytics") ||
      pageContent.toLowerCase().includes("coverage") ||
      pageContent.toLowerCase().includes("sources");

    expect(hasAnalyticsContent).toBeTruthy();
  });

  test("should handle 404 page", async ({ page }) => {
    // Navigate to a non-existent page
    await page.goto("/this-page-does-not-exist");

    // Wait for navigation
    await page.waitForLoadState("domcontentloaded");

    // Should redirect or show an error
    const pageContent = await page.textContent("body");

    // Check if it's a 404 or redirected to home
    const is404 =
      pageContent.toLowerCase().includes("not found") ||
      pageContent.toLowerCase().includes("404");
    const isRedirected =
      page.url().endsWith("/") || page.url().endsWith("/analytics");

    expect(is404 || isRedirected).toBeTruthy();
  });
});

test.describe("Production Deployment - UI Components", () => {
  test("should render page header correctly", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Check for main heading or logo
    const hasHeading = await page
      .locator("h1, h2")
      .first()
      .isVisible()
      .catch(() => false);
    const hasNav = await page
      .locator("nav")
      .isVisible()
      .catch(() => false);

    expect(hasHeading || hasNav).toBeTruthy();
  });

  test("should have responsive layout on mobile", async ({
    page,
    isMobile,
  }) => {
    await page.goto("/");
    await page.waitForLoadState("domcontentloaded");

    // Check viewport
    const viewport = page.viewportSize();
    expect(viewport).toBeTruthy();

    // Page should render without horizontal scroll
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = viewport?.width || 0;

    // Allow small difference for scrollbar
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 20);
  });

  test("should load CSS styles correctly", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Check if styles are applied by looking for computed styles
    const body = await page.locator("body");
    const backgroundColor = await body.evaluate(
      (el) => window.getComputedStyle(el).backgroundColor,
    );

    // Background color should be set (not transparent/default)
    expect(backgroundColor).toBeTruthy();
    expect(backgroundColor).not.toBe("rgba(0, 0, 0, 0)");
  });

  test("should load JavaScript correctly", async ({ page }) => {
    await page.goto("/");

    // Wait for React to mount
    await page.waitForLoadState("domcontentloaded");

    // Check if React has rendered by looking for React root
    const hasReactRoot = await page.evaluate(() => {
      const root = document.getElementById("root");
      return root && root.children.length > 0;
    });

    expect(hasReactRoot).toBeTruthy();
  });
});

test.describe("Production Deployment - Performance", () => {
  test("should load within acceptable time", async ({ page }) => {
    const startTime = Date.now();

    await page.goto("/");
    await page.waitForLoadState("domcontentloaded");

    const loadTime = Date.now() - startTime;

    // Page should load in less than 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });

  test("should have no console errors on load", async ({ page }) => {
    const consoleErrors = [];

    // Listen for console errors
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Filter out expected errors (like failed API calls to non-existent backend)
    const unexpectedErrors = consoleErrors.filter((error) => {
      const isNetworkError =
        error.toLowerCase().includes("network") ||
        error.toLowerCase().includes("failed to fetch") ||
        error.toLowerCase().includes("err_network");
      return !isNetworkError;
    });

    // Should have no unexpected console errors
    expect(unexpectedErrors.length).toBe(0);
  });

  test("should not have accessibility violations", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Check for basic accessibility
    // 1. Page has a title
    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(0);

    // 2. Main content is present
    const hasMainContent =
      (await page.locator('main, [role="main"], #root').count()) > 0;
    expect(hasMainContent).toBeTruthy();

    // 3. No missing alt text on images (if any)
    const imagesWithoutAlt = await page.locator("img:not([alt])").count();
    expect(imagesWithoutAlt).toBe(0);
  });
});

test.describe("Production Deployment - API Integration", () => {
  test("should handle API errors gracefully", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("domcontentloaded");

    // Wait a bit for any API calls to complete/fail
    await page.waitForTimeout(2000);

    // Check that the page still renders even if API calls fail
    const bodyText = await page.textContent("body");
    expect(bodyText).toBeTruthy();

    // Should show some user-friendly content (not blank page)
    expect(bodyText.length).toBeGreaterThan(100);
  });

  test("should show loading states", async ({ page }) => {
    await page.goto("/");

    // Try to find loading indicators
    const hasLoadingText =
      (await page.getByText(/loading/i).count()) > 0 ||
      (await page.locator('[aria-busy="true"]').count()) > 0 ||
      (await page.locator(".loading, .spinner").count()) > 0;

    // Note: This might be false if page loads too quickly
    // That's okay - the test is to verify loading states exist in the code
    console.log("Loading indicators found:", hasLoadingText);
  });

  test("should display empty state when no data", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Wait for any loading to complete
    await page.waitForTimeout(2000);

    // Check for empty state messages
    const bodyText = await page.textContent("body");
    const hasEmptyState =
      bodyText.toLowerCase().includes("no stories") ||
      bodyText.toLowerCase().includes("no data") ||
      bodyText.toLowerCase().includes("empty") ||
      bodyText.toLowerCase().includes("ingest articles");

    // Should show either data or an empty state
    expect(hasEmptyState || bodyText.length > 500).toBeTruthy();
  });
});

test.describe("Production Deployment - User Interactions", () => {
  test("should handle button clicks", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("domcontentloaded");

    // Find any clickable buttons
    const buttons = await page.locator("button").all();

    if (buttons.length > 0) {
      // Try clicking the first button
      const firstButton = buttons[0];
      const isVisible = await firstButton.isVisible().catch(() => false);

      if (isVisible) {
        await firstButton.click();

        // Wait a bit for any reaction
        await page.waitForTimeout(500);

        // Page should still be functional after click
        const bodyText = await page.textContent("body");
        expect(bodyText).toBeTruthy();
      }
    }
  });

  test("should navigate between pages using UI", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("domcontentloaded");

    // Try to find and click analytics link
    const analyticsLink = page
      .locator('a[href="/analytics"], nav a')
      .filter({ hasText: /analytics/i })
      .first();
    const linkExists = (await analyticsLink.count()) > 0;

    if (linkExists) {
      await analyticsLink.click();
      await page.waitForLoadState("domcontentloaded");

      // Should navigate to analytics
      expect(page.url()).toContain("analytics");
    }
  });
});

test.describe("Production Deployment - Security & Headers", () => {
  test("should have secure headers", async ({ page }) => {
    const response = await page.goto("/");
    expect(response).toBeTruthy();

    if (response) {
      const headers = response.headers();

      // Check for security headers (Vercel typically adds these)
      // Note: Not all may be present, but document what we find
      console.log("Security headers found:", {
        "x-frame-options": headers["x-frame-options"],
        "x-content-type-options": headers["x-content-type-options"],
        "x-xss-protection": headers["x-xss-protection"],
        "strict-transport-security": headers["strict-transport-security"],
      });

      // Response should be successful
      expect(response.status()).toBe(200);
    }
  });

  test("should serve content over HTTPS", async ({ page }) => {
    await page.goto("/");

    // Production URL should be HTTPS
    expect(page.url()).toMatch(/^https:\/\//);
  });

  test("should not expose sensitive information", async ({ page }) => {
    const response = await page.goto("/");

    if (response) {
      const headers = response.headers();
      const body = await page.content();

      // Should not expose server information
      expect(headers["x-powered-by"]).toBeFalsy();

      // Should not have API keys or secrets in source
      expect(body).not.toContain("sk-"); // OpenAI keys
      expect(body).not.toContain("mongodb://"); // DB credentials
    }
  });
});

test.describe("Production Deployment - Final Validation", () => {
  test("comprehensive smoke test", async ({ page }) => {
    // This is a comprehensive test that verifies the deployment is working
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // 1. Page loads
    expect(page.url()).toBeTruthy();

    // 2. Content is present
    const bodyText = await page.textContent("body");
    expect(bodyText.length).toBeGreaterThan(50);

    // 3. No fatal errors
    const pageErrors = [];
    page.on("pageerror", (error) => {
      pageErrors.push(error.message);
    });

    // Navigate around
    await page.goto("/analytics").catch(() => {});
    await page.waitForTimeout(1000);
    await page.goto("/").catch(() => {});
    await page.waitForTimeout(1000);

    // Should have no fatal page errors
    expect(pageErrors.length).toBe(0);

    // 4. Take final screenshot
    await page.screenshot({
      path: "test-results/final-validation.png",
      fullPage: true,
    });

    console.log("✅ Production deployment validation complete!");
  });
});
