"use client"

import { useEffect, useState } from "react"
import { cn } from "@/lib/utils"

import { useAuth } from "@/context/auth-context"
import { Navbar } from "@/components/layout/navbar"
import { Footer } from "@/components/layout/footer"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { StatsCard } from "@/components/dashboard/stats-card"
import { MessageSquare, ShieldCheck, Clock, ArrowUpRight, BookOpen, Lightbulb, Bell } from "lucide-react"
import Link from "next/link"
import { redirect } from "next/navigation"

export default function DashboardPage() {
  const { user, isLoading } = useAuth()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    console.log("Dashboard - isLoading:", isLoading);
    console.log("Dashboard - user:", user);
    console.log("Token in localStorage:", localStorage.getItem('access_token'));
  }, [isLoading, user])

  if (!mounted || isLoading) return null
  if (!user) redirect("/login")

  const activities = [
    {
      type: "chat",
      title: "Legal Consultation #104",
      time: "2 hours ago",
      icon: MessageSquare,
      color: "text-primary bg-primary/10",
    },
    {
      type: "bias",
      title: "Document Analysis: Labor Contract",
      time: "Yesterday",
      icon: ShieldCheck,
      color: "text-accent bg-accent/10",
    },
    {
      type: "resource",
      title: "Read: Consumer Protection Rights",
      time: "2 days ago",
      icon: BookOpen,
      color: "text-success bg-success/10",
    },
  ]

  const tips = [
    "Always keep a signed copy of any legal notice you receive.",
    "Property rights in Nepal are protected under the 2072 Constitution.",
    "Labor laws require a 30-day notice for contract termination.",
  ]

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1 p-4 md:p-8 bg-muted/20">
        <div className="container mx-auto max-w-7xl">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
            <div className="space-y-1">
              <h1 className="text-3xl font-bold tracking-tight">Welcome back, {user.name}!</h1>
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
              value="12"
              description="+2 from last month"
              icon={MessageSquare}
              color="primary"
            />
            <StatsCard
              title="Documents Analyzed"
              value="5"
              description="3 inclusive, 2 flagged"
              icon={ShieldCheck}
              color="accent"
            />
            <StatsCard
              title="Days Active"
              value="24"
              description="Current streak: 4 days"
              icon={Clock}
              color="success"
            />
            <StatsCard
              title="Profile Progress"
              value="85%"
              description="Complete your details"
              icon={ArrowUpRight}
              color="primary"
            />
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
                  {activities.map((activity, i) => (
                    <div key={i} className="flex items-start gap-4 group cursor-pointer">
                      <div className={cn("p-2 rounded-lg border border-transparent transition-colors", activity.color)}>
                        <activity.icon className="h-5 w-5" />
                      </div>
                      <div className="flex-1 space-y-1">
                        <p className="text-sm font-bold group-hover:text-primary transition-colors">{activity.title}</p>
                        <p className="text-xs text-muted-foreground">{activity.time}</p>
                      </div>
                      <ArrowUpRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  ))}
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
                  <p className="text-sm leading-relaxed opacity-90">{tips[0]}</p>
                  <Button variant="secondary" size="sm" className="mt-4 w-full">
                    View More Tips
                  </Button>
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
