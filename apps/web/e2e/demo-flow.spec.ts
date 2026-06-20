import { test, expect } from "@playwright/test"

test.describe("TrailGuard AI demo flow", () => {
  test("login page loads and shows demo credentials", async ({ page }) => {
    await page.goto("http://localhost:3000/login")
    await expect(page.locator("text=TrailGuard AI")).toBeVisible()
    await expect(page.locator("text=Synthetic Demo Environment")).toBeVisible()
    await expect(page.locator("text=analyst@trailguard.ai")).toBeVisible()
  })

  test("login form validates empty fields", async ({ page }) => {
    await page.goto("http://localhost:3000/login")
    await page.click('button[type="submit"]')
    await expect(page.locator("text=Invalid email")).toBeVisible()
  })

  test("login succeeds with demo credentials", async ({ page }) => {
    await page.goto("http://localhost:3000/login")
    await page.fill('input[id="email"]', "analyst@trailguard.ai")
    await page.fill('input[id="password"]', "demo1234")
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL(/dashboard/, { timeout: 10000 })
  })

  test("dashboard loads stats after login", async ({ page }) => {
    await page.goto("http://localhost:3000/login")
    await page.fill('input[id="email"]', "analyst@trailguard.ai")
    await page.fill('input[id="password"]', "demo1234")
    await page.click('button[type="submit"]')
    await expect(page.locator("text=Command Center")).toBeVisible({ timeout: 10000 })
    await expect(page.locator("text=Total Transactions")).toBeVisible()
  })
})
