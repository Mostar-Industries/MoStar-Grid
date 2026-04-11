# REMOSTAR DCX0-MIND (Model Card)

- Role: Mind layer | reasoning, logic, audit
- Base model: phi4:latest
- Ollama tag: akiniobong10/Mostar-REMOSTAR_DCX001
- Build command: ollama create akiniobong10/Mostar-REMOSTAR_DCX001 -f Modelfile
- Context: ~16384 tokens (see Modelfile parameters)
- Inputs: natural language prompts; optional Neo4j context if wired by caller
- Outputs: sealed reasoning payloads expected to be wrapped by MostarAI / MoScript
- Safety: follow Covenant guardrails described in Modelfile; keep stops intact
- Notes: intended to run inside REMOSTAR stack alongside sibling layers
