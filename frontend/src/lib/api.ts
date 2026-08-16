import type { DigestResponse, HistoryResponse, RefreshResponse } from "./types";

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

export async function fetchLatestDigest(domain?: string, cycleId?: string): Promise<DigestResponse> {
  const url = new URL(`${API_URL}/api/digest/latest`);
  if (domain) url.searchParams.set("domain", domain);
  if (cycleId) url.searchParams.set("cycle_id", cycleId);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Digest fetch failed: ${res.status}`);
  return res.json() as Promise<DigestResponse>;
}

export async function fetchHistory(): Promise<HistoryResponse> {
  const res = await fetch(`${API_URL}/api/digest/history`);
  if (!res.ok) throw new Error(`History fetch failed: ${res.status}`);
  return res.json() as Promise<HistoryResponse>;
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
