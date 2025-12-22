"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { MessageCircle, X, Send, Bot, User, Minimize2, Maximize2, Paperclip, GripVertical } from "lucide-react"
import { useChatContext, type Message } from "@/lib/contexts/chat-context"

const mockBotResponses = [
  "I can help you plan marketing campaigns, schedule product launches, and analyze sales trends. What would you like assistance with?",
  "Based on your sales data, I recommend launching a flash sale for the summer collection. Would you like me to create a campaign plan?",
  "Here's a suggested social media campaign for your new arrivals. Should I add this to your calendar?",
  "I've analyzed your customer engagement. Consider scheduling Instagram posts during peak hours (6-9 PM). Need help creating content?",
  "Your email open rates are strong. I can design a newsletter campaign for your fall collection launch.",
]

export function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const { messages, addMessage, isTyping, setIsTyping } = useChatContext()
  const [inputValue, setInputValue] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const dragRef = useRef<{ startX: number; startY: number; initialX: number; initialY: number } | null>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleCircleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault()
    setIsDragging(true)
    dragRef.current = {
      startX: e.clientX,
      startY: e.clientY,
      initialX: position.x,
      initialY: position.y,
    }
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true)
    dragRef.current = {
      startX: e.clientX,
      startY: e.clientY,
      initialX: position.x,
      initialY: position.y,
    }
  }

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || !dragRef.current) return
      const deltaX = e.clientX - dragRef.current.startX
      const deltaY = e.clientY - dragRef.current.startY
      setPosition({
        x: dragRef.current.initialX + deltaX,
        y: dragRef.current.initialY + deltaY,
      })
    }

    const handleMouseUp = (e: MouseEvent) => {
      if (isDragging && dragRef.current) {
        const deltaX = Math.abs(e.clientX - dragRef.current.startX)
        const deltaY = Math.abs(e.clientY - dragRef.current.startY)
        if (deltaX < 5 && deltaY < 5 && !isOpen) {
          setIsOpen(true)
        }
      }
      setIsDragging(false)
      dragRef.current = null
    }

    if (isDragging) {
      document.addEventListener("mousemove", handleMouseMove)
      document.addEventListener("mouseup", handleMouseUp)
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove)
      document.removeEventListener("mouseup", handleMouseUp)
    }
  }, [isDragging, isOpen])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    }

    addMessage(userMessage)
    setInputValue("")
    setIsTyping(true)

    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: mockBotResponses[Math.floor(Math.random() * mockBotResponses.length)],
        sender: "bot",
        timestamp: new Date(),
      }
      addMessage(botResponse)
      setIsTyping(false)
    }, 1500)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleFileUpload = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const userMessage: Message = {
        id: Date.now().toString(),
        content: `[Uploaded file: ${file.name}]`,
        sender: "user",
        timestamp: new Date(),
      }
      addMessage(userMessage)

      setTimeout(() => {
        const botResponse: Message = {
          id: (Date.now() + 1).toString(),
          content: `I've received your file "${file.name}". I'll analyze it and get back to you with insights.`,
          sender: "bot",
          timestamp: new Date(),
        }
        addMessage(botResponse)
      }, 1500)
    }
    e.target.value = ""
  }

  if (!isOpen) {
    return (
      <div
        className="fixed bottom-6 right-6 z-50"
        style={{ transform: `translate(${-position.x}px, ${-position.y}px)` }}
      >
        <div
          onMouseDown={handleCircleMouseDown}
          className="h-14 w-14 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 shadow-lg flex items-center justify-center cursor-grab active:cursor-grabbing"
        >
          <MessageCircle className="h-6 w-6 text-white pointer-events-none" />
        </div>
      </div>
    )
  }

  return (
    <div className="fixed bottom-6 right-6 z-50" style={{ transform: `translate(${-position.x}px, ${-position.y}px)` }}>
      <Card
        className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-xl transition-all duration-300 ${
          isMinimized ? "w-72 h-14" : "w-80 h-[420px]"
        }`}
      >
        <CardHeader className="p-3 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div
                className="cursor-grab active:cursor-grabbing p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                onMouseDown={handleMouseDown}
              >
                <GripVertical className="h-4 w-4 text-gray-400" />
              </div>
              <div className="p-1.5 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/20 dark:to-pink-900/20 rounded-full">
                <Bot className="h-4 w-4 text-purple-600" />
              </div>
              <div>
                <CardTitle className="text-sm font-semibold text-gray-900 dark:text-white">AI Co-pilot</CardTitle>
                {!isMinimized && <p className="text-xs text-gray-500 dark:text-gray-400">Online</p>}
              </div>
            </div>
            <div className="flex items-center gap-1">
              <Button variant="ghost" size="sm" onClick={() => setIsMinimized(!isMinimized)} className="h-7 w-7 p-0">
                {isMinimized ? <Maximize2 className="h-3 w-3" /> : <Minimize2 className="h-3 w-3" />}
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setIsOpen(false)} className="h-7 w-7 p-0">
                <X className="h-3 w-3" />
              </Button>
            </div>
          </div>
        </CardHeader>

        {!isMinimized && (
          <>
            <CardContent className="p-0 flex-1 overflow-hidden">
              <div className="h-[290px] overflow-y-auto p-3 space-y-3">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex items-start gap-2 ${message.sender === "user" ? "flex-row-reverse" : "flex-row"}`}
                  >
                    <div
                      className={`p-1.5 rounded-full flex-shrink-0 ${
                        message.sender === "user"
                          ? "bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/20 dark:to-pink-900/20"
                          : "bg-gray-100 dark:bg-gray-700"
                      }`}
                    >
                      {message.sender === "user" ? (
                        <User className="h-3 w-3 text-purple-600" />
                      ) : (
                        <Bot className="h-3 w-3 text-gray-600 dark:text-gray-400" />
                      )}
                    </div>
                    <div className={`max-w-[200px] ${message.sender === "user" ? "text-right" : "text-left"}`}>
                      <div
                        className={`p-2 rounded-lg ${
                          message.sender === "user"
                            ? "bg-gradient-to-br from-purple-500 to-pink-500 text-white"
                            : "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white"
                        }`}
                      >
                        <p className="text-xs whitespace-pre-wrap">{message.content}</p>
                      </div>
                      <p className="text-[10px] text-gray-500 dark:text-gray-400 mt-1">
                        {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </p>
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="flex items-start gap-2">
                    <div className="p-1.5 bg-gray-100 dark:bg-gray-700 rounded-full">
                      <Bot className="h-3 w-3 text-gray-600 dark:text-gray-400" />
                    </div>
                    <div className="bg-gray-100 dark:bg-gray-700 p-2 rounded-lg">
                      <div className="flex space-x-1">
                        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                        <div
                          className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: "0.1s" }}
                        ></div>
                        <div
                          className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        ></div>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            </CardContent>

            <div className="p-2 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-2">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  className="hidden"
                  accept="image/*,.pdf,.doc,.docx,.xls,.xlsx"
                />
                <Button variant="ghost" size="sm" onClick={handleFileUpload} className="h-8 w-8 p-0 flex-shrink-0">
                  <Paperclip className="h-4 w-4 text-gray-500" />
                </Button>
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything..."
                  className="flex-1 h-8 text-sm"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isTyping}
                  className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 h-8 w-8 p-0"
                  size="sm"
                >
                  <Send className="h-3 w-3" />
                </Button>
              </div>
            </div>
          </>
        )}
      </Card>
    </div>
  )
}
