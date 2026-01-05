import { type NextRequest, NextResponse } from "next/server"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

export async function POST(req: NextRequest) {
  try {
    const authHeader = req.headers.get("authorization")
    const headers: Record<string, string> = {
      "Content-Type": "application/json"
    }
    if (authHeader) {
      headers["Authorization"] = authHeader
    }

    const body = await req.json()

    const response = await fetch(`${BACKEND_URL}/api/v1/bias-detection-hitl/approve-suggestion`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || "Failed to approve/reject suggestion")
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("[HITL Approve Error]:", error)
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Failed to process approval",
      },
      { status: 500 }
    )
  }
}
