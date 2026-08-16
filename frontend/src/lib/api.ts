// Placeholder — full implementation in Phase 1c/1d

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const REFRESH_KEY = process.env.NEXT_PUBLIC_REFRESH_KEY ?? "";

import type { DigestResponse, RefreshResponse } from "./types";

export async function fetchLatestDigest(domain?: string): Promise<DigestResponse> {
  const url = new URL(`${API_URL}/api/digest/latest`);
  if (domain) url.searchParams.set("domain", domain);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Digest fetch failed: ${res.status}`);
  return res.json() as Promise<DigestResponse>;
}

export async function triggerRefresh(): Promise<RefreshResponse> {
  const res = await fetch(`${API_URL}/api/refresh`, {
    method: "POST",
    headers: { "X-Refresh-Key": REFRESH_KEY },
  });
  if (!res.ok) throw new Error(`Refresh failed: ${res.status}`);
  return res.json() as Promise<RefreshResponse>;
}

export async function pollRefreshStatus(jobId: string): Promise<RefreshResponse> {
  const res = await fetch(`${API_URL}/api/refresh/${jobId}`);
  if (!res.ok) throw new Error(`Status poll failed: ${res.status}`);
  return res.json() as Promise<RefreshResponse>;
}
