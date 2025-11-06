// src/moscripts/engine.ts
import type { MoScript, MoScriptMeta } from './MoScript';
import { ScrollValidator } from './MoScript';
import { evaluateTruth } from './truthFilter';
import { verifyHMACBase64 } from './provenance';
import type { Verdict, VerdictStatus, AuditRecord, ExecutionContext, ExecutionOptions } from './covenant';
import { statusFromScore, makeTokenBucket } from './covenant';

/** In-memory audit log for demonstration purposes. */
const auditLog: AuditRecord[] = [];
export function getAuditLog(): ReadonlyArray<AuditRecord> { return auditLog; }
export function clearAuditLog() { auditLog.length = 0; }

/** Registered scripts with uniqueness enforcement. */
export class ScrollRegistry {
  private byId = new Map<string, MoScript<any, any>>();

  register<T, R>(script: MoScript<T, R>, meta?: MoScriptMeta): void {
    ScrollValidator.validate(script);
    if (this.byId.has(script.id)) throw new Error(`Duplicate MoScript id: ${script.id}`);
    this.byId.set(script.id, script);
  }

  get<T, R>(id: string): MoScript<T, R> {
    const s = this.byId.get(id);
    if (!s) throw new Error(`Unknown MoScript id: ${id}`);
    return s as any;
  }

  list(): MoScript[] { return Array.from(this.byId.values()); }
}

/** Execute a MoScript with covenant checks and audit, returning verdict + output. */
export async function runMoScript<T, R>(
  registry: ScrollRegistry,
  id: string,
  inputs: T,
  ctx: ExecutionContext = {},
  opts: ExecutionOptions = {}
): Promise<{ verdict: Verdict, output?: R, message: string, audit: AuditRecord }> {

  const script = registry.get<T, R>(id);
  const startedAt = new Date().toISOString();
  const t0 = Date.now();

  // Rate limiting
  const limiter = opts.limiter ?? makeTokenBucket();
  const rateKey = ctx.rateKey || `script:${id}`;
  if (!limiter.consume(rateKey)) {
    const verdict: Verdict = { status: 'denied', score: 0.0, explanation: 'rate-limit', tips: ['Reduce call frequency.'] };
    const audit: AuditRecord = makeAudit(id, script.trigger, verdict, 'Throttled', undefined, startedAt, t0, false);
    auditLog.push(audit);
    return { verdict, output: undefined, message: 'Throttled', audit };
  }

  // Build claim
  const claim = `MoScript ${id} triggered=${script.trigger} sass=${script.sass}`;
  const timestamp = ctx.timestamp || new Date().toISOString();
  const messageToSign = claim + '\n' + timestamp;
  const provenanceOk = (ctx.signature && ctx.secret) ? await verifyHMACBase64(messageToSign, ctx.signature!, ctx.secret!) : false;

  // Truth filter
  const truth = evaluateTruth({
    claim,
    evidence: ctx.evidence || [],
    provenanceOk,
    topic: ctx.topic || ''
  });

  // Status mapping
  const status = statusFromScore(truth.score);
  if (script.sass && status === 'denied') {
    const verdict: Verdict = { status, score: truth.score, explanation: truth.explanation, tips: truth.tips };
    const audit: AuditRecord = makeAudit(id, script.trigger, verdict, 'Denied by covenant', undefined, startedAt, t0, provenanceOk);
    auditLog.push(audit);
    return { verdict, output: undefined, message: 'Denied by covenant', audit };
  }

  // Execute logic
  let output: R | undefined;
  let message = '';
  try {
    output = await script.logic(inputs);
    message = script.voiceLine(output);
  } catch (err: any) {
    const verdict: Verdict = { status: 'denied', score: Math.min(truth.score, 0.5), explanation: `runtime-error: ${String(err?.message || err)}` };
    const audit: AuditRecord = makeAudit(id, script.trigger, verdict, 'Runtime error', undefined, startedAt, t0, provenanceOk);
    auditLog.push(audit);
    return { verdict, output: undefined, message: 'Runtime error', audit };
  }

  // Finalize verdict (escalate if needed)
  const verdict: Verdict = { status, score: truth.score, explanation: truth.explanation, tips: truth.tips };
  const audit: AuditRecord = makeAudit(id, script.trigger, verdict, message, output, startedAt, t0, provenanceOk);
  auditLog.push(audit);
  return { verdict, output, message, audit };
}

function makeAudit<R>(
  scriptId: string,
  trigger: string,
  verdict: Verdict,
  message: string,
  output: R | undefined,
  startedAt: string,
  t0: number,
  provenanceOk: boolean
): AuditRecord<R> {
  const finishedAt = new Date().toISOString();
  return {
    id: `${scriptId}:${Date.now()}`,
    scriptId,
    trigger,
    verdict,
    message,
    output,
    startedAt,
    finishedAt,
    durationMs: Date.now() - t0,
    provenanceOk
  };
}
