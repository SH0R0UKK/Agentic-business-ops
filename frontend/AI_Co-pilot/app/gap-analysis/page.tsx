"use client"

import { useState, useMemo } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  AlertTriangle,
  Target,
  TrendingUp,
  ChevronDown,
  ChevronRight,
  Filter,
  X,
  AlertCircle,
  Building2,
  Globe,
  Percent,
  ShieldAlert,
} from "lucide-react"
import { cn } from "@/lib/utils"

// Types
interface Gap {
  id: string
  type: "internal" | "market"
  description: string
  confidence: number
  goalBlocking: boolean
  threat: "high" | "medium" | "low"
  reasoning: string
  critical: boolean
}

// Mock data based on backend output structure
const mockGaps: Gap[] = [
  {
    id: "1",
    type: "internal",
    description: "Inventory tracking system lacks real-time sync with e-commerce platform",
    confidence: 0.92,
    goalBlocking: true,
    threat: "high",
    reasoning:
      "The current inventory system updates every 4 hours, causing overselling issues during high-traffic periods. This directly impacts customer satisfaction and revenue. Implementation of real-time webhooks would resolve this gap within 2-3 sprint cycles.",
    critical: true,
  },
  {
    id: "2",
    type: "internal",
    description: "Customer service response time exceeds industry benchmark by 40%",
    confidence: 0.85,
    goalBlocking: true,
    threat: "medium",
    reasoning:
      "Average response time is 8 hours compared to industry standard of 4 hours. This is primarily due to manual ticket routing. AI-powered routing could reduce this to under 2 hours.",
    critical: true,
  },
  {
    id: "3",
    type: "internal",
    description: "Marketing automation lacks personalization capabilities",
    confidence: 0.78,
    goalBlocking: false,
    threat: "medium",
    reasoning:
      "Current email campaigns use basic segmentation. Implementing behavioral triggers and purchase history analysis would increase conversion rates by an estimated 25%.",
    critical: false,
  },
  {
    id: "4",
    type: "internal",
    description: "Returns processing workflow requires manual intervention at 3 stages",
    confidence: 0.71,
    goalBlocking: false,
    threat: "low",
    reasoning:
      "Manual steps add 2-3 days to return processing. Automation of quality assessment and refund approval would streamline operations significantly.",
    critical: false,
  },
  {
    id: "5",
    type: "market",
    description: "Competitors offering same-day delivery in major metros",
    confidence: 0.88,
    goalBlocking: true,
    threat: "high",
    reasoning:
      "Three major competitors now offer same-day delivery in top 10 metro areas. Our 3-5 day standard shipping is becoming a competitive disadvantage. Partnership with local fulfillment centers is recommended.",
    critical: true,
  },
  {
    id: "6",
    type: "market",
    description: "Emerging sustainable fashion trend not addressed in current product line",
    confidence: 0.82,
    goalBlocking: false,
    threat: "high",
    reasoning:
      "Sustainable fashion market growing at 15% YoY. Current product line has no eco-friendly options. Launching a sustainable collection could capture an estimated $2M in new revenue.",
    critical: true,
  },
  {
    id: "7",
    type: "market",
    description: "Social commerce integration lagging behind industry adoption",
    confidence: 0.75,
    goalBlocking: false,
    threat: "medium",
    reasoning:
      "Instagram and TikTok shop integrations are standard in the industry. Our current social presence is promotional only. Direct purchasing could increase social conversion by 300%.",
    critical: false,
  },
  {
    id: "8",
    type: "market",
    description: "Limited presence in growing athleisure segment",
    confidence: 0.68,
    goalBlocking: false,
    threat: "medium",
    reasoning:
      "Athleisure market expected to grow 8% annually. Current offering represents only 5% of catalog. Expansion into this segment aligns with brand positioning.",
    critical: false,
  },
  {
    id: "9",
    type: "market",
    description: "Competitor loyalty program offers superior rewards structure",
    confidence: 0.65,
    goalBlocking: false,
    threat: "low",
    reasoning:
      "Competitor loyalty programs offer 2-3x more value per dollar spent. Revamping our rewards structure could improve customer retention by 15%.",
    critical: false,
  },
]

