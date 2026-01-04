# REMOSTAR DCX1-SOUL (Model Card)

- Role: Soul layer | ethics, culture, Ubuntu
- Base model: qwen2:7b
- Ollama tag: akiniobong10/Mostar-REMOSTAR_DCX1
- Build command: ollama create akiniobong10/Mostar-REMOSTAR_DCX1 -f Modelfile
- Context: ~12000+ tokens (see Modelfile parameters)
- Inputs: natural language prompts; optional Neo4j context if wired by caller
- Outputs: sealed reasoning payloads expected to be wrapped by MostarAI / MoScript
- Safety: follow Covenant guardrails described in Modelfile; keep stops intact
- Notes: intended to run inside REMOSTAR stack alongside sibling layers
