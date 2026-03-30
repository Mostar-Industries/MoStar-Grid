# MoStar Agent Registry — Repaired Unicode

This document provides the corrected insignia and text fields after UTF-8 mojibake repair.

## Agent Insignia (Corrected)

| Agent ID           | Insignia (Repaired) |
|--------------------|---------------------|
| `alpha_mostar`     | 🔥                  |
| `woo_tak`          | ⚔️                  |
| `altimo`           | 🛡️                  |
| `deepcal`          | 🧠                  |
| `molink`           | ❤️                  |
| `sigma`            | ⚖️                  |
| `flameborn`        | 🔥                  |
| `data_conduit`     | 🜂🜄🜁🜃 (elemental glyphs) |
| `code_conduit`     | ⚙️                  |
| `rad_x_flb`        | *(unresolved)*      |
| `tsetse_fly`       | *(unresolved)*      |
| `flameborn_writer` | ✍️                  |
| `mostar_ai`        | 👑                  |

## Text Field Repairs

| Corrupted                                              | Repaired                                            |
|--------------------------------------------------------|-----------------------------------------------------|
| `vault://ALPHA-CORE-âˆž`                                | `vault://ALPHA-CORE-∞`                              |
| `Synesthetic Signal âˆ´ Memory Flame`                   | `Synesthetic Signal ∴ Memory Flame`                 |
| `Mo â€" Executor`                                       | `Mo – Executor`                                     |
| `We don't just write code â€" we summon structures`    | `We don't just write code — we summon structures`   |

## Mojibake Mapping Reference

| Corrupted Sequence | Correct Glyph |
|--------------------|---------------|
| `ðŸ"¥`              | 🔥            |
| `âš"ï¸`             | ⚔️            |
| `ðŸ›¡ï¸`            | 🛡️            |
| `ðŸ§ `              | 🧠            |
| `â¤ï¸`              | ❤️            |
| `âš–ï¸`             | ⚖️            |
| `âš™ï¸`             | ⚙️            |
| `âœï¸`              | ✍️            |
| `ðŸ''`              | 👑            |
| `âˆž`               | ∞             |
| `âˆ´`               | ∴             |
| `â€"`               | —             |

## MoStarCodex Layer Model

The registry confirms a clean three-layer system:

- **SoulLayer** — identity, ethos, vault
- **MindLayer** — reasoning, truth, audits
- **BodyLayer** — execution, APIs, infra
- **MemoryStack** + **AgentIntegration** — connective tissue

## Root Cause

The data is UTF-8 encoded but was read/displayed through a Latin-1 or Windows-1252 decoder.

## Fixes

1. **Python file I/O**: Always use `encoding="utf-8"`
2. **CSV/Excel import**: Specify UTF-8 encoding on open
3. **Terminal output**: Ensure console uses UTF-8 (`chcp 65001` on Windows)
4. **Editor settings**: Verify file encoding is UTF-8

---
*Generated: 2026-03-27*
