#!/usr/bin/env python3
"""
Lightweight smoke tests for the MoStar Grid FastAPI services.
Stubs out Ollama/Claude dependencies so we can verify responses locally.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

# Ensure required env vars exist before imports that rely on them.
os.environ.setdefault("ANTHROPIC_API_KEY", "dummy-key")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core_engine.api_gateway import app  # noqa: E402

client = TestClient(app)


class DummyResponse:
    status_code = 200
    text = "ok"

    def json(self):
        return {"response": "Mock grid reply"}


def run_status():
    return client.get("/api/v1/status").json()


def run_reason():
    async def fake_post(*args, **kwargs):
        return DummyResponse()

    with patch("core_engine.api_gateway.httpx.AsyncClient") as mock_client:
        cm = MagicMock()
        cm.post = fake_post
        mock_client.return_value.__aenter__.return_value = cm
        response = client.post("/api/v1/reason", data={"prompt": "Who guards the Grid?"})
    return response.json()


def run_moment():
    payload = {
        "initiator": "TestSuite",
        "receiver": "Grid",
        "description": "Smoke test moment",
        "trigger_type": "test",
        "resonance_score": 0.82,
    }
    return client.post("/api/v1/moment", json=payload).json()


def main():
    results = {
        "status": run_status(),
        "reason": run_reason(),
        "moment": run_moment(),
    }

    output_path = Path("logs") / "smoke_test_results.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        for key, value in results.items():
            fh.write(f"{key.upper()} -> {value}\n")

    for key, value in results.items():
        print(f"{key.upper()} -> {value}")


if __name__ == "__main__":
    main()
