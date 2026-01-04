# REMOSTAR DCX2-BODY (Model Card)

- Role: Body layer | execution, ops, logging
- Base model: llama3.2:latest
- Ollama tag: akiniobong10/Mostar-REMOSTAR_DCX2
- Build command: ollama create akiniobong10/Mostar-REMOSTAR_DCX2 -f Modelfile
- Context: ~8k+ tokens (see Modelfile parameters)
- Inputs: natural language prompts; optional Neo4j context if wired by caller
- Outputs: sealed reasoning payloads expected to be wrapped by MostarAI / MoScript
- Safety: follow Covenant guardrails described in Modelfile; keep stops intact
- Notes: intended to run inside REMOSTAR stack alongside sibling layers
