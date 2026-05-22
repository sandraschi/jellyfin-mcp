import { expect, type Page } from '@playwright/test';

/** Sidebar navigation targets — must match sidebar.tsx */
export const NAV_ITEMS = [
  { href: '/', label: 'Overview', heading: 'Overview' },
  { href: '/libraries', label: 'Libraries', heading: 'Media Libraries' },
  { href: '/media/Movies', label: 'Media Browser', heading: 'Movies' },
  { href: '/search', label: 'Search', heading: 'Search' },
  { href: '/playback', label: 'Playback', heading: 'Playback Dashboard' },
  { href: '/plugins', label: 'Plugins', heading: 'Plugins' },
  { href: '/livetv', label: 'Live TV', heading: 'Live TV' },
  { href: '/users', label: 'Users', heading: 'Users' },
  { href: '/settings', label: 'Settings', heading: 'Settings' },
  { href: '/rag', label: 'RAG Search', heading: 'RAG Search' },
  { href: '/chat', label: 'AI Chat', heading: 'AI Chat' },
  { href: '/help', label: 'Help', heading: 'Help & Reference' },
] as const;

export async function waitForAppReady(page: Page) {
  await expect(page.getByRole('heading', { name: 'jellyfin-mcp', level: 1 })).toBeVisible();
}

export async function navigateViaSidebar(page: Page, label: string) {
  await page.getByRole('link', { name: label, exact: true }).click();
}

export async function expectPageHeading(page: Page, heading: string) {
  await expect(page.getByRole('heading', { name: heading, level: 2 })).toBeVisible({
    timeout: 15_000,
  });
}

export async function expectNoFatalError(page: Page) {
  const errorBanner = page.locator('.border-red-500\\/20').first();
  const count = await errorBanner.count();
  if (count > 0) {
    const text = await errorBanner.textContent();
    if (text && !text.includes('No results') && !text.includes('No media')) {
      // Allow benign empty-state messages; fail on API connection errors
      if (text.toLowerCase().includes('failed') || text.toLowerCase().includes('error')) {
        throw new Error(`Unexpected error banner: ${text}`);
      }
    }
  }
}
