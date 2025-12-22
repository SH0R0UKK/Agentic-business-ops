"use client"
import { Card, CardContent } from "@/components/ui/card"
import { MessageCircle, Users, Bot, Clock } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

const overviewData = [
  {
    title: "Unread Messages",
    value: "8",
    icon: MessageCircle,
    color: "text-purple-600",
    bgColor: "bg-purple-100 dark:bg-purple-900/20",
  },
  {
    title: "Active Conversations",
    value: "15",
    icon: Users,
    color: "text-pink-600",
    bgColor: "bg-pink-100 dark:bg-pink-900/20",
  },
  {
    title: "AI Assistance",
    value: "47",
    icon: Bot,
    color: "text-blue-600",
    bgColor: "bg-blue-100 dark:bg-blue-900/20",
  },
  {
    title: "Avg Response",
    value: "1.2h",
    icon: Clock,
    color: "text-green-600",
    bgColor: "bg-green-100 dark:bg-green-900/20",
  },
]

export function MessagesOverview() {
  return (
    <TooltipProvider>
      <div className="flex gap-2">
        {overviewData.map((item, index) => (
          <Tooltip key={index}>
            <TooltipTrigger asChild>
              <Card className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 cursor-pointer hover:border-purple-300 dark:hover:border-purple-600 transition-colors">
                <CardContent className="p-3 w-16 h-16 flex flex-col items-center justify-center">
                  <div className={`p-1.5 rounded-lg ${item.bgColor} mb-1`}>
                    <item.icon className={`h-4 w-4 ${item.color}`} />
                  </div>
                  <p className="text-sm font-bold text-gray-900 dark:text-white">{item.value}</p>
                </CardContent>
              </Card>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              <p>{item.title}</p>
            </TooltipContent>
          </Tooltip>
        ))}
      </div>
    </TooltipProvider>
  )
}
