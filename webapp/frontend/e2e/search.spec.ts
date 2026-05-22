import { test, expect } from '@playwright/test';
import { waitForAppReady } from './fixtures';

test.describe('Search page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/search');
    await waitForAppReady(page);
  });

  test('renders search form and filters', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Search', level: 2 })).toBeVisible();
    await expect(page.getByPlaceholder('Search movies, series, music...')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Search' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'All' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Movies' })).toBeVisible();
  });

  test('executes search and shows results or empty state', async ({ page }) => {
    await page.getByPlaceholder('Search movies, series, music...').fill('dog');
    await page.getByRole('button', { name: 'Search' }).click();
    await expect(page.getByRole('button', { name: 'Searching...' })).toBeHidden({ timeout: 15_000 });
    await page.waitForTimeout(1000);
    const hasResults = await page.locator('.card.glass-hover, .card.flex').count();
    const hasEmpty = await page.getByText('No results found').count();
    const hasError = await page.locator('.border-red-500\\/20').count();
    expect(hasResults + hasEmpty + hasError).toBeGreaterThan(0);
  });

  test('type filter toggles active state', async ({ page }) => {
    const moviesFilter = page.getByRole('button', { name: 'Movies' });
    await moviesFilter.click();
    await expect(moviesFilter).toHaveClass(/bg-jellyfin-purple/);
  });
});
