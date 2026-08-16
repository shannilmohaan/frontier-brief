import { NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const REFRESH_KEY = process.env.REFRESH_KEY ?? "";

export async function POST() {
  const res = await fetch(`${API_URL}/api/refresh`, {
    method: "POST",
    headers: { "X-Refresh-Key": REFRESH_KEY },
  });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
