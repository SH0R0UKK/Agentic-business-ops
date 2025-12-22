"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { ChevronLeft, ChevronRight, CalendarIcon, Plus, Trash2, Edit2, Check, X, Undo2 } from "lucide-react"
import { useCalendarContext, type CalendarEvent } from "@/lib/contexts/calendar-context"

const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
const months = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
]

const currentDate = new Date()
const currentMonth = currentDate.getMonth()
const currentYear = currentDate.getFullYear()

const colorOptions = ["purple", "pink", "blue", "green", "orange", "red", "yellow", "cyan"]

export default function CampaignsPage() {
  const {
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
  } = useCalendarContext()

  const [selectedDate, setSelectedDate] = useState(currentDate.getDate())
  const [viewMonth, setViewMonth] = useState(currentMonth)
  const [viewYear, setViewYear] = useState(currentYear)
  const [showYearSelector, setShowYearSelector] = useState(false)
  const [showAddEventModal, setShowAddEventModal] = useState(false)
  const [newEventTitle, setNewEventTitle] = useState("")
  const [newEventType, setNewEventType] = useState("")
  const [newEventEndDate, setNewEventEndDate] = useState("")
  const [newEventIsTodo, setNewEventIsTodo] = useState(false)
  const [editingTypeId, setEditingTypeId] = useState<string | null>(null)
  const [editingTypeName, setEditingTypeName] = useState("")
  const [newTypeName, setNewTypeName] = useState("")
  const [newTypeColor, setNewTypeColor] = useState("purple")

  useEffect(() => {
    if (deletedEvent) {
      const timer = setTimeout(() => clearDeletedEvent(), 5000)
      return () => clearTimeout(timer)
    }
  }, [deletedEvent, clearDeletedEvent])

  useEffect(() => {
    if (deletedEventType) {
      const timer = setTimeout(() => clearDeletedEventType(), 5000)
      return () => clearTimeout(timer)
    }
  }, [deletedEventType, clearDeletedEventType])

  const getDaysInMonth = (month: number, year: number) => {
    return new Date(year, month + 1, 0).getDate()
  }

  const getFirstDayOfMonth = (month: number, year: number) => {
    return new Date(year, month, 1).getDay()
  }

  const navigateMonth = (direction: "prev" | "next") => {
    if (direction === "prev") {
      if (viewMonth === 0) {
        setViewMonth(11)
        setViewYear(viewYear - 1)
      } else {
        setViewMonth(viewMonth - 1)
      }
    } else {
      if (viewMonth === 11) {
        setViewMonth(0)
        setViewYear(viewYear + 1)
      } else {
        setViewMonth(viewMonth + 1)
      }
    }
  }

  const selectMonthFromYear = (monthIndex: number) => {
    setViewMonth(monthIndex)
    setShowYearSelector(false)
  }

  const daysInMonth = getDaysInMonth(viewMonth, viewYear)
  const firstDayOfMonth = getFirstDayOfMonth(viewMonth, viewYear)
  const monthName = months[viewMonth]

  const calendarDays: (number | null)[] = []
  for (let i = 0; i < firstDayOfMonth; i++) {
    calendarDays.push(null)
  }
  for (let day = 1; day <= daysInMonth; day++) {
    calendarDays.push(day)
  }

  const getEventsForDay = (day: number) => {
    return events.filter((event) => {
      // Skip unchecked todos from calendar display
      if (event.isTodo && !event.completed) return false

      if (event.endDate) {
        return day >= event.date && day <= event.endDate
      }
      return event.date === day
    })
  }

  const getEventColor = (typeId: string) => {
    const eventType = eventTypes.find((et) => et.id === typeId)
    const color = eventType?.color || "gray"
    const colorMap: Record<string, string> = {
      purple: "bg-purple-500",
      pink: "bg-pink-500",
      blue: "bg-blue-500",
      green: "bg-green-500",
      orange: "bg-orange-500",
      red: "bg-red-500",
      yellow: "bg-yellow-500",
      cyan: "bg-cyan-500",
      gray: "bg-gray-500",
    }
    return colorMap[color] || colorMap.gray
  }

  const getEventBgColor = (typeId: string) => {
    const eventType = eventTypes.find((et) => et.id === typeId)
    const color = eventType?.color || "gray"
    const colorMap: Record<string, string> = {
      purple: "bg-purple-100 dark:bg-purple-900/30",
      pink: "bg-pink-100 dark:bg-pink-900/30",
      blue: "bg-blue-100 dark:bg-blue-900/30",
      green: "bg-green-100 dark:bg-green-900/30",
      orange: "bg-orange-100 dark:bg-orange-900/30",
      red: "bg-red-100 dark:bg-red-900/30",
      yellow: "bg-yellow-100 dark:bg-yellow-900/30",
      cyan: "bg-cyan-100 dark:bg-cyan-900/30",
      gray: "bg-gray-100 dark:bg-gray-700",
    }
    return colorMap[color] || colorMap.gray
  }

  const getDayEventPosition = (day: number, event: CalendarEvent) => {
    if (!event.endDate || event.date === event.endDate) return "single"
    if (day === event.date) return "start"
    if (day === event.endDate) return "end"
    return "middle"
  }

  const handleDayClick = (day: number) => {
    setSelectedDate(day)
    setShowAddEventModal(true)
  }

  const handleAddEvent = () => {
    if (!newEventTitle.trim() || !newEventType) return
    const newEvent: CalendarEvent = {
      id: Date.now().toString(),
      date: selectedDate,
      endDate: newEventEndDate ? Number.parseInt(newEventEndDate) : undefined,
      title: newEventTitle,
      type: newEventType,
      isTodo: newEventIsTodo,
      completed: false,
    }
    addEvent(newEvent)
    setNewEventTitle("")
    setNewEventType("")
    setNewEventEndDate("")
    setNewEventIsTodo(false)
    setShowAddEventModal(false)
  }

  const handleAddEventType = () => {
    if (!newTypeName.trim()) return
    addEventType({
      id: newTypeName.toLowerCase().replace(/\s+/g, "-"),
      name: newTypeName,
      color: newTypeColor,
    })
    setNewTypeName("")
    setNewTypeColor("purple")
  }

  const handleUpdateEventType = (id: string) => {
    if (!editingTypeName.trim()) return
    updateEventType(id, { name: editingTypeName })
    setEditingTypeId(null)
    setEditingTypeName("")
  }

  const todoEvents = events.filter((e) => e.isTodo)
  const selectedDayEvents = getEventsForDay(selectedDate)

  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-80px)] gap-3">
        {deletedEvent && (
          <Alert className="bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
            <AlertDescription className="flex items-center justify-between">
              <span className="text-sm">Event "{deletedEvent.title}" deleted</span>
              <Button variant="ghost" size="sm" onClick={undoDeleteEvent} className="h-7 gap-1">
                <Undo2 className="h-3 w-3" /> Undo
              </Button>
            </AlertDescription>
          </Alert>
        )}
        {deletedEventType && (
          <Alert className="bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
            <AlertDescription className="flex items-center justify-between">
              <span className="text-sm">Event type "{deletedEventType.name}" deleted</span>
              <Button variant="ghost" size="sm" onClick={undoDeleteEventType} className="h-7 gap-1">
                <Undo2 className="h-3 w-3" /> Undo
              </Button>
            </AlertDescription>
          </Alert>
        )}

        <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-3 min-h-0">
          {/* Calendar - takes more space */}
          <div className="lg:col-span-7">
            <Card className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 h-full flex flex-col">
              <CardHeader className="p-2 flex-shrink-0">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-semibold text-gray-900 dark:text-white">
                    Campaign Calendar
                  </CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 w-7 p-0"
                    onClick={() => setShowYearSelector(!showYearSelector)}
                  >
                    <CalendarIcon className="h-4 w-4 text-purple-600" />
                  </Button>
                </div>
                <div className="flex items-center justify-between mt-1">
                  <h3 className="text-xs font-medium text-gray-900 dark:text-white">
                    {monthName} {viewYear}
                  </h3>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-6 w-6 p-0 bg-transparent"
                      onClick={() => navigateMonth("prev")}
                    >
                      <ChevronLeft className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-6 w-6 p-0 bg-transparent"
                      onClick={() => navigateMonth("next")}
                    >
                      <ChevronRight className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-2 pt-0 flex-1 overflow-auto">
                {showYearSelector && (
                  <div className="mb-2 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0"
                        onClick={() => setViewYear(viewYear - 1)}
                      >
                        <ChevronLeft className="h-3 w-3" />
                      </Button>
                      <span className="font-medium text-xs">{viewYear}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0"
                        onClick={() => setViewYear(viewYear + 1)}
                      >
                        <ChevronRight className="h-3 w-3" />
                      </Button>
                    </div>
                    <div className="grid grid-cols-4 gap-1">
                      {months.map((month, index) => (
                        <Button
                          key={month}
                          variant={viewMonth === index ? "default" : "ghost"}
                          size="sm"
                          className={`text-[10px] h-6 ${viewMonth === index ? "bg-purple-500 hover:bg-purple-600" : ""}`}
                          onClick={() => selectMonthFromYear(index)}
                        >
                          {month.slice(0, 3)}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-7 gap-0.5 mb-1">
                  {daysOfWeek.map((day) => (
                    <div
                      key={day}
                      className="p-0.5 text-center text-[10px] font-medium text-gray-500 dark:text-gray-400"
                    >
                      {day}
                    </div>
                  ))}
                </div>
                <div className="grid grid-cols-7 gap-0.5">
                  {calendarDays.map((day, index) => {
                    const dayEvents = day ? getEventsForDay(day) : []
                    const mainEvent = dayEvents[0]
                    const position = mainEvent && day ? getDayEventPosition(day, mainEvent) : null

                    return (
                      <div key={index} className="aspect-square relative">
                        {day && (
                          <button
                            onClick={() => handleDayClick(day)}
                            className={`w-full h-full flex flex-col items-center justify-center text-[11px] transition-colors relative overflow-hidden ${
                              day === selectedDate
                                ? "bg-gradient-to-br from-purple-500 to-pink-500 text-white font-semibold rounded-lg"
                                : mainEvent
                                  ? `${getEventBgColor(mainEvent.type)} ${
                                      position === "start"
                                        ? "rounded-l-md"
                                        : position === "end"
                                          ? "rounded-r-md"
                                          : position === "middle"
                                            ? "rounded-none"
                                            : "rounded-md"
                                    }`
                                  : "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-white rounded-md"
                            }`}
                          >
                            {day}
                            {dayEvents.length > 0 && day !== selectedDate && (
                              <div className="flex gap-0.5 mt-0.5">
                                {dayEvents.slice(0, 2).map((event, i) => (
                                  <div key={i} className={`w-1 h-1 rounded-full ${getEventColor(event.type)}`}></div>
                                ))}
                              </div>
                            )}
                          </button>
                        )}
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Side panels - minimized */}
          <div className="lg:col-span-5 flex flex-col gap-3">
            {/* Selected Day Events - compact */}
            <Card className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 flex-shrink-0">
              <CardHeader className="p-2">
                <CardTitle className="text-xs font-semibold text-gray-900 dark:text-white">
                  {selectedDate} {monthName}
                </CardTitle>
              </CardHeader>
              <CardContent className="p-2 pt-0 max-h-24 overflow-y-auto">
                {selectedDayEvents.length > 0 ? (
                  <div className="space-y-1">
                    {selectedDayEvents.map((event) => (
                      <div
                        key={event.id}
                        className="flex items-center justify-between p-1.5 bg-gray-50 dark:bg-gray-700 rounded text-xs"
                      >
                        <div className="flex items-center gap-1.5">
                          <span className={`w-2 h-2 rounded-full ${getEventColor(event.type)}`}></span>
                          <span className="text-gray-900 dark:text-white truncate max-w-[120px]">{event.title}</span>
                        </div>
                        <Button variant="ghost" size="sm" className="h-5 w-5 p-0" onClick={() => removeEvent(event.id)}>
                          <Trash2 className="h-3 w-3 text-red-500" />
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-[10px] text-gray-500 dark:text-gray-400 text-center py-2">No events</p>
                )}
              </CardContent>
            </Card>

            {/* To-Do Events - compact */}
            <Card className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 flex-1 flex flex-col min-h-0">
              <CardHeader className="p-2 flex-shrink-0">
                <CardTitle className="text-xs font-semibold text-gray-900 dark:text-white">To-Do Events</CardTitle>
                <p className="text-[10px] text-gray-500">Check to show on calendar</p>
              </CardHeader>
              <CardContent className="p-2 pt-0 flex-1 overflow-y-auto">
                {todoEvents.length > 0 ? (
                  <div className="space-y-1">
                    {todoEvents.map((todo) => (
                      <div
                        key={todo.id}
                        className={`flex items-center gap-1.5 p-1.5 rounded text-xs ${
                          todo.completed ? "bg-green-50 dark:bg-green-900/20" : "bg-gray-50 dark:bg-gray-700"
                        }`}
                      >
                        <Checkbox
                          checked={todo.completed}
                          onCheckedChange={() => toggleEventComplete(todo.id)}
                          className="h-3 w-3"
                        />
                        <div className="flex-1 min-w-0">
                          <p
                            className={`text-[11px] truncate ${todo.completed ? "line-through text-gray-400" : "text-gray-900 dark:text-white"}`}
                          >
                            {todo.title}
                          </p>
                        </div>
                        <Button variant="ghost" size="sm" className="h-4 w-4 p-0" onClick={() => removeEvent(todo.id)}>
                          <Trash2 className="h-2.5 w-2.5 text-red-500" />
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-[10px] text-gray-500 dark:text-gray-400 text-center py-2">No to-do items</p>
                )}
              </CardContent>
            </Card>

            {/* Event Types - compact */}
            <Card className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 flex-shrink-0">
              <CardHeader className="p-2">
                <CardTitle className="text-xs font-semibold text-gray-900 dark:text-white">Event Types</CardTitle>
              </CardHeader>
              <CardContent className="p-2 pt-0 max-h-32 overflow-y-auto space-y-1">
                {eventTypes.map((type) => (
                  <div
                    key={type.id}
                    className="flex items-center gap-1.5 p-1 bg-gray-50 dark:bg-gray-700 rounded text-xs"
                  >
                    <div className={`w-2.5 h-2.5 rounded-full bg-${type.color}-500`}></div>
                    {editingTypeId === type.id ? (
                      <>
                        <Input
                          value={editingTypeName}
                          onChange={(e) => setEditingTypeName(e.target.value)}
                          className="flex-1 h-5 text-[10px] px-1"
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-4 w-4 p-0"
                          onClick={() => handleUpdateEventType(type.id)}
                        >
                          <Check className="h-2.5 w-2.5 text-green-500" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-4 w-4 p-0"
                          onClick={() => setEditingTypeId(null)}
                        >
                          <X className="h-2.5 w-2.5 text-gray-500" />
                        </Button>
                      </>
                    ) : (
                      <>
                        <span className="flex-1 text-[11px] text-gray-700 dark:text-gray-300 truncate">
                          {type.name}
                        </span>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-4 w-4 p-0"
                          onClick={() => {
                            setEditingTypeId(type.id)
                            setEditingTypeName(type.name)
                          }}
                        >
                          <Edit2 className="h-2.5 w-2.5 text-gray-500" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-4 w-4 p-0"
                          onClick={() => removeEventType(type.id)}
                        >
                          <Trash2 className="h-2.5 w-2.5 text-red-500" />
                        </Button>
                      </>
                    )}
                  </div>
                ))}

                <div className="pt-1 border-t border-gray-200 dark:border-gray-600">
                  <div className="flex items-center gap-1">
                    <Select value={newTypeColor} onValueChange={setNewTypeColor}>
                      <SelectTrigger className="w-10 h-5 text-[10px] px-1">
                        <div className={`w-2.5 h-2.5 rounded-full bg-${newTypeColor}-500`}></div>
                      </SelectTrigger>
                      <SelectContent>
                        {colorOptions.map((color) => (
                          <SelectItem key={color} value={color}>
                            <div className="flex items-center gap-1">
                              <div className={`w-2.5 h-2.5 rounded-full bg-${color}-500`}></div>
                              <span className="text-[10px] capitalize">{color}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Input
                      value={newTypeName}
                      onChange={(e) => setNewTypeName(e.target.value)}
                      placeholder="New type..."
                      className="flex-1 h-5 text-[10px] px-1"
                    />
                    <Button
                      size="sm"
                      className="h-5 w-5 p-0 bg-purple-500 hover:bg-purple-600"
                      onClick={handleAddEventType}
                    >
                      <Plus className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Add Event Modal */}
      <Dialog open={showAddEventModal} onOpenChange={setShowAddEventModal}>
        <DialogContent className="sm:max-w-[350px]">
          <DialogHeader>
            <DialogTitle className="text-sm">
              Add Event - {selectedDate} {monthName}
            </DialogTitle>
          </DialogHeader>
          <div className="grid gap-3 py-3">
            <Input
              placeholder="Event title"
              value={newEventTitle}
              onChange={(e) => setNewEventTitle(e.target.value)}
              className="h-8 text-sm"
            />
            <Select value={newEventType} onValueChange={setNewEventType}>
              <SelectTrigger className="h-8 text-sm">
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                {eventTypes.map((type) => (
                  <SelectItem key={type.id} value={type.id}>
                    <div className="flex items-center gap-2">
                      <div className={`w-2.5 h-2.5 rounded-full bg-${type.color}-500`}></div>
                      <span className="text-sm">{type.name}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              type="number"
              placeholder="End date (optional)"
              value={newEventEndDate}
              onChange={(e) => setNewEventEndDate(e.target.value)}
              min={selectedDate}
              max={daysInMonth}
              className="h-8 text-sm"
            />
            <div className="flex items-center gap-2">
              <Checkbox
                id="isTodo"
                checked={newEventIsTodo}
                onCheckedChange={(checked) => setNewEventIsTodo(checked as boolean)}
              />
              <label htmlFor="isTodo" className="text-sm text-gray-700 dark:text-gray-300">
                Add as To-Do item
              </label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setShowAddEventModal(false)}>
              Cancel
            </Button>
            <Button size="sm" className="bg-purple-500 hover:bg-purple-600" onClick={handleAddEvent}>
              Add Event
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  )
}
