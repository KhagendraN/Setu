import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Scale, MessageSquare, ShieldCheck, BookOpen, ArrowRight } from "lucide-react"

export function Footer() {
  return (
    <footer className="w-full border-t bg-muted/30">
      <div className="container max-w-7xl mx-auto py-12 md:py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-primary">
              <Scale className="h-6 w-6" />
              <span className="font-bold text-lg">SETU</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Empowering citizens of Nepal through legal literacy and digital assistance.
            </p>
            {/* <div className="flex gap-4">
              <Link href="#" className="text-muted-foreground hover:text-primary">
                <Facebook className="h-5 w-5" />
              </Link>
              <Link href="#" className="text-muted-foreground hover:text-primary">
                <Twitter className="h-5 w-5" />
              </Link>
              <Link href="#" className="text-muted-foreground hover:text-primary">
                <Instagram className="h-5 w-5" />
              </Link>
              <Link href="#" className="text-muted-foreground hover:text-primary">
                <Mail className="h-5 w-5" />
              </Link>
            </div> */}
          </div>
          <div className="md:col-span-3">
            <h3 className="font-semibold mb-6 text-lg">Quick Access</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Link
                href="/chatbot"
                className="group relative overflow-hidden rounded-lg border bg-card p-5 hover:shadow-lg transition-all duration-300 hover:border-primary/50"
              >
                <div className="flex items-start gap-3">
                  <div className="rounded-lg bg-primary/10 p-2.5 group-hover:bg-primary/20 transition-colors">
                    <MessageSquare className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm mb-1 group-hover:text-primary transition-colors">
                      Law Chatbot
                    </h4>
                    <p className="text-xs text-muted-foreground">
                      Get instant legal guidance
                    </p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                </div>
              </Link>

              <Link
                href="/bias-checker"
                className="group relative overflow-hidden rounded-lg border bg-card p-5 hover:shadow-lg transition-all duration-300 hover:border-primary/50"
              >
                <div className="flex items-start gap-3">
                  <div className="rounded-lg bg-primary/10 p-2.5 group-hover:bg-primary/20 transition-colors">
                    <ShieldCheck className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm mb-1 group-hover:text-primary transition-colors">
                      Bias Checker
                    </h4>
                    <p className="text-xs text-muted-foreground">
                      Analyze legal documents
                    </p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                </div>
              </Link>

              <Link
                href="/resources"
                className="group relative overflow-hidden rounded-lg border bg-card p-5 hover:shadow-lg transition-all duration-300 hover:border-primary/50"
              >
                <div className="flex items-start gap-3">
                  <div className="rounded-lg bg-primary/10 p-2.5 group-hover:bg-primary/20 transition-colors">
                    <BookOpen className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm mb-1 group-hover:text-primary transition-colors">
                      Legal Resources
                    </h4>
                    <p className="text-xs text-muted-foreground">
                      Browse legal information
                    </p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                </div>
              </Link>
            </div>
          </div>
          {/* <div>
            <h3 className="font-semibold mb-4">Support</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="#" className="text-muted-foreground hover:text-primary">
                  Contact Us
                </Link>
              </li>
              <li>
                <Link href="#" className="text-muted-foreground hover:text-primary">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="#" className="text-muted-foreground hover:text-primary">
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div> */}
          {/* <div className="bg-primary/5 p-6 rounded-xl border border-primary/10">
            <h3 className="font-semibold mb-2">Need Urgent Help?</h3>
            <p className="text-xs text-muted-foreground mb-4">
              Contact our 24/7 legal helpline for immediate assistance.
            </p>
            <Button size="sm" className="w-full">
              Call Hotline
            </Button>
          </div> */}
        </div>
        <div className="mt-12 pt-8 border-t text-center text-xs text-muted-foreground">
          © {new Date().getFullYear()} SETU. All rights reserved.
        </div>
      </div>
    </footer>
  )
}
