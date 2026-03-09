import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const backendBaseUrl = process.env.BACKEND_API_BASE_URL;
  if (!backendBaseUrl) {
    return NextResponse.json(
      { detail: "Missing BACKEND_API_BASE_URL configuration." },
      { status: 500 }
    );
  }

  const response = await fetch(`${backendBaseUrl}/api/recipes`, { cache: "no-store" });
  const payload = await response.json();
  return NextResponse.json(payload, { status: response.status });
}
