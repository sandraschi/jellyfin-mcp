import { test, expect } from '@playwright/test';
import { waitForAppReady } from './fixtures';

test.describe('Overview dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);
  });

  test('renders overview heading and stat cards', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Overview', level: 2 })).toBeVisible();
    await expect(page.getByText('Active Sessions')).toBeVisible();
    await expect(page.getByText('Total Items')).toBeVisible();
    await expect(page.getByText('Server Version')).toBeVisible();
  });

  test('shows server version from live Jellyfin', async ({ page }) => {
    await page.waitForTimeout(3000);
    const card = page.locator('text=Server Version').locator('xpath=ancestor::div[contains(@class,"card")]').first();
    const text = await card.textContent();
    if (!text || text.includes('—')) {
      test.skip(true, 'Jellyfin server info unavailable — check JELLYFIN_API_KEY in .env');
    }
    expect(text).toMatch(/10\.\d+/);
  });

  test('connected status indicator visible', async ({ page }) => {
    await expect(page.getByText('Connected')).toBeVisible();
  });
});
