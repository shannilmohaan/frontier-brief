// Placeholder — full types added in Phase 1c

export type ContentType = "video" | "paper" | "newsletter" | "blog" | "social" | "discussion";

export type Domain =
  | "Agentic AI"
  | "New Model Capabilities"
  | "Context Management"
  | "Token Economics"
  | "Tool Use & Function Calling"
  | "AI Coding Agents"
  | "Reasoning & Planning"
  | "Agent Memory & Persistence"
  | "Applied AI Engineering"
  | "AI Research";

export interface DigestItem {
  id: string;
  narrative: string;
  source_name: string;
  source_url: string;
  content_type: ContentType;
  domain_tags: Domain[];
  relevance_score: number;
  created_at: string;
}

export interface DigestResponse {
  items: DigestItem[];
  domain_filter: string | null;
  cycle_id: string | null;
}

export interface RefreshResponse {
  job_id: string;
  status: string;
}
