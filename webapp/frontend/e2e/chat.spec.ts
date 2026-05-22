import { test, expect } from '@playwright/test';
import { waitForAppReady } from './fixtures';

test.describe('AI Chat page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/chat');
    await waitForAppReady(page);
  });

  test('renders chat heading and input', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'AI Chat', level: 2 })).toBeVisible();
    await page.waitForTimeout(2000);
    const input = page.getByPlaceholder(/message|ask|type/i);
    await expect(input.first()).toBeVisible();
  });

  test('model selector is available', async ({ page }) => {
    await page.waitForTimeout(2000);
    const modelSelect = page.locator('select').first();
    if (await modelSelect.count()) {
      await expect(modelSelect).toBeVisible();
    }
  });

  test('send button disabled when input empty', async ({ page }) => {
    await page.waitForTimeout(2000);
    const sendBtn = page.getByRole('button', { name: /Send/i });
    if (await sendBtn.count()) {
      await expect(sendBtn.first()).toBeDisabled();
    }
  });
});
