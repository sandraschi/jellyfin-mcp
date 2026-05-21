import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  retries: 1,
  use: {
    baseURL: 'http://localhost:10935',
    headless: true,
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npx next dev -p 10935',
    url: 'http://localhost:10935',
    reuseExistingServer: true,
    timeout: 60000,
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
});
