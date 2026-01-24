/**
 * Startup API - Backend integration for document upload, questions, and plan generation
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// --- Types ---

export interface UploadResponse {
  startup_id: string;
  message: string;
}

export interface SupportingEvidence {
  source_type: "offline" | "online";
  summary: string;
  url?: string | null;
  doc_title?: string;
}

export interface QuestionResponse {
  startup_id: string;
  question: string;
  answer: string;
  supporting_evidence: SupportingEvidence[];
}

export interface PlanPhase {
  phase_id: string;
  name: string;
  order: number;
  start_date: string;
  end_date: string;
}

export interface PlanTask {
  task_id: string;
  phase_id: string;
  title: string;
  description: string;
  status: "todo" | "in_progress" | "done";
  priority: "low" | "medium" | "high";
  assignee: string | null;
  start_date: string;
  end_date: string;
  dependencies: string[];
  tags: string[];
}

export interface PlanResponse {
  plan_id: string;
  startup_id: string;
  version: number;
  title: string;
  created_at: string;
  time_horizon_days: number;
  strategy_advice?: string;
  phases: PlanPhase[];
  tasks: PlanTask[];
}

export interface StartupProfile {
  startup_id: string;
  business_name: string;
  business_type: string;
  location?: string;
  sector?: string;
  stage?: string;
  goals?: string[];
  documents?: string[];
}

export interface PlanSummary {
  plan_id: string;
  title: string;
  version: number;
  created_at: string;
}

// --- API Functions ---

/**
 * Upload a business document
 */
export async function uploadDocument(
  file: File,
  startupId?: string
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  if (startupId) {
    formData.append("startup_id", startupId);
  }

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(error.detail || "Upload failed");
  }

  return response.json();
}

/**
 * Ask a question about a startup
 */
export async function askQuestion(
  startupId: string,
  question: string
): Promise<QuestionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/question`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      startup_id: startupId,
      question,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Question failed" }));
    throw new Error(error.detail || "Failed to get answer");
  }

  return response.json();
}

/**
 * Generate an action plan
 */
export async function generatePlan(
  startupId: string,
  goal: string,
  timeHorizonDays: number = 60
): Promise<PlanResponse> {
  const response = await fetch(`${API_BASE_URL}/api/plan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      startup_id: startupId,
      goal,
      time_horizon_days: timeHorizonDays,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Plan generation failed" }));
    throw new Error(error.detail || "Failed to generate plan");
  }

  return response.json();
}

/**
 * Get a startup's profile
 */
export async function getProfile(startupId: string): Promise<StartupProfile> {
  const response = await fetch(`${API_BASE_URL}/api/profile/${startupId}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Profile not found" }));
    throw new Error(error.detail || "Failed to get profile");
  }

  return response.json();
}

/**
 * Get a specific plan by ID
 */
export async function getPlan(planId: string): Promise<PlanResponse> {
  const response = await fetch(`${API_BASE_URL}/api/plan/${planId}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Plan not found" }));
    throw new Error(error.detail || "Failed to get plan");
  }

  return response.json();
}

/**
 * Get all plans for a startup
 */
export async function getStartupPlans(
  startupId: string,
  limit: number = 10
): Promise<{ startup_id: string; plans: PlanSummary[] }> {
  const response = await fetch(
    `${API_BASE_URL}/api/plans/${startupId}?limit=${limit}`
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to get plans" }));
    throw new Error(error.detail || "Failed to get plans");
  }

  return response.json();
}

/**
 * Health check
 */
export async function checkHealth(): Promise<{ status: string; timestamp: string }> {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  return response.json();
}

export const startupApi = {
  uploadDocument,
  askQuestion,
  generatePlan,
  getProfile,
  getPlan,
  getStartupPlans,
  checkHealth,
};
