"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/context/auth-context"
import { Navbar } from "@/components/layout/navbar"
import { Footer } from "@/components/layout/footer"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { useToast } from "@/hooks/use-toast"
import { redirect } from "next/navigation"

export default function ProfilePage() {
  const { user, isLoading, updateUserDetails } = useAuth()
  const { toast } = useToast()
  const [age, setAge] = useState("")
  const [nid, setNid] = useState("")
  const [nidError, setNidError] = useState("")

  useEffect(() => {
    if (user?.details?.age) {
      setAge(user.details.age.toString())
    }
    if (user?.details?.nid) {
      setNid(user.details.nid)
    }
  }, [user])

  if (isLoading) return null
  if (!user) redirect("/login")

  // Get the first letter of the user's name
  const getInitial = () => {
    if (user?.name) {
      return user.name.charAt(0).toUpperCase()
    }
    return "U"
  }

  // Handle age input - only allow numbers, max 3 digits
  const handleAgeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    // Only allow numbers and limit to 3 digits
    if (value === "" || (/^\d+$/.test(value) && value.length <= 3)) {
      setAge(value)
    }
  }

  // Handle NID input with auto-hyphen formatting (xxx-xxx-xxx-x)
  const handleNidChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value
    // Remove all non-digit characters
    value = value.replace(/\D/g, "")

    // Limit to 10 digits
    if (value.length > 10) {
      value = value.slice(0, 10)
    }

    // Format with hyphens: xxx-xxx-xxx-x
    let formatted = ""
    if (value.length > 0) {
      formatted = value.slice(0, 3)
      if (value.length > 3) {
        formatted += "-" + value.slice(3, 6)
      }
      if (value.length > 6) {
        formatted += "-" + value.slice(6, 9)
      }
      if (value.length > 9) {
        formatted += "-" + value.slice(9, 10)
      }
    }

    setNid(formatted)

    // Validate NID format
    if (formatted && formatted.length < 13) {
      setNidError("NID must be in format: xxx-xxx-xxx-x")
    } else {
      setNidError("")
    }
  }

  // Handle form submission
  const handleSave = async () => {
    // Validate NID format before saving
    if (nid && nid.length !== 13) {
      toast({
        title: "Error",
        description: "NID must be in format: xxx-xxx-xxx-x (10 digits)",
        variant: "destructive",
      })
      return
    }

    // Validate age
    if (age && (parseInt(age) < 0 || parseInt(age) > 150)) {
      toast({
        title: "Error",
        description: "Please enter a valid age",
        variant: "destructive",
      })
      return
    }

    // Update user details in auth context
    const updatedDetails = {
      ...user.details,
      nid: nid || user.details?.nid,
      age: age ? parseInt(age) : user.details?.age,
    }

    await updateUserDetails(updatedDetails)

    // Here you would typically save to backend
    toast({
      title: "Success",
      description: "Profile updated successfully!",
    })
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1 p-4 md:p-8 bg-muted/20">
        <div className="container mx-auto max-w-2xl">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-primary tracking-tight">Profile</h1>
            <p className="text-muted-foreground">View and manage your personal information</p>
          </div>

          <Card className="border-primary/10">
            <CardHeader>
              <div className="flex flex-col items-center gap-4 text-center">
                <Avatar className="h-32 w-32 border-4 border-primary">
                  <AvatarFallback className="bg-primary text-primary-foreground text-5xl">
                    {getInitial()}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <CardTitle className="text-2xl">{user.name}</CardTitle>
                  <CardDescription className="text-base mt-1">{user.email}</CardDescription>
                  
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">

              <div className="space-y-2">
                <Label htmlFor="age">Age</Label>
                <Input
                  id="age"
                  type="text"
                  value={age}
                  onChange={handleAgeChange}
                  placeholder="Enter your age"
                  className="max-w-xs"
                />
                <p className="text-xs text-muted-foreground">Enter numbers only</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="nid">National ID (NID)</Label>
                <Input
                  id="nid"
                  type="text"
                  value={nid}
                  onChange={handleNidChange}
                  placeholder="xxx-xxx-xxx-x"
                  maxLength={13}
                />
                {nidError && (
                  <p className="text-xs text-destructive">{nidError}</p>
                )}
                <p className="text-xs text-muted-foreground">Format: xxx-xxx-xxx-x (10 digits)</p>
              </div>

              <div className="pt-4">
                <Button
                  onClick={handleSave}
                  className="w-full bg-primary hover:bg-primary/90"
                  disabled={!!nidError && nid.length > 0}
                >
                  Save Changes
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
      <Footer />
    </div>
  )
}
