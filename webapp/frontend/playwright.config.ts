import { defineConfig } from '@playwright/test';
import path from 'node:path';

const frontendDir = __dirname;
const projectRoot = path.resolve(frontendDir, '../..');

export default defineConfig({
  testDir: './e2e',
  globalSetup: './e2e/global-setup.ts',
  timeout: 60_000,
  expect: { timeout: 15_000 },
  retries: process.env.CI ? 2 : 1,
  workers: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://127.0.0.1:10935',
    headless: true,
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
    video: 'retain-on-failure',
  },
  webServer: [
    {
      command:
        'powershell -NoProfile -ExecutionPolicy Bypass -File ..\\e2e-start-backend.ps1',
      cwd: frontendDir,
      url: 'http://127.0.0.1:10934/health',
      reuseExistingServer: false,
      timeout: 120_000,
      stdout: 'pipe',
      stderr: 'pipe',
    },
    {
      command: 'npm run dev',
      cwd: frontendDir,
      url: 'http://127.0.0.1:10935',
      reuseExistingServer: false,
      timeout: 120_000,
      stdout: 'pipe',
      stderr: 'pipe',
    },
  ],
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
});
