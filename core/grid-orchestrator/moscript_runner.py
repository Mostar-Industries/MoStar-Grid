# ═══════════════════════════════════════════════════════════════════
# MOSTAR GRID — MOSCRIPT RUNNER (CLI)
# The Flame Architect — MSTR-⚡ — MoStar Industries
# "Interface for executing sovereign rituals from the shell."
# ═══════════════════════════════════════════════════════════════════

import sys
import json
import asyncio
import argparse
from core_engine.moscript_engine import MoScriptEngine

async def run_ritual(op: str, payload_json: str):
    engine = MoScriptEngine()
    
    try:
        # Attempt to parse as JSON; fallback to query wrapper if it's a raw string
        payload = json.loads(payload_json) if payload_json.strip() else {}
    except json.JSONDecodeError:
        payload = {"query": payload_json, "purpose": "cli_shorthand"}
    
    ritual = {
        "operation": op,
        "payload":   payload,
        "target":    "Grid.Body"
    }
    
    response = await engine.interpret(ritual)
    status   = response.get("status")

    # Standardized Exit Codes 
    # 0 = ALIGNED | 2 = DISRUPTED | 3 = DENIED | 4 = FAILED
    if status == "disrupted":
        print(json.dumps(response, indent=2, ensure_ascii=False))
        print("\n[MOSCRIPT] Ritual disrupted (Interpreter error).")
        sys.exit(2)
    elif status == "denied":
        print(json.dumps(response, indent=2, ensure_ascii=False))
        print("\n[MOSCRIPT] Ritual denied by Covenant.")
        sys.exit(3)
    elif status == "failed":
        print(json.dumps(response, indent=2, ensure_ascii=False))
        print("\n[MOSCRIPT] Ritual failed during execution.")
        sys.exit(4)
    else:
        print(json.dumps(response, indent=2, ensure_ascii=False))
        print(f"\n[MOSCRIPT] Ritual '{op}' successfully sealed.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MoStar MoScript CLI")
    parser.add_argument("operation", help="Ritual operation name")
    parser.add_argument("--payload", help="JSON payload for the ritual", default="{}")
    parser.add_argument("--file", help="Path to JSON file containing payload", default=None)
    
    args = parser.parse_args()
    
    payload_str = args.payload
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            payload_str = f.read()
    
    asyncio.run(run_ritual(args.operation, payload_str))
