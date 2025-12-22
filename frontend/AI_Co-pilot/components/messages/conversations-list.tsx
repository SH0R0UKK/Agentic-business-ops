"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, Bot, Pin } from "lucide-react"

interface Conversation {
  id: number
  name: string
  lastMessage: string
  timestamp: string
  unread: number
  isBot: boolean
  isPinned?: boolean
  avatar: string | null
}

const conversations: Conversation[] = [
  {
    id: 0,
    name: "Urban Threads AI Assistant",
    lastMessage: "How can I help you with your business today?",
    timestamp: "Always active",
    unread: 0,
    isBot: true,
    isPinned: true,
    avatar: null,
  },
  {
    id: 1,
    name: "Emma Wilson",
    lastMessage: "Do you have the cardigan in size M?",
    timestamp: "2 min ago",
    unread: 2,
    isBot: false,
    avatar: "https://i.pravatar.cc/60?img=1",
  },
  {
    id: 2,
    name: "James Chen",
    lastMessage: "What's the material of the wool scarf?",
    timestamp: "15 min ago",
    unread: 1,
    isBot: false,
    avatar: "https://i.pravatar.cc/60?img=2",
  },
  {
    id: 3,
    name: "Sarah Martinez",
    lastMessage: "Is the pleated skirt available in navy?",
    timestamp: "1 hour ago",
    unread: 0,
    isBot: false,
    avatar: "https://i.pravatar.cc/60?img=3",
  },
  {
    id: 4,
    name: "Michael Brown",
    lastMessage: "Can you check my order status? #UT2847",
    timestamp: "2 hours ago",
    unread: 3,
    isBot: false,
    avatar: "https://i.pravatar.cc/60?img=4",
  },
  {
    id: 5,
    name: "Lisa Anderson",
    lastMessage: "When will the summer collection drop?",
    timestamp: "5 hours ago",
    unread: 0,
    isBot: false,
    avatar: "https://i.pravatar.cc/60?img=5",
  },
]

interface ConversationsListProps {
  selectedConversationId: number
  onSelectConversation: (id: number) => void
}

export function ConversationsList({ selectedConversationId, onSelectConversation }: ConversationsListProps) {
  const [searchTerm, setSearchTerm] = useState("")

  const filteredConversations = conversations.filter((conversation) =>
    conversation.name.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  const pinnedConversations = filteredConversations.filter((c) => c.isPinned)
  const otherConversations = filteredConversations.filter((c) => !c.isPinned)
  const sortedConversations = [...pinnedConversations, ...otherConversations]

  return (
    <Card className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 h-full flex flex-col">
      <CardHeader className="p-3 flex-shrink-0">
        <CardTitle className="text-base font-semibold text-gray-900 dark:text-white">Messages</CardTitle>
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-8 h-8 text-sm"
          />
        </div>
      </CardHeader>
      <CardContent className="p-0 flex-1 overflow-y-auto">
        <div className="space-y-0.5">
          {sortedConversations.map((conversation) => (
            <div
              key={conversation.id}
              onClick={() => onSelectConversation(conversation.id)}
              className={`flex items-center gap-2 p-3 cursor-pointer transition-colors relative ${
                selectedConversationId === conversation.id
                  ? "bg-purple-50 dark:bg-purple-900/20 border-r-2 border-purple-600"
                  : "hover:bg-gray-50 dark:hover:bg-gray-700/50"
              }`}
            >
              {conversation.isPinned && (
                <Pin className="absolute top-1.5 right-1.5 h-3 w-3 text-purple-600 fill-purple-600" />
              )}
              <div className="relative flex-shrink-0">
                {conversation.isBot ? (
                  <div className="w-9 h-9 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/20 dark:to-pink-900/20 rounded-full flex items-center justify-center">
                    <Bot className="h-4 w-4 text-purple-600" />
                  </div>
                ) : (
                  <img
                    src={conversation.avatar || "/placeholder.svg"}
                    alt={conversation.name}
                    className="w-9 h-9 rounded-full object-cover"
                  />
                )}
                {conversation.unread > 0 && (
                  <Badge className="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] px-1 py-0 min-w-[16px] h-4 flex items-center justify-center">
                    {conversation.unread}
                  </Badge>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-0.5">
                  <h3 className="font-medium text-gray-900 dark:text-white text-sm truncate">{conversation.name}</h3>
                  <span className="text-[10px] text-gray-500 dark:text-gray-400 flex-shrink-0 ml-1">
                    {conversation.timestamp}
                  </span>
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-300 truncate">{conversation.lastMessage}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
