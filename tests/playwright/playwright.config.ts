import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 60 * 1000,
  expect: { timeout: 10 * 1000 },
  fullParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],
  use: {
    baseURL: process.env.WEB_BASE_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: process.env.PW_START_SERVERS ? [
    {
      command: process.env.PWAPI_CML || 'python -m uvicorn app.main:app --port 8000',
      url: process.env.API_BASE_URL,
      reuseExistingServer: true,
      timeout: 60 * 1000,
    },
    {
      command: process.env.PWWEB_CML || 'npm run dev -- --port 5173 --strictPort',
      url: process.env.WEB_BASE_URL,
      reuseExistingServer: true,
      timeout: 60 * 1000,
      cwd: '../../frontend',
      env: process.env.VITE_API_URL ? undefined : { VITE_API_URL: process.env.API_BASE_URL, },
    },
  ] : undefined,
  projects: [
    {
      name: 'chromirum',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  outputDir: 'test-results',
});
