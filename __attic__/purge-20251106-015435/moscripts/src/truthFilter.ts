// src/moscripts/truthFilter.ts

export interface TruthInput {
  claim: string;
  evidence?: string[];
  provenanceOk?: boolean;
  topic?: string;
}

export interface TruthResult {
  score: number; // 0..1
  explanation: string;
  tips?: string[];
}

/** Explainable heuristic truth filter suitable for live deltas. */
export function evaluateTruth(input: TruthInput): TruthResult {
  const claim = String(input.claim || '').trim();
  const evidence = Array.isArray(input.evidence) ? input.evidence : [];
  const topic = (input.topic || '').toLowerCase();
  const provOk = !!input.provenanceOk;

  let score = 0.50;
  const tips: string[] = [];

  // Linguistic sanity
  const allCapsRatio = (claim.replace(/[^A-Z]/g, '').length) / Math.max(1, claim.length);
  if (claim.length >= 80) score += 0.10;
  if (claim.length < 20) { score -= 0.10; tips.push('Add more context.'); }
  if (allCapsRatio > 0.30) { score -= 0.10; tips.push('Avoid excessive ALL CAPS.'); }
  if (/[!?]{3,}/.test(claim)) { score -= 0.05; tips.push('Reduce dramatic punctuation.'); }

  // Evidence
  const urlCount = evidence.filter(e => /^https?:\/\//i.test(e)).length;
  const nonUrlCount = evidence.length - urlCount;
  if (urlCount >= 1) score += 0.15;
  if (urlCount >= 2) score += 0.05;
  if (nonUrlCount >= 1) score += 0.05;
  if (evidence.length === 0) tips.push('Attach at least one reputable source.');

  // Provenance
  if (provOk) score += 0.12; else { score -= 0.05; tips.push('Include a signed provenance header.'); }

  // Topic caution
  if (/(health|finance|politics|security)/.test(topic)) {
    score -= 0.05;
    if (urlCount < 2) tips.push('High-stakes topics need multiple independent sources.');
  }

  score = Math.max(0, Math.min(1, score));

  const explanation = [
    `len=${claim.length}`,
    `evidence(urls=${urlCount}, other=${nonUrlCount})`,
    `provenance=${provOk ? 'verified' : 'unverified'}`,
    topic ? `topic=${topic}` : null
  ].filter(Boolean).join(' | ');

  return { score, explanation, tips };
}
