import { getAnalyzedDocuments, getGeneratedLetters } from "./document-cache"
import { FileText, MessageSquare, ShieldCheck } from "lucide-react"

export interface Activity {
  id: string
  type: "chat" | "document" | "letter"
  title: string
  time: string
  timestamp: Date
  icon: any
  color: string
  conversationId?: string
  documentId?: string
  letterId?: string
}

/**
 * Format relative time from date string or Date object
 */
export function formatRelativeTime(date: string | Date): string {
  const dateObj = typeof date === "string" ? new Date(date) : date
  const now = new Date()
  const diffMs = now.getTime() - dateObj.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 60) {
    return diffMins <= 1 ? "Just now" : `${diffMins} minutes ago`
  } else if (diffHours < 24) {
    return diffHours === 1 ? "1 hour ago" : `${diffHours} hours ago`
  } else if (diffDays === 1) {
    return "Yesterday"
  } else if (diffDays < 7) {
    return `${diffDays} days ago`
  } else {
    return dateObj.toLocaleDateString()
  }
}

/**
 * Get all activities for a user (combines chat, documents, and letters)
 */
export async function getAllActivities(userId: string, token?: string): Promise<Activity[]> {
  const activities: Activity[] = []

  // 1. Get chat conversations from backend
  if (token) {
    try {
      const BACKEND_URL = (process.env.NEXT_PUBLIC_BACKEND_URL as string) || "http://localhost:8000"
      const response = await fetch(`${BACKEND_URL}/api/v1/chat-history/conversations`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const conversations = await response.json()
        conversations.forEach((conv: any) => {
          activities.push({
            id: `chat_${conv.id}`,
            type: "chat",
            title: conv.title,
            time: formatRelativeTime(conv.updated_at),
            timestamp: new Date(conv.updated_at),
            icon: MessageSquare,
            color: "text-primary bg-primary/10",
            conversationId: conv.id,
          })
        })
      }
    } catch (error) {
      console.error("Failed to fetch chat conversations:", error)
    }
  }

  // 2. Get analyzed documents from cache
  const analyzedDocs = getAnalyzedDocuments(userId)
  analyzedDocs.forEach((doc) => {
    activities.push({
      id: doc.id,
      type: "document",
      title: `Analyzed: ${doc.filename}`,
      time: formatRelativeTime(doc.analyzedAt),
      timestamp: new Date(doc.analyzedAt),
      icon: ShieldCheck,
      color: "text-accent bg-accent/10",
      documentId: doc.id,
    })
  })

  // 3. Get generated letters from cache
  const generatedLetters = getGeneratedLetters(userId)
  generatedLetters.forEach((letter) => {
    activities.push({
      id: letter.id,
      type: "letter",
      title: `Generated: ${letter.templateName.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}`,
      time: formatRelativeTime(letter.generatedAt),
      timestamp: new Date(letter.generatedAt),
      icon: FileText,
      color: "text-success bg-success/10",
      letterId: letter.id,
    })
  })

  // Sort by timestamp (most recent first)
  activities.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())

  return activities
}
