"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send, Bot, User, MoreVertical, Paperclip } from "lucide-react"
import { useChatContext, type Message } from "@/lib/contexts/chat-context"

const conversationData: Record<number, { name: string; avatar: string | null; isBot: boolean; messages: Message[] }> = {
  1: {
    name: "Emma Wilson",
    avatar: "https://i.pravatar.cc/60?img=1",
    isBot: false,
    messages: [
      {
        id: "1",
        content: "Hi! I'm interested in the oversized cardigan I saw on your Instagram. Do you have it in medium?",
        sender: "user",
        timestamp: new Date(Date.now() - 300000),
      },
      {
        id: "2",
        content:
          "Hello! Thank you for your interest in our oversized cardigan. Yes, we have it available in Medium! The cardigan is made from 100% merino wool and comes in three colors: Cream, Charcoal, and Sage Green.\n\n**Product Details:**\n- Price: $89\n- Sizes: XS - XL\n- Material: 100% Merino Wool\n- Care: Hand wash cold\n\nWould you like to know more about sizing or place an order?",
        sender: "bot",
        timestamp: new Date(Date.now() - 240000),
      },
      {
        id: "3",
        content: "Perfect! I'd like the sage green one. How long does shipping usually take?",
        sender: "user",
        timestamp: new Date(Date.now() - 180000),
      },
      {
        id: "4",
        content:
          "Excellent choice! The Sage Green is one of our bestsellers this season.\n\n**Shipping Information:**\n- Standard Shipping: 5-7 business days (Free on orders over $100)\n- Express Shipping: 2-3 business days ($15)\n- Next Day: Available in select areas ($25)\n\nAll orders ship within 24 hours on business days. Would you like me to help you complete your order?",
        sender: "bot",
        timestamp: new Date(Date.now() - 120000),
      },
    ],
  },
  2: {
    name: "James Chen",
    avatar: "https://i.pravatar.cc/60?img=2",
    isBot: false,
    messages: [
      {
        id: "1",
        content: "Hi there! What's the material of your wool scarves? Are they pure wool or a blend?",
        sender: "user",
        timestamp: new Date(Date.now() - 900000),
      },
      {
        id: "2",
        content:
          'Hello James! Great question about our scarves.\n\n**Wool Scarf Specifications:**\n- Material: 100% Merino Wool (no blend)\n- Dimensions: 70" x 28"\n- Weight: Lightweight yet warm\n- Price: $65\n- Available Colors: 8 options including Charcoal, Navy, Burgundy, and Camel\n\nOur merino wool is incredibly soft, naturally temperature-regulating, and hypoallergenic. Would you like to see specific color options?',
        sender: "bot",
        timestamp: new Date(Date.now() - 840000),
      },
      {
        id: "3",
        content: "That sounds perfect! Do you have the charcoal color in stock?",
        sender: "user",
        timestamp: new Date(Date.now() - 720000),
      },
    ],
  },
  3: {
    name: "Sarah Martinez",
    avatar: "https://i.pravatar.cc/60?img=3",
    isBot: false,
    messages: [
      {
        id: "1",
        content: "Hello! I love the pleated midi skirt on your website. Is it available in navy blue?",
        sender: "user",
        timestamp: new Date(Date.now() - 7200000),
      },
      {
        id: "2",
        content:
          'Hi Sarah! Yes, the pleated midi skirt is absolutely available in Navy Blue!\n\n**Pleated Midi Skirt Details:**\n- Price: $78\n- Available Colors: Navy, Black, Burgundy, Olive\n- Sizes: XS - XL\n- Material: Polyester blend (wrinkle-resistant)\n- Length: 28" (midi)\n- Features: Elastic waistband, pleated design, lined\n\nThe navy is a beautiful deep shade that pairs wonderfully with both casual and dressy tops. What size would you need?',
        sender: "bot",
        timestamp: new Date(Date.now() - 7140000),
      },
    ],
  },
  4: {
    name: "Michael Brown",
    avatar: "https://i.pravatar.cc/60?img=4",
    isBot: false,
    messages: [
      {
        id: "1",
        content:
          "Hi, I placed an order last week (order #UT2847) and I haven't received a shipping notification yet. Can you check the status?",
        sender: "user",
        timestamp: new Date(Date.now() - 10800000),
      },
      {
        id: "2",
        content:
          "Hello Michael! Let me check that for you right away.\n\nI've looked up order #UT2847. Your order was processed and shipped yesterday! Here are the details:\n\n**Order Status:**\n- Status: Shipped\n- Tracking #: 1Z999AA10123456784\n- Carrier: UPS Ground\n- Expected Delivery: 2-3 business days\n- Items: Black Crew Neck Sweater (L), Grey Chinos (32)\n\nYou should have received a shipping confirmation email. Would you like me to resend it to your email on file?",
        sender: "bot",
        timestamp: new Date(Date.now() - 10740000),
      },
      {
        id: "3",
        content: "Oh great! I must have missed the email. No need to resend, thank you for the tracking number!",
        sender: "user",
        timestamp: new Date(Date.now() - 10680000),
      },
    ],
  },
  5: {
    name: "Lisa Anderson",
    avatar: "https://i.pravatar.cc/60?img=5",
    isBot: false,
    messages: [
      {
        id: "1",
        content: "Hey! I'm excited about your new collection. When will the summer line be available?",
        sender: "user",
        timestamp: new Date(Date.now() - 18000000),
      },
      {
        id: "2",
        content:
          "Hi Lisa! We're thrilled about the summer collection too!\n\n**Summer Collection Launch:**\n- Launch Date: June 1st, 2024\n- Early Access: May 28th for newsletter subscribers\n- Preview: Sneak peeks starting May 15th on Instagram\n- Special Offer: 15% off for first 48 hours\n\nThe collection features lightweight linens, breezy dresses, and our signature printed scarves. Would you like me to add you to our VIP early access list?",
        sender: "bot",
        timestamp: new Date(Date.now() - 17940000),
      },
    ],
  },
}

