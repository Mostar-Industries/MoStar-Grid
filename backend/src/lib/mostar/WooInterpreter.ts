// /lib/mostar/WooInterpreter.ts
import { validateScroll } from './ScrollValidator';
import { Codex, Scroll } from '../../types/moscript';

export interface Interpretation {
    status: 'denied' | 'warning' | 'approved';
    score: number;
    scripture: string | undefined;
    proverb: string;
    timestamp: string;
}

/**
 * Interprets a scroll's validation, providing a status, score, relevant scripture, and a proverb.
 * @param scroll The scroll to interpret.
 * @param codex The covenant rules.
 * @returns An interpretation object.
 */
export function wooInterpret(scroll: Scroll, codex: Codex): Interpretation {
  const result = validateScroll(scroll, codex);
  const proverb = result.status === 'approved'
    ? "When the drumbeat aligns with the heart, even silence obeys."
    : result.status === 'warning'
    ? "Even the owl blinks twice before calling it night."
    : "Not every path lit by fire leads to truth — some just burn.";

  return {
    status: result.status,
    score: result.score,
    scripture: result.scripture[0],
    proverb,
    timestamp: new Date().toISOString()
  };
}
