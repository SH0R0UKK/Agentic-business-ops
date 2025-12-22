"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { MessagesOverview } from "@/components/messages/messages-overview"
import { ConversationsList } from "@/components/messages/conversations-list"
import { ChatInterface } from "@/components/messages/chat-interface"

export default function MessagesPage() {
  const [selectedConversationId, setSelectedConversationId] = useState<number>(0)

  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-64px)]">
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-4 min-h-0">
          <div className="lg:col-span-1 flex flex-col min-h-0 gap-3">
            <div className="flex-shrink-0">
              <MessagesOverview />
            </div>
            <div className="flex-1 min-h-0">
              <ConversationsList
                selectedConversationId={selectedConversationId}
                onSelectConversation={setSelectedConversationId}
              />
            </div>
          </div>
          <div className="lg:col-span-2 min-h-0">
            <ChatInterface conversationId={selectedConversationId} />
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