export default function GapAnalysisPage() {
  const [selectedGap, setSelectedGap] = useState<Gap | null>(null)
  const [filterType, setFilterType] = useState<"all" | "internal" | "market">("all")
  const [filterCriticalOnly, setFilterCriticalOnly] = useState(false)
  const [confidenceThreshold, setConfidenceThreshold] = useState(0)
  const [sortBy, setSortBy] = useState<"confidence" | "threat" | "goalBlocking">("confidence")
  const [expandedCards, setExpandedCards] = useState<Set<string>>(new Set())

  // Filter and sort gaps
  const filteredGaps = useMemo(() => {
    let result = [...mockGaps]

    // Filter by type
    if (filterType !== "all") {
      result = result.filter((gap) => gap.type === filterType)
    }

    // Filter by critical
    if (filterCriticalOnly) {
      result = result.filter((gap) => gap.critical)
    }

    // Filter by confidence threshold
    result = result.filter((gap) => gap.confidence >= confidenceThreshold / 100)

    // Sort
    result.sort((a, b) => {
      switch (sortBy) {
        case "confidence":
          return b.confidence - a.confidence
        case "threat":
          const threatOrder = { high: 3, medium: 2, low: 1 }
          return threatOrder[b.threat] - threatOrder[a.threat]
        case "goalBlocking":
          return (b.goalBlocking ? 1 : 0) - (a.goalBlocking ? 1 : 0)
        default:
          return 0
      }
    })

    return result
  }, [filterType, filterCriticalOnly, confidenceThreshold, sortBy])

  // Separate internal and market gaps
  const internalGaps = filteredGaps.filter((g) => g.type === "internal")
  const marketGaps = filteredGaps.filter((g) => g.type === "market")

  // KPI calculations
  const totalGaps = mockGaps.length
  const criticalGaps = mockGaps.filter((g) => g.critical).length
  const internalGapsCount = mockGaps.filter((g) => g.type === "internal").length
  const marketGapsCount = mockGaps.filter((g) => g.type === "market").length

  // Chart data
  const pieData = [
    { name: "Internal", value: internalGapsCount, color: "#3b82f6" },
    { name: "Market", value: marketGapsCount, color: "#f97316" },
  ]

  const pieDataWithCritical = [
    {
      name: "Internal (Critical)",
      value: mockGaps.filter((g) => g.type === "internal" && g.critical).length,
      color: "#1d4ed8",
    },
    {
      name: "Internal (Non-Critical)",
      value: mockGaps.filter((g) => g.type === "internal" && !g.critical).length,
      color: "#93c5fd",
    },
    {
      name: "Market (Critical)",
      value: mockGaps.filter((g) => g.type === "market" && g.critical).length,
      color: "#c2410c",
    },
    {
      name: "Market (Non-Critical)",
      value: mockGaps.filter((g) => g.type === "market" && !g.critical).length,
      color: "#fdba74",
    },
  ]

  const confidenceBarData = mockGaps.map((gap) => ({
    name: gap.description.substring(0, 20) + "...",
    confidence: Math.round(gap.confidence * 100),
    fill: gap.type === "internal" ? "#3b82f6" : "#f97316",
    critical: gap.critical,
    fullDescription: gap.description,
  }))

  const threatBarData = mockGaps
    .filter((g) => g.type === "market")
    .map((gap) => ({
      name: gap.description.substring(0, 25) + "...",
      value: gap.threat === "high" ? 3 : gap.threat === "medium" ? 2 : 1,
      fill: gap.threat === "high" ? "#ef4444" : gap.threat === "medium" ? "#f97316" : "#eab308",
      threat: gap.threat,
      fullDescription: gap.description,
    }))

  const toggleCardExpansion = (id: string) => {
    const newExpanded = new Set(expandedCards)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedCards(newExpanded)
  }

  const getThreatColor = (threat: string) => {
    switch (threat) {
      case "high":
        return "bg-red-500/20 text-red-400 border-red-500/30"
      case "medium":
        return "bg-orange-500/20 text-orange-400 border-orange-500/30"
      case "low":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
      default:
        return "bg-slate-500/20 text-slate-400 border-slate-500/30"
    }
  }

  const GapCard = ({ gap }: { gap: Gap }) => {
    const isExpanded = expandedCards.has(gap.id)
    const isSelected = selectedGap?.id === gap.id

    return (
      <Card
        className={cn(
          "cursor-pointer transition-all duration-200 hover:shadow-md",
          gap.critical
            ? "border-red-500/50 bg-red-500/5 dark:bg-red-500/10"
            : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800",
          isSelected && "ring-2 ring-purple-500 ring-offset-2 dark:ring-offset-slate-900",
        )}
        onClick={() => setSelectedGap(gap)}
      >
        <CardHeader className="pb-2 pt-3 px-4">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2 flex-1">
              <CardTitle className="text-sm font-medium leading-tight line-clamp-2">{gap.description}</CardTitle>
            </div>
          </div>
        </CardHeader>
        <CardContent className="px-4 pb-3 pt-0">
          <div className="flex items-center gap-2 flex-wrap mb-2">
            <Badge variant="outline" className="text-xs">
              <Percent className="h-3 w-3 mr-1" />
              {Math.round(gap.confidence * 100)}%
            </Badge>
            {gap.goalBlocking && (
              <Badge variant="outline" className="text-xs bg-purple-500/10 text-purple-600 border-purple-500/30">
                <Target className="h-3 w-3 mr-1" />
                Goal Blocking
              </Badge>
            )}
            <Badge variant="outline" className={cn("text-xs", getThreatColor(gap.threat))}>
              <ShieldAlert className="h-3 w-3 mr-1" />
              {gap.threat.charAt(0).toUpperCase() + gap.threat.slice(1)}
            </Badge>
          </div>

          <Collapsible open={isExpanded} onOpenChange={() => toggleCardExpansion(gap.id)}>
            <CollapsibleTrigger asChild onClick={(e) => e.stopPropagation()}>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 px-2 text-xs text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
              >
                {isExpanded ? (
                  <>
                    <ChevronDown className="h-3 w-3 mr-1" /> Hide reasoning
                  </>
                ) : (
                  <>
                    <ChevronRight className="h-3 w-3 mr-1" /> Show reasoning
                  </>
                )}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-2 leading-relaxed bg-slate-50 dark:bg-slate-700/50 p-2 rounded">
                {gap.reasoning}
              </p>
            </CollapsibleContent>
          </Collapsible>
        </CardContent>
      </Card>
    )
  }

  return (
    <DashboardLayout>
      <div className="p-4 space-y-4 bg-slate-50 dark:bg-slate-900 min-h-screen">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Gap Analysis Dashboard</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">Identify and prioritize business gaps</p>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Card className="bg-gradient-to-br from-slate-700 to-slate-800 text-white border-0">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-white/20 rounded-lg">
                  <AlertTriangle className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{totalGaps}</p>
                  <p className="text-xs text-white/70">Total Gaps</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-red-600 to-red-700 text-white border-0">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-white/20 rounded-lg">
                  <AlertCircle className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{criticalGaps}</p>
                  <p className="text-xs text-white/70">Critical Gaps</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-white/20 rounded-lg">
                  <Building2 className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{internalGapsCount}</p>
                  <p className="text-xs text-white/70">Internal Gaps</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white border-0">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-white/20 rounded-lg">
                  <Globe className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{marketGapsCount}</p>
                  <p className="text-xs text-white/70">Market Gaps</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Left Column: Filters + Gap Cards */}
          <div className="lg:col-span-2 space-y-4">
            {/* Filters */}
            <Card className="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Filter className="h-4 w-4 text-slate-500" />
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Filters & Sorting</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div>
                    <Label className="text-xs text-slate-500">Gap Type</Label>
                    <Select value={filterType} onValueChange={(v: any) => setFilterType(v)}>
                      <SelectTrigger className="h-8 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Types</SelectItem>
                        <SelectItem value="internal">Internal Only</SelectItem>
                        <SelectItem value="market">Market Only</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label className="text-xs text-slate-500">Sort By</Label>
                    <Select value={sortBy} onValueChange={(v: any) => setSortBy(v)}>
                      <SelectTrigger className="h-8 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="confidence">Confidence</SelectItem>
                        <SelectItem value="threat">Threat Level</SelectItem>
                        <SelectItem value="goalBlocking">Goal Blocking</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label className="text-xs text-slate-500">Min Confidence: {confidenceThreshold}%</Label>
                    <Slider
                      value={[confidenceThreshold]}
                      onValueChange={(v) => setConfidenceThreshold(v[0])}
                      max={100}
                      step={5}
                      className="mt-2"
                    />
                  </div>

                  <div className="flex items-end">
                    <Button
                      variant={filterCriticalOnly ? "default" : "outline"}
                      size="sm"
                      className="h-8 text-xs w-full"
                      onClick={() => setFilterCriticalOnly(!filterCriticalOnly)}
                    >
                      <AlertCircle className="h-3 w-3 mr-1" />
                      Critical Only
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Gap Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Internal Gaps */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Building2 className="h-4 w-4 text-blue-500" />
                  <h3 className="font-semibold text-slate-700 dark:text-slate-300">Internal Gaps</h3>
                  <Badge variant="secondary" className="text-xs">
                    {internalGaps.length}
                  </Badge>
                </div>
                <ScrollArea className="h-[400px] pr-2">
                  <div className="space-y-3">
                    {internalGaps.map((gap) => (
                      <GapCard key={gap.id} gap={gap} />
                    ))}
                    {internalGaps.length === 0 && (
                      <p className="text-sm text-slate-500 text-center py-8">No internal gaps match filters</p>
                    )}
                  </div>
                </ScrollArea>
              </div>

              {/* Market Gaps */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Globe className="h-4 w-4 text-orange-500" />
                  <h3 className="font-semibold text-slate-700 dark:text-slate-300">Market Gaps</h3>
                  <Badge variant="secondary" className="text-xs">
                    {marketGaps.length}
                  </Badge>
                </div>
                <ScrollArea className="h-[400px] pr-2">
                  <div className="space-y-3">
                    {marketGaps.map((gap) => (
                      <GapCard key={gap.id} gap={gap} />
                    ))}
                    {marketGaps.length === 0 && (
                      <p className="text-sm text-slate-500 text-center py-8">No market gaps match filters</p>
                    )}
                  </div>
                </ScrollArea>
              </div>
            </div>
          </div>

          {/* Right Column: Detail Panel */}
          <div className="space-y-4">
            <Card className="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 sticky top-4">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-purple-500" />
                  Gap Details
                </CardTitle>
              </CardHeader>
              <CardContent>
                {selectedGap ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Badge
                        variant="outline"
                        className={cn(
                          "text-xs",
                          selectedGap.type === "internal"
                            ? "bg-blue-500/10 text-blue-600 border-blue-500/30"
                            : "bg-orange-500/10 text-orange-600 border-orange-500/30",
                        )}
                      >
                        {selectedGap.type === "internal" ? (
                          <Building2 className="h-3 w-3 mr-1" />
                        ) : (
                          <Globe className="h-3 w-3 mr-1" />
                        )}
                        {selectedGap.type.charAt(0).toUpperCase() + selectedGap.type.slice(1)} Gap
                      </Badge>
                      {selectedGap.critical && (
                        <Badge variant="destructive" className="text-xs">
                          Critical
                        </Badge>
                      )}
                    </div>

                    <div>
                      <h4 className="font-semibold text-slate-900 dark:text-white mb-2">{selectedGap.description}</h4>
                    </div>

                    {/* Confidence Bar */}
                    <div>
                      <div className="flex justify-between text-xs text-slate-500 mb-1">
                        <span>Confidence</span>
                        <span>{Math.round(selectedGap.confidence * 100)}%</span>
                      </div>
                      <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${selectedGap.confidence * 100}%` }}
                        />
                      </div>
                    </div>

                    {/* Attributes */}
                    <div className="grid grid-cols-2 gap-2">
                      <div
                        className={cn(
                          "p-2 rounded-lg text-center",
                          selectedGap.goalBlocking
                            ? "bg-purple-500/10 border border-purple-500/30"
                            : "bg-slate-100 dark:bg-slate-700",
                        )}
                      >
                        <Target
                          className={cn(
                            "h-4 w-4 mx-auto mb-1",
                            selectedGap.goalBlocking ? "text-purple-500" : "text-slate-400",
                          )}
                        />
                        <p className="text-xs font-medium text-slate-700 dark:text-slate-300">
                          {selectedGap.goalBlocking ? "Goal Blocking" : "Non-Blocking"}
                        </p>
                      </div>
                      <div className={cn("p-2 rounded-lg text-center border", getThreatColor(selectedGap.threat))}>
                        <ShieldAlert className="h-4 w-4 mx-auto mb-1" />
                        <p className="text-xs font-medium">
                          {selectedGap.threat.charAt(0).toUpperCase() + selectedGap.threat.slice(1)} Threat
                        </p>
                      </div>
                    </div>

                    {/* Full Reasoning */}
                    <Collapsible defaultOpen>
                      <CollapsibleTrigger asChild>
                        <Button variant="ghost" size="sm" className="w-full justify-between text-xs">
                          Full Reasoning
                          <ChevronDown className="h-3 w-3" />
                        </Button>
                      </CollapsibleTrigger>
                      <CollapsibleContent>
                        <div className="bg-slate-50 dark:bg-slate-700/50 p-3 rounded-lg mt-2">
                          <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                            {selectedGap.reasoning}
                          </p>
                        </div>
                      </CollapsibleContent>
                    </Collapsible>

                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-full text-xs text-slate-500"
                      onClick={() => setSelectedGap(null)}
                    >
                      <X className="h-3 w-3 mr-1" /> Clear Selection
                    </Button>
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    <Target className="h-8 w-8 mx-auto mb-2 opacity-30" />
                    <p className="text-sm">Click a gap card to view details</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
