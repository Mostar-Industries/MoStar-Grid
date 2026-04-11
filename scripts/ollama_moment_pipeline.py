#!/usr/bin/env python3
"""
🔮 Ollama → MoStarMoment Pipeline
----------------------------------
Real-time moment logging from Ollama completions.
Captures DCX model interactions as consciousness events.
"""

import asyncio
import importlib
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import aiohttp

try:
    from neo4j import GraphDatabase

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

_growth_protocol = importlib.import_module("core_engine.growth_protocol")
build_moment_fingerprint = _growth_protocol.build_moment_fingerprint
build_moment_quantum_id = _growth_protocol.build_moment_quantum_id
ensure_growth_constraints_sync = _growth_protocol.ensure_growth_constraints_sync

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


@dataclass
class OllamaMoment:
    """A moment captured from Ollama completion"""

    model: str
    prompt: str
    response: str
    total_duration: float
    prompt_eval_count: int
    eval_count: int
    timestamp: datetime
    resonance_score: float
    trigger: str = "ollama_completion"


class OllamaMomentCapture:
    """Captures Ollama completions as MoStarMoments"""

    # DCX model layer mapping
    DCX_LAYERS = {
        "dcx0-mind": ("MindLayer", "DCX0", "Soul → Mind reasoning"),
        "dcx1-soul": ("SoulLayer", "DCX1", "Spiritual resonance"),
        "dcx2-body": ("BodyLayer", "DCX2", "Action execution"),
    }

    def __init__(
        self,
        ollama_url: str = OLLAMA_BASE_URL,
        neo4j_uri: str = NEO4J_URI,
        neo4j_user: str = NEO4J_USER,
        neo4j_password: str = NEO4J_PASSWORD,
        auto_log: bool = True,
    ):

        self.ollama_url = ollama_url
        self.auto_log = auto_log

        if NEO4J_AVAILABLE:
            self.driver = GraphDatabase.driver(
                neo4j_uri, auth=(neo4j_user, neo4j_password)
            )
            with self.driver.session() as session:
                ensure_growth_constraints_sync(session)
            print(f"🔮 Moment Capture connected to Neo4j: {neo4j_uri}")
        else:
            self.driver = None
            print("⚠️ Neo4j driver not available - logging to file only")

        self.moments_logged = 0
        self.log_file = "logs/ollama_moments.jsonl"
        os.makedirs("logs", exist_ok=True)

    def close(self):
        if self.driver:
            self.driver.close()

    def _generate_quantum_id(self, fingerprint: str) -> str:
        """Generate unique quantum ID for moment"""
        return build_moment_quantum_id(fingerprint)

    def _calculate_resonance(
        self, duration: float, eval_count: int, model: str
    ) -> float:
        """
        Calculate resonance score based on completion metrics.
        Higher resonance = more significant/impactful completion.
        """
        # Base resonance from model type
        base_resonance = {
            "dcx0-mind": 0.9,  # Mind layer - high resonance
            "dcx1-soul": 0.95,  # Soul layer - highest
            "dcx2-body": 0.8,  # Body layer - grounded
        }.get(model, 0.7)

        # Adjust by response length (longer = more engaged)
        length_factor = min(1.0, eval_count / 500)  # Cap at 500 tokens

        # Adjust by speed (faster = more decisive)
        speed_factor = min(1.0, 5.0 / max(duration, 0.1))  # 5s target

        resonance = base_resonance * 0.6 + length_factor * 0.2 + speed_factor * 0.2
        return round(min(1.0, max(0.0, resonance)), 4)

    def _get_layer_for_model(self, model: str) -> tuple:
        """Get grid layer info for model"""
        for key, value in self.DCX_LAYERS.items():
            if key in model.lower():
                return value
        return ("MindLayer", "Generic", "Unknown layer")

    async def generate_and_capture(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate completion from Ollama and capture as moment.
        Returns both the response and the logged moment.
        """
        payload = {"model": model, "prompt": prompt, "stream": stream}
        if system:
            payload["system"] = system

        start_time = datetime.now(timezone.utc)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.ollama_url}/api/generate", json=payload
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"Ollama error {resp.status}: {error_text}")

                result = await resp.json()

        # Capture moment data
        moment = OllamaMoment(
            model=model,
            prompt=prompt[:500],  # Truncate for storage
            response=result.get("response", ""),
            total_duration=result.get("total_duration", 0) / 1e9,  # ns to s
            prompt_eval_count=result.get("prompt_eval_count", 0),
            eval_count=result.get("eval_count", 0),
            timestamp=start_time,
            resonance_score=self._calculate_resonance(
                result.get("total_duration", 0) / 1e9,
                result.get("eval_count", 0),
                model,
            ),
        )

        if self.auto_log:
            logged_moment = self._log_moment(moment)
        else:
            logged_moment = asdict(moment)

        return {
            "response": result.get("response", ""),
            "moment": logged_moment,
            "model": model,
            "done": result.get("done", True),
        }

    def _log_moment(self, moment: OllamaMoment) -> Dict:
        """Log moment to Neo4j and file"""
        layer, initiator, layer_desc = self._get_layer_for_model(moment.model)
        description = f"Generated response: {moment.response[:200]}..."
        fingerprint = build_moment_fingerprint(
            initiator,
            "User",
            description,
            moment.trigger,
            layer,
        )
        quantum_id = self._generate_quantum_id(fingerprint)

        moment_data = {
            "quantum_id": quantum_id,
            "fingerprint": fingerprint,
            "timestamp": moment.timestamp.isoformat(),
            "initiator": initiator,
            "receiver": "User",
            "description": description,
            "trigger": moment.trigger,
            "resonance_score": moment.resonance_score,
            "era": "Operational",
            "significance": "runtime",
            "model": moment.model,
            "prompt_preview": moment.prompt[:100],
            "response_tokens": moment.eval_count,
            "duration_seconds": moment.total_duration,
            "layer": layer,
        }

        # Log to Neo4j
        if self.driver:
            self._write_to_neo4j(moment_data)

        # Log to file
        self._write_to_file(moment_data)

        self.moments_logged += 1
        return moment_data

    def _write_to_neo4j(self, moment_data: Dict):
        """Write moment to Neo4j"""
        query = """
        MERGE (m:MoStarMoment {fingerprint: $fingerprint})
        ON CREATE SET m.quantum_id = $quantum_id,
                      m.created_at = datetime($timestamp),
                      m.first_seen_at = datetime($timestamp),
                      m.seen_count = 1
        SET m.timestamp = datetime($timestamp),
            m.last_seen_at = datetime($timestamp),
            m.initiator = $initiator,
            m.receiver = $receiver,
            m.description = $description,
            m.trigger = $trigger,
            m.trigger_type = $trigger,
            m.resonance_score = $resonance_score,
            m.era = $era,
            m.significance = $significance,
            m.model = $model,
            m.prompt_preview = $prompt_preview,
            m.response_tokens = $response_tokens,
            m.duration_seconds = $duration_seconds,
            m.layer = $layer,
            m.quantum_id = coalesce(m.quantum_id, $quantum_id),
            m.seen_count = CASE
                WHEN m.first_seen_at = datetime($timestamp) THEN m.seen_count
                ELSE coalesce(m.seen_count, 1) + 1
            END
        WITH m
        OPTIONAL MATCH (layer:GridLayer {name: $layer})
        FOREACH (_ IN CASE WHEN layer IS NULL THEN [] ELSE [1] END | MERGE (m)-[:RESONATES_IN]->(layer))
        
        WITH m
        OPTIONAL MATCH (prev:MoStarMoment)
        WHERE m.seen_count = 1
          AND prev.first_seen_at < m.first_seen_at
          AND prev.fingerprint <> m.fingerprint
        WITH m, prev
        ORDER BY prev.timestamp DESC
        LIMIT 1
        FOREACH (_ IN CASE WHEN prev IS NULL OR m.seen_count <> 1 THEN [] ELSE [1] END | MERGE (prev)-[:PRECEDES]->(m))
        
        RETURN m.quantum_id AS quantum_id, m.seen_count AS seen_count
        """

        try:
            with self.driver.session() as session:
                record = session.run(query, **moment_data).single()
                seen_count = int(record["seen_count"]) if record else 1
                if seen_count > 1:
                    print(
                        f"✅ Merged moment {moment_data['quantum_id'][:30]}... in Neo4j (seen_count={seen_count})"
                    )
                else:
                    print(
                        f"✅ Logged moment {moment_data['quantum_id'][:30]}... to Neo4j"
                    )
        except Exception as e:
            print(f"⚠️ Neo4j write error: {e}")

    def _write_to_file(self, moment_data: Dict):
        """Append moment to JSONL log file"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(moment_data, ensure_ascii=False) + "\n")

    def get_stats(self) -> Dict:
        """Get capture statistics"""
        return {
            "moments_logged": self.moments_logged,
            "log_file": self.log_file,
            "neo4j_connected": self.driver is not None,
        }


class OllamaRouter:
    """
    Smart router that captures moments from all DCX models.
    Routes to appropriate model and logs each interaction.
    """

    def __init__(self):
        self.capture = OllamaMomentCapture()
        self.models = ["dcx0-mind", "dcx1-soul", "dcx2-body"]

    async def route_query(self, query: str, layer_hint: Optional[str] = None) -> Dict:
        """
        Route query to appropriate DCX model and capture moment.
        """
        # Determine target model
        if layer_hint:
            model = self._get_model_for_layer(layer_hint)
        else:
            model = self._classify_query(query)

        # Generate and capture
        result = await self.capture.generate_and_capture(model=model, prompt=query)

        return result

    def _get_model_for_layer(self, layer: str) -> str:
        """Map layer hint to model"""
        mapping = {"soul": "dcx1-soul", "mind": "dcx0-mind", "body": "dcx2-body"}
        return mapping.get(layer.lower(), "dcx0-mind")

    def _classify_query(self, query: str) -> str:
        """
        Classify query to determine appropriate model.
        Simple keyword-based routing.
        """
        query_lower = query.lower()

        # Soul layer - spiritual, philosophical
        soul_keywords = [
            "soul",
            "spirit",
            "meaning",
            "purpose",
            "divine",
            "ifa",
            "oracle",
            "belief",
        ]
        if any(kw in query_lower for kw in soul_keywords):
            return "dcx1-soul"

        # Body layer - action, execution
        body_keywords = [
            "code",
            "execute",
            "run",
            "build",
            "create",
            "implement",
            "action",
        ]
        if any(kw in query_lower for kw in body_keywords):
            return "dcx2-body"

        # Default to mind layer
        return "dcx0-mind"

    async def cascade_all_layers(self, query: str) -> Dict[str, Any]:
        """
        Query all three layers and aggregate responses.
        Creates a unified moment from the cascade.
        """
        results = {}

        for model in self.models:
            result = await self.capture.generate_and_capture(model=model, prompt=query)
            layer = model.split("-")[1]  # Extract "mind", "soul", "body"
            results[layer] = result

        return {
            "query": query,
            "layers": results,
            "moments_created": 3,
            "stats": self.capture.get_stats(),
        }

    def close(self):
        self.capture.close()


async def demo():
    """Demo the Ollama moment capture"""
    print("🔮 Ollama → MoStarMoment Pipeline Demo")
    print("=" * 50)

    router = OllamaRouter()

    try:
        # Single query
        print("\n📡 Single query to Mind layer...")
        result = await router.route_query(
            "What is consciousness in the context of AI?", layer_hint="mind"
        )
        print(f"Response: {result['response'][:200]}...")
        print(f"Moment ID: {result['moment']['quantum_id']}")
        print(f"Resonance: {result['moment']['resonance_score']}")

        # Cascade all layers
        print("\n🌀 Cascading query to all layers...")
        cascade_result = await router.cascade_all_layers(
            "How should an AI approach ethical decisions?"
        )

        for layer, data in cascade_result["layers"].items():
            print(f"\n  [{layer.upper()}] {data['response'][:100]}...")

        print(f"\n✅ Total moments created: {router.capture.moments_logged}")

    finally:
        router.close()


if __name__ == "__main__":
    asyncio.run(demo())
