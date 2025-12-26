import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3001',
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: [
    {
      command: 'cd ../backend && venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000',
      port: 8000,
      timeout: 300 * 1000,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'cd ../backend && SKIP_DB_CHECK=1 npm run dev',
      port: 3000,
      timeout: 300 * 1000,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'npm run dev',
      port: 3001,
      timeout: 300 * 1000,
      reuseExistingServer: !process.env.CI,
    },
  ],
});
