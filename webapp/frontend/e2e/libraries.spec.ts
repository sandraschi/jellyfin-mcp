import { test, expect } from '@playwright/test';
import { navigateViaSidebar, waitForAppReady } from './fixtures';

test.describe('Libraries page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/libraries');
    await waitForAppReady(page);
  });

  test('loads library list from API', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Media Libraries', level: 2 })).toBeVisible();
    await expect(page.getByText(/\d+ libraries configured/)).toBeVisible();
  });

  test('shows library cards or empty state', async ({ page }) => {
    await page.waitForTimeout(2000);
    const hasLibraries = await page.getByText('items in library').count();
    const hasEmpty = await page.getByText('No media libraries found').count();
    expect(hasLibraries + hasEmpty).toBeGreaterThan(0);
  });

  test('accessible from sidebar', async ({ page }) => {
    await page.goto('/');
    await navigateViaSidebar(page, 'Libraries');
    await expect(page).toHaveURL('/libraries');
  });
});
