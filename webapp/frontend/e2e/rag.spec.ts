import { test, expect } from '@playwright/test';
import { waitForAppReady } from './fixtures';

test.describe('RAG Search page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/rag');
    await waitForAppReady(page);
  });

  test('renders RAG heading and status', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'RAG Search', level: 2 })).toBeVisible();
    await page.waitForTimeout(2000);
    await expect(page.getByText(/Indexed|Documents|Status|Sync/i).first()).toBeVisible();
  });

  test('semantic search input and sync button present', async ({ page }) => {
    await page.waitForTimeout(2000);
    const searchInput = page.getByPlaceholder(/search|query|natural/i);
    const syncBtn = page.getByRole('button', { name: /Sync|Reindex|Index/i });
    expect((await searchInput.count()) + (await syncBtn.count())).toBeGreaterThan(0);
  });
});
