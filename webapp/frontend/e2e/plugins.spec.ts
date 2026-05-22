import { test, expect } from '@playwright/test';
import { waitForAppReady } from './fixtures';

test.describe('Plugins page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/plugins');
    await waitForAppReady(page);
  });

  test('renders plugins heading and tabs', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Plugins', level: 2 })).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByRole('button', { name: /Installed/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Catalog/i })).toBeVisible();
  });

  test('installed tab loads plugin list or empty state', async ({ page }) => {
    await page.getByRole('button', { name: /Installed/i }).click();
    await page.waitForTimeout(3000);
    const hasPlugins = await page.locator('main .card').count();
    const hasEmpty = await page.getByText('No plugins installed').count();
    expect(hasPlugins + hasEmpty).toBeGreaterThan(0);
  });

  test('catalog tab loads available plugins or empty state', async ({ page }) => {
    await page.getByRole('button', { name: /Catalog/i }).click();
    await page.waitForTimeout(3000);
    const hasCatalog = await page.locator('main .card').count();
    const hasSearch = await page.getByPlaceholder('Search plugins...').count();
    const hasEmpty = await page.getByText(/no plugins/i).count();
    expect(hasCatalog + hasSearch + hasEmpty).toBeGreaterThan(0);
  });
});
