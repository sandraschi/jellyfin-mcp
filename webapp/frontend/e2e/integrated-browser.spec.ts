/**
 * Integrated-browser e2e scenarios.
 *
 * Run manually with Cursor's integrated browser (cursor-ide-browser MCP):
 * 1. Start servers: `just e2e-serve` or `npx playwright test --grep @noop` (starts webServer)
 * 2. Open http://127.0.0.1:10935 in the integrated browser
 * 3. Walk through INTEGRATED_BROWSER_SCENARIOS below
 *
 * Playwright runs the same assertions headlessly for CI.
 */
import { test, expect } from '@playwright/test';
import { NAV_ITEMS, navigateViaSidebar, waitForAppReady } from './fixtures';

export const INTEGRATED_BROWSER_SCENARIOS = [
  {
    id: 'overview',
    url: '/',
    heading: 'Overview',
    checks: ['Libraries stat', 'Server Version'],
  },
  ...NAV_ITEMS.filter((item) => item.href !== '/').map((item) => ({
    id: item.label.toLowerCase().replace(/\s+/g, '-'),
    url: item.href,
    heading: item.heading,
    checks: [`heading:${item.heading}`],
  })),
] as const;

test.describe('Integrated browser parity @browser', () => {
  test('all sidebar routes render without fatal errors', async ({ page }) => {
    test.setTimeout(180_000);
    const errors: string[] = [];
    page.on('pageerror', (err) => errors.push(err.message));

    for (const item of NAV_ITEMS) {
      await page.goto(item.href);
      await waitForAppReady(page);
      await expect(page.getByRole('heading', { name: item.heading, level: 2 })).toBeVisible({
        timeout: 20_000,
      });
      await page.waitForTimeout(800);
    }

    const critical = errors.filter(
      (e) => !e.includes('favicon') && !e.includes('hydration'),
    );
    expect(critical).toEqual([]);
  });

  test('libraries page shows Jellyfin data when configured', async ({ page }) => {
    await page.goto('/libraries');
    await waitForAppReady(page);
    await expect(page.getByRole('heading', { name: 'Media Libraries', level: 2 })).toBeVisible();
    await page.waitForTimeout(2500);

    const configured = page.getByText(/\d+ libraries configured/);
    const empty = page.getByText('No media libraries found');
    const hasConfigured = (await configured.count()) > 0;
    const hasEmpty = (await empty.count()) > 0;
    expect(hasConfigured || hasEmpty).toBeTruthy();

    if (hasConfigured) {
      await expect(configured).toBeVisible();
    }
  });

  test('search flow returns results or empty state', async ({ page }) => {
    await page.goto('/search');
    await waitForAppReady(page);
    await page.getByPlaceholder('Search movies, series, music...').fill('a');
    await page.getByRole('button', { name: 'Search' }).click();
    await page.waitForTimeout(3000);

    const body = await page.locator('main').textContent();
    expect(body?.length).toBeGreaterThan(0);
  });

  test('settings shows Jellyfin URL field', async ({ page }) => {
    await page.goto('/settings');
    await waitForAppReady(page);
    await expect(page.getByPlaceholder('http://localhost:8096')).toBeVisible();
  });

  test('help quickstart visible', async ({ page }) => {
    await page.goto('/help');
    await waitForAppReady(page);
    await expect(page.getByText('Quickstart')).toBeVisible();
  });
});

test('@noop', () => {
  // Used to start webServer without running assertions: npx playwright test -g @noop
});
