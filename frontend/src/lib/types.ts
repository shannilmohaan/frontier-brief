export type ContentType = "video" | "paper" | "newsletter" | "blog" | "social" | "discussion" | "podcast" | "article";

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
  source_title: string;
  narrative: string;
  source_name: string;
  source_url: string;
  content_type: ContentType;
  domain_tags: Domain[];
  relevance_score: number;
  created_at: string;
  thumbnail_url: string | null;
}

export interface DigestResponse {
  items: DigestItem[];
  domain_filter: string | null;
  cycle_id: string | null;
}

export interface CycleInfo {
  id: string;
  completed_at: string;
  items_synthesized: number;
}

export interface HistoryResponse {
  cycles: CycleInfo[];
}

export interface RefreshResponse {
  job_id: string;
  status: string;
  created?: boolean;
}
