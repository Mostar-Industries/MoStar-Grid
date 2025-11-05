// /lib/mostar/MoScriptEngine.ts
import { Scroll } from '../../types/moscript';

/**
 * Executes a validated scroll.
 * @param scroll The scroll object to execute.
 * @returns The result of the evaluated scroll code.
 */
export function executeMoScript(scroll: Scroll): any {
  if (!scroll.id || !scroll.code || !scroll.author)
    throw new Error('MoScriptEngine: Missing required fields.');

  if (!scroll.soulprint)
    throw new Error('MoScriptEngine: Scroll must be sealed with soulprint.');

  if (!scroll.id.match(/^[a-f0-9-]{36}$/))
    throw new Error('MoScriptEngine: Invalid UUID format.');

  // Sealed scroll eval — secure boundary handled by validator and runtime.
  // In a real sandboxed environment, this would use a more secure mechanism than direct eval.
  try {
    return new Function(scroll.code)();
  } catch (error) {
    console.error(`Error executing scroll ${scroll.id}:`, error);
    throw new Error(`Execution of scroll '${scroll.name}' failed.`);
  }
}
