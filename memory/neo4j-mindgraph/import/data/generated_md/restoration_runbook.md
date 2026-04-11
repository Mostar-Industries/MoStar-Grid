# MoStar Restoration Runbook

Generated from the current restoration state and architecture collation.

## Purpose

Capture existing modules, generate import-ready files for missing modules, and keep execution approval-gated.

## Files in this pack

- `generated_csv/entity_capture_matrix.csv`
- `generated_csv/missing_modules_seed.csv`
- `generated_json/gap_capture_manifest.json`
- `generated_cypher/phase_g_missing_modules.cypher`
- `generated_cypher/integrity_audit_queries.cypher`

## What this pack adds

This pack does **not** touch Neo4j by itself. It creates import-ready files for architecture elements that were referenced in the system collation but did not have clean import files:

- DeepCAL
- CodeConduit
- WooCommerceLayer
- WooTruthBridge
- FlameBornMoStarBridge

## Recommended approval order

1. Review `entity_capture_matrix.csv`
2. Review `missing_modules_seed.csv`
3. Review `phase_g_missing_modules.cypher`
4. Run `integrity_audit_queries.cypher`
5. If approved, run `phase_g_missing_modules.cypher`
6. Checkpoint: `MATCH (n) RETURN count(n)`

## Guardrails

- No deletes
- No dedupe
- No schema drops
- No autonomous execution
- Namespace labels preserved
