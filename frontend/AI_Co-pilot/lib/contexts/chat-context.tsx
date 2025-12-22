"use client"

import type React from "react"
import { createContext, useContext, useState, useCallback } from "react"

export interface Message {
  id: string
  content: string
  sender: "user" | "bot"
  timestamp: Date
}

interface ChatContextType {
  messages: Message[]
  addMessage: (message: Message) => void
  isTyping: boolean
  setIsTyping: (typing: boolean) => void
}

const ChatContext = createContext<ChatContextType | undefined>(undefined)

const initialMessages: Message[] = [
  {
    id: "1",
    content:
      "Hello! I'm your AI Co-pilot. I can help you with:\n\n• Planning marketing campaigns\n• Scheduling product launches\n• Analyzing sales trends\n• Managing inventory\n• Customer insights\n\nWhat would you like assistance with today?",
    sender: "bot",
    timestamp: new Date(Date.now() - 3600000),
  },
]

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [isTyping, setIsTyping] = useState(false)

  const addMessage = useCallback((message: Message) => {
    setMessages((prev) => [...prev, message])
  }, [])

  return <ChatContext.Provider value={{ messages, addMessage, isTyping, setIsTyping }}>{children}</ChatContext.Provider>
}

export function useChatContext() {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error("useChatContext must be used within ChatProvider")
  }
  return context
}
