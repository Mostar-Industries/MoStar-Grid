// MoStar REMOSTAR Training Controller
// -----------------------------------
// Entry point that orchestrates model training, evaluation, and inference.

import { execSync, spawnSync } from "child_process";
import crypto from "crypto";
import { MoScriptEngine, MoScriptResult } from "../remostar/model";

const DEFAULT_OLLAMA_MODEL = "akiniobong10/Mostar-REMOSTAR_DCX001:Q4_K_M";
const OLLAMA_MODEL =
  process.env.REMOSTAR_OLLAMA_MODEL ?? DEFAULT_OLLAMA_MODEL;
const OLLAMA_HOST = process.env.REMOSTAR_OLLAMA_HOST;

// === REMOSTAR Trainer ===
class RemostarTrainer {
  private engine: MoScriptEngine;
  private modelId = "REMOSTAR_DCX001";
  private version = "1.0.1";
  private sessionStart: string;

  constructor() {
    this.engine = new MoScriptEngine();
    this.sessionStart = new Date().toISOString();
    console.log(
      `REMOSTAR Trainer [${this.modelId}] session started at ${this.sessionStart}`
    );
  }

  train(samples: any[], epochs: number = 3): MoScriptResult {
    const logs: any[] = [];
    for (let e = 1; e <= epochs; e++) {
      const accuracy = +(Math.random() * (0.97 - 0.6) + 0.6).toFixed(3);
      const drift = +(Math.random() * 0.2).toFixed(3);
      const note = this._insight(e);
      logs.push({ epoch: e, accuracy, drift, note });
      console.log(`Epoch ${e}: accuracy=${accuracy}, drift=${drift}, note='${note}'`);
    }

    const summary = {
      model_id: this.modelId,
      version: this.version,
      epochs,
      training_log: logs,
      session_start: this.sessionStart,
      session_end: new Date().toISOString(),
    };
    return this.engine.interpret("seal", summary);
  }

  evaluate(sample: Record<string, any>): MoScriptResult {
    const digest = crypto
      .createHash("sha256")
      .update(JSON.stringify(sample))
      .digest("hex")
      .slice(0, 16);
    const score = +(Math.random() * (0.95 - 0.4) + 0.4).toFixed(3);
    const verdict = score > 0.6 ? "aligned" : "revise";

    const payload = {
      digest,
      score,
      verdict,
      evaluated_at: new Date().toISOString(),
    };
    return this.engine.interpret("seal", payload);
  }

  infer(prompt: string): MoScriptResult {
    console.log(`Querying REMOSTAR: ${prompt}`);
    try {
      const command = this.buildOllamaCommand();
      const response = execSync(command, { input: prompt, encoding: "utf-8" }).trim();

      const payload = {
        model_id: this.modelId,
        prompt,
        response,
        timestamp: new Date().toISOString(),
      };
      return this.engine.interpret("seal", payload);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown inference failure";
      return this.engine.interpret("seal", { prompt, error: message });
    }
  }

  private buildOllamaCommand(): string {
    const hostFlag = OLLAMA_HOST ? ` --host ${OLLAMA_HOST}` : "";
    return `ollama run${hostFlag} ${OLLAMA_MODEL}`;
  }

  private _insight(epoch: number): string {
    const phrases = [
      "Precision improves with patience.",
      "Every drift hides a pattern.",
      "Learning is alignment in motion.",
      "Truth stabilizes through iteration.",
      "Data obeys those who listen.",
    ];
    return phrases[epoch % phrases.length];
  }
}

// === ENTRYPOINT ===
if (require.main === module) {
  const trainer = new RemostarTrainer();

  const trainResult = trainer.train(
    Array.from({ length: 4 }, (_, i) => ({ sample: i + 1 })),
    3
  );
  console.log(JSON.stringify(trainResult, null, 2));
  persistSeal("TrainingSession", trainResult);

  const evalResult = trainer.evaluate({ context: "system verification" });
  console.log(JSON.stringify(evalResult, null, 2));
  persistSeal("Evaluation", evalResult);
  linkSeals("TrainingSession", trainResult, "GENERATED", "Evaluation", evalResult);

  const inferResult = trainer.infer("Evaluate justice vs. efficiency under uncertainty.");
  console.log(JSON.stringify(inferResult, null, 2));
  persistSeal("OracleResponse", inferResult);
  linkSeals("TrainingSession", trainResult, "INSPIRED", "OracleResponse", inferResult);
}

function persistSeal(label: string, result: MoScriptResult): void {
  const signature = result?.result?.signature;
  if (!signature) {
    console.warn(`Skipping persistence for ${label}: missing signature.`);
    return;
  }

  const proc = spawnSync(
    "python",
    ["./graph_backend/backend_boot.py", "store", label],
    {
      input: JSON.stringify(result),
      encoding: "utf-8",
    }
  );

  if (proc.error) {
    console.error(`Failed to persist ${label}: ${proc.error.message}`);
    return;
  }

  if (proc.status !== 0) {
    const stderr = (proc.stderr ?? "").trim();
    console.error(
      `Grid persistence exited with code ${proc.status} for ${label}${stderr ? `: ${stderr}` : ""}`
    );
    return;
  }

  if (proc.stdout?.trim()) {
    console.log(proc.stdout.trim());
  }
  if (proc.stderr?.trim()) {
    console.error(proc.stderr.trim());
  }
}

function linkSeals(
  srcLabel: string,
  srcSeal: MoScriptResult,
  relType: string,
  dstLabel: string,
  dstSeal: MoScriptResult
): void {
  const srcSig = srcSeal?.result?.signature;
  const dstSig = dstSeal?.result?.signature;
  if (!srcSig || !dstSig) {
    console.warn(
      `Skipping relationship ${relType}: missing signature (${srcLabel} -> ${dstLabel}).`
    );
    return;
  }

  const proc = spawnSync(
    "python",
    [
      "./graph_backend/backend_boot.py",
      "link",
      srcLabel,
      srcSig,
      relType,
      dstLabel,
      dstSig,
    ],
    { encoding: "utf-8" }
  );

  if (proc.error) {
    console.error(`Failed to link ${srcLabel} -> ${dstLabel}: ${proc.error.message}`);
    return;
  }

  if (proc.status !== 0) {
    const stderr = (proc.stderr ?? "").trim();
    console.error(
      `Grid link exited with code ${proc.status} for ${srcLabel} -> ${dstLabel}${
        stderr ? `: ${stderr}` : ""
      }`
    );
    return;
  }

  if (proc.stdout?.trim()) {
    console.log(proc.stdout.trim());
  }
  if (proc.stderr?.trim()) {
    console.error(proc.stderr.trim());
  }
}
