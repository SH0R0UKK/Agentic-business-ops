"use client"

import { useMemo } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useCalendarContext } from "@/lib/contexts/calendar-context"
import { useChatContext } from "@/lib/contexts/chat-context"
import {
  CheckCircle2,
  Circle,
  Calendar,
  MessageSquare,
  AlertTriangle,
  FileText,
  ArrowRight,
  Clock,
  Sparkles,
  Target,
  TrendingUp,
  Zap,
} from "lucide-react"
import { cn } from "@/lib/utils"
import Link from "next/link"

// Mock data for dashboard
const mockStats = {
  totalGaps: 8,
  criticalGaps: 3,
  documents: 5,
  goalsTracked: 4,
}

const quickActions = [
  { label: "New Campaign", href: "/campaigns", icon: Calendar, color: "purple" },
  { label: "View Gaps", href: "/gap-analysis", icon: AlertTriangle, color: "red" },
  { label: "Check Messages", href: "/messages", icon: MessageSquare, color: "blue" },
  { label: "Documents", href: "/document-analysis", icon: FileText, color: "green" },
]

const recentActivity = [
  { id: "1", action: "New gap identified", detail: "Inventory sync issue", time: "2 hours ago", type: "gap" },
  { id: "2", action: "Campaign scheduled", detail: "Summer Collection Launch", time: "4 hours ago", type: "campaign" },
  { id: "3", action: "Customer inquiry", detail: "Sarah M. asked about order", time: "5 hours ago", type: "message" },
  { id: "4", action: "Document analyzed", detail: "Q2 Marketing Strategy", time: "1 day ago", type: "document" },
]

