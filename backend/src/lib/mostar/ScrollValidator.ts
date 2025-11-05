// /lib/mostar/ScrollValidator.ts
import { calculateResonance, getScriptureAlignment } from './ResonanceEngine';
import { Codex, Scroll } from '../../types/moscript';

export interface ValidationResult {
    status: 'denied' | 'warning' | 'approved';
    score: number;
    scripture: string[];
}

/**
 * Validates a scroll against the codex using a resonance threshold.
 * @param scroll The scroll to validate.
 * @param codex The covenant rules.
 * @returns A validation result object.
 */
export function validateScroll(scroll: Scroll, codex: Codex): ValidationResult {
  const score = calculateResonance(scroll.code, codex);
  const scripture = getScriptureAlignment(scroll.code, codex);

  if (score < 0.92)
    return { status: 'denied', score, scripture };

  if (score < 0.95)
    return { status: 'warning', score, scripture };

  return { status: 'approved', score, scripture };
}
