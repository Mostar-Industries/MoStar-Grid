// types/moscript.ts

/**
 * Represents a self-contained, executable unit of logic.
 */
export interface Scroll {
  id: string; // UUID
  name: string;
  description: string;
  code: string;
  author: string;
  soulprint: string;
  resonance_score?: number;
  approved?: boolean;
}

/**
 * Represents a single rule or principle within the Grid's covenant.
 */
export interface CodexItem {
  term: string;
  weight: number;
  scripture: string;
}

export type Codex = CodexItem[];
