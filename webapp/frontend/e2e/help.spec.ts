import { test, expect } from '@playwright/test';
import { waitForAppReady } from './fixtures';

test.describe('Help page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/help');
    await waitForAppReady(page);
  });

  test('renders help sections', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Help & Reference', level: 2 })).toBeVisible();
    await expect(page.getByText('Quickstart')).toBeVisible();
    await expect(page.getByText('MCP Tool Reference')).toBeVisible();
    await expect(page.getByText('Frequently Asked Questions')).toBeVisible();
  });

  test('tool reference cards are listed', async ({ page }) => {
    await expect(page.getByText('jellyfin_search_library')).toBeVisible();
    await expect(page.getByText('jellyfin_rag_search')).toBeVisible();
  });

  test('external resource links have correct hrefs', async ({ page }) => {
    const jellyfinDocs = page.getByRole('link', { name: 'Jellyfin Documentation' });
    await expect(jellyfinDocs).toHaveAttribute('href', 'https://jellyfin.org/docs');
    await expect(jellyfinDocs).toHaveAttribute('target', '_blank');
  });

  test('FAQ entries are rendered', async ({ page }) => {
    await expect(page.getByText('How do I connect jellyfin-mcp to my Jellyfin server?')).toBeVisible();
    await expect(page.getByText(/API key/i).first()).toBeVisible();
  });
});
