/**
 * MoScript Registry & Execution Engine
 * Manages registration, discovery, and execution of MoScripts
 */

import { MoScript } from '../types/moscript';

export class MoScriptRegistry {
  private scripts: Map<string, MoScript> = new Map();
  private triggerMap: Map<string, Set<string>> = new Map(); // trigger -> script IDs

  /**
   * Register a MoScript in the registry
   */
  register(script: MoScript): void {
    this.scripts.set(script.id, script);
    
    // Index by trigger for fast lookup
    if (!this.triggerMap.has(script.trigger)) {
      this.triggerMap.set(script.trigger, new Set());
    }
    this.triggerMap.get(script.trigger)!.add(script.id);
    
    console.log(`[MoScript] Registered: ${script.name} (${script.id})`);
  }

  /**
   * Execute a specific MoScript by ID
   */
  async execute(scriptId: string, inputs: Record<string, any>): Promise<{
    result: any;
    voiceLine?: string;
    script: MoScript;
  }> {
    const script = this.scripts.get(scriptId);
    
    if (!script) {
      throw new Error(`MoScript not found: ${scriptId}`);
    }

    // Validate inputs
    const missingInputs = script.inputs.filter(input => !(input in inputs));
    if (missingInputs.length > 0) {
      throw new Error(`Missing required inputs: ${missingInputs.join(', ')}`);
    }

    // Execute logic
    const result = await Promise.resolve(script.logic(inputs));

    // Generate voice line if available
    const voiceLine = script.voiceLine ? script.voiceLine(result) : undefined;

    return {
      result,
      voiceLine,
      script
    };
  }

  /**
   * Execute all MoScripts that respond to a specific trigger
   */
  async executeTrigger(trigger: string, inputs: Record<string, any>): Promise<Array<{
    scriptId: string;
    scriptName: string;
    result: any;
    voiceLine?: string;
    error?: string;
  }>> {
    const scriptIds = this.triggerMap.get(trigger);
    
    if (!scriptIds || scriptIds.size === 0) {
      console.log(`[MoScript] No scripts registered for trigger: ${trigger}`);
      return [];
    }

    const results = await Promise.allSettled(
      Array.from(scriptIds).map(async (scriptId) => {
        const execution = await this.execute(scriptId, inputs);
        return {
          scriptId,
          scriptName: execution.script.name,
          result: execution.result,
          voiceLine: execution.voiceLine
        };
      })
    );

    return results.map((result, index) => {
      const scriptId = Array.from(scriptIds)[index];
      const script = this.scripts.get(scriptId)!;
      
      if (result.status === 'fulfilled') {
        return result.value;
      } else {
        return {
          scriptId,
          scriptName: script.name,
          result: null,
          error: result.reason?.message || 'Unknown error'
        };
      }
    });
  }

  /**
   * Get all registered scripts
   */
  getAll(): MoScript[] {
    return Array.from(this.scripts.values());
  }

  /**
   * Get scripts by trigger
   */
  getByTrigger(trigger: string): MoScript[] {
    const scriptIds = this.triggerMap.get(trigger);
    if (!scriptIds) return [];
    
    return Array.from(scriptIds)
      .map(id => this.scripts.get(id)!)
      .filter(Boolean);
  }

  /**
   * Get a specific script by ID
   */
  getById(scriptId: string): MoScript | undefined {
    return this.scripts.get(scriptId);
  }

  /**
   * List all available triggers
   */
  getTriggers(): string[] {
    return Array.from(this.triggerMap.keys());
  }

  /**
   * Get registry statistics
   */
  getStats() {
    return {
      totalScripts: this.scripts.size,
      totalTriggers: this.triggerMap.size,
      scriptsWithSass: Array.from(this.scripts.values()).filter(s => s.sass).length,
      scriptsWithVoice: Array.from(this.scripts.values()).filter(s => s.voiceLine).length
    };
  }
}

// Singleton instance
export const moscriptRegistry = new MoScriptRegistry();
