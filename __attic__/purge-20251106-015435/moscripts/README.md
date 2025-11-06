# moscript-core

Core TypeScript modules for MoScript execution in the MoStar GRID:

- `MoScript.ts` – interface + validator (keeps original shape; adds stricter checks).
- `covenant.ts` – covenant rules and reusable validators.
- `truthFilter.ts` – explainable scoring with tips.
- `provenance.ts` – HMAC verification for signatures (Node/WebCrypto).
- `engine.ts` – pipeline: validate → provenance → truth → rate-limit → execute → voiceLine → audit.

Run the example demo:
```bash
npm i
npm run demo
```