interface ChatInterfaceProps {
  conversationId: number
}

export function ChatInterface({ conversationId }: ChatInterfaceProps) {
  const chatContext = useChatContext()
  const isAIAssistant = conversationId === 0

  const customerConversation = conversationData[conversationId]

  const [localMessages, setLocalMessages] = useState<Message[]>(customerConversation?.messages || [])
  const [inputValue, setInputValue] = useState("")
  const [localIsTyping, setLocalIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const messages = isAIAssistant ? chatContext.messages : localMessages
  const isTyping = isAIAssistant ? chatContext.isTyping : localIsTyping

  useEffect(() => {
    if (!isAIAssistant && customerConversation) {
      setLocalMessages(customerConversation.messages)
    }
  }, [conversationId, isAIAssistant, customerConversation])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const mockBotResponses = isAIAssistant
    ? [
        "I can help you plan marketing campaigns, schedule product launches, and analyze sales trends. What would you like assistance with?",
        "Based on your sales data, I recommend launching a flash sale for the summer collection. Would you like me to create a campaign plan?",
        "Here's a suggested social media campaign for your new arrivals. Should I add this to your calendar?",
        "I've analyzed your customer engagement. Consider scheduling Instagram posts during peak hours (6-9 PM). Need help creating content?",
      ]
    : [
        "Our cashmere items are incredibly soft and perfect for the season! They're available in multiple colors. Would you like to see our full collection?",
        "Yes, that item is currently in stock in all sizes! Would you like me to help you place an order?",
        "I'd be happy to check that for you! Your order is on its way and should arrive within 2-3 business days.",
        "That's a great choice! We have that available in multiple colors. Which one would you prefer?",
      ]

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    }

    if (isAIAssistant) {
      chatContext.addMessage(userMessage)
      chatContext.setIsTyping(true)
    } else {
      setLocalMessages((prev) => [...prev, userMessage])
      setLocalIsTyping(true)
    }

    setInputValue("")

    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: mockBotResponses[Math.floor(Math.random() * mockBotResponses.length)],
        sender: "bot",
        timestamp: new Date(),
      }
      if (isAIAssistant) {
        chatContext.addMessage(botResponse)
        chatContext.setIsTyping(false)
      } else {
        setLocalMessages((prev) => [...prev, botResponse])
        setLocalIsTyping(false)
      }
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

      if (isAIAssistant) {
        chatContext.addMessage(userMessage)
        chatContext.setIsTyping(true)
      } else {
        setLocalMessages((prev) => [...prev, userMessage])
        setLocalIsTyping(true)
      }

      setTimeout(() => {
        const botResponse: Message = {
          id: (Date.now() + 1).toString(),
          content: `I've received your file "${file.name}". I'll analyze it and get back to you with insights.`,
          sender: "bot",
          timestamp: new Date(),
        }
        if (isAIAssistant) {
          chatContext.addMessage(botResponse)
          chatContext.setIsTyping(false)
        } else {
          setLocalMessages((prev) => [...prev, botResponse])
          setLocalIsTyping(false)
        }
      }, 1500)
    }
    e.target.value = ""
  }

  const conversationName = isAIAssistant ? "Urban Threads AI Assistant" : customerConversation?.name || "Unknown"
  const conversationAvatar = isAIAssistant ? null : customerConversation?.avatar

  return (
    <Card className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 h-full flex flex-col">
      <CardHeader className="p-3 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {isAIAssistant ? (
              <div className="w-8 h-8 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/20 dark:to-pink-900/20 rounded-full flex items-center justify-center">
                <Bot className="h-4 w-4 text-purple-600" />
              </div>
            ) : (
              <img
                src={conversationAvatar || "/placeholder.svg"}
                alt={conversationName}
                className="w-8 h-8 rounded-full object-cover"
              />
            )}
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white text-sm">{conversationName}</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {isAIAssistant ? "AI Assistant" : "Active now"}
              </p>
            </div>
          </div>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
            <MoreVertical className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="flex-1 p-0 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-3 space-y-3">
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
              <div className={`max-w-md ${message.sender === "user" ? "text-right" : "text-left"}`}>
                <div
                  className={`p-3 rounded-lg ${
                    message.sender === "user"
                      ? "bg-gradient-to-br from-purple-500 to-pink-500 text-white"
                      : "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
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
              <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.1s" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  ></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="p-3 border-t border-gray-200 dark:border-gray-700 flex-shrink-0 bg-white dark:bg-gray-800">
          <div className="flex items-center gap-2">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="hidden"
              accept="image/*,.pdf,.doc,.docx,.xls,.xlsx"
            />
            <Button variant="ghost" size="sm" onClick={handleFileUpload} className="h-9 w-9 p-0 flex-shrink-0">
              <Paperclip className="h-4 w-4 text-gray-500" />
            </Button>
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 h-9"
            />
            <Button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isTyping}
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 h-9"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
