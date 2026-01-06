"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/context/auth-context"
import { Navbar } from "@/components/layout/navbar"
import { Footer } from "@/components/layout/footer"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { MessageSquare, Search, BookOpen, CheckCircle } from "lucide-react"
import Link from "next/link"

export default function Home() {
  const router = useRouter()
  const { user, isLoading } = useAuth()

  useEffect(() => {
    // Redirect logged-in users to dashboard
    if (!isLoading && user) {
      router.push("/dashboard")
    }
  }, [user, isLoading, router])

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading...</p>
          </div>
        </main>
        <Footer />
      </div>
    )
  }

  // Don't render the landing page if user is logged in (will redirect)
  if (user) {
    return null
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative py-20 md:py-32 overflow-hidden">
          <div className="absolute inset-0 nepali-pattern -z-10" />
          <div className="container max-w-7xl mx-auto relative text-center space-y-8">
            {/* <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold mb-4 border border-primary/20">
              <CheckCircle className="h-3 w-3" />
              Trusted by 5,000+ Nepali Citizens
            </div> */}
            <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-balance">
              SETU - <span className="text-primary">Your Legal Assistance</span>
            </h1>
            <p className="max-w-[700px] mx-auto text-muted-foreground md:text-xl text-pretty">
              Your digital gateway to legal justice in Nepal. Access our AI-powered law assistant, analyze legal notices
              for bias, and learn about your fundamental rights.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button size="lg" className="h-12 px-8 bg-primary hover:bg-primary/90" asChild>
                <Link href="/chatbot">Start Legal Consultation</Link>
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="h-12 px-8 border-primary text-primary hover:bg-primary/5 bg-transparent"
                asChild
              >
                <Link href="/bias-checker">Analyze Legal Documents</Link>
              </Button>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section className="py-20 bg-muted/30">
          <div className="container max-w-7xl mx-auto">
            <div className="text-center mb-16 space-y-4">
              <h2 className="text-3xl font-bold tracking-tight">Comprehensive Legal Services</h2>
              <p className="text-muted-foreground max-w-[600px] mx-auto">
                Tailored solutions for every legal need, built with privacy and accessibility in mind.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <Card className="hover:shadow-lg transition-all border-primary/10">
                <CardHeader>
                  <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                    <MessageSquare className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle>Law Chatbot</CardTitle>
                  <CardDescription>Get instant answers to your legal queries based on Nepali law.</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="link" className="p-0 h-auto text-primary" asChild>
                    <Link href="/chatbot">Learn more →</Link>
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-all border-primary/10">
                <CardHeader>
                  <div className="h-12 w-12 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                    <Search className="h-6 w-6 text-accent" />
                  </div>
                  <CardTitle>Bias Checker</CardTitle>
                  <CardDescription>
                    Analyze legal notices and contracts for potential linguistic biases.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="link" className="p-0 h-auto text-accent" asChild>
                    <Link href="/bias-checker">Try it now →</Link>
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-all border-primary/10">
                <CardHeader>
                  <div className="h-12 w-12 rounded-lg bg-success/10 flex items-center justify-center mb-4">
                    <BookOpen className="h-6 w-6 text-success" />
                  </div>
                  <CardTitle>Letter Generator</CardTitle>
                  <CardDescription>
                    Generate professional government letters effortlessly. Describe what you need, provide the required information, and get an official letter tailored to your reques
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="link" className="p-0 h-auto text-success" asChild>
                    <Link href="/letter-generator">Generate Letters →</Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* It is the section that shows the users stats */}
        {/* Statistics Section */}
        {/* <section className="py-20 border-y">
          <div className="container grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div className="space-y-2">
              <div className="text-4xl font-bold text-primary">15k+</div>
              <p className="text-sm text-muted-foreground uppercase tracking-wider font-semibold">Users Helped</p>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-primary">50k+</div>
              <p className="text-sm text-muted-foreground uppercase tracking-wider font-semibold">Queries Answered</p>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-primary">2.5k+</div>
              <p className="text-sm text-muted-foreground uppercase tracking-wider font-semibold">Docs Analyzed</p>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-primary">98%</div>
              <p className="text-sm text-muted-foreground uppercase tracking-wider font-semibold">Satisfaction Rate</p>
            </div>
          </div>
        </section> */}

        {/* CTA Section */}
        {/** This is the section we can add to get the Create account section */}
        {/* <section className="py-20 bg-primary text-primary-foreground relative overflow-hidden">
          <div className="absolute inset-0 opacity-10 nepali-pattern" />
          <div className="container relative text-center space-y-6">
            <h2 className="text-3xl md:text-4xl font-bold">Ready to take control of your legal journey?</h2>
            <p className="max-w-[600px] mx-auto opacity-90">
              Join thousands of Nepali citizens who are using our platform to understand their rights and seek justice.
            </p>
            <Button size="lg" variant="secondary" className="h-12 px-8" asChild>
              <Link href="/register">Create Your Account</Link>
            </Button>
          </div>
        </section> */}
      </main>
      <Footer />
    </div>
  )
}
