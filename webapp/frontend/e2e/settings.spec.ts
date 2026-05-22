import { test, expect } from '@playwright/test';
import { waitForAppReady } from './fixtures';

test.describe('Settings page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
    await waitForAppReady(page);
  });

  test('renders settings form sections', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Settings', level: 2 })).toBeVisible();
    await page.waitForTimeout(2000);
    await expect(page.getByText('Jellyfin Server')).toBeVisible();
    await expect(page.getByPlaceholder('http://localhost:8096')).toBeVisible();
    await expect(page.getByPlaceholder('Enter your Jellyfin API key')).toBeVisible();
  });

  test('LLM configuration section visible', async ({ page }) => {
    await page.waitForTimeout(2000);
    await expect(page.getByText(/LLM.*RAG Configuration/i)).toBeVisible();
    await expect(page.getByText('LLM Provider')).toBeVisible();
  });

  test('save button is present and clickable', async ({ page }) => {
    await page.waitForTimeout(2000);
    const saveBtn = page.getByRole('button', { name: 'Save' });
    await expect(saveBtn).toBeVisible();
    await expect(saveBtn).toBeEnabled();
  });
});
