// 🔁 Unified Symbolic Transformer: MoStarAI.ts
// ------------------------------------------------------------------
// Centralized entrypoint to access DCX0 (Mind), DCX1 (Soul), DCX2 (Body)
// Symbolic alignment, sealed output, shared MoScript utils
// ------------------------------------------------------------------

import { execSync } from "child_process";
import crypto from "crypto";

// === Shared MoSeal & MoScript Engine ===
export type MoSeal = {
  payload: any;
  blessing: string;
  sealed_at: string;
  signature: string;
};

export type MoScriptResult = {
  status: "aligned" | "disrupted";
  operation: string;
  result?: any;
  error?: string;
};

export class MoScriptEngine {
  private static readonly SEAL_PREFIX = "qseal:";
  private static readonly TRUTH_SALT = "MÒṢE_TRUTH_BINDING";

  interpret(op: string, payload: any): MoScriptResult {
    try {
      const result =
        op === "seal"
          ? this._sealPayload(payload)
          : op === "echo"
          ? payload
          : `Unknown op: ${op}`;

      return { status: "aligned", operation: op, result };
    } catch (err: any) {
      return { status: "disrupted", operation: op, error: err.message };
    }
  }

  private _sealPayload(payload: any): MoSeal {
    const data = JSON.stringify(payload);
    const blessing = crypto
      .createHash("sha256")
      .update(`${data}-${MoScriptEngine.TRUTH_SALT}`)
      .digest("hex")
      .slice(0, 12);
    const now = new Date().toISOString();

    return {
      payload,
      blessing,
      sealed_at: now,
      signature: `${MoScriptEngine.SEAL_PREFIX}${blessing}`,
    };
  }
}

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
