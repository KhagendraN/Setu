import type React from "react"
import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import "./globals.css"
import { AuthProvider } from "@/context/auth-context"
import { Toaster } from "@/components/ui/toaster"

const _geist = Geist({ subsets: ["latin"] })
const _geistMono = Geist_Mono({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Setu",
  description: "Your digital legal assistant for legal welfare and rights in Nepal.",
  icons: {
    icon: [
      {
        url: "/logo.png",
        // media: "(prefers-color-scheme: light)",
      },
      {
        url: "/logo.png",
        // media: "(prefers-color-scheme: dark)",
      },
      {
        url: "/logo.png",
        // type: "image/svg+xml",
      },
    ],
    // apple: "/apple-icon.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`font-sans antialiased min-h-screen flex flex-col`}>
        <AuthProvider>
          {children}
          <Toaster />
        </AuthProvider>
      </body>
    </html>
  )
}
