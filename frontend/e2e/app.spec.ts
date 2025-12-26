import { test, expect } from "@playwright/test";

test.describe("Authentication Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3001");
  });

  test("should allow user to sign up", async ({ page }) => {
    await page.click("text=Sign Up");
    await expect(page).toHaveURL(/.*signup/);

    const timestamp = Date.now();
    await page.fill("#email", `test${timestamp}@example.com`);
    await page.fill("#password", "Test1234");
    await page.fill("#displayName", "Test User");

    await page.click('button[type="submit"]');

    // Should redirect to home page after successful signup
    await expect(page).toHaveURL("/");
    await expect(page.locator("text=Welcome")).toBeVisible();
  });

  test("should allow user to login", async ({ page }) => {
    // First create a user
    await page.click("text=Sign Up");
    const timestamp = Date.now();
    const email = `test${timestamp}@example.com`;

    await page.fill("#email", email);
    await page.fill("#password", "Test1234");
    await page.click('button[type="submit"]');

    // Logout
    await page.click("text=Logout");

    // Now login
    await page.click("text=Login");
    await expect(page).toHaveURL(/.*login/);

    await page.fill("#email", email);
    await page.fill("#password", "Test1234");
    await page.click('button[type="submit"]');

    // Should redirect to home page after successful login
    await expect(page).toHaveURL("/");
    await expect(page.locator("text=Welcome")).toBeVisible();
  });

  test("should show error for invalid credentials", async ({ page }) => {
    await page.click("text=Login");

    await page.fill("#email", "nonexistent@example.com");
    await page.fill("#password", "wrongpassword");
    await page.click('button[type="submit"]');

    await expect(page.locator(".error")).toBeVisible();
    await expect(page.locator(".error")).toContainText("Invalid credentials");
  });

  test("should allow user to logout", async ({ page }) => {
    // Sign up first
    await page.click("text=Sign Up");
    const timestamp = Date.now();

    await page.fill("#email", `test${timestamp}@example.com`);
    await page.fill("#password", "Test1234");
    await page.click('button[type="submit"]');

    // Logout
    await page.click("text=Logout");

    // Should see login/signup links again
    await expect(page.locator("text=Login")).toBeVisible();
    await expect(page.locator("text=Sign Up")).toBeVisible();
  });
});

test.describe("Profile Management", () => {
  test.beforeEach(async ({ page }) => {
    // Create and login a user
    await page.goto("http://localhost:3001");
    await page.click("text=Sign Up");

    const timestamp = Date.now();
    await page.fill("#email", `test${timestamp}@example.com`);
    await page.fill("#password", "Test1234");
    await page.fill("#displayName", "Original Name");
    await page.click('button[type="submit"]');
  });

  test("should allow user to view profile", async ({ page }) => {
    await page.click("text=Profile");
    await expect(page).toHaveURL(/.*profile/);

    await expect(page.locator("text=Original Name")).toBeVisible();
  });

  test("should allow user to edit profile", async ({ page }) => {
    await page.click("text=Profile");
    await page.click("text=Edit Profile");

    await page.fill("#displayName", "Updated Name");
    await page.click('button[type="submit"]');

    await expect(page.locator(".success")).toBeVisible();
    await expect(page.locator("text=Updated Name")).toBeVisible();
  });
});

test.describe("Bookmark Management", () => {
  test.beforeEach(async ({ page }) => {
    // Create and login a user
    await page.goto("http://localhost:3001");
    await page.click("text=Sign Up");

    const timestamp = Date.now();
    await page.fill("#email", `test${timestamp}@example.com`);
    await page.fill("#password", "Test1234");
    await page.click('button[type="submit"]');
  });

  test("should show bookmarks page", async ({ page }) => {
    await page.click("text=Bookmarks");
    await expect(page).toHaveURL(/.*bookmarks/);

    await expect(page.locator("h1")).toContainText("My Bookmarks");
  });

  test("should show no bookmarks message initially", async ({ page }) => {
    await page.click("text=Bookmarks");

    await expect(page.locator("text=No bookmarks yet")).toBeVisible();
  });
});

test.describe("Filter Management", () => {
  test.beforeEach(async ({ page }) => {
    // Create and login a user
    await page.goto("http://localhost:3001");
    await page.click("text=Sign Up");

    const timestamp = Date.now();
    await page.fill("#email", `test${timestamp}@example.com`);
    await page.fill("#password", "Test1234");
    await page.click('button[type="submit"]');
  });

  test("should show filters page", async ({ page }) => {
    await page.click("text=Filters");
    await expect(page).toHaveURL(/.*filters/);

    await expect(page.locator("h1")).toContainText("Saved Filters");
  });

  test("should allow creating a new filter", async ({ page }) => {
    await page.click("text=Filters");
    await page.click("text=Add New Filter");

    await page.fill("#name", "Tech News");
    await page.fill("#filterQuery", '{"category": "tech"}');
    await page.click('button[type="submit"]');

    await expect(page.locator("text=Tech News")).toBeVisible();
  });
});

test.describe("Protected Routes", () => {
  test("should redirect to login when accessing protected route without auth", async ({
    page,
  }) => {
    await page.goto("http://localhost:3001/profile");

    // Should redirect to login
    await expect(page).toHaveURL(/.*login/);
  });

  test("should allow access to protected route when authenticated", async ({
    page,
  }) => {
    // Sign up first
    await page.goto("http://localhost:3001");
    await page.click("text=Sign Up");

    const timestamp = Date.now();
    await page.fill("#email", `test${timestamp}@example.com`);
    await page.fill("#password", "Test1234");
    await page.click('button[type="submit"]');

    // Navigate to protected route
    await page.goto("http://localhost:3001/profile");

    // Should stay on profile page
    await expect(page).toHaveURL(/.*profile/);
  });
});
