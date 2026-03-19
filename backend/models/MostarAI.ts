// 🔁 Unified Symbolic Transformer: MoStarAI.ts
// ------------------------------------------------------------------
// Centralized entrypoint to access DCX0 (Mind), DCX1 (Soul), DCX2 (Body)
// Symbolic alignment, sealed output, shared MoScript utils
// ------------------------------------------------------------------

import { execSync } from "child_process";
import { MoScriptEngine, MoScriptResult } from "../lib/moScript";

export type { MoSeal, MoScriptResult } from "../lib/moScript";
export { MoScriptEngine };

// === Proxy Interface to DCX0 / DCX1 / DCX2 ===
const runOllama = (modelTag: string, prompt: string): string => {
  try {
    const command = `ollama run ${modelTag}`;
    const output = execSync(command, { input: prompt, encoding: "utf-8" });
    return output.trim();
  } catch (error: any) {
    return `Ollama error (${modelTag}): ${error.message}`;
  }
};

export class MostarAI {
  private engine: MoScriptEngine;
  private dcx0Tag = "akiniobong10/Mostar-REMOSTAR_DCX001";
  private dcx1Tag = "akiniobong10/Mostar-REMOSTAR_DCX1";
  private dcx2Tag = "akiniobong10/Mostar-REMOSTAR_DCX2";

  constructor() {
    this.engine = new MoScriptEngine();
  }

  inferFromMind(prompt: string): MoScriptResult {
    const output = runOllama(this.dcx0Tag, prompt);
    return this._seal("mind", prompt, output);
  }

  inferFromSoul(prompt: string): MoScriptResult {
    const output = runOllama(this.dcx1Tag, prompt);
    return this._seal("soul", prompt, output);
  }

  inferFromBody(prompt: string): MoScriptResult {
    const output = runOllama(this.dcx2Tag, prompt);
    return this._seal("body", prompt, output);
  }

  private _seal(source: string, prompt: string, output: string): MoScriptResult {
    const payload = {
      layer: source,
      prompt,
      response: output,
      timestamp: new Date().toISOString(),
    };
    return this.engine.interpret("seal", payload);
  }
}

// === Entrypoint Test (Optional) ===
if (require.main === module) {
  const ai = new MostarAI();

  console.log("🧠 DCX0:");
  console.log(ai.inferFromMind("Evaluate balance between efficiency and truth."));

  console.log("🧬 DCX1:");
  console.log(ai.inferFromSoul("Bless this output with Ubuntu ethics."));

  console.log("⚙️ DCX2:");
  console.log(ai.inferFromBody("Transform CSV into sanitized JSON."));
}
