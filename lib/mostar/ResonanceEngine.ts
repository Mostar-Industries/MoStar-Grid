// /lib/mostar/ResonanceEngine.ts
import { Codex } from '../../types/moscript';

/**
 * Calculates the resonance score of a code string against the codex.
 * @param code The code of the scroll.
 * @param codex The covenant rules.
 * @returns A normalized score between 0 and 1.
 */
export function calculateResonance(code: string, codex: Codex): number {
  const baseScore = codex.reduce((acc, item) =>
    acc + (code.includes(item.term) ? item.weight : 0), 0);
  
  // Normalize the score. Assuming a max positive score around 10.
  const normalizedScore = Math.max(0, Math.min(1, baseScore / 10));
  return normalizedScore; 
}

/**
 * Finds all scriptures from the codex that are relevant to the given code.
 * @param code The code of the scroll.
 * @param codex The covenant rules.
 * @returns An array of scripture strings.
 */
export function getScriptureAlignment(code: string, codex: Codex): string[] {
  return codex
    .filter(item => code.includes(item.term))
    .map(item => item.scripture);
}
