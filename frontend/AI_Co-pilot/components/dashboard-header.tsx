"use client"

import { usePathname } from "next/navigation"
import { useTheme } from "next-themes"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { Moon, Sun } from "lucide-react"

export function DashboardHeader() {
  const pathname = usePathname()
  const { theme, setTheme } = useTheme()

  const getPageTitle = () => {
    switch (pathname) {
      case "/":
        return "Dashboard"
      case "/messages":
        return "Messages"
      case "/settings":
        return "Settings"
      case "/campaigns":
        return "Campaigns"
      case "/gap-analysis":
        return "Gap Analysis"
      case "/document-analysis":
        return "Document Analysis"
      default:
        return "Dashboard"
    }
  }

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark")
  }

  return (
    <header className="sticky top-0 z-50 flex items-center justify-between border-b border-slate-200 dark:border-slate-700 bg-gradient-to-r from-white to-blue-50 dark:from-slate-900 dark:to-blue-900/20 px-6 py-4 shadow-sm">
      <div className="flex items-center gap-4">
        <SidebarTrigger className="text-slate-600 dark:text-slate-300 hover:bg-blue-100 dark:hover:bg-blue-900/30 hover:text-blue-600 dark:hover:text-blue-300 transition-colors" />
        <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-700 to-blue-600 bg-clip-text text-transparent">
          {getPageTitle()}
        </h1>
      </div>

      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          className="text-slate-600 dark:text-slate-300 hover:bg-blue-100 dark:hover:bg-blue-900/30 hover:text-blue-600 dark:hover:text-blue-300 transition-colors"
        >
          {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          <span className="sr-only">Toggle theme</span>
        </Button>
      </div>
    </header>
  )
}
