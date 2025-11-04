// /lib/mostar/BuilderPacket.ts
import { validateScroll } from './ScrollValidator';
import { Codex, Scroll } from '../../types/moscript';
import { WooTraceLog } from '../../types';
import { saveScroll, logWooTrace } from '../db';
import { wooInterpret } from './WooInterpreter';

// In a real app, these would be fetched from an API. For this packet, we import them.
import { codexData } from '../../data/mogrid_u_codex';
import { scrollsData } from '../../data/scrolls';

const fetchCodex = async (): Promise<Codex> => {
  return Promise.resolve(codexData);
};

const fetchScrolls = async (): Promise<Scroll[]> => {
  return Promise.resolve(scrollsData);
};

/**
 * Initializes the MoStar Grid's covenant, validates the core scrolls, and (simulates) saving them to the database.
 * This function should be called once when the application starts.
 */
export async function initializeCovenant() {
  console.log('⚙️ MoStar Grid Phase 1 Initialization Started');

  const codex = await fetchCodex();
  const scrolls = await fetchScrolls(); 
  
  console.log(`[Covenant Loaded] ${codex.length} scriptures registered.`);

  for (const scroll of scrolls) {
    const result = validateScroll(scroll, codex);
    const scorePercent = (result.score * 100).toFixed(2);
    console.log(`[Scroll Validation] "${scroll.name}" → ${result.status.toUpperCase()} (Resonance: ${scorePercent}%)`);
    
    // --- Database Activation Step ---
    const interpretation = wooInterpret(scroll, codex);
    
    // 1. Save the scroll itself
    await saveScroll({
      ...scroll,
      resonance_score: interpretation.score,
      approved: interpretation.status === 'approved'
    });
    
    // 2. Log the Woo trace for this validation event
    const traceLog: WooTraceLog = {
      id: crypto.randomUUID(),
      scroll_id: scroll.id,
      status: interpretation.status,
      score: interpretation.score,
      explanation: interpretation.scripture || 'No specific scripture alignment.',
      proverb: interpretation.proverb,
      timestamp: interpretation.timestamp,
    };
    await logWooTrace(traceLog);
  }

  console.log('✅ MoScript, Woo, Validator, Registry loaded. Covenant bootstrapped. DB persistence simulated.');
}

// Export all core functions for potential use throughout the application
export { executeMoScript } from './MoScriptEngine';
export { wooInterpret };
export { calculateResonance, getScriptureAlignment } from './ResonanceEngine';
