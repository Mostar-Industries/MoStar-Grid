// src/moscripts/covenant.ts
import type { MoScript } from './MoScript';

/** Result of covenant evaluation prior to execution. */
export type VerdictStatus = 'approved' | 'warning' | 'denied';

export interface Verdict {
  status: VerdictStatus;
  score: number;         // 0..1
  explanation: string;
  tips?: string[];
}

/** Audit record emitted after an execution. */
export interface AuditRecord<R = any> {
  id: string;
  scriptId: string;
  trigger: string;
  verdict: Verdict;
  message: string;
  output?: R;
  startedAt: string;
  finishedAt: string;
  durationMs: number;
  provenanceOk: boolean;
}

export interface ExecutionContext {
  /** ISO timestamp used in signature calculation. */
  timestamp?: string;
  /** Base64 HMAC signature for provenance. */
  signature?: string;
  /** Secret used to verify signature on the server side. */
  secret?: string;
  /** Evidence list supporting the invocation. */
  evidence?: string[];
  /** Topic classification influences truth filter. */
  topic?: string;
  /** Optional rate limiting key (e.g., user id). */
  rateKey?: string;
}

export interface RateLimiter {
  consume: (key: string) => boolean; // true if allowed, false if throttled
}

export interface ExecutionOptions {
  limiter?: RateLimiter;
  truthThreshold?: number; // default 0.95 approved; 0.90-0.95 warning
}

/** Helper to map score to status bands. */
export function statusFromScore(score: number): VerdictStatus {
  if (score >= 0.95) return 'approved';
  if (score >= 0.90) return 'warning';
  return 'denied';
}

/** Simple token-bucket limiter for demo usage. */
export function makeTokenBucket(opsPerMinute = 60): RateLimiter {
  const tokens = new Map<string, { t: number, c: number }>();
  const refill = opsPerMinute;
  return {
    consume(key: string) {
      const now = Date.now();
      const slot = Math.floor(now / 60000); // 1-minute slots
      const cur = tokens.get(key);
      if (!cur || cur.t !== slot) {
        tokens.set(key, { t: slot, c: refill - 1 });
        return true;
      }
      if (cur.c <= 0) return false;
      cur.c -= 1;
      return true;
    }
  };
}
