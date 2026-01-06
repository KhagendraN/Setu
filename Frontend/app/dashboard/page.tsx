"use client"

import { useEffect, useState } from "react"
import { cn } from "@/lib/utils"

import { useAuth } from "@/context/auth-context"
import { Navbar } from "@/components/layout/navbar"
import { Footer } from "@/components/layout/footer"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { StatsCard } from "@/components/dashboard/stats-card"
import { MessageSquare, ShieldCheck, Clock, ArrowUpRight, BookOpen, Lightbulb, Bell, FileText } from "lucide-react"
import Link from "next/link"
import { redirect } from "next/navigation"
import { getDocumentStats } from "@/lib/document-cache"

export default function DashboardPage() {
  const { user, isLoading } = useAuth()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    console.log("Dashboard - isLoading:", isLoading);
    console.log("Dashboard - user:", user);
    console.log("Token in localStorage:", localStorage.getItem('access_token'));
  }, [isLoading, user])

  const [tips, setTips] = useState<any[]>([])
  const [currentTipIndex, setCurrentTipIndex] = useState<number>(0)
  const [showNepali, setShowNepali] = useState<boolean>(false)
  const [totalConsultations, setTotalConsultations] = useState<number>(0)
  const [recentActivities, setRecentActivities] = useState<any[]>([])
  const [documentStats, setDocumentStats] = useState({
    totalAnalyzed: 0,
    totalInclusive: 0,
    totalFlagged: 0,
    totalLetters: 0,
  })

  useEffect(() => {
    fetch("/data.json")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setTips(data)
          setCurrentTipIndex(Math.floor(Math.random() * data.length))
        }
      })
      .catch((err) => console.error("Failed to load tips:", err))

    // Load document stats from cache
    const stats = getDocumentStats()
    setDocumentStats(stats)
  }, [])

  // Fetch total consultations count and recent activities
  useEffect(() => {
    const fetchConsultations = async () => {
      const token = localStorage.getItem("access_token")
      if (!token) return

      const BACKEND_URL = (process.env.NEXT_PUBLIC_BACKEND_URL as string) || "http://localhost:8000"

      try {
        const response = await fetch(`${BACKEND_URL}/api/v1/chat-history/conversations`, {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        })

        if (response.ok) {
          const data = await response.json()
          setTotalConsultations(data.length)

          // Transform conversations into activity format
          const activities = data.slice(0, 5).map((conv: any) => ({
            type: "chat",
            title: conv.title,
            time: formatRelativeTime(conv.updated_at),
            icon: MessageSquare,
            color: "text-primary bg-primary/10",
            conversationId: conv.id,
          }))
          setRecentActivities(activities)
        }
      } catch (error) {
        console.error("Failed to fetch consultations:", error)
      }
    }

    if (user) {
      fetchConsultations()
    }
  }, [user])

  // Helper function to format relative time
  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
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
      return date.toLocaleDateString()
    }
  }

  if (!mounted || isLoading) return null
  if (!user) redirect("/login")

  // Calculate profile progress based on name, email, NID, and age
  const calculateProfileProgress = () => {
    let completedFields = 0
    const totalFields = 4

    // Name is always present (required during registration)
    if (user.name) completedFields++

    // Email is always present (required during registration)
    if (user.email) completedFields++

    // Check if NID is filled
    if (user.details?.nid) completedFields++

    // Check if age is filled
    if (user.details?.age) completedFields++

    return Math.round((completedFields / totalFields) * 100)
  }

  const profileProgress = calculateProfileProgress()


  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1 p-4 md:p-8 bg-muted/20">
        <div className="container mx-auto max-w-7xl">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
            <div className="space-y-1">
              <h1 className="text-3xl font-bold tracking-tight">Welcome back, {user.name}</h1>
              <p className="text-muted-foreground">Here&apos;s an overview of your legal welfare activity.</p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" size="icon" className="relative bg-transparent">
                <Bell className="h-5 w-5" />
                <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-destructive" />
              </Button>
              <Button className="bg-primary" asChild>
                <Link href="/chatbot">Start New Consultation</Link>
              </Button>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatsCard
              title="Total Consultations"
              value={totalConsultations.toString()}
              description={`${totalConsultations} chat ${totalConsultations === 1 ? 'history' : 'histories'}`}
              icon={MessageSquare}
              color="primary"
            />
            <StatsCard
              title="Documents Analyzed"
              value={documentStats.totalAnalyzed.toString()}
              description={`${documentStats.totalInclusive} inclusive, ${documentStats.totalFlagged} flagged`}
              icon={ShieldCheck}
              color="accent"
            />
            <StatsCard
              title="Letters Generated"
              value={documentStats.totalLetters.toString()}
              description="Cached locally"
              icon={FileText}
              color="success"
            />
            <Link href="/profile" className="block">
              <StatsCard
                title="Profile Progress"
                value={`${profileProgress}%`}
                description="Complete your details"
                icon={ArrowUpRight}
                color="primary"
              />
            </Link>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Recent Activity */}
            <Card className="lg:col-span-2 border-primary/10">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Recent Activity</CardTitle>
                  <CardDescription>Your latest interactions with our legal tools.</CardDescription>
                </div>
                <Button variant="ghost" size="sm" className="text-primary">
                  View All
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {recentActivities.length > 0 ? (
                    recentActivities.map((activity, i) => (
                      <Link key={i} href="/chatbot">
                        <div className="flex items-start gap-4 group cursor-pointer">
                          <div className={cn("p-2 rounded-lg border border-transparent transition-colors", activity.color)}>
                            <activity.icon className="h-5 w-5" />
                          </div>
                          <div className="flex-1 space-y-1">
                            <p className="text-sm font-bold group-hover:text-primary transition-colors">{activity.title}</p>
                            <p className="text-xs text-muted-foreground">{activity.time}</p>
                          </div>
                          <ArrowUpRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                      </Link>
                    ))
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <MessageSquare className="h-12 w-12 mx-auto mb-3 opacity-20" />
                      <p className="text-sm">No recent activity yet</p>
                      <p className="text-xs mt-1">Start a conversation with our legal chatbot</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Side Panel: Tips & Actions */}
            <div className="space-y-8">
              <Card className="bg-primary text-primary-foreground border-none relative overflow-hidden">
                <div className="absolute inset-0 nepali-pattern opacity-10" />
                <CardHeader className="relative">
                  <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="h-5 w-5 text-accent" />
                    Legal Tip of the Day
                  </CardTitle>
                </CardHeader>
                <CardContent className="relative">
                  <p className="text-sm leading-relaxed opacity-90">
                    {tips.length > 0 ? (showNepali ? tips[currentTipIndex]?.fact_np : tips[currentTipIndex]?.fact_en) : "Loading tip..."}
                  </p>

                  <div className="mt-4 w-full flex gap-3 items-center">
                    <Button
                      variant="ghost"
                      size="lg"
                      className="flex-1 bg-white/10 hover:bg-white/20 text-white/95 rounded-lg px-4 py-2 flex items-center gap-3 justify-center shadow-md"
                      onClick={() => {
                        // pick a new random tip (keep current language)
                        if (tips.length > 1) {
                          let idx = Math.floor(Math.random() * tips.length)
                          if (tips.length > 1 && idx === currentTipIndex) idx = (idx + 1) % tips.length
                          setCurrentTipIndex(idx)
                        }
                      }}
                      title={showNepali ? "नेपालीमा" : "View more tips"}
                    >
                      <Lightbulb className="h-4 w-4 text-accent" />
                      <span className="font-medium">
                        {showNepali ? "थप सुझावहरू" : "View More Tips"}
                      </span>
                    </Button>

                    <Button
                      variant="default"
                      size="sm"
                      className="rounded-full w-12 h-12 flex items-center justify-center shadow ring-1 ring-white/10 hover:scale-105 transition-transform"
                      onClick={() => setShowNepali((s) => !s)}
                      aria-label={showNepali ? "Switch to English" : "नेपालीमा हेर्नुहोस्"}
                      title={showNepali ? "Show in English" : "नेपालीमा हेर्नुहोस्"}
                    >
                      <span className="text-lg">{showNepali ? "EN" : "🇳🇵"}</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-primary/10">
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="grid gap-4">
                  <Button variant="outline" className="w-full justify-start text-sm bg-transparent" asChild>
                    <Link href="/bias-checker">
                      <ShieldCheck className="mr-2 h-4 w-4 text-accent" />
                      Analyze a New Document
                    </Link>
                  </Button>
                  <Button variant="outline" className="w-full justify-start text-sm bg-transparent" asChild>
                    <Link href="/resources">
                      <BookOpen className="mr-2 h-4 w-4 text-success" />
                      Browse Legal Guides
                    </Link>
                  </Button>
                  <Button variant="outline" className="w-full justify-start text-sm bg-transparent" asChild>
                    <Link href="/profile">
                      <Clock className="mr-2 h-4 w-4 text-primary" />
                      Update Personal Details
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
