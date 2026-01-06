"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useAuth } from "@/context/auth-context"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Menu, X, Scale, LogOut, LayoutDashboard, MessageSquare, Search, User } from "lucide-react"
import { useState } from "react"
import { clearAuthData } from "@/lib/auth-utils"

export function Navbar() {
  const { user, logout } = useAuth()
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const router = useRouter()

  const handleLogout = () => {
    // Clear all auth data from localStorage first
    clearAuthData()
    // Update auth context
    logout()
    // Force navigation to landing page
    window.location.href = "/"
  }

  const handleHomeClick = (e: React.MouseEvent) => {
    if (user) {
      e.preventDefault()
      router.push("/dashboard")
    }
  }

  // Define navigation items based on authentication status
  const getNavItems = () => {
    if (user) {
      // Show only protected features when logged in
      return [
        { label: "Chatbot", href: "/chatbot", icon: MessageSquare },
        { label: "Bias Checker", href: "/bias-checker", icon: Search },
        { label: "Letter Generator", href: "/letter-generator" },
      ]
    } else {
      // Show only Home when not logged in
      return [
        { label: "Home", href: "/" },
      ]
    }
  }

  const navItems = getNavItems()

  return (
    <nav className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-2">
          <Link
            href={user ? "/dashboard" : "/"}
            onClick={handleHomeClick}
            className="flex items-center gap-2 text-primary"
          >
            <Scale className="h-6 w-6" />
            <span className="font-bold text-lg tracking-tight">Know Your Rights Nepal</span>
          </Link>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-6">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="text-sm font-medium transition-colors hover:text-primary">
              {item.label}
            </Link>
          ))}

          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full focus-visible:ring-0 focus-visible:ring-offset-0 hover:bg-transparent">
                  <Avatar className="h-8 w-8 border hover:border-primary transition-colors">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      {user?.name ? user.name.slice(0, 2).toUpperCase() : 'U'}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <div className="px-4 py-3 border-b">
                  <div className="font-medium">{user?.name}</div>
                  <div className="text-xs text-muted-foreground">{user?.email}</div>
                </div>
                <DropdownMenuItem asChild>
                  <Link href="/dashboard">
                    <LayoutDashboard className="mr-2 h-4 w-4" />
                    Dashboard
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/profile">
                    <User className="mr-2 h-4 w-4" />
                    Profile
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleLogout} className="text-destructive">
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <div className="flex items-center gap-2">
              <Button asChild variant="ghost">
                <Link href="/login">Login</Link>
              </Button>
              <Button asChild className="bg-primary hover:bg-primary/90">
                <Link href="/register">Register</Link>
              </Button>
            </div>
          )}
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden flex items-center">
          <Button variant="ghost" size="icon" onClick={() => setIsMenuOpen(!isMenuOpen)}>
            {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </Button>
        </div>
      </div>

      {isMenuOpen && (
        <div className="md:hidden border-t bg-background p-4 animate-in fade-in slide-in-from-top-2">
          <div className="flex flex-col gap-4">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setIsMenuOpen(false)}
                className="text-sm font-medium p-2 hover:bg-muted rounded-md"
              >
                {item.label}
              </Link>
            ))}

            {user ? (
              <>
                <Link
                  href="/dashboard"
                  onClick={() => setIsMenuOpen(false)}
                  className="text-sm font-medium p-2 hover:bg-muted rounded-md flex items-center gap-2"
                >
                  <LayoutDashboard className="h-4 w-4" />
                  Dashboard
                </Link>
                <Link
                  href="/profile"
                  onClick={() => setIsMenuOpen(false)}
                  className="text-sm font-medium p-2 hover:bg-muted rounded-md flex items-center gap-2"
                >
                  <User className="h-4 w-4" />
                  Profile
                </Link>
                <Button
                  onClick={() => {
                    setIsMenuOpen(false)
                    handleLogout()
                  }}
                  variant="destructive"
                  className="w-full"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Button asChild variant="outline" className="w-full">
                  <Link href="/login" onClick={() => setIsMenuOpen(false)}>
                    Login
                  </Link>
                </Button>
                <Button asChild className="w-full bg-primary">
                  <Link href="/register" onClick={() => setIsMenuOpen(false)}>
                    Register
                  </Link>
                </Button>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  )
}
