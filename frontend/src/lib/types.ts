export type ContentType = "video" | "paper" | "newsletter" | "blog" | "social" | "discussion" | "podcast" | "article";

export type Domain =
  | "Agentic AI"
  | "AI Architecture"
  | "AI Engineering"
  | "AI Coding"
  | "Production AI"
  | "Models"
  | "AI Applications"
  | "Industry";

export type BuildImpact = "Very High" | "High" | "Medium" | "Low" | "Background";

export type ProductionReadiness =
  | "Experimental"
  | "Preview"
  | "Beta"
  | "Production Ready"
  | "Enterprise Ready"
  | "N/A";

export interface DigestItem {
  id: string;
  source_title: string;
  narrative: string;
  why_it_matters: string | null;
  what_changed: string | null;
  who_should_care: string | null;
  build_impact: BuildImpact | null;
  production_readiness: ProductionReadiness | null;
  importance: number;
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
