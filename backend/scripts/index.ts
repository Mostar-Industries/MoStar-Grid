/**
 * MoScript Registry Initialization
 * Imports and registers all available MoScripts
 */

import { moscriptRegistry } from '../services/moscriptRegistry';

// Import logistics scripts
import { mo_FWD_EFFICIENCY } from './logistics/freightEfficiency';
import { mo_COST_ALERT } from './logistics/costOptimization';

/**
 * Initialize and register all MoScripts
 */
export function initializeMoScripts(): void {
  console.log('[MoScript] Initializing script registry...');
  
  // Register logistics scripts
  moscriptRegistry.register(mo_FWD_EFFICIENCY);
  moscriptRegistry.register(mo_COST_ALERT);
  
  // Future categories:
  // - Analytics scripts
  // - Compliance scripts
  // - Communication scripts
  // - Predictive scripts
  
  const stats = moscriptRegistry.getStats();
  console.log(`[MoScript] Registry initialized:`, stats);
  console.log(`[MoScript] Available triggers:`, moscriptRegistry.getTriggers());
}

// Auto-initialize on import (can be called manually if preferred)
initializeMoScripts();

export { moscriptRegistry };
