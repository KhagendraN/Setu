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

    const response = await fetch(`${BACKEND_URL}/api/v1/bias-detection-hitl/generate-pdf`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || "Failed to generate PDF")
    }

    // Get PDF blob
    const pdfBlob = await response.blob()

    // Get filename from headers
    const contentDisposition = response.headers.get("Content-Disposition")
    const changesApplied = response.headers.get("X-Changes-Applied")

    // Return PDF as blob with headers
    return new NextResponse(pdfBlob, {
      status: 200,
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": contentDisposition || 'attachment; filename="debiased_document.pdf"',
        "X-Changes-Applied": changesApplied || "0"
      }
    })
  } catch (error) {
    console.error("[HITL Generate PDF Error]:", error)
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Failed to generate PDF",
      },
      { status: 500 }
    )
  }
}