export default function DashboardPage() {
  const { events, toggleEventComplete } = useCalendarContext()
  const { messages } = useChatContext()

  // Get to-do items from calendar
  const todoItems = useMemo(() => {
    return events.filter((e) => e.isTodo).sort((a, b) => (a.completed ? 1 : -1))
  }, [events])

  // Get upcoming events (non-todo)
  const upcomingEvents = useMemo(() => {
    return events
      .filter((e) => !e.isTodo)
      .sort((a, b) => a.date - b.date)
      .slice(0, 4)
  }, [events])

  // Get recent customer messages (not bot messages)
  const recentMessages = useMemo(() => {
    return messages.filter((m) => m.sender === "user").slice(-3)
  }, [messages])

  const getEventColor = (type: string) => {
    const colors: Record<string, string> = {
      launch: "bg-purple-500",
      social: "bg-pink-500",
      email: "bg-blue-500",
      sale: "bg-green-500",
    }
    return colors[type] || "bg-gray-500"
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case "gap":
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      case "campaign":
        return <Calendar className="h-4 w-4 text-purple-500" />
      case "message":
        return <MessageSquare className="h-4 w-4 text-blue-500" />
      case "document":
        return <FileText className="h-4 w-4 text-green-500" />
      default:
        return <Circle className="h-4 w-4 text-gray-500" />
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6 p-6">
        {/* Welcome Section */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Welcome back</h2>
            <p className="text-slate-500 dark:text-slate-400">Here's what's happening with your business today.</p>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-lg border border-purple-200 dark:border-purple-800">
            <Sparkles className="h-5 w-5 text-purple-500" />
            <span className="text-sm font-medium text-purple-700 dark:text-purple-300">AI Co-pilot Active</span>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-br from-red-50 to-orange-50 dark:from-red-950/30 dark:to-orange-950/30 border-red-200 dark:border-red-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-red-600 dark:text-red-400">Critical Gaps</p>
                  <p className="text-3xl font-bold text-red-700 dark:text-red-300">{mockStats.criticalGaps}</p>
                </div>
                <div className="h-12 w-12 rounded-full bg-red-100 dark:bg-red-900/50 flex items-center justify-center">
                  <AlertTriangle className="h-6 w-6 text-red-600 dark:text-red-400" />
                </div>
              </div>
              <p className="text-xs text-red-500 dark:text-red-400 mt-2">Requires immediate attention</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30 border-purple-200 dark:border-purple-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-purple-600 dark:text-purple-400">Upcoming Events</p>
                  <p className="text-3xl font-bold text-purple-700 dark:text-purple-300">{upcomingEvents.length}</p>
                </div>
                <div className="h-12 w-12 rounded-full bg-purple-100 dark:bg-purple-900/50 flex items-center justify-center">
                  <Calendar className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                </div>
              </div>
              <p className="text-xs text-purple-500 dark:text-purple-400 mt-2">Scheduled this month</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/30 dark:to-cyan-950/30 border-blue-200 dark:border-blue-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-600 dark:text-blue-400">Goals Tracked</p>
                  <p className="text-3xl font-bold text-blue-700 dark:text-blue-300">{mockStats.goalsTracked}</p>
                </div>
                <div className="h-12 w-12 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center">
                  <Target className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
              </div>
              <p className="text-xs text-blue-500 dark:text-blue-400 mt-2">Active business goals</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30 border-green-200 dark:border-green-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-600 dark:text-green-400">Documents</p>
                  <p className="text-3xl font-bold text-green-700 dark:text-green-300">{mockStats.documents}</p>
                </div>
                <div className="h-12 w-12 rounded-full bg-green-100 dark:bg-green-900/50 flex items-center justify-center">
                  <FileText className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
              </div>
              <p className="text-xs text-green-500 dark:text-green-400 mt-2">Analyzed documents</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* To-Do List */}
          <Card className="lg:col-span-1">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-purple-500" />
                  To-Do List
                </CardTitle>
                <Badge
                  variant="secondary"
                  className="bg-purple-100 text-purple-700 dark:bg-purple-900/50 dark:text-purple-300"
                >
                  {todoItems.filter((t) => !t.completed).length} pending
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[280px] pr-4">
                <div className="space-y-3">
                  {todoItems.length === 0 ? (
                    <p className="text-sm text-slate-500 text-center py-8">No to-do items yet</p>
                  ) : (
                    todoItems.map((todo) => (
                      <div
                        key={todo.id}
                        className={cn(
                          "flex items-start gap-3 p-3 rounded-lg border transition-all",
                          todo.completed
                            ? "bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 opacity-60"
                            : "bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:border-purple-300 dark:hover:border-purple-700",
                        )}
                      >
                        <Checkbox
                          checked={todo.completed}
                          onCheckedChange={() => toggleEventComplete(todo.id)}
                          className="mt-0.5"
                        />
                        <div className="flex-1 min-w-0">
                          <p
                            className={cn(
                              "text-sm font-medium",
                              todo.completed ? "line-through text-slate-400" : "text-slate-700 dark:text-slate-200",
                            )}
                          >
                            {todo.title}
                          </p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={cn("w-2 h-2 rounded-full", getEventColor(todo.type))} />
                            <span className="text-xs text-slate-500">Day {todo.date}</span>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </ScrollArea>
              <Link href="/campaigns">
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full mt-3 text-purple-600 hover:text-purple-700 hover:bg-purple-50"
                >
                  View All in Calendar
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Upcoming Events */}
          <Card className="lg:col-span-1">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-blue-500" />
                  Upcoming Events
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[280px] pr-4">
                <div className="space-y-3">
                  {upcomingEvents.length === 0 ? (
                    <p className="text-sm text-slate-500 text-center py-8">No upcoming events</p>
                  ) : (
                    upcomingEvents.map((event) => (
                      <div
                        key={event.id}
                        className="p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-blue-300 dark:hover:border-blue-700 transition-all"
                      >
                        <div className="flex items-start gap-3">
                          <div className={cn("w-1 h-12 rounded-full", getEventColor(event.type))} />
                          <div className="flex-1">
                            <p className="text-sm font-medium text-slate-700 dark:text-slate-200">{event.title}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <Clock className="h-3 w-3 text-slate-400" />
                              <span className="text-xs text-slate-500">
                                Day {event.date}
                                {event.endDate && ` - ${event.endDate}`}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </ScrollArea>
              <Link href="/campaigns">
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full mt-3 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                >
                  View Calendar
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card className="lg:col-span-1">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-500" />
                  Recent Activity
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[280px] pr-4">
                <div className="space-y-3">
                  {recentActivity.map((activity) => (
                    <div
                      key={activity.id}
                      className="flex items-start gap-3 p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                    >
                      <div className="mt-0.5">{getActivityIcon(activity.type)}</div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-700 dark:text-slate-200">{activity.action}</p>
                        <p className="text-xs text-slate-500 truncate">{activity.detail}</p>
                        <p className="text-xs text-slate-400 mt-1">{activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Zap className="h-5 w-5 text-yellow-500" />
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {quickActions.map((action) => (
                <Link key={action.label} href={action.href}>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full h-20 flex flex-col items-center justify-center gap-2 transition-all hover:scale-[1.02]",
                      action.color === "purple" &&
                        "hover:border-purple-400 hover:bg-purple-50 dark:hover:bg-purple-950/30",
                      action.color === "red" && "hover:border-red-400 hover:bg-red-50 dark:hover:bg-red-950/30",
                      action.color === "blue" && "hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/30",
                      action.color === "green" && "hover:border-green-400 hover:bg-green-50 dark:hover:bg-green-950/30",
                    )}
                  >
                    <action.icon
                      className={cn(
                        "h-6 w-6",
                        action.color === "purple" && "text-purple-500",
                        action.color === "red" && "text-red-500",
                        action.color === "blue" && "text-blue-500",
                        action.color === "green" && "text-green-500",
                      )}
                    />
                    <span className="text-sm font-medium">{action.label}</span>
                  </Button>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
