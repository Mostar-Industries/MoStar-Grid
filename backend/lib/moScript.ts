// Shared MoScript types and engine used across backend modules.

import crypto from "crypto";

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
