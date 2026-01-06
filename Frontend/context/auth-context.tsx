"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"
import { clearUserCache } from "@/lib/document-cache"

export interface User {
  id: string
  email: string
  name: string
  role: "user" | "admin"
  isFirstTime: boolean
  details?: {
    nid?: string
    age?: number
    education?: string
    salary?: string
    disability?: { hasDisability: boolean; type?: string }
    address?: { province: string; district: string; municipality: string; ward: string }
  }
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (token: string) => void
  logout: () => void
  updateUserDetails: (details: User["details"]) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Helper function to decode JWT
function decodeToken(token: string): { sub: string; exp: number } | null {
  try {
    const payload = token.split(".")[1]
    return JSON.parse(atob(payload))
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")

    if (token) {
      const decoded = decodeToken(token)

      if (decoded && decoded.exp * 1000 > Date.now()) {
        // Token is valid, check if we have cached user details
        const cachedDetails = localStorage.getItem("know_rights_user_details")
        const details = cachedDetails ? JSON.parse(cachedDetails) : undefined

        // Try to get stored user data from localStorage and prefer stored email/name when available
        const storedUserData = localStorage.getItem("user")
        let userName = decoded.sub.split("@")[0] // default fallback
        let userEmail = decoded.sub

        if (storedUserData) {
          try {
            const parsedUser: any = JSON.parse(storedUserData)
            userName = parsedUser.full_name || parsedUser.name || userName
            userEmail = parsedUser.email || parsedUser.email_address || parsedUser.emailAddress || userEmail
          } catch (e) {
            console.error("Failed to parse user data:", e)
          }
        }

        setUser({
          id: decoded.sub,
          email: userEmail,
          name: userName,
          role: "user",
          isFirstTime: !details,
          details,
        })
      } else {
        // Token expired or invalid
        localStorage.removeItem("access_token")
        localStorage.removeItem("know_rights_user_details")
      }
    }

    setIsLoading(false)
  }, [])

  const login = (token: string) => {
    localStorage.setItem("access_token", token)

    const decoded = decodeToken(token)
    if (decoded) {
      // Check if a different user is logging in
      const previousUserId = user?.id
      if (previousUserId && previousUserId !== decoded.sub) {
        // Different user - clear previous user's cache
        clearUserCache(previousUserId)
      }

      // Try to get stored user data from localStorage and prefer stored email/name when available
      const storedUserData = localStorage.getItem("user")
      let userName = decoded.sub.split("@")[0] // default fallback
      let userEmail = decoded.sub

      console.log("Auth Context - Stored user data:", storedUserData)

      if (storedUserData) {
        try {
          const parsedUser: any = JSON.parse(storedUserData)
          console.log("Auth Context - Parsed user:", parsedUser)
          console.log("Auth Context - full_name:", parsedUser.full_name)
          console.log("Auth Context - name:", parsedUser.name)
          userName = parsedUser.full_name || parsedUser.name || userName
          userEmail = parsedUser.email || parsedUser.email_address || parsedUser.emailAddress || userEmail
          console.log("Auth Context - Final userName:", userName)
          console.log("Auth Context - Final userEmail:", userEmail)
        } catch (e) {
          console.error("Failed to parse user data:", e)
        }
      }

      setUser({
        id: decoded.sub,
        email: userEmail,
        name: userName,
        role: "user",
        isFirstTime: true,
      })
    }
  }

  const logout = () => {
    // Clear user-specific caches before logout
    if (user?.id) {
      clearUserCache(user.id)
    }

    setUser(null)
    localStorage.removeItem("access_token")
    localStorage.removeItem("know_rights_user_details")
    localStorage.removeItem("user")
  }

  const updateUserDetails = async (details: User["details"]) => {
    if (!user) return
    const updatedUser = { ...user, details, isFirstTime: false }
    setUser(updatedUser)
    localStorage.setItem("know_rights_user_details", JSON.stringify(details))
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, updateUserDetails }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) throw new Error("useAuth must be used within AuthProvider")
  return context
}