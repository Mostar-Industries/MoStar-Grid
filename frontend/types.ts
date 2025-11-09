// types.ts

export enum Page {
  DASHBOARD = 'dashboard',
  CHAT = 'chat',
  NOTES = 'notes',
  VISION = 'vision',
  AUDIO = 'audio',
  FORGE = 'forge',
  ORCHESTRA = 'orchestra',
  SOVEREIGNTY = 'sovereignty',
  CONNECTION = 'connection', // Renamed from Backend Alignment
  BACKEND_STATS = 'backend_stats', // Renamed from MOSTAR_GRID
  ANALYTICS = 'analytics',
  SETTINGS = 'settings',
  QUERY_BUILDER = 'query_builder', // New: Graph Query Builder
}

export interface FilePart {
  type: 'image' | 'video';
  mimeType: string;
  base64Data: string;
}

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export enum MessageRole {
  USER = 'user',
  MODEL = 'model',
  SYSTEM = 'system', // Added for Kairo chatbot system instruction
}

export interface MessagePart {
  text?: string;
  image?: string; // base64 image data
  video?: string; // video URL or base64 data
  audio?: string; // base64 audio data
}

// New types for Thinking Mode visualization
export interface ReasoningStep {
  type: string;
  action: string;
  culturalContext: string;
  culturalSources?: string[];
  confidence: number;
  careValidated: boolean;
  symbolicLogic?: string;
  careBreakdown?: {
    collectiveBenefit: { score: number; explanation: string; };
    authorityControl: { score: number; explanation: string; };
    responsibility: { score: number; explanation: string; };
    ethics: { score: number; explanation: string; };
  };
}

export interface CulturalContext {
  careScore: number;
  culturalAccuracy: number;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  parts: MessagePart[];
  timestamp: Date;
  metadata?: {
    model?: string;
    thinkingMode?: boolean;
    isLoading?: boolean;
    error?: string;
    rawResponse?: any; // For debugging/inspection
    searchGrounding?: string[]; // URLs from Google Search
    mapsGrounding?: string[]; // URLs from Google Maps
    thinkingProcess?: { // New property for detailed reasoning
      steps: ReasoningStep[];
      context: CulturalContext;
    };
  };
}

// Backend Service Types (from backendService.ts and BackendAlignmentPage.tsx)
export interface KnowledgeNodeContent {
  remedy?: string;
  uses?: string;
  safety_level?: 'High' | 'Moderate' | 'Low' | 'N/A';
  // Add other properties if implied elsewhere for general knowledge
  // For the example, it seems to be tailored to herbal remedies.
}

export interface CAREMetadata {
  fpic_obtained: boolean;
  permission_level: string; // e.g., 'open', 'restricted', 'private'
  community: string;
  governance_protocol: string;
}

export interface KnowledgeNodeResponse {
  node_id: string;
  culture: string;
  ontology: string;
  content: KnowledgeNodeContent;
  provenance: string[];
  confidence?: number;
  care_metadata: CAREMetadata;
}

export interface MostarGridQueryResponse {
  nodes: KnowledgeNodeResponse[];
  query_id: string;
  timestamp: string;
}

export interface GridStatusConsciousness {
  grid_id: string;
  consciousness_level: string;
  connected_agents: number;
  active_agents: number;
  cultures_represented: number;
  uptime_seconds: number;
}

export interface GridStatusKnowledgeFabric {
  total_nodes: number;
  cultures: number;
  ontologies: number;
  care_compliant_percentage: number;
  recent_contributions: number;
  top_cultures: string[];
}

export interface GridStatusAgents {
  total: number;
  active: number;
  by_type: { [key: string]: number };
}

export interface GridStatusReasoningChains {
  active: number;
  completed_today: number;
  total: number;
}

export interface GridStatusResponse {
  consciousness: GridStatusConsciousness;
  knowledge_fabric: GridStatusKnowledgeFabric;
  agents: GridStatusAgents;
  reasoning_chains: GridStatusReasoningChains;
  timestamp: string;
}

export interface CAREAccessResponse {
  node_id: string;
  compliant: boolean;
  fpic_obtained: boolean;
  permission_level: string;
  community: string;
  governance_protocol: string;
  reason?: string;
}


// Ticker Feed / Dashboard / Mock Data Types
export interface StatPayload {
  coherence: number;
  activeNodes: number;
  qps: number;
  uploads: number;
}

export interface EventPayload {
  ts: string; // ISO string
  level: 'info' | 'warn' | 'error';
  text: string;
}

export type StatColor = 'purple' | 'blue' | 'green' | 'yellow' | 'teal' | 'red' | 'indigo' | 'pink';

export interface StatsCardData {
  title: string;
  value: string;
  icon: string; // e.g., 'fa-brain'
  color: StatColor;
}

export interface Tag {
  name: string;
  color: StatColor;
}

export interface KnowledgeCardData {
  title: string;
  subtitle: string;
  description: string;
  icon: string;
  iconColor: StatColor;
  tags: Tag[];
  updated: string;
  size: string;
}

export interface Scroll {
  id: string;
  name: string;
  author: string;
  description: string;
  content: string; // MoScript content
}

export interface Interpretation {
  status: 'approved' | 'warning' | 'rejected';
  score: number;
  proverb: string;
}

// ServiceHealthCard status literal types (from mockData.ts)
export type ServiceStatus = "ok" | "warn" | "fail";