"use client"

import { useState, useMemo } from "react"
import {
  Building2,
  MapPin,
  Target,
  AlertTriangle,
  FileText,
  Users,
  Volume2,
  Search,
  ChevronDown,
  ChevronUp,
  X,
} from "lucide-react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"

// Sample data based on the agent output structure
const walletData = {
  business_name: "Urban Plant Life",
  business_type: "Boutique Plant Shop & Interior Greening Consultancy",
  location: "Cairo, Egypt (Physical Hub) + Online Store",
  goals: [
    {
      id: "g1",
      text: "Increase online sales by 40% in the next quarter",
      type: "marketing",
      priority: "high",
      alignedCampaigns: ["Spring Collection Launch", "Social Media Push"],
    },
    {
      id: "g2",
      text: "Expand B2B interior greening consultancy services to 10 new corporate clients",
      type: "collaboration",
      priority: "high",
      alignedCampaigns: ["B2B Outreach Campaign"],
    },
    {
      id: "g3",
      text: "Launch a plant subscription box service by Q2",
      type: "operations",
      priority: "medium",
      alignedCampaigns: ["Subscription Launch"],
    },
    {
      id: "g4",
      text: "Reduce plant mortality rate during shipping to under 2%",
      type: "operations",
      priority: "high",
      alignedCampaigns: [],
    },
    {
      id: "g5",
      text: "Build a community of 50,000 plant enthusiasts on social media",
      type: "marketing",
      priority: "medium",
      alignedCampaigns: ["Social Media Push", "Influencer Partnerships"],
    },
    {
      id: "g6",
      text: "Partner with 5 local cafes for pop-up plant corners",
      type: "collaboration",
      priority: "low",
      alignedCampaigns: ["Local Partnerships"],
    },
  ],
  key_constraints: [
    { id: "c1", text: "Limited warehouse space for inventory expansion", critical: true },
    { id: "c2", text: "Seasonal fluctuations in plant availability", critical: false },
    { id: "c3", text: "High shipping costs for fragile plant deliveries", critical: true },
    { id: "c4", text: "Small marketing budget of $5,000/month", critical: true },
    { id: "c5", text: "Dependency on single supplier for rare plants", critical: false },
  ],
  target_audience:
    "Urban millennials and Gen-Z professionals aged 25-40 who are passionate about sustainable living, home decor, and wellness. They live in apartments, value aesthetic Instagram-worthy spaces, and are willing to invest in quality plants and care accessories.",
  brand_voice:
    "Warm, knowledgeable, and approachable. We speak like a friendly plant expert neighbor who genuinely wants to help you succeed in your plant journey. Our tone is encouraging, educational, and sprinkled with plant puns.",
  available_documents: [
    {
      id: "d1",
      name: "Q4 Sales Report 2024",
      type: "report",
      summary:
        "Detailed analysis of Q4 performance showing 23% growth in online sales, with succulents and rare aroids being top sellers.",
    },
    {
      id: "d2",
      name: "Brand Guidelines v2.1",
      type: "guidelines",
      summary:
        "Complete brand identity guide including logo usage, color palette (earth tones with pops of green), typography, and voice guidelines.",
    },
    {
      id: "d3",
      name: "Competitor Analysis",
      type: "research",
      summary:
        "Comprehensive review of 8 competitors in the Cairo plant market, identifying gaps in B2B services and subscription offerings.",
    },
    {
      id: "d4",
      name: "Customer Survey Results",
      type: "research",
      summary:
        "Survey of 500 customers showing 78% satisfaction rate, with requests for more care guides and plant bundles.",
    },
    {
      id: "d5",
      name: "Shipping SOP",
      type: "operations",
      summary:
        "Standard operating procedures for plant packaging and shipping, including temperature control protocols.",
    },
  ],
  user_request:
    "Create a marketing campaign for our new spring collection that targets young professionals and emphasizes sustainable packaging.",
}

