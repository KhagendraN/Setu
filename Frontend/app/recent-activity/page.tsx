"use client"

import { useEffect, useState } from "react"
import { useAuth } from "@/context/auth-context"
import { Navbar } from "@/components/layout/navbar"
import { Footer } from "@/components/layout/footer"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowLeft, ArrowUpRight, Clock, Filter } from "lucide-react"
import Link from "next/link"
import { redirect } from "next/navigation"
import { cn } from "@/lib/utils"
import { getAllActivities, type Activity } from "@/lib/activity-helper"

export default function RecentActivityPage() {
  const { user, isLoading } = useAuth()
  const [mounted, setMounted] = useState(false)
  const [activities, setActivities] = useState<Activity[]>([])
  const [filteredActivities, setFilteredActivities] = useState<Activity[]>([])
  const [filterType, setFilterType] = useState<"all" | "chat" | "document" | "letter">("all")
  const [isLoadingActivities, setIsLoadingActivities] = useState(true)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    const fetchActivities = async () => {
      if (!user?.id) return

      setIsLoadingActivities(true)
      const token = localStorage.getItem("access_token")
      const allActivities = await getAllActivities(user.id, token || undefined)
      setActivities(allActivities)
      setFilteredActivities(allActivities)
      setIsLoadingActivities(false)
    }

    if (user) {
      fetchActivities()
    }
  }, [user])

  useEffect(() => {
    if (filterType === "all") {
      setFilteredActivities(activities)
    } else {
      setFilteredActivities(activities.filter((a) => a.type === filterType))
    }
  }, [filterType, activities])

  if (!mounted || isLoading) return null
  if (!user) redirect("/login")

  const getActivityLink = (activity: Activity) => {
    switch (activity.type) {
      case "chat":
        return "/chatbot"
      case "document":
        return "/bias-checker"
      case "letter":
        return "/letter-generation"
      default:
        return "#"
    }
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1 p-4 md:p-8 bg-muted/20">
        <div className="container mx-auto max-w-5xl">
          {/* Header */}
          <div className="flex items-center gap-4 mb-6">
            <Button variant="ghost" size="icon" asChild>
              <Link href="/dashboard">
                <ArrowLeft className="h-5 w-5" />
              </Link>
            </Button>
            <div className="flex-1">
              <h1 className="text-3xl font-bold tracking-tight">Recent Activity</h1>
              <p className="text-muted-foreground">All your interactions with Setu</p>
            </div>
          </div>

          {/* Filter Section */}
          <Card className="mb-6 border-primary/10">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Filter className="h-5 w-5 text-primary" />
                  <CardTitle className="text-lg">Filter Activities</CardTitle>
                </div>
                <Badge variant="secondary">{filteredActivities.length} activities</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant={filterType === "all" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setFilterType("all")}
                >
                  All ({activities.length})
                </Button>
                <Button
                  variant={filterType === "chat" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setFilterType("chat")}
                >
                  Chats ({activities.filter((a) => a.type === "chat").length})
                </Button>
                <Button
                  variant={filterType === "document" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setFilterType("document")}
                >
                  Documents ({activities.filter((a) => a.type === "document").length})
                </Button>
                <Button
                  variant={filterType === "letter" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setFilterType("letter")}
                >
                  Letters ({activities.filter((a) => a.type === "letter").length})
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Activities List */}
          <Card className="border-primary/10">
            <CardHeader>
              <CardTitle>Activity Timeline</CardTitle>
              <CardDescription>Chronological list of all your activities</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingActivities ? (
                <div className="text-center py-12">
                  <Clock className="h-12 w-12 mx-auto mb-3 text-muted-foreground animate-spin" />
                  <p className="text-sm text-muted-foreground">Loading activities...</p>
                </div>
              ) : filteredActivities.length > 0 ? (
                <div className="space-y-4">
                  {filteredActivities.map((activity) => (
                    <Link key={activity.id} href={getActivityLink(activity)}>
                      <div className="flex items-start gap-4 p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors group cursor-pointer">
                        <div className={cn("p-3 rounded-lg border", activity.color)}>
                          <activity.icon className="h-5 w-5" />
                        </div>
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center justify-between">
                            <p className="font-semibold group-hover:text-primary transition-colors">
                              {activity.title}
                            </p>
                            <ArrowUpRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                          </div>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground">
                            <Badge variant="outline" className="text-xs">
                              {activity.type}
                            </Badge>
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {activity.time}
                            </span>
                          </div>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center mb-4 mx-auto">
                    <Clock className="h-10 w-10 text-muted-foreground/50" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">No activities found</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {filterType === "all"
                      ? "Start using Setu to see your activities here"
                      : `No ${filterType} activities yet`}
                  </p>
                  <Button asChild>
                    <Link href="/dashboard">Go to Dashboard</Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
      <Footer />
    </div>
  )
}
