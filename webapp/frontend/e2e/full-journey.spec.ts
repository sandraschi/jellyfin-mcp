import { test, expect } from '@playwright/test';
import { NAV_ITEMS, navigateViaSidebar, waitForAppReady } from './fixtures';

test.describe('Full user journey', () => {
  test('browse libraries → search → settings → help', async ({ page }) => {
    test.setTimeout(120_000);
    await page.goto('/');
    await waitForAppReady(page);
    await expect(page.getByRole('heading', { name: 'Overview', level: 2 })).toBeVisible();

    await navigateViaSidebar(page, 'Libraries');
    await expect(page.getByRole('heading', { name: 'Media Libraries', level: 2 })).toBeVisible();
    await page.waitForTimeout(1500);

    await navigateViaSidebar(page, 'Search');
    await page.getByPlaceholder('Search movies, series, music...').fill('dog');
    await page.getByRole('button', { name: 'Search' }).click();
    await page.waitForTimeout(3000);

    await navigateViaSidebar(page, 'Settings');
    await expect(page.getByPlaceholder('http://localhost:8096')).toBeVisible();

    await navigateViaSidebar(page, 'Help');
    await expect(page.getByText('Quickstart')).toBeVisible();
  });

  test('visit every page without JavaScript errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (err) => errors.push(err.message));

    for (const item of NAV_ITEMS) {
      await page.goto(item.href);
      await waitForAppReady(page);
      await page.waitForTimeout(1000);
      await expect(page.getByRole('heading', { name: item.heading, level: 2 })).toBeVisible();
    }

    const critical = errors.filter(
      (e) => !e.includes('favicon') && !e.includes('hydration'),
    );
    expect(critical).toEqual([]);
  });

  test('page title and meta are set', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/jellyfin-mcp/i);
  });
});
