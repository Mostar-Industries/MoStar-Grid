export interface Provenance {
  source: string;
  timestamp: string;
  upstream_id?: string;
  ingestion_run_id: string;
  confidence?: number;
  error?: string;
  error_type?: string;
  lineage?: Array<Record<string, unknown>>;
}

export interface GridEntity {
  id: string;
  provenance: Provenance;
  [key: string]: unknown;
}

export function hasValidProvenance<T extends GridEntity>(
  entity: T,
  opts?: { ttlMs?: number; disallowSources?: string[] }
): entity is T & { provenance: Provenance } {
  if (!entity?.provenance) return false;
  const { source, timestamp, ingestion_run_id } = entity.provenance;
  if (!source || !timestamp || !ingestion_run_id) return false;
  if (source === 'error' || source === 'fallback') return false;
  if (opts?.disallowSources?.includes(source)) return false;
  if (opts?.ttlMs) {
    const age = Date.now() - new Date(timestamp).getTime();
    if (age > opts.ttlMs) return false;
  }
  return true;
}
