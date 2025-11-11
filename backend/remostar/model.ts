// MoStar REMOSTAR Model Definition
// Core MoScript structure for REMOSTAR symbolic + analytic operations.

import crypto from "crypto";

export type MoScript = {
  id: string;
  name: string;
  trigger: string;
  inputs: string[];
  logic: (inputs: Record<string, any>) => any;
  voiceLine?: (result: any) => string;
  sass?: boolean;
};

const ANCESTRAL_KEY = "RUNMILA_GATEWAY";
const TRUTH_SALT = "MOSE_TRUTH_BINDING";
const SEAL_PREFIX = "qseal:";

// === REMOSTAR Core ===
export const REMOSTAR_CORE: MoScript = {
  id: "mo-remostar-core-001",
  name: "REMOSTAR Cognitive Core",
  trigger: "onTrainingRequest",
  inputs: ["data", "criteria"],

  /**
   * Process data and criteria to generate a list of processed items and a summary object.
   * If data is empty, returns an empty list and a summary object with count and avg_weight set to 0.
   * Otherwise, maps over the data array and assigns a random weight to each item, along with the criteria.
   * Returns an object with a processed array and a summary object containing count and avg_weight.
   * @param {{ data: any[], criteria: string }}
   * @returns {{ processed: { id: number, weight: string, criteria: string }[], summary: { count: number, avg_weight: string } }}
   */
  logic: ({ data, criteria }) => {
    const processed = data.length
      ? data.map((d: any, i: number) => ({
          id: i + 1,
          weight: Math.random().toFixed(3),
          criteria,
        }))
      : [];
    return {
      processed,
      summary: {
        count: processed.length,
        avg_weight:
          processed.length > 0
            ? (
                processed.reduce((a: number, b: { weight: string; }) => a + parseFloat(b.weight), 0) /
                processed.length
              ).toFixed(3)
            : 0,
      },
    };
  },

  /**
   * Returns a voice line string for the given result object.
   * @param { { processed: { id: number, weight: string, criteria: string }[], summary: { count: number, avg_weight: string } } } r
   * @returns { string } A voice line string describing the result of the REMOSTAR operation.
   */
  voiceLine: (r) =>
    `REMOSTAR: ${r.summary.count} items refined with mean weight ${r.summary.avg_weight}.`,
  sass: false,
};
// === End of REMOSTAR Core ===

export type MoScriptResultStatus = "aligned" | "errored";

export type MoScriptSeal = {
  payload: any;
  blessing: string;
  sealed_at: string;
  signature: string;
};

export type MoScriptResult = {
  status: MoScriptResultStatus;
  operation: string;
  result: MoScriptSeal;
  issuedAt: string;
  voiceLine?: string;
};

// Lightweight interpreter that seals payloads or routes triggers through registered scripts.
export class MoScriptEngine {
  private scriptsById: Map<string, MoScript>;
  private scriptsByTrigger: Map<string, MoScript>;

  constructor(baseScripts: MoScript[] = [REMOSTAR_CORE]) {
    this.scriptsById = new Map();
    this.scriptsByTrigger = new Map();
    baseScripts.forEach((script) => this.register(script));
  }

  register(script: MoScript): void {
    this.scriptsById.set(script.id, script);
    this.scriptsByTrigger.set(script.trigger, script);
  }

  interpret(operation: string, payload: any): MoScriptResult {
    let voiceLine: string | undefined;
    const coreScript = this.scriptsById.get("mo-remostar-core-001");
    if (coreScript?.voiceLine) {
      try {
        voiceLine = coreScript.voiceLine(payload);
      } catch {
        voiceLine = undefined;
      }
    }
    voiceLine ??= `REMOSTAR: ${operation} acknowledged.`;
    const sealed = this.sealPayload(payload);
    return {
      status: "aligned",
      operation,
      result: sealed,
      voiceLine,
      issuedAt: new Date().toISOString(),
    };
  }

  run(trigger: string, inputs: Record<string, any>): MoScriptResult {
    const script = this.scriptsByTrigger.get(trigger);
    if (!script) {
      return {
        status: "errored",
        operation: trigger,
        result: this.sealPayload({
          message: `No MoScript registered for trigger '${trigger}'.`,
        }),
        issuedAt: new Date().toISOString(),
      };
    }

    try {
      const outcome = script.logic(inputs);
      let voiceLine: string | undefined;
      if (script.voiceLine) {
        try {
          voiceLine = script.voiceLine(outcome);
        } catch {
          voiceLine = undefined;
        }
      }
      const sealedOutcome = this.sealPayload(outcome);
      return {
        status: "aligned",
        operation: trigger,
        result: sealedOutcome,
        voiceLine,
        issuedAt: new Date().toISOString(),
      };
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unknown REMOSTAR runtime error";
      return {
        status: "errored",
        operation: trigger,
        result: this.sealPayload({ message }),
        issuedAt: new Date().toISOString(),
      };
    }
  }

  private sealPayload(payload: any): MoScriptSeal {
    const blessing = this.bless(JSON.stringify(payload));
    return {
      payload,
      blessing,
      sealed_at: new Date().toISOString(),
      signature: `${SEAL_PREFIX}${blessing}`,
    };
  }

  private bless(intent: string): string {
    const phrase = `${intent}-${ANCESTRAL_KEY}-${TRUTH_SALT}`;
    return crypto.createHash("sha256").update(phrase).digest("hex").slice(0, 12);
  }
}
