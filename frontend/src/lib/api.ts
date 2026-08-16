import type { DigestResponse, RefreshResponse } from "./types";

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

export async function fetchLatestDigest(domain?: string): Promise<DigestResponse> {
  const url = new URL(`${API_URL}/api/digest/latest`);
  if (domain) url.searchParams.set("domain", domain);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Digest fetch failed: ${res.status}`);
  return res.json() as Promise<DigestResponse>;
}

export async function triggerRefresh(): Promise<RefreshResponse> {
  const res = await fetch("/api/refresh", { method: "POST" });
  if (!res.ok) throw new Error(`Refresh failed: ${res.status}`);
  return res.json() as Promise<RefreshResponse>;
}

export async function pollRefreshStatus(jobId: string): Promise<RefreshResponse> {
  const res = await fetch(`${API_URL}/api/refresh/${jobId}`);
  if (!res.ok) throw new Error(`Status poll failed: ${res.status}`);
  return res.json() as Promise<RefreshResponse>;
}
