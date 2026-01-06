import { type NextRequest, NextResponse } from "next/server"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

export async function POST(req: NextRequest) {
  try {
    const { messages, type, conversation_id } = await req.json()

    if (type !== "legal") {
      return NextResponse.json({ content: "Standard AI response for non-legal queries." })
    }

    const lastMessage = messages[messages.length - 1].content

    // Get Authorization header from incoming request
    const authHeader = req.headers.get("authorization")
    const headers: Record<string, string> = { "Content-Type": "application/json" }
    if (authHeader) {
      headers["Authorization"] = authHeader
    }

    // Use the new context-aware chat endpoint
    const response = await fetch(`${BACKEND_URL}/api/v1/law-explanation/chat`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        query: lastMessage,
        conversation_id: conversation_id || null,
      }),
    })

    if (!response.ok) {
      throw new Error(`Backend API returned ${response.status}`)
    }

    const data = await response.json()

    // Check if this is a non-legal query (greeting, thanks, etc.)
    if (data.is_non_legal) {
      return NextResponse.json({ content: data.explanation })
    }

    // Format sources properly from backend response
    let sourcesText = ""
    console.log("[Legal Chat] Sources from backend:", data.sources)

    if (data.sources && data.sources.length > 0) {
      const formattedSources = data.sources
        .filter((s: any) => s && (s.file || s.section)) // Only include sources with file or section
        .map((s: any, i: number) => {
          // Extract and clean filename
          let fileName = "Legal Document"
          if (s.file) {
            fileName = s.file
              .replace(/_en\.pdf$/i, "") // Remove _en.pdf extension
              .replace(/\.pdf$/i, "") // Remove .pdf extension
              .replace(/_/g, " ") // Replace underscores with spaces
          }

          // Format: **filename** (section)
          const section = s.section || s.article_section || "General Reference"
          return `   ${i + 1}. **${fileName}** (${section})`
        })
        .join("\n")

      if (formattedSources) {
        sourcesText = `\n\n### 📚 Resources\n${formattedSources}`
      }
    }

    // Add context indicator if context was used
    const contextBadge = data.context_used ? "\n\n> 💡 *Used conversation context*" : ""

    // Return the data as-is since backend already returns markdown format
    // Format it nicely for the frontend with clear sections
    const formattedContent = `### 📝 Summary\n${data.summary}

### 💬 Detailed Explanation\n${data.explanation}

### 🔑 Key Points
- ${data.key_point}

### 📋 Next Steps
${data.next_steps}${sourcesText}${contextBadge}`.trim()

    return NextResponse.json({
      content: formattedContent,
      suggested_action: data.suggested_action || null
    })
  } catch (error) {
    console.error("[Legal Chat API Error]:", error)
    return NextResponse.json(
      { error: "Failed to fetch response from legal AI backend. Please ensure the backend server is running." },
      { status: 500 }
    )
  }
}
