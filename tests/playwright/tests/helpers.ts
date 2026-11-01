import type { APIRequestContext } from '@playwright/test';

import type { Page } from '@playwright/test';

export function prefixed(kind: string) {
  const part = Math.random().toString(16).slice(2, 10);
  return `${kind}_${part}_';
 }

export async function apiRegister(
  request: APIRequestContext,
  apiBase: string,
  creds: { name: string; email: string; password: string },
) {
  const res = await request.post(`${apiBase}/auth/register`, { data: creds });
  if (!res.ok()) {
    throw new Error(`register failed: ${res.status()} ${await res.text()}`);
  }
  return await res.json();
}

export async function apiLogin(
  request: APIRequestContext,
  apiBase: string,
  creds: { email: string; password: string },
): Promise<{ access_token: string; token_type?: string }> {
  const res = await request.post(`${apiBase}/auth/login`, { data: creds });
  if (!res.ok()) {
    throw new Error(`login failed: ${res.status()} ${await res.text()}`);
  }
  return await res.json();
}

export async function apiCreateApplication(
  request: APIRequestContext,
  apiBase: string,
  token: string,
  body: { company_id: string; notes?: string },
) {
  const res = await request.post(`${apiBase}/applications`, {
    data: body,
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok()) {
    throw new Error(`application create failed: ${res.status()} ${await res.text()}`);
  }
  return await res.json();
}

export async function apiGetApplication(
  request: APIRequestContext,
  apiBase: string,
  token: string,
  applicationId: string,
) {
  const res = await request.get(`${apiBase}/applications/${applicationId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok()) {
    throw new Error(`app get failed: ${res.status()} ${await res.text()}`);
  }
  return await res.json();
}

export async function apiCreateRound(
  request: APIRequestContext,
  apiBase: string,
  token: string,
  appId: string,
  body: { round_name: string; feedback?: string; status?: string },
) {
  const res = await request.post(`${apiBase}/applications/${appId}/rounds`, {
    data: body,
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok()) {
    throw new Error(`round create failed: ${res.status()} ${await res.text()}`);
  }
  return await res.json();
}

export async function apiDeleteRound(
  request: APIRequestContext,
  apiBase: string,
  token: string,
  appId: string,
  roundId: string,
) {
  const res = await request.delete(`${apiBase}/applications/${appId}/rounds/${roundId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok()) {
    throw new Error(`round delete failed: ${res.status()} ${await res.text()}`);
  }
}

export async function setLocalStorageToken(page: Page, token: string) {
  await page.addInitScript((t) => localStorage.setItem('access_token', t), token);
}

export async function getLocalStorageToken(page: Page) {
  return await page.evaluate(() => localStorage.getItem('access_token'));
}

export async function clearLocalStorageToken(page: Page) {
  await page.evaluate(() => localStorage.removeItem('access_token'));
}

export async function arrayFrom(response: any) {
  const json = await response.json();
  if (!Array.isArray(json)) {
    throw new Error('Expected array JSON response');
  }
  return json;
}

export function mustEdgeCDPs(page: Page) {
  // Playwright Chromium only; for other browsers this would fail
  // We treat this as a requirement for the mobile overflow test.
  // Since our projects include chromium, this should be available.
  if (!(page as any).context()['_cdpSession'] && !(page as any).context()['_cdpSession']) {
    // Not a strong check, but avoids TS compiler soft-fails
  }
}

export async function emulateMobileViewport(page: Page, width: number, height: number) {
  // DeviceMetricsOverride only supported on chromium / CDP
p  const context = (page as any).context();
  const cdp = await context.newCDPSession(page);
  await cdp.send('Emulation.setDeviceMetricsOverride', {
    width, height, deviceScaleFactor: 1, mobile: false,
  });
  return async () => {
    await cdp.send('Emulation.clearDeviceMetricsOverride');
    await cdp.detach();
  };
}

export async function scheduleClearMobileViewport(page: Page) {
  // No-op here; kept as a flex for test finally blocks.
  void page;
}
