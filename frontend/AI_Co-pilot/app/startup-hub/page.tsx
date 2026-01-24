"use client"

import { useState, useCallback } from "react"
import {
  Upload,
  FileText,
  MessageSquare,
  Calendar,
  Loader2,
  CheckCircle,
  AlertCircle,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Target,
  Clock,
  Tag,
} from "lucide-react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import {
  uploadDocument,
  askQuestion,
  generatePlan,
  type UploadResponse,
  type QuestionResponse,
  type PlanResponse,
  type PlanTask,
  type SupportingEvidence,
} from "@/lib/api/startupApi"
import { cn } from "@/lib/utils"

type UploadStatus = "idle" | "uploading" | "success" | "error"
type QueryStatus = "idle" | "loading" | "success" | "error"

export default function StartupHubPage() {
  // --- Upload State ---
  const [file, setFile] = useState<File | null>(null)
  const [startupId, setStartupId] = useState<string>("")
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>("idle")
  const [uploadMessage, setUploadMessage] = useState("")

  // --- Question State ---
  const [question, setQuestion] = useState("")
  const [questionStatus, setQuestionStatus] = useState<QueryStatus>("idle")
  const [questionResponse, setQuestionResponse] = useState<QuestionResponse | null>(null)
  const [questionError, setQuestionError] = useState("")

  // --- Plan State ---
  const [goal, setGoal] = useState("")
  const [timeHorizon, setTimeHorizon] = useState(60)
  const [planStatus, setPlanStatus] = useState<QueryStatus>("idle")
  const [planResponse, setPlanResponse] = useState<PlanResponse | null>(null)
  const [planError, setPlanError] = useState("")
  const [expandedTasks, setExpandedTasks] = useState<Set<string>>(new Set())

  // --- Handlers ---

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setUploadStatus("idle")
      setUploadMessage("")
    }
  }, [])

  const handleUpload = useCallback(async () => {
    if (!file) return

    setUploadStatus("uploading")
    setUploadMessage("")

    try {
      const response = await uploadDocument(file, startupId || undefined)
      setStartupId(response.startup_id)
      setUploadStatus("success")
      setUploadMessage(response.message)
    } catch (error) {
      setUploadStatus("error")
      setUploadMessage(error instanceof Error ? error.message : "Upload failed")
    }
  }, [file, startupId])

  const handleAskQuestion = useCallback(async () => {
    if (!startupId || !question.trim()) return

    setQuestionStatus("loading")
    setQuestionError("")
    setQuestionResponse(null)

    try {
      const response = await askQuestion(startupId, question)
      setQuestionResponse(response)
      setQuestionStatus("success")
    } catch (error) {
      setQuestionError(error instanceof Error ? error.message : "Failed to get answer")
      setQuestionStatus("error")
    }
  }, [startupId, question])

  const handleGeneratePlan = useCallback(async () => {
    if (!startupId || !goal.trim()) return

    setPlanStatus("loading")
    setPlanError("")
    setPlanResponse(null)

    try {
      const response = await generatePlan(startupId, goal, timeHorizon)
      setPlanResponse(response)
      setPlanStatus("success")
    } catch (error) {
      setPlanError(error instanceof Error ? error.message : "Failed to generate plan")
      setPlanStatus("error")
    }
  }, [startupId, goal, timeHorizon])

  const toggleTaskExpanded = useCallback((taskId: string) => {
    setExpandedTasks((prev) => {
      const next = new Set(prev)
      if (next.has(taskId)) {
        next.delete(taskId)
      } else {
        next.add(taskId)
      }
      return next
    })
  }, [])

  // --- Render Helpers ---

  const renderEvidence = (evidence: SupportingEvidence[]) => {
    if (!evidence || evidence.length === 0) return null

    return (
      <div className="mt-4 space-y-2">
        <h4 className="text-sm font-medium text-muted-foreground">Supporting Evidence</h4>
        {evidence.map((item, index) => (
          <div
            key={index}
            className="flex items-start gap-2 rounded-lg bg-muted/50 p-3 text-sm"
          >
            <Badge variant={item.source_type === "online" ? "default" : "secondary"}>
              {item.source_type}
            </Badge>
            <div className="flex-1">
              <p className="font-medium">{item.doc_title || "Source"}</p>
              <p className="text-muted-foreground">{item.summary}</p>
              {item.url && (
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-1 inline-flex items-center gap-1 text-xs text-primary hover:underline"
                >
                  View Source <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    )
  }

  const renderTask = (task: PlanTask) => {
    const isExpanded = expandedTasks.has(task.task_id)
    const priorityColors = {
      high: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
      medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
      low: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    }
    const statusColors = {
      todo: "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200",
      in_progress: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
      done: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    }

    return (
      <div
        key={task.task_id}
        className="rounded-lg border bg-card p-4 transition-all hover:shadow-md"
      >
        <div
          className="flex cursor-pointer items-center gap-3"
          onClick={() => toggleTaskExpanded(task.task_id)}
        >
          {isExpanded ? (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          )}
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h4 className="font-medium">{task.title}</h4>
              <Badge className={cn("text-xs", priorityColors[task.priority])}>
                {task.priority}
              </Badge>
              <Badge className={cn("text-xs", statusColors[task.status])}>
                {task.status.replace("_", " ")}
              </Badge>
            </div>
            <div className="mt-1 flex items-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {task.start_date} → {task.end_date}
              </span>
            </div>
          </div>
        </div>

        {isExpanded && (
          <div className="mt-3 space-y-2 border-t pt-3">
            <p className="text-sm text-muted-foreground">{task.description}</p>
            {task.tags && task.tags.length > 0 && (
              <div className="flex items-center gap-2">
                <Tag className="h-3 w-3 text-muted-foreground" />
                {task.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
            {task.dependencies && task.dependencies.length > 0 && (
              <p className="text-xs text-muted-foreground">
                Depends on: {task.dependencies.join(", ")}
              </p>
            )}
          </div>
        )}
      </div>
    )
  }

  return (
    <DashboardLayout>
      <div className="container mx-auto max-w-6xl space-y-6 p-6">
        <div>
          <h1 className="text-3xl font-bold">Startup Analysis Hub</h1>
          <p className="text-muted-foreground">
            Upload documents, ask questions, and generate action plans for your startup
          </p>
        </div>

        {/* Current Startup ID Display */}
        {startupId && (
          <Card className="border-primary/50 bg-primary/5">
            <CardContent className="flex items-center gap-3 py-3">
              <CheckCircle className="h-5 w-5 text-primary" />
              <div>
                <p className="text-sm font-medium">Active Startup</p>
                <p className="font-mono text-xs text-muted-foreground">{startupId}</p>
              </div>
            </CardContent>
          </Card>
        )}

        <Tabs defaultValue="upload" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <Upload className="h-4 w-4" />
              Upload Document
            </TabsTrigger>
            <TabsTrigger value="question" className="flex items-center gap-2" disabled={!startupId}>
              <MessageSquare className="h-4 w-4" />
              Ask Question
            </TabsTrigger>
            <TabsTrigger value="plan" className="flex items-center gap-2" disabled={!startupId}>
              <Calendar className="h-4 w-4" />
              Generate Plan
            </TabsTrigger>
          </TabsList>

          {/* Upload Tab */}
          <TabsContent value="upload">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Upload Business Document
                </CardTitle>
                <CardDescription>
                  Upload a PDF, pitch deck, or business document to get started
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Startup ID (optional)</label>
                  <Input
                    placeholder="Leave empty to generate a new ID"
                    value={startupId}
                    onChange={(e) => setStartupId(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Document</label>
                  <div className="flex items-center gap-4">
                    <Input
                      type="file"
                      accept=".pdf,.pptx,.docx,.txt"
                      onChange={handleFileChange}
                      className="flex-1"
                    />
                    <Button
                      onClick={handleUpload}
                      disabled={!file || uploadStatus === "uploading"}
                    >
                      {uploadStatus === "uploading" ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Uploading...
                        </>
                      ) : (
                        <>
                          <Upload className="mr-2 h-4 w-4" />
                          Upload
                        </>
                      )}
                    </Button>
                  </div>
                </div>

                {uploadMessage && (
                  <div
                    className={cn(
                      "flex items-center gap-2 rounded-lg p-3",
                      uploadStatus === "success"
                        ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                        : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                    )}
                  >
                    {uploadStatus === "success" ? (
                      <CheckCircle className="h-4 w-4" />
                    ) : (
                      <AlertCircle className="h-4 w-4" />
                    )}
                    {uploadMessage}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Question Tab */}
          <TabsContent value="question">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Ask a Question
                </CardTitle>
                <CardDescription>
                  Ask questions about your startup based on uploaded documents
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Your Question</label>
                  <Textarea
                    placeholder="e.g., How can I improve my fundraising chances in Egypt?"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    rows={3}
                  />
                </div>

                <Button
                  onClick={handleAskQuestion}
                  disabled={!question.trim() || questionStatus === "loading"}
                  className="w-full"
                >
                  {questionStatus === "loading" ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <MessageSquare className="mr-2 h-4 w-4" />
                      Get Answer
                    </>
                  )}
                </Button>

                {questionError && (
                  <div className="flex items-center gap-2 rounded-lg bg-red-100 p-3 text-red-800 dark:bg-red-900 dark:text-red-200">
                    <AlertCircle className="h-4 w-4" />
                    {questionError}
                  </div>
                )}

                {questionResponse && (
                  <div className="space-y-4 rounded-lg border bg-muted/30 p-4">
                    <div>
                      <h4 className="text-sm font-medium text-muted-foreground">Question</h4>
                      <p className="mt-1">{questionResponse.question}</p>
                    </div>
                    <Separator />
                    <div>
                      <h4 className="text-sm font-medium text-muted-foreground">Answer</h4>
                      <p className="mt-1 whitespace-pre-wrap">{questionResponse.answer}</p>
                    </div>
                    {renderEvidence(questionResponse.supporting_evidence)}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Plan Tab */}
          <TabsContent value="plan">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Generate Action Plan
                </CardTitle>
                <CardDescription>
                  Create a structured action plan with phases and tasks
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Goal</label>
                    <Textarea
                      placeholder="e.g., Raise pre-seed round in 3 months"
                      value={goal}
                      onChange={(e) => setGoal(e.target.value)}
                      rows={3}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Time Horizon (days)</label>
                    <Input
                      type="number"
                      value={timeHorizon}
                      onChange={(e) => setTimeHorizon(parseInt(e.target.value) || 60)}
                      min={7}
                      max={365}
                    />
                    <p className="text-xs text-muted-foreground">
                      How many days should the plan cover?
                    </p>
                  </div>
                </div>

                <Button
                  onClick={handleGeneratePlan}
                  disabled={!goal.trim() || planStatus === "loading"}
                  className="w-full"
                >
                  {planStatus === "loading" ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating Plan...
                    </>
                  ) : (
                    <>
                      <Calendar className="mr-2 h-4 w-4" />
                      Generate Plan
                    </>
                  )}
                </Button>

                {planError && (
                  <div className="flex items-center gap-2 rounded-lg bg-red-100 p-3 text-red-800 dark:bg-red-900 dark:text-red-200">
                    <AlertCircle className="h-4 w-4" />
                    {planError}
                  </div>
                )}

                {planResponse && (
                  <div className="space-y-4 rounded-lg border p-4">
                    {/* Plan Header */}
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-lg font-semibold">{planResponse.title}</h3>
                        <p className="text-sm text-muted-foreground">
                          Created: {new Date(planResponse.created_at).toLocaleDateString()} •{" "}
                          {planResponse.time_horizon_days} days • Version {planResponse.version}
                        </p>
                      </div>
                      <Badge variant="outline" className="font-mono text-xs">
                        {planResponse.plan_id.slice(0, 8)}
                      </Badge>
                    </div>

                    <Separator />

                    {/* Strategy Advice */}
                    {planResponse.strategy_advice && (
                      <div className="rounded-lg bg-muted/50 p-4">
                        <h4 className="mb-2 font-medium">Strategy Overview</h4>
                        <p className="whitespace-pre-wrap text-sm text-muted-foreground">
                          {planResponse.strategy_advice}
                        </p>
                      </div>
                    )}

                    {/* Phases */}
                    {planResponse.phases && planResponse.phases.length > 0 && (
                      <div>
                        <h4 className="mb-2 font-medium">Phases</h4>
                        <div className="flex flex-wrap gap-2">
                          {planResponse.phases.map((phase) => (
                            <Badge key={phase.phase_id} variant="secondary">
                              {phase.name}: {phase.start_date} → {phase.end_date}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Tasks */}
                    {planResponse.tasks && planResponse.tasks.length > 0 && (
                      <div>
                        <h4 className="mb-3 font-medium">
                          Tasks ({planResponse.tasks.length})
                        </h4>
                        <ScrollArea className="max-h-[400px]">
                          <div className="space-y-3">
                            {planResponse.tasks.map((task) => renderTask(task))}
                          </div>
                        </ScrollArea>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
