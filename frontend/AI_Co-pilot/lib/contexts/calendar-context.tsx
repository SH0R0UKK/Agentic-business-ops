"use client"

import type React from "react"
import { createContext, useContext, useState, useCallback } from "react"

export interface CalendarEvent {
  id: string
  date: number
  endDate?: number
  title: string
  type: string
  completed?: boolean
  isTodo?: boolean
}

export interface EventType {
  id: string
  name: string
  color: string
}

interface CalendarContextType {
  events: CalendarEvent[]
  eventTypes: EventType[]
  addEvent: (event: CalendarEvent) => void
  removeEvent: (id: string) => void
  toggleEventComplete: (id: string) => void
  addEventType: (eventType: EventType) => void
  updateEventType: (id: string, updates: Partial<EventType>) => void
  removeEventType: (id: string) => void
  deletedEvent: CalendarEvent | null
  deletedEventType: EventType | null
  undoDeleteEvent: () => void
  undoDeleteEventType: () => void
  clearDeletedEvent: () => void
  clearDeletedEventType: () => void
}

const CalendarContext = createContext<CalendarContextType | undefined>(undefined)

const initialEventTypes: EventType[] = [
  { id: "launch", name: "Product Launch", color: "purple" },
  { id: "social", name: "Social Media", color: "pink" },
  { id: "email", name: "Email Campaign", color: "blue" },
  { id: "sale", name: "Sales Event", color: "green" },
]

const initialEvents: CalendarEvent[] = [
  { id: "1", date: 5, endDate: 7, title: "Summer Collection Launch", type: "launch" },
  { id: "2", date: 12, title: "Instagram Campaign", type: "social" },
  { id: "3", date: 18, endDate: 20, title: "Email Newsletter Series", type: "email" },
  { id: "4", date: 25, endDate: 28, title: "Flash Sale Event", type: "sale" },
  { id: "5", date: 10, title: "Review influencer contracts", type: "social", isTodo: true },
  { id: "6", date: 15, title: "Prepare summer lookbook photos", type: "launch", isTodo: true },
  { id: "7", date: 22, title: "Send VIP customer emails", type: "email", isTodo: true, completed: true },
]

export function CalendarProvider({ children }: { children: React.ReactNode }) {
  const [events, setEvents] = useState<CalendarEvent[]>(initialEvents)
  const [eventTypes, setEventTypes] = useState<EventType[]>(initialEventTypes)
  const [deletedEvent, setDeletedEvent] = useState<CalendarEvent | null>(null)
  const [deletedEventType, setDeletedEventType] = useState<EventType | null>(null)

  const addEvent = useCallback((event: CalendarEvent) => {
    setEvents((prev) => [...prev, event])
  }, [])

  const removeEvent = useCallback((id: string) => {
    setEvents((prev) => {
      const eventToDelete = prev.find((e) => e.id === id)
      if (eventToDelete) {
        setDeletedEvent(eventToDelete)
      }
      return prev.filter((e) => e.id !== id)
    })
  }, [])

  const toggleEventComplete = useCallback((id: string) => {
    setEvents((prev) => prev.map((e) => (e.id === id ? { ...e, completed: !e.completed } : e)))
  }, [])

  const addEventType = useCallback((eventType: EventType) => {
    setEventTypes((prev) => [...prev, eventType])
  }, [])

  const updateEventType = useCallback((id: string, updates: Partial<EventType>) => {
    setEventTypes((prev) => prev.map((et) => (et.id === id ? { ...et, ...updates } : et)))
  }, [])

  const removeEventType = useCallback((id: string) => {
    setEventTypes((prev) => {
      const typeToDelete = prev.find((et) => et.id === id)
      if (typeToDelete) {
        setDeletedEventType(typeToDelete)
      }
      return prev.filter((et) => et.id !== id)
    })
  }, [])

  const undoDeleteEvent = useCallback(() => {
    if (deletedEvent) {
      setEvents((prev) => [...prev, deletedEvent])
      setDeletedEvent(null)
    }
  }, [deletedEvent])

  const undoDeleteEventType = useCallback(() => {
    if (deletedEventType) {
      setEventTypes((prev) => [...prev, deletedEventType])
      setDeletedEventType(null)
    }
  }, [deletedEventType])

  const clearDeletedEvent = useCallback(() => {
    setDeletedEvent(null)
  }, [])

  const clearDeletedEventType = useCallback(() => {
    setDeletedEventType(null)
  }, [])

  return (
    <CalendarContext.Provider
      value={{
        events,
        eventTypes,
        addEvent,
        removeEvent,
        toggleEventComplete,
        addEventType,
        updateEventType,
        removeEventType,
        deletedEvent,
        deletedEventType,
        undoDeleteEvent,
        undoDeleteEventType,
        clearDeletedEvent,
        clearDeletedEventType,
      }}
    >
      {children}
    </CalendarContext.Provider>
  )
}

export function useCalendarContext() {
  const context = useContext(CalendarContext)
  if (!context) {
    throw new Error("useCalendarContext must be used within CalendarProvider")
  }
  return context
}
