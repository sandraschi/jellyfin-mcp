import { test, expect } from '@playwright/test';
import { NAV_ITEMS, navigateViaSidebar, expectPageHeading, waitForAppReady } from './fixtures';

test.describe('Sidebar navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);
  });

  for (const item of NAV_ITEMS) {
    test(`navigates to ${item.label} (${item.href})`, async ({ page }) => {
      await navigateViaSidebar(page, item.label);
      await expect(page).toHaveURL(new RegExp(`${item.href.replace('/', '\\/')}$`));
      await expectPageHeading(page, item.heading);
    });
  }

  test('highlights active nav item', async ({ page }) => {
    await navigateViaSidebar(page, 'Libraries');
    const link = page.getByRole('link', { name: 'Libraries', exact: true });
    await expect(link).toHaveClass(/text-jellyfin-purple-light/);
  });

  test('brand header is visible on all pages', async ({ page }) => {
    for (const item of NAV_ITEMS.slice(0, 4)) {
      await navigateViaSidebar(page, item.label);
      await expect(page.getByText('Jellyfin++').first()).toBeVisible();
    }
  });
});
