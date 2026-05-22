import { test, expect } from '@playwright/test';

test.describe.configure({ mode: 'serial' });

test.describe('API proxy & backend health', () => {
  test('backend health endpoint responds', async ({ request }) => {
    const res = await request.get('http://127.0.0.1:10934/health');
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body.status).toMatch(/healthy|ok/i);
  });

  test('frontend proxies /health to backend', async ({ request }) => {
    const res = await request.get('http://127.0.0.1:10935/health');
    expect(res.ok()).toBeTruthy();
  });

  test('frontend proxies /api/server/info to Jellyfin', async ({ request }) => {
    const res = await request.get('http://127.0.0.1:10935/api/server/info');
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    const info = body.data ?? body;
    expect(info.Version).toBeTruthy();
  });

  test('frontend proxies /api/libraries', async ({ request }) => {
    const res = await request.get('http://127.0.0.1:10935/api/libraries');
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    const libraries = body.data ?? body;
    expect(Array.isArray(libraries)).toBeTruthy();
  });

  test('frontend proxies /api/users', async ({ request }) => {
    const res = await request.get('http://127.0.0.1:10935/api/users');
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    const users = body.data ?? body;
    expect(Array.isArray(users)).toBeTruthy();
    expect(users.length).toBeGreaterThan(0);
  });

  test('frontend proxies /api/plugins/catalog', async ({ request }) => {
    const res = await request.get('http://127.0.0.1:10935/api/plugins/catalog');
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    const catalog = body.data ?? body;
    expect(Array.isArray(catalog)).toBeTruthy();
    expect(catalog.length).toBeGreaterThan(0);
  });
});
