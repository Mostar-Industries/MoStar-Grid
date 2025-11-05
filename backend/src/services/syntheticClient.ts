/**
 * syntheticClient.ts
 * Client for MostlyAI synthetic data generation with lifecycle awareness
 */

import { API_BASE } from '../lib/env';

export interface LifecycleSize {
  infancy?: number;
  childhood?: number;
  adolescence?: number;
  young_adult?: number;
  midlife?: number;
  elder?: number;
}

export interface GeneratorInfo {
  id: string;
  name?: string;
  status?: string;
  created_at?: string;
}

export interface ProbeResult {
  ok: boolean;
  job_id?: string;
  status?: string;
  size: number;
  lifecycle_distribution: LifecycleSize;
  generator_id?: string;
  error?: string;
}

/**
 * Fetch generator metadata from backend
 */
export async function getGeneratorInfo(): Promise<GeneratorInfo> {
  const res = await fetch(`${API_BASE}/synthetic/generator`);
  if (!res.ok) {
    const error = await res.text();
    throw new Error(`GET ${API_BASE}/synthetic/generator failed: ${res.status} ${error}`);
  }
  return res.json();
}

/**
 * Generate synthetic data probe with lifecycle-aware sizing
 */
export async function generateSyntheticProbe(size: LifecycleSize): Promise<ProbeResult> {
  const res = await fetch(`${API_BASE}/synthetic/probe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ size }),
  });
  
  if (!res.ok) {
    const error = await res.text();
    throw new Error(`POST ${API_BASE}/synthetic/probe failed: ${res.status} ${error}`);
  }
  
  return res.json();
}

/**
 * Lifecycle stage metadata
 */
export const LIFECYCLE_STAGES = {
  infancy: { label: 'Infancy', range: '0-2 years', focus: 'Early Bonding' },
  childhood: { label: 'Childhood', range: '3-12 years', focus: 'Cultural Learning' },
  adolescence: { label: 'Adolescence', range: '13-19 years', focus: 'Identity Formation' },
  young_adult: { label: 'Young Adult', range: '20-35 years', focus: 'Community Building' },
  midlife: { label: 'Midlife', range: '36-55 years', focus: 'Wisdom Transfer' },
  elder: { label: 'Elder', range: '56+ years', focus: 'Ancestral Guidance' },
} as const;
