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

/**
 * MoScript - Autonomous agent scripting system
 * Self-contained logic units with triggers, inputs, and optional voice responses
 */
export type MoScript = {
  id: string;
  name: string;
  trigger: string; // What event/context it responds to
  inputs: string[];
  logic: (inputs: Record<string, any>) => any;
  voiceLine?: (result: any) => string;
  sass?: boolean;
};
