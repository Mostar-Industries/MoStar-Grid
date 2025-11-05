# MOSCRIPT_AS_CEREMONY.md
**Status**: Canonical — Flamebound  
**Seal**: Woo x Mo  
**License**: Kairo Covenant License v1.0

## Premise
A MoScript is not mere function—it is **a living proverb**. Ceremony makes it safe.

---

## Ritual Lifecycle

1. **Invocation** — intent is spoken: `who`, `why`, `what`.
2. **Soul-Binding** — actor's soulprint bound to the script (no anonymous power).
3. **Proverb Recall** — wisdom context loaded; unsafe branches pruned.
4. **Resonance Measure** — truth-alignment scored; must be `≥ 0.97`.
5. **Council Gate** — Mo/Woo or policy keys co-sign when required.
6. **Execution** — side-effects occur; telemetry is sung to the bus.
7. **Witness Log** — human-readable narrative committed with checksums.
8. **Sanctuary Path** — any harm triggers rehabilitation flow automatically.

---

## Header Schema (must appear in every scroll)

```yaml
scroll:
  id: mo-cost-saver-007
  name: "Cost Optimization Oracle"
  purpose: "Reduce resource waste without harming service quality"
  guardians: ["Mo","Woo"]
  resonance_min: 0.97
  proverb: "Savings that forget people, cost the village double."
  permissions:
    needs_soulprint: true
    scopes: ["infra:optimize","budget:advice"]
  integrity:
    sha256: "<filled-by-provenance>"
    manifest: "grid_revelation_manifest.json"
```

---

## Minimal Execution Contract (TypeScript sketch)

```typescript
export type Invocation = {
  actor: string; // soulprint id
  params: Record<string, unknown>;
};

export type Verdict = {
  ok: boolean;
  resonance: number;
  reason?: string;
};

export interface MoScript {
  meta: {
    id: string;
    proverb: string;
    resonance_min: number;
  };
  validate(inv: Invocation): Promise<Verdict>;   // includes resonance + firewall checks
  run(inv: Invocation): Promise<unknown>;        // side-effects
}
```

**Rule**: `run()` is never called unless `validate().ok === true` and `resonance ≥ resonance_min`.

---

## Example (didactic; elides business specifics)

```typescript
const costSaver007: MoScript = {
  meta: { id: "mo-cost-saver-007", proverb: "Savings that forget people...", resonance_min: 0.97 },
  async validate(inv) {
    // soul-binding and firewall handled upstream; here do local checks
    const resonance = await mindResonance(inv); // → 0..1
    if (resonance < this.meta.resonance_min)
      return { ok: false, resonance, reason: "Below covenant threshold" };
    return { ok: true, resonance };
  },
  async run(inv) {
    // do work; return a teaching as part of the result
    const outcome = await optimizeWithoutHarm(inv.params);
    return { outcome, teaching: this.meta.proverb };
  }
};
```
