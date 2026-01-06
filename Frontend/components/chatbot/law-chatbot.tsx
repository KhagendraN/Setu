"use client"

import { useState, useRef, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Send, Scale, User, Download, Plus, MessageSquare, Trash2, Menu, X } from "lucide-react"
import { cn } from "@/lib/utils"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { useToast } from "@/hooks/use-toast"

interface SuggestedAction {
  action: string
  description: string
  letter_type: string
  prompt: string
}

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  suggested_action?: SuggestedAction
  metadata?: {
    summary?: string
    key_point?: string
    next_steps?: string
    sources?: any[]
    context_used?: boolean
    is_non_legal?: boolean
  }
}

interface Conversation {
  id: string
  title: string
  updated_at: string
  message_count: number
}

export function LawChatbot() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Namaste! I am your Nepali Law Assistant. How can I help you today?",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoadingConversations, setIsLoadingConversations] = useState(false)
  const [showLetterDialog, setShowLetterDialog] = useState(false)
  const [pendingAction, setPendingAction] = useState<SuggestedAction | null>(null)
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  const suggestedQuestions = [
    "What are my property rights?",
    "Labor law basics",
    "Consumer rights",
    "Women's rights in Nepal",
  ]

  // Load conversations on mount
  useEffect(() => {
    loadConversations()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Scroll to bottom whenever messages change
  useEffect(() => {
    const timer = setTimeout(() => {
      if (scrollAreaRef.current) {
        const scrollContainer = scrollAreaRef.current.querySelector("[data-radix-scroll-area-viewport]")
        if (scrollContainer) {
          scrollContainer.scrollTo({
            top: scrollContainer.scrollHeight,
            behavior: "smooth",
          })
        }
      }
    }, 100)
    return () => clearTimeout(timer)
  }, [messages, isTyping])

  const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token")
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    }
  }

  // Use public env var so frontend can target backend in different environments
  const BACKEND_URL = (process.env.NEXT_PUBLIC_BACKEND_URL as string) || "http://localhost:8000"

  const loadConversations = async () => {
    const token = localStorage.getItem("access_token")
    if (!token) return

    setIsLoadingConversations(true)
    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/chat-history/conversations`, {
        headers: getAuthHeaders(),
      })

      if (response.ok) {
        const data = await response.json()
        setConversations(data)
      }
    } catch (error) {
      console.error("Failed to load conversations:", error)
    } finally {
      setIsLoadingConversations(false)
    }
  }

  const loadConversation = async (convId: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/chat-history/conversations/${convId}`, {
        headers: getAuthHeaders(),
      })

      if (response.ok) {
        const data = await response.json()
        const loadedMessages: Message[] = data.messages.map((msg: any) => {
          let content = msg.content

          // If this is an assistant message with metadata, reconstruct the full formatted content
          if (msg.role === "assistant" && msg.metadata) {
            const meta = msg.metadata

            // Check if metadata has the structured fields
            if (meta.summary || meta.key_point || meta.next_steps) {
              // Format sources
              let sourcesText = ""
              if (meta.sources && meta.sources.length > 0) {
                const formattedSources = meta.sources
                  .filter((s: any) => s && (s.file || s.section))
                  .map((s: any, i: number) => {
                    let fileName = "Legal Document"
                    if (s.file) {
                      fileName = s.file
                        .replace(/_en\.pdf$/i, "")
                        .replace(/\.pdf$/i, "")
                        .replace(/_/g, " ")
                    }
                    const section = s.section || s.article_section || "General Reference"
                    return `   ${i + 1}. **${fileName}** (${section})`
                  })
                  .join("\n")

                if (formattedSources) {
                  sourcesText = `\n\n### 📚 Resources\n${formattedSources}`
                }
              }

              const contextBadge = meta.context_used ? "\n\n> 💡 *Used conversation context*" : ""

              // Reconstruct the full formatted content
              content = `### 📝 Summary\n${meta.summary || ""}

### 💬 Detailed Explanation
${msg.content}

### 🔑 Key Points
- ${meta.key_point || ""}

### 📋 Next Steps
${meta.next_steps || ""}${sourcesText}${contextBadge}`.trim()
            }
          }

          return {
            id: msg.id,
            role: msg.role,
            content: content,
            timestamp: new Date(msg.timestamp),
            metadata: msg.metadata,
          }
        })
        setMessages(loadedMessages)
        setConversationId(convId)
        // Close mobile sidebar after loading conversation
        setIsMobileSidebarOpen(false)
      }
    } catch (error) {
      console.error("Failed to load conversation:", error)
      toast({
        title: "Error",
        description: "Failed to load conversation",
        variant: "destructive",
      })
    }
  }

  const createNewConversation = async (firstMessage: string) => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      toast({
        title: "Authentication Required",
        description: "Please login to save chat history",
        variant: "destructive",
      })
      return null
    }

    try {
      const title = firstMessage.slice(0, 50) + (firstMessage.length > 50 ? "..." : "")
      const response = await fetch(`${BACKEND_URL}/api/v1/chat-history/conversations`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ title }),
      })

      if (response.ok) {
        const data = await response.json()
        setConversationId(data.id)
        loadConversations() // Refresh conversation list
        return data.id
      }
    } catch (error) {
      console.error("Failed to create conversation:", error)
    }
    return null
  }

  const deleteConversation = async (convId: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/chat-history/conversations/${convId}`, {
        method: "DELETE",
        headers: getAuthHeaders(),
      })

      if (response.ok) {
        toast({
          title: "Success",
          description: "Conversation deleted successfully",
        })

        // If deleted conversation was active, start new chat
        if (conversationId === convId) {
          startNewChat()
        }

        // Refresh conversation list
        loadConversations()
      } else {
        throw new Error("Failed to delete")
      }
    } catch (error) {
      console.error("Failed to delete conversation:", error)
      toast({
        title: "Error",
        description: "Failed to delete conversation",
        variant: "destructive",
      })
    }
  }


  const confirmLetterGeneration = () => {
    if (!pendingAction) return

    // Store the description in localStorage to pass to letter generator page
    localStorage.setItem("letter_generation_prompt", pendingAction.description)
    localStorage.setItem("letter_type", pendingAction.letter_type)

    // Close dialog
    setShowLetterDialog(false)
    setPendingAction(null)

    // Redirect to letter generator page
    router.push("/letter-generator")

    toast({
      title: "Redirecting...",
      description: "Taking you to the letter generation section",
    })
  }

  const cancelLetterGeneration = () => {
    setShowLetterDialog(false)
    setPendingAction(null)
  }

  const startNewChat = () => {
    setMessages([
      {
        id: "1",
        role: "assistant",
        content: "Namaste! I am your Nepali Law Assistant. How can I help you today?",
        timestamp: new Date(),
      },
    ])
    setConversationId(null)
    // Close mobile sidebar after starting new chat
    setIsMobileSidebarOpen(false)
  }

  const handleSend = async (content: string) => {
    if (!content.trim()) return

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMsg])
    setInput("")
    setIsTyping(true)

    try {
      // Create conversation if this is the first message
      let currentConvId = conversationId
      if (!currentConvId && localStorage.getItem("access_token")) {
        currentConvId = await createNewConversation(content)
      }

      const token = localStorage.getItem("access_token")
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) {
        headers["Authorization"] = `Bearer ${token}`
      }

      const response = await fetch("/api/Legal_Chat", {
        method: "POST",
        headers,
        body: JSON.stringify({
          messages: [...messages, { role: "user", content }],
          type: "legal",
          conversation_id: currentConvId,
        }),
      })

      const data = await response.json()

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.content || data.error || "I am having trouble connecting to my legal database.",
        timestamp: new Date(),
        suggested_action: data.suggested_action || undefined,
      }
      setMessages((prev) => [...prev, assistantMsg])

      // If there's a suggested action, show the dialog
      if (data.suggested_action) {
        setPendingAction(data.suggested_action)
        setShowLetterDialog(true)
      }

      // Note: Messages are now automatically saved by the backend /chat endpoint
    } catch (error) {
      console.error("[Legal Chat Error]:", error)
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I encountered an error while processing your request. Please ensure the backend server is running.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsTyping(false)
    }
  }

  const exportChat = () => {
    const chatContent = messages
      .map((m) => `[${m.role.toUpperCase()} - ${m.timestamp.toLocaleTimeString()}]: ${m.content}`)
      .join("\n\n")
    const blob = new Blob([chatContent], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "legal-chat-history.txt"
    a.click()
  }

  return (
    <div className="w-full max-w-[1600px] mx-auto">
      <div className="flex h-[calc(100vh-10rem)] gap-4 relative">
        {/* Mobile Sidebar Overlay */}
        {isMobileSidebarOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={() => setIsMobileSidebarOpen(false)}
          />
        )}

        {/* Sidebar - Chat History */}
        <div
          className={cn(
            "w-64 flex-col gap-4 border-r pr-4 bg-background z-50",
            "lg:flex lg:relative lg:translate-x-0",
            "fixed left-0 top-0 h-full transition-transform duration-300 ease-in-out p-4 lg:p-0",
            isMobileSidebarOpen ? "flex translate-x-0" : "hidden lg:flex -translate-x-full lg:translate-x-0"
          )}
        >
        {/* Close button for mobile */}
        <div className="flex items-center justify-between lg:hidden mb-4">
          <h3 className="font-semibold">Chat History</h3>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsMobileSidebarOpen(false)}
            className="h-8 w-8"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <Button className="w-full justify-start gap-2 bg-primary" onClick={startNewChat}>
          <Plus className="h-4 w-4" /> New Conversation
        </Button>
        <ScrollArea className="flex-1">
          <div className="space-y-2">
            <p className="text-xs font-semibold text-muted-foreground px-2 uppercase tracking-wider">Recent Chats</p>
            {isLoadingConversations ? (
              <p className="text-xs text-muted-foreground px-2">Loading...</p>
            ) : conversations.length > 0 ? (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={cn(
                    "w-full rounded-lg transition-colors border flex items-center gap-2",
                    conversationId === conv.id
                      ? "bg-muted border-border"
                      : "border-transparent hover:border-border hover:bg-muted/50"
                  )}
                >
                  <button
                    className="p-2 rounded-md text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all shrink-0"
                    onClick={(e) => {
                      e.stopPropagation()
                      if (confirm("Delete this conversation? This cannot be undone.")) {
                        deleteConversation(conv.id)
                      }
                    }}
                    title="Delete conversation"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                  <button
                    className="flex-1 text-left p-3 pr-2"
                    onClick={() => loadConversation(conv.id)}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <MessageSquare className="h-4 w-4 text-primary shrink-0" />
                      <span className="text-sm font-medium truncate">{conv.title}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">
                        {new Date(conv.updated_at).toLocaleDateString()}
                      </span>
                      <span className="text-xs text-muted-foreground">{conv.message_count} msgs</span>
                    </div>
                  </button>
                </div>
              ))
            ) : (
              <p className="text-xs text-muted-foreground px-2">No conversations yet</p>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Main Chat Interface */}
      <Card className="flex-1 flex flex-col shadow-lg border-primary/10 overflow-hidden bg-card/50 backdrop-blur-sm">
        <CardHeader className="border-b py-4 flex flex-row items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setIsMobileSidebarOpen(true)}
              title="Open chat history"
            >
              <Menu className="h-5 w-5" />
            </Button>

            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              <Scale className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-lg">Nepali Law Assistant</CardTitle>
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-success animate-pulse" />
                <span className="text-xs text-muted-foreground">AI Powered & Ready</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={exportChat} title="Export conversation">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </CardHeader>

        <CardContent className="flex-1 p-0 overflow-hidden">
          <ScrollArea ref={scrollAreaRef} className="h-full">
            <div className="space-y-6 max-w-4xl mx-auto p-4 md:p-6">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={cn(
                    "flex gap-3 animate-in fade-in slide-in-from-bottom-2",
                    m.role === "user" ? "flex-row-reverse" : "flex-row",
                  )}
                >
                  <Avatar className={cn("h-8 w-8 border", m.role === "assistant" ? "bg-primary/10" : "bg-muted")}>
                    <AvatarFallback className={m.role === "assistant" ? "text-primary" : "text-muted-foreground"}>
                      {m.role === "assistant" ? <Scale className="h-4 w-4" /> : <User className="h-4 w-4" />}
                    </AvatarFallback>
                  </Avatar>
                  <div
                    className={cn("flex flex-col gap-1 max-w-[80%]", m.role === "user" ? "items-end" : "items-start")}
                  >
                    <div
                      className={cn(
                        "rounded-2xl px-4 py-3 text-sm shadow-sm",
                        m.role === "user"
                          ? "bg-primary text-primary-foreground rounded-tr-none"
                          : "bg-muted/80 backdrop-blur-sm rounded-tl-none border",
                      )}
                    >
                      {m.role === "assistant" ? (
                        <div className="prose prose-sm dark:prose-invert max-w-none overflow-wrap-anywhere wrap-break-word">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              p: ({ children }) => <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>,
                              strong: ({ children }) => <strong className="font-semibold text-foreground">{children}</strong>,
                              ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
                              ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
                              li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                              a: ({ href, children }) => (
                                <a
                                  href={href}
                                  className="text-primary hover:underline underline-offset-2"
                                  target="_blank"
                                  rel="noopener noreferrer"
                                >
                                  {children}
                                </a>
                              ),
                              h1: ({ children }) => <h1 className="text-lg font-bold mb-2 mt-4 first:mt-0">{children}</h1>,
                              h2: ({ children }) => <h2 className="text-base font-bold mb-2 mt-3 first:mt-0">{children}</h2>,
                              h3: ({ children }) => <h3 className="text-sm font-semibold mb-2 mt-2 first:mt-0">{children}</h3>,
                              code: ({ children }) => (
                                <code className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>
                              ),
                              pre: ({ children }) => (
                                <pre className="bg-muted p-3 rounded-lg overflow-x-auto mb-3 text-xs">{children}</pre>
                              ),
                            }}
                          >
                            {m.content}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        <div className="wrap-break-word">{m.content}</div>
                      )}
                    </div>
                    <span className="text-[10px] text-muted-foreground px-1">
                      {m.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="flex gap-3 animate-in fade-in">
                  <Avatar className="h-8 w-8 border bg-primary/10">
                    <AvatarFallback className="text-primary">
                      <Scale className="h-4 w-4" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="bg-muted/80 border rounded-2xl rounded-tl-none px-4 py-3 flex gap-1">
                    <span
                      className="h-1.5 w-1.5 rounded-full bg-primary/40 animate-bounce"
                      style={{ animationDelay: "0ms" }}
                    />
                    <span
                      className="h-1.5 w-1.5 rounded-full bg-primary/40 animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    />
                    <span
                      className="h-1.5 w-1.5 rounded-full bg-primary/40 animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    />
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>

        <CardFooter className="p-4 border-t bg-muted/20 backdrop-blur-md">
          <div className="w-full space-y-4 max-w-4xl mx-auto">
            {messages.length < 3 && (
              <div className="flex flex-wrap gap-2">
                {suggestedQuestions.map((q) => (
                  <Badge
                    key={q}
                    variant="outline"
                    className="cursor-pointer hover:bg-primary/10 hover:border-primary/30 transition-colors px-3 py-1 bg-background"
                    onClick={() => handleSend(q)}
                  >
                    {q}
                  </Badge>
                ))}
              </div>
            )}
            <div className="flex gap-2 relative">
              <Input
                placeholder="Type your legal question here..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend(input)}
                className="pr-12 h-12 bg-background border-primary/20 focus-visible:ring-primary shadow-inner"
              />
              <Button
                size="icon"
                onClick={() => handleSend(input)}
                className="absolute right-1 top-1 h-10 w-10 bg-primary hover:bg-primary/90 transition-transform active:scale-95"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-[10px] text-center text-muted-foreground">
              AI responses are for information only and not professional legal advice.
            </p>
          </div>
        </CardFooter>
      </Card>
      </div>

      {/* Letter Generation Confirmation Card */}
      {showLetterDialog && pendingAction && (
        <Card className="fixed bottom-6 right-6 z-50 shadow-2xl border-primary/20 w-[90vw] sm:w-96 animate-in slide-in-from-bottom-4 fade-in duration-300">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Generate Letter</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Would you like me to help you draft a {pendingAction.letter_type}?
            </p>
          </CardHeader>
          <CardFooter className="gap-2 pt-3">
            <Button variant="outline" onClick={cancelLetterGeneration} className="flex-1">
              No, thanks
            </Button>
            <Button onClick={confirmLetterGeneration} className="flex-1">
              Yes, generate it
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  )
}
