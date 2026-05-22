import { test, expect } from '@playwright/test';
import { waitForAppReady } from './fixtures';

test.describe('Playback dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/playback');
    await waitForAppReady(page);
  });

  test('renders playback heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Playback Dashboard', level: 2 })).toBeVisible();
  });

  test('loads sessions from API', async ({ page }) => {
    await expect(page.getByText(/WebSocket (Live|Offline)/)).toBeVisible({ timeout: 20_000 });
    await expect(page.getByText(/\d+ active session|No active sessions/i)).toBeVisible({
      timeout: 20_000,
    });
  });

  test('websocket status indicator present', async ({ page }) => {
    await expect(page.getByText(/WebSocket (Live|Offline)/)).toBeVisible({ timeout: 20_000 });
  });
});
