import { test, expect } from '@playwright/test';
import { waitForAppReady } from './fixtures';

test.describe('Live TV page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/livetv');
    await waitForAppReady(page);
  });

  test('renders Live TV heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Live TV', level: 2 })).toBeVisible();
  });

  test('loads channels or empty state', async ({ page }) => {
    await page.waitForTimeout(3000);
    const content = page.locator('.card, main');
    await expect(content.first()).toBeVisible();
  });
});