export default function DocumentAnalysisPage() {
  const [selectedDocument, setSelectedDocument] = useState<(typeof walletData.available_documents)[0] | null>(null)
  const [expandedGoals, setExpandedGoals] = useState<Set<string>>(new Set())
  const [filterGoalType, setFilterGoalType] = useState<string>("all")
  const [filterConstraintCritical, setFilterConstraintCritical] = useState<boolean>(false)
  const [documentSearch, setDocumentSearch] = useState("")
  const [goalSearch, setGoalSearch] = useState("")

  const toggleGoalExpansion = (id: string) => {
    const newExpanded = new Set(expandedGoals)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedGoals(newExpanded)
  }

  // Filter goals
  const filteredGoals = useMemo(() => {
    return walletData.goals.filter((goal) => {
      const matchesType = filterGoalType === "all" || goal.type === filterGoalType
      const matchesSearch = goal.text.toLowerCase().includes(goalSearch.toLowerCase())
      return matchesType && matchesSearch
    })
  }, [filterGoalType, goalSearch])

  // Filter constraints
  const filteredConstraints = useMemo(() => {
    return walletData.key_constraints.filter((constraint) => {
      if (filterConstraintCritical && !constraint.critical) return false
      return true
    })
  }, [filterConstraintCritical])

  // Filter documents
  const filteredDocuments = useMemo(() => {
    return walletData.available_documents.filter(
      (doc) =>
        doc.name.toLowerCase().includes(documentSearch.toLowerCase()) ||
        doc.summary.toLowerCase().includes(documentSearch.toLowerCase()),
    )
  }, [documentSearch])

  const getGoalTypeIcon = (type: string) => {
    switch (type) {
      case "marketing":
        return <Volume2 className="h-3 w-3" />
      case "operations":
        return <X className="h-3 w-3" />
      case "collaboration":
        return <Users className="h-3 w-3" />
      default:
        return <Target className="h-3 w-3" />
    }
  }

  const getGoalTypeColor = (type: string) => {
    switch (type) {
      case "marketing":
        return "bg-purple-500/10 text-purple-600 border-purple-500/30"
      case "operations":
        return "bg-amber-500/10 text-amber-600 border-amber-500/30"
      case "collaboration":
        return "bg-emerald-500/10 text-emerald-600 border-emerald-500/30"
      default:
        return "bg-slate-500/10 text-slate-600 border-slate-500/30"
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-500/10 text-red-600 border-red-500/30"
      case "medium":
        return "bg-amber-500/10 text-amber-600 border-amber-500/30"
      case "low":
        return "bg-slate-500/10 text-slate-600 border-slate-500/30"
      default:
        return "bg-slate-500/10 text-slate-600 border-slate-500/30"
    }
  }

  const getDocTypeIcon = (type: string) => {
    switch (type) {
      case "report":
        return <FileText className="h-4 w-4" />
      case "guidelines":
        return <FileText className="h-4 w-4" />
      case "research":
        return <Search className="h-4 w-4" />
      case "operations":
        return <X className="h-4 w-4" />
      default:
        return <FileText className="h-4 w-4" />
    }
  }

  return (
    <DashboardLayout>
      <TooltipProvider>
        <div className="p-4 space-y-4 bg-slate-50 dark:bg-slate-900 min-h-screen">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Document Analysis</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Business intelligence from uploaded documents
              </p>
            </div>
            <Badge variant="outline" className="bg-purple-500/10 text-purple-600 border-purple-500/30">
              <FileText className="h-3 w-3 mr-1" />
              AI Analyzed
            </Badge>
          </div>

          {/* KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            <Card className="bg-gradient-to-br from-purple-600 to-purple-700 text-white border-0">
              <CardContent className="p-3">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-white/20 rounded-lg">
                    <Building2 className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-lg font-bold truncate">{walletData.business_name}</p>
                    <p className="text-xs text-white/70 truncate">{walletData.business_type.split("&")[0].trim()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0">
              <CardContent className="p-3">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-white/20 rounded-lg">
                    <MapPin className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-lg font-bold">Cairo</p>
                    <p className="text-xs text-white/70">Egypt + Online</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-emerald-500 to-emerald-600 text-white border-0">
              <CardContent className="p-3">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-white/20 rounded-lg">
                    <Target className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-lg font-bold">{walletData.goals.length}</p>
                    <p className="text-xs text-white/70">Goals</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white border-0">
              <CardContent className="p-3">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-white/20 rounded-lg">
                    <AlertTriangle className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-lg font-bold">{walletData.key_constraints.length}</p>
                    <p className="text-xs text-white/70">Constraints</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-amber-500 to-amber-600 text-white border-0">
              <CardContent className="p-3">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-white/20 rounded-lg">
                    <FileText className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-lg font-bold">{walletData.available_documents.length}</p>
                    <p className="text-xs text-white/70">Documents</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-pink-500 to-pink-600 text-white border-0">
              <CardContent className="p-3">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-white/20 rounded-lg">
                    <AlertTriangle className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-lg font-bold">{walletData.key_constraints.filter((c) => c.critical).length}</p>
                    <p className="text-xs text-white/70">Critical</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content Grid - Goals and Constraints Side by Side */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Goals Section */}
            <Card className="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
              <CardHeader className="pb-2 pt-3 px-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-emerald-500" />
                    <CardTitle className="text-sm font-semibold">Goals</CardTitle>
                    <Badge variant="secondary" className="text-xs">
                      {filteredGoals.length}
                    </Badge>
                  </div>
                </div>
                {/* Filters */}
                <div className="flex gap-2 mt-2">
                  <Input
                    placeholder="Search goals..."
                    value={goalSearch}
                    onChange={(e) => setGoalSearch(e.target.value)}
                    className="h-7 text-xs flex-1"
                  />
                  <Select value={filterGoalType} onValueChange={setFilterGoalType}>
                    <SelectTrigger className="h-7 text-xs w-28">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      <SelectItem value="marketing">Marketing</SelectItem>
                      <SelectItem value="operations">Operations</SelectItem>
                      <SelectItem value="collaboration">Collaboration</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
              <CardContent className="px-4 pb-3">
                <ScrollArea className="h-[320px]">
                  <div className="space-y-2 pr-2">
                    {filteredGoals.map((goal) => (
                      <Tooltip key={goal.id}>
                        <TooltipTrigger asChild>
                          <Card
                            className={cn(
                              "cursor-pointer transition-all duration-200 hover:shadow-md border-slate-200 dark:border-slate-700",
                              expandedGoals.has(goal.id) && "ring-1 ring-purple-500",
                            )}
                            onClick={() => toggleGoalExpansion(goal.id)}
                          >
                            <CardContent className="p-3">
                              <div className="flex items-start gap-2">
                                <div className="flex-1 min-w-0">
                                  <p className="text-xs font-medium line-clamp-2 text-slate-700 dark:text-slate-300">
                                    {goal.text}
                                  </p>
                                  <div className="flex items-center gap-1 mt-2 flex-wrap">
                                    <Badge variant="outline" className={cn("text-xs", getGoalTypeColor(goal.type))}>
                                      {getGoalTypeIcon(goal.type)}
                                      <span className="ml-1 capitalize">{goal.type}</span>
                                    </Badge>
                                    <Badge variant="outline" className={cn("text-xs", getPriorityColor(goal.priority))}>
                                      {goal.priority}
                                    </Badge>
                                  </div>
                                </div>
                                {expandedGoals.has(goal.id) ? (
                                  <ChevronDown className="h-4 w-4 text-slate-400 flex-shrink-0" />
                                ) : (
                                  <ChevronUp className="h-4 w-4 text-slate-400 flex-shrink-0" />
                                )}
                              </div>
                              {expandedGoals.has(goal.id) && goal.alignedCampaigns.length > 0 && (
                                <div className="mt-2 pt-2 border-t border-slate-100 dark:border-slate-700">
                                  <p className="text-xs text-slate-500 mb-1">Aligned Campaigns:</p>
                                  <div className="flex flex-wrap gap-1">
                                    {goal.alignedCampaigns.map((campaign, idx) => (
                                      <Badge key={idx} variant="secondary" className="text-xs">
                                        <FileText className="h-2 w-2 mr-1" />
                                        {campaign}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        </TooltipTrigger>
                        <TooltipContent side="right" className="max-w-xs">
                          <p className="text-sm">{goal.text}</p>
                        </TooltipContent>
                      </Tooltip>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Constraints Section */}
            <Card className="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
              <CardHeader className="pb-2 pt-3 px-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-500" />
                    <CardTitle className="text-sm font-semibold">Constraints</CardTitle>
                    <Badge variant="secondary" className="text-xs">
                      {filteredConstraints.length}
                    </Badge>
                  </div>
                  <Button
                    variant={filterConstraintCritical ? "default" : "outline"}
                    size="sm"
                    className="h-6 text-xs"
                    onClick={() => setFilterConstraintCritical(!filterConstraintCritical)}
                  >
                    Critical Only
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="px-4 pb-3">
                <ScrollArea className="h-[320px]">
                  <div className="space-y-2 pr-2">
                    {filteredConstraints.map((constraint) => (
                      <Tooltip key={constraint.id}>
                        <TooltipTrigger asChild>
                          <Card
                            className={cn(
                              "transition-all duration-200",
                              constraint.critical
                                ? "border-red-500/50 bg-red-500/5 dark:bg-red-500/10"
                                : "border-slate-200 dark:border-slate-700",
                            )}
                          >
                            <CardContent className="p-3">
                              <div className="flex items-start gap-2">
                                <p className="text-xs text-slate-700 dark:text-slate-300 line-clamp-2 flex-1">
                                  {constraint.text}
                                </p>
                                {constraint.critical && (
                                  <Badge variant="destructive" className="text-xs flex-shrink-0">
                                    Critical
                                  </Badge>
                                )}
                              </div>
                            </CardContent>
                          </Card>
                        </TooltipTrigger>
                        <TooltipContent side="right" className="max-w-xs">
                          <p className="text-sm">{constraint.text}</p>
                        </TooltipContent>
                      </Tooltip>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          {/* Bottom Section: Target Audience, Brand Voice, and Documents */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
              <CardHeader className="pb-2 pt-3 px-4">
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-blue-500" />
                  <CardTitle className="text-sm font-semibold">Target Audience</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="px-4 pb-3">
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                  {walletData.target_audience}
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
              <CardHeader className="pb-2 pt-3 px-4">
                <div className="flex items-center gap-2">
                  <Volume2 className="h-4 w-4 text-pink-500" />
                  <CardTitle className="text-sm font-semibold">Brand Voice</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="px-4 pb-3">
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{walletData.brand_voice}</p>
              </CardContent>
            </Card>
          </div>

          {/* Documents Section - Full Width at Bottom */}
          <Card className="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
            <CardHeader className="pb-2 pt-3 px-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-amber-500" />
                  <CardTitle className="text-sm font-semibold">Available Documents</CardTitle>
                  <Badge variant="secondary" className="text-xs">
                    {filteredDocuments.length}
                  </Badge>
                </div>
                <div className="relative w-48">
                  <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3 w-3 text-slate-400" />
                  <Input
                    placeholder="Search documents..."
                    value={documentSearch}
                    onChange={(e) => setDocumentSearch(e.target.value)}
                    className="h-7 text-xs pl-7"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-2">
                {filteredDocuments.map((doc) => (
                  <Card
                    key={doc.id}
                    className="cursor-pointer transition-all duration-200 hover:shadow-md hover:border-purple-500/50 border-slate-200 dark:border-slate-700"
                    onClick={() => setSelectedDocument(doc)}
                  >
                    <CardContent className="p-3">
                      <div className="flex items-start gap-2">
                        <div className="p-1.5 bg-slate-100 dark:bg-slate-700 rounded">{getDocTypeIcon(doc.type)}</div>
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-medium text-slate-700 dark:text-slate-300 truncate">{doc.name}</p>
                          <Badge variant="outline" className="text-xs mt-1 capitalize">
                            {doc.type}
                          </Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Document Modal */}
          <Dialog open={!!selectedDocument} onOpenChange={() => setSelectedDocument(null)}>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  {selectedDocument && getDocTypeIcon(selectedDocument.type)}
                  {selectedDocument?.name}
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-3">
                <Badge variant="outline" className="capitalize">
                  {selectedDocument?.type}
                </Badge>
                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  {selectedDocument?.summary}
                </p>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </TooltipProvider>
    </DashboardLayout>
  )
}
