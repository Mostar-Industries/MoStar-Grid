export type Page = 'dashboard' | 'chat' | 'vision' | 'audio' | 'forge' | 'analytics' | 'settings' | 'sovereignty' | 'imageForge' | 'moscript' | 'notes';

export type ChatModel = 'flash-lite' | 'flash' | 'pro-thinking';

export interface ChatMessage {
    role: 'user' | 'model';
    parts: { text: string }[];
    timestamp: number;
}

export interface StatsCardData {
    title: string;
    value: string;
    icon: string;
    color: 'purple' | 'blue' | 'green' | 'yellow' | 'teal';
}

export interface Tag {
    name: string;
    color: 'purple' | 'blue' | 'green' | 'yellow' | 'red' | 'indigo' | 'pink' | 'teal';
}

export interface KnowledgeCardData {
    id: string;
    title: string;
    subtitle: string;
    description: string;
    icon: string;
    iconColor: 'purple' | 'blue' | 'green' | 'yellow' | 'red' | 'indigo' | 'pink' | 'teal';
    tags: Tag[];
    updated: string;
    size: string;
}

export interface WooTraceLog {
    id: string; // UUID for the trace itself
    scroll_id: string;
    status: 'denied' | 'warning' | 'approved';
    score: number;
    explanation: string;
    proverb: string;
    timestamp: string;
}

export interface Note {
    id: string;
    title: string;
    created_at: string;
    shared: boolean;
}

// Real-time metric types
export type StatPayload = {
  activeNodes: number;
  coherence: number;     // 0..1
  qps: number;           // queries per second
  uploads: number;
  soulprints: number;
};

export type ServicePayload = {
  name: string;          // "API", "DB", "Cache", "Queue", "Auth", "Models"
  status: "ok" | "warn" | "fail";
  rps: number;           // requests/sec (or ops/sec)
  p50: number;           // ms
  p95: number;           // ms
  errorRate: number;     // 0..1
  uptime: number;        // seconds
  version?: string;
};

export type EventPayload = {
  ts: string;
  level: "info" | "warn" | "error";
  text: string;
};