import { test, expect } from '@playwright/test';
import { navigateViaSidebar, waitForAppReady } from './fixtures';

test.describe('Media browser', () => {
  test('loads Movies grid', async ({ page }) => {
    await page.goto('/media/Movies');
    await waitForAppReady(page);
    await expect(page.getByRole('heading', { name: 'Movies', level: 2 })).toBeVisible();
  });

  test('accessible via sidebar Media Browser link', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);
    await navigateViaSidebar(page, 'Media Browser');
    await expect(page).toHaveURL('/media/Movies');
    await expect(page.getByRole('heading', { name: 'Movies', level: 2 })).toBeVisible();
  });

  test('shows media items or empty state after load', async ({ page }) => {
    await page.goto('/media/Movies');
    await waitForAppReady(page);
    await page.waitForTimeout(3000);
    const grid = page.locator('.card, [class*="grid"]').first();
    await expect(grid).toBeVisible();
  });
});
