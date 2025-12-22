import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ReduxProvider } from "@/components/providers/redux-provider"
import { ThemeProvider } from "@/components/providers/theme-provider"
import { Toaster } from "@/components/ui/toaster"
import { ChatbotWidget } from "@/components/chatbot/chatbot-widget"
import { ChatProvider } from "@/lib/contexts/chat-context"
import { CalendarProvider } from "@/lib/contexts/calendar-context"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Bareeq - AI business partner",
  description: "Agentic Business Operations System for SME Clothing Brands",
    generator: 'v0.app'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider>
          <ReduxProvider>
            <ChatProvider>
              <CalendarProvider>
                {children}
                <ChatbotWidget />
                <Toaster />
              </CalendarProvider>
            </ChatProvider>
          </ReduxProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
