"use client"

import { useState } from "react"
import { usePathname } from "next/navigation"
import Link from "next/link"
import { Home, Calendar, Settings, Moon, Sun, Sparkles, MessageSquare, AlertTriangle, FileSearch, Rocket } from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"

const menuItems = [
  {
    title: "Dashboard",
    url: "/",
    icon: Home,
  },
  {
    title: "Startup Hub",
    url: "/startup-hub",
    icon: Rocket,
  },
  {
    title: "Messages",
    url: "/messages",
    icon: MessageSquare,
  },
  {
    title: "Campaigns",
    url: "/campaigns",
    icon: Calendar,
  },
  {
    title: "Gap Analysis",
    url: "/gap-analysis",
    icon: AlertTriangle,
  },
  {
    title: "Doc Analysis",
    url: "/document-analysis",
    icon: FileSearch,
  },
  {
    title: "Settings",
    url: "/settings",
    icon: Settings,
  },
]

export function AppSidebar() {
  const pathname = usePathname()
  const [isDarkMode, setIsDarkMode] = useState(false)

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode)
    document.documentElement.classList.toggle("dark")
  }

  return (
    <Sidebar className="border-r border-slate-200 bg-gradient-to-b from-slate-50 to-purple-50 dark:border-slate-700 dark:from-slate-900 dark:to-purple-900/20 w-64">
      <SidebarHeader className="p-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-lg">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              AI Co-pilot
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Business Assistant</p>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu className="space-y-2">
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === item.url}
                    className="data-[active=true]:bg-gradient-to-r data-[active=true]:from-purple-100 data-[active=true]:to-pink-100 data-[active=true]:text-purple-800 data-[active=true]:border-l-4 data-[active=true]:border-purple-500 dark:data-[active=true]:from-purple-900/30 dark:data-[active=true]:to-pink-900/30 dark:data-[active=true]:text-purple-300 hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 hover:text-purple-800 dark:hover:from-slate-800 dark:hover:to-purple-900/20 dark:hover:text-purple-300 rounded-lg transition-all duration-200 text-slate-700 dark:text-slate-300"
                  >
                    <Link href={item.url} className="flex items-center gap-3 px-3 py-2.5">
                      <item.icon className="h-5 w-5" />
                      <span className="font-medium">{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-6 space-y-4">
        <Button
          variant="outline"
          onClick={toggleDarkMode}
          className="w-full justify-start gap-3 bg-gradient-to-r from-slate-700 to-purple-700 text-white hover:from-slate-600 hover:to-purple-600 dark:from-slate-200 dark:to-purple-200 dark:text-slate-900 dark:hover:from-slate-100 dark:hover:to-purple-100 border-0 shadow-md"
        >
          {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          {isDarkMode ? "Light mode" : "Dark mode"}
        </Button>

        <div className="flex items-center gap-3">
          <img
            src="https://i.pravatar.cc/60?img=33"
            alt="User"
            className="w-10 h-10 rounded-full border-2 border-purple-200 dark:border-purple-700"
          />
          <div className="flex-1">
            <p className="font-semibold text-slate-700 dark:text-slate-200 text-sm">Sarah Mitchell</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">Brand Manager</p>
          </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
