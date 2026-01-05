"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Send, FileText, User, Download, Loader2, CheckCircle2, Printer } from "lucide-react"
import { cn } from "@/lib/utils"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import html2canvas from "html2canvas"

type MessageRole = "user" | "assistant" | "system"

interface Message {
  id: string
  role: MessageRole
  content: string
  timestamp: Date
}

type ConversationState = "initial" | "template-search" | "collecting-placeholders" | "generating" | "completed"

interface PlaceholderData {
  [key: string]: string
}

export function LetterGenerator() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Namaste! I am your Letter Generation Assistant. What kind of letter would you like to generate? (e.g., citizenship application, leave application, complaint letter, etc.)",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [conversationState, setConversationState] = useState<ConversationState>("initial")
  const [templateName, setTemplateName] = useState<string | null>(null)
  const [placeholders, setPlaceholders] = useState<string[]>([])
  const [placeholderData, setPlaceholderData] = useState<PlaceholderData>({})
  const [currentPlaceholderIndex, setCurrentPlaceholderIndex] = useState(0)
  const [generatedLetter, setGeneratedLetter] = useState<string | null>(null)
  const [generatedLetterImage, setGeneratedLetterImage] = useState<string | null>(null)
  const [isGeneratingImage, setIsGeneratingImage] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const letterTemplateRef = useRef<HTMLDivElement>(null)

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

  const addMessage = (role: MessageRole, content: string) => {
    const newMessage: Message = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`, // Unique ID
      role,
      content,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, newMessage])
  }

  const handleSend = async (content: string) => {
    if (!content.trim()) return

    addMessage("user", content)
    setInput("")
    setIsTyping(true)

    try {
      if (conversationState === "initial" || conversationState === "template-search") {
        // Step 1: Search for template
        await searchTemplate(content)
      } else if (conversationState === "collecting-placeholders") {
        // Step 2: Collect placeholder values
        await collectPlaceholder(content)
      }
    } catch (error) {
      console.error("[Letter Generation Error]:", error)
      addMessage("assistant", "I encountered an error. Please try again or rephrase your request.")
    } finally {
      setIsTyping(false)
    }
  }

  const searchTemplate = async (query: string) => {
    try {
      const response = await fetch("/api/letter-generation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "search-template",
          data: { query },
        }),
      })

      const data = await response.json()

      if (data.success && data.templateName) {
        setTemplateName(data.templateName)
        addMessage(
          "assistant",
          `I found a template: **${data.templateName}**. Let me get the required information for this letter.`
        )

        // Get template details
        await getTemplateDetails(data.templateName)
      } else {
        addMessage(
          "assistant",
          "I couldn't find a suitable template for your request. Could you please provide more details about the type of letter you need?"
        )
        setConversationState("template-search")
      }
    } catch (error) {
      throw error
    }
  }

  const getTemplateDetails = async (templateName: string) => {
    try {
      const response = await fetch("/api/letter-generation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "get-template-details",
          data: { templateName },
        }),
      })

      const data = await response.json()

      if (data.success && data.placeholders) {
        setPlaceholders(data.placeholders)
        setCurrentPlaceholderIndex(0)
        setConversationState("collecting-placeholders")

        if (data.placeholders.length > 0) {
          const firstPlaceholder = data.placeholders[0]
          addMessage(
            "assistant",
            `Great! I need some information from you. Please provide the **${formatPlaceholder(firstPlaceholder)}**:`
          )
        } else {
          // No placeholders needed, generate directly
          await fillTemplate(templateName, {})
        }
      } else {
        addMessage("assistant", "I encountered an issue retrieving the template details. Please try again.")
      }
    } catch (error) {
      throw error
    }
  }

  const collectPlaceholder = async (value: string) => {
    const currentPlaceholder = placeholders[currentPlaceholderIndex]
    const newPlaceholderData = {
      ...placeholderData,
      [currentPlaceholder]: value,
    }
    setPlaceholderData(newPlaceholderData)

    const nextIndex = currentPlaceholderIndex + 1

    if (nextIndex < placeholders.length) {
      // Ask for next placeholder
      setCurrentPlaceholderIndex(nextIndex)
      const nextPlaceholder = placeholders[nextIndex]
      addMessage("assistant", `Thank you! Now, please provide the **${formatPlaceholder(nextPlaceholder)}**:`)
    } else {
      // All placeholders collected, generate letter
      setConversationState("generating")
      addMessage("assistant", "Perfect! I have all the information I need. Generating your letter...")
      await fillTemplate(templateName!, newPlaceholderData)
    }
  }

  const fillTemplate = async (templateName: string, placeholders: PlaceholderData) => {
    try {
      const response = await fetch("/api/letter-generation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "fill-template",
          data: { templateName, placeholders },
        }),
      })

      const data = await response.json()

      if (data.success && data.letter) {
        setGeneratedLetter(data.letter)
        setConversationState("completed")
        addMessage(
          "assistant",
          `✅ Your letter has been generated successfully! You can download it using the button below.\n\n**Preview:**\n\n${data.letter}`
        )
      } else {
        addMessage("assistant", "Failed to generate the letter. Please try again.")
        setConversationState("initial")
      }
    } catch (error) {
      throw error
    }
  }

  const formatPlaceholder = (placeholder: string): string => {
    return placeholder
      .replace(/{|}/g, "")
      .replace(/_/g, " ")
      .replace(/\b\w/g, (char) => char.toUpperCase())
  }

  const generateLetterImage = async () => {
    if (!letterTemplateRef.current) {
      console.log("Letter template ref not available")
      return
    }

    setIsGeneratingImage(true)
    try {
      console.log("Starting image generation...")

      // Create an iframe to completely isolate rendering context
      const iframe = document.createElement('iframe')
      iframe.style.cssText = 'position: fixed; left: -10000px; top: 0; width: 794px; height: 1123px; border: none;'
      document.body.appendChild(iframe)

      const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document
      if (!iframeDoc) throw new Error('Unable to access iframe document')

      // Write clean HTML with only our content
      iframeDoc.open()
      iframeDoc.write(`
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600;700&display=swap" rel="stylesheet">
            <style>
              * { margin: 10; padding: 10; box-sizing: border-box; }
              body { background: white; margin: 0; padding: 0; }
            </style>
          </head>
          <body>${letterTemplateRef.current.innerHTML}</body>
        </html>
      `)
      iframeDoc.close()

      // Wait for fonts to load
      await new Promise(resolve => setTimeout(resolve, 500))

      const canvas = await html2canvas(iframeDoc.body, {
        scale: 2,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff',
        logging: false,
        width: 794,
        height: 1123,
      })

      // Clean up
      document.body.removeChild(iframe)

      console.log("Canvas created, converting to data URL...")
      const dataUrl = canvas.toDataURL("image/png", 1.0)
      console.log("Image generated successfully")
      setGeneratedLetterImage(dataUrl)
      setIsGeneratingImage(false)
    } catch (error) {
      console.error("Image generation failed:", error)
      setIsGeneratingImage(false)
      addMessage("assistant", "Failed to generate letter image. You can still download the text version.")
    }
  }

  useEffect(() => {
    if (generatedLetter && conversationState === "completed") {
      // Generate image after a short delay to ensure DOM is rendered
      setTimeout(() => {
        generateLetterImage()
      }, 500)
    }
  }, [generatedLetter, conversationState])

  const downloadLetterImage = () => {
    if (!generatedLetterImage) {
      console.log("No image available to download")
      return
    }

    try {
      console.log("Starting download...")
      const link = document.createElement("a")
      link.href = generatedLetterImage
      link.download = `${templateName || "letter"}_${Date.now()}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      console.log("Download initiated successfully")
    } catch (error) {
      console.error("Download failed:", error)
      addMessage("assistant", "Download failed. Please try the Print option or download as text.")
    }
  }

  const downloadLetterText = () => {
    if (!generatedLetter) return

    const blob = new Blob([generatedLetter], { type: "text/plain;charset=utf-8" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `${templateName || "letter"}_${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  const printLetter = () => {
    if (!generatedLetterImage) return

    const printWindow = window.open("", "", "width=800,height=600")
    if (!printWindow) return

    printWindow.document.write(`
      <html>
        <head>
          <title>Print Letter</title>
          <style>
            @page { size: A4; margin: 0; }
            body { margin: 10; padding: 10; }
            img { width: 80%; height: auto; display: block; }
          </style>
        </head>
        <body>
          <img src="${generatedLetterImage}" onload="window.print(); window.close();" />
        </body>
      </html>
    `)
    printWindow.document.close()
  }

  const startNew = () => {
    setConversationState("initial")
    setTemplateName(null)
    setPlaceholders([])
    setPlaceholderData({})
    setCurrentPlaceholderIndex(0)
    setGeneratedLetter(null)
    setGeneratedLetterImage(null)
    setMessages([
      {
        id: Date.now().toString(),
        role: "assistant",
        content:
          "Let's generate another letter! What kind of letter would you like to create?",
        timestamp: new Date(),
      },
    ])
  }

  return (
    <div className="w-full max-w-[1600px] mx-auto">
      <div className="flex h-[calc(100vh-10rem)] gap-4">
        {/* Main Chat Interface */}
        <Card className="flex-1 flex flex-col shadow-lg border-primary/10 overflow-hidden bg-card/50 backdrop-blur-sm">
        <CardHeader className="border-b py-4 flex flex-row items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-lg">Letter Generation Assistant</CardTitle>
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-success animate-pulse" />
                <span className="text-xs text-muted-foreground">AI Powered & Ready</span>
              </div>
            </div>
          </div>
          {conversationState === "completed" && (
            <div className="flex gap-2">
              <Button
                variant="default"
                size="sm"
                onClick={downloadLetterImage}
                disabled={!generatedLetterImage || isGeneratingImage}
              >
                <Download className="h-4 w-4 mr-2" />
                {isGeneratingImage ? "Generating..." : "Download Image"}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={printLetter}
                disabled={!generatedLetterImage || isGeneratingImage}
              >
                <Printer className="h-4 w-4 mr-2" />
                Print
              </Button>
              <Button variant="outline" size="sm" onClick={downloadLetterText}>
                <FileText className="h-4 w-4 mr-2" />
                Download Text
              </Button>
              <Button variant="secondary" size="sm" onClick={startNew}>
                <FileText className="h-4 w-4 mr-2" />
                New Letter
              </Button>
            </div>
          )}
        </CardHeader>

        <CardContent className="flex-1 p-0 overflow-hidden">
          <ScrollArea ref={scrollAreaRef} className="h-full">
            <div className="space-y-6 max-w-4xl mx-auto p-4 md:p-6">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={cn(
                    "flex gap-3 animate-in fade-in slide-in-from-bottom-2",
                    m.role === "user" ? "flex-row-reverse" : "flex-row"
                  )}
                >
                  <Avatar className={cn("h-8 w-8 border", m.role === "assistant" ? "bg-primary/10" : "bg-muted")}>
                    <AvatarFallback className={m.role === "assistant" ? "text-primary" : "text-muted-foreground"}>
                      {m.role === "assistant" ? <FileText className="h-4 w-4" /> : <User className="h-4 w-4" />}
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
                          : "bg-muted/80 backdrop-blur-sm rounded-tl-none border"
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
                              code: ({ children }) => (
                                <code className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>
                              ),
                              pre: ({ children }) => (
                                <pre className="bg-muted p-3 rounded-lg overflow-x-auto mb-3 text-xs whitespace-pre-wrap">
                                  {children}
                                </pre>
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
                      <FileText className="h-4 w-4" />
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

          {/* Preview of generated letter image */}
          {conversationState === "completed" && (
            <div className="p-4 border-t bg-muted/10">
              <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-sm font-semibold">Generated Letter Preview (Nepali Format):</h3>
                  {!generatedLetterImage && !isGeneratingImage && (
                    <Button size="sm" variant="outline" onClick={generateLetterImage}>
                      Generate Image
                    </Button>
                  )}
                  {isGeneratingImage && (
                    <span className="text-xs text-muted-foreground flex items-center gap-2">
                      <Loader2 className="h-3 w-3 animate-spin" />
                      Generating image...
                    </span>
                  )}
                </div>
                {generatedLetterImage ? (
                  <div className="border rounded-lg overflow-hidden shadow-lg bg-white">
                    <img src={generatedLetterImage} alt="Nepali Letter" className="w-full" />
                  </div>
                ) : (
                  <div className="border rounded-lg p-8 text-center bg-muted/50">
                    <p className="text-sm text-muted-foreground">
                      Click "Generate Image" to create the Nepali format version
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>

        <CardFooter className="p-4 border-t bg-muted/20 backdrop-blur-md">
          <div className="w-full space-y-4 max-w-4xl mx-auto">
            {conversationState !== "completed" && (
              <div className="flex gap-2 relative">
                <Input
                  placeholder={
                    conversationState === "collecting-placeholders"
                      ? `Enter ${formatPlaceholder(placeholders[currentPlaceholderIndex] || "")}...`
                      : "Describe the letter you need..."
                  }
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend(input)}
                  className="pr-12 h-12 bg-background border-primary/20 focus-visible:ring-primary shadow-inner"
                  disabled={isTyping}
                />
                <Button
                  size="icon"
                  onClick={() => handleSend(input)}
                  className="absolute right-1 top-1 h-10 w-10 bg-primary hover:bg-primary/90 transition-transform active:scale-95"
                  disabled={isTyping || !input.trim()}
                >
                  {isTyping ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                </Button>
              </div>
            )}
            <p className="text-[10px] text-center text-muted-foreground">
              AI-generated letters should be reviewed before official use.
            </p>
          </div>
        </CardFooter>
      </Card>
      </div>

      {/* Hidden Nepali Paper Template for Image Generation */}
      {generatedLetter && (
        <div
          ref={letterTemplateRef}
          style={{
            position: "fixed",
            left: "-10000px",
            top: "90",
            width: "794px", // A4 width at 96 DPI
            minHeight: "1123px", // A4 height at 96 DPI
            backgroundColor: "rgb(255, 255, 255)",
            fontFamily: '"Noto Sans Devanagari", "Kalimati", Arial, sans-serif',
            fontSize: "14pt",
            lineHeight: "1.8",
            color: "rgb(0, 0, 0)",
            padding: "80px 80px",
            boxSizing: "border-box",
            visibility: "hidden",
            pointerEvents: "none",
            border: "none",
            margin: "10",
            isolation: "isolate", // Isolate from parent styles
          }}
        >
          {/* Reference Number (Date removed) */}
          <div
            style={{
              marginBottom: "24px",
              fontSize: "11pt",
              fontWeight: "600",
              color: "rgb(0, 0, 0)",
            }}
          >
            <div style={{marginLeft:"40px",marginTop:"50px"}}>चि. नं.: {placeholderData.reference_no || placeholderData.ref_no || "............."}</div>
          </div>

          {/* Recipient Address */}
          {(placeholderData.recipient_name || placeholderData.receiver_name) && (
            <div style={{ marginBottom: "24px", fontSize: "12pt", color: "rgb(0, 0, 0)",marginRight:"30px", }}>
              <div style={{ fontWeight: "600" }}>श्रीमान्,</div>
              <div>{placeholderData.recipient_name || placeholderData.receiver_name}</div>
              {placeholderData.recipient_designation && <div>{placeholderData.recipient_designation}</div>}
              {placeholderData.recipient_address && <div>{placeholderData.recipient_address}</div>}
            </div>
          )}

          {/* Subject */}
          {placeholderData.subject && (
            <div style={{ marginBottom: "20px", fontSize: "12pt", fontWeight: "600", color: "rgb(0, 0, 0)",marginLeft:"50px",marginRight:"30px", }}>
              <strong>विषय:</strong> {placeholderData.subject}
            </div>
          )}

          {/* Salutation */}
          <div style={{ marginBottom: "16px", fontSize: "12pt", color: "rgb(0, 0, 0)",marginLeft:"40px",marginRight:"30px", }}>महोदय,</div>

          {/* Main Letter Content */}
          <div
            style={{
              marginBottom: "40px",
              marginLeft: "40px",
              marginRight:"30px",
              textAlign: "justify",
              whiteSpace: "pre-wrap",
              fontSize: "12pt",
              lineHeight: "2",
              color: "rgb(0, 0, 0)",
            }}
          >
            {generatedLetter}
          </div>

          {/* Signature Section */}
          {/* <div style={{ marginTop: "60px", float: "right", textAlign: "center", fontSize: "12pt", color: "rgb(0, 0, 0)" }}>
            <div
              style={{
                borderTop: "2px solid rgb(0, 0, 0)",
                paddingTop: "8px",
                minWidth: "200px",
                marginTop: "60px",
              }}
            >
              <div style={{ fontWeight: "700", marginBottom: "4px", color: "rgb(0, 0, 0)" }}>
                {placeholderData.sender_name || placeholderData.name || "........................."}
              </div>
              <div style={{ fontSize: "11pt", color: "rgb(55, 65, 81)" }}>
                {placeholderData.sender_designation ||
                  placeholderData.designation ||
                  placeholderData.position ||
                  "........................."}
              </div>
              {placeholderData.sender_office && (
                <div style={{ fontSize: "10pt", color: "rgb(107, 114, 128)", marginTop: "2px" }}>
                  {placeholderData.sender_office}
                </div>
              )}
            </div>
          </div> */}

          {/* Footer with contact info (if available) */}
          <div style={{ clear: "both", marginTop: "100px", paddingTop: "20px", borderTop: "1px solid rgb(229, 231, 235)" }}>
            <div style={{ fontSize: "9pt", color: "rgb(107, 114, 128)", textAlign: "center" }}>
              {placeholderData.contact_email && <span>Email: {placeholderData.contact_email} | </span>}
              {placeholderData.contact_phone && <span>Phone: {placeholderData.contact_phone}</span>}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
