"use client"

import type React from "react"
import { useMediaQuery } from "@/hooks/use-media-query"
import { SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import { DashboardHeader } from "@/components/dashboard-header"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const isDesktop = useMediaQuery("(min-width: 1024px)")

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 flex">
      <SidebarProvider defaultOpen={isDesktop}>
        <AppSidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <DashboardHeader />
          <main className="flex-1 p-6 overflow-hidden">{children}</main>
        </div>
      </SidebarProvider>
    </div>
  )
}
