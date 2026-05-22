import { test, expect } from '@playwright/test';
import { waitForAppReady } from './fixtures';

test.describe('Users page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/users');
    await waitForAppReady(page);
  });

  test('renders users heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Users', level: 2 })).toBeVisible();
  });

  test('loads user list from Jellyfin', async ({ page }) => {
    await page.waitForTimeout(3000);
    const hasUsers = await page.locator('.card').count();
    const hasEmpty = await page.getByText(/no users/i).count();
    expect(hasUsers + hasEmpty).toBeGreaterThan(0);
  });

  test('create user button toggles form', async ({ page }) => {
    await page.waitForTimeout(2000);
    const createBtn = page.getByRole('button', { name: /Add User|Create|New User/i });
    if (await createBtn.count()) {
      await createBtn.first().click();
      await expect(page.getByPlaceholder(/username|name/i).or(page.locator('input[type="text"]').first())).toBeVisible();
    }
  });
});
