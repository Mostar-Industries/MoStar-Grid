#!/usr/bin/env python3
"""
Graph Backend – Boot
--------------------
Handles Neo4j initialization and graph persistence utilities.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from neo4j import GraphDatabase

from core_engine.moscript_engine import MoScriptEngine


class GraphBackend:
    def __init__(self, uri: str | None = None, user: str = "neo4j", password: str | None = None):
        self.mo = MoScriptEngine()
        self.uri = uri or os.getenv("NEO4J_URI")
        self.user = user
        self.password = password or os.getenv("NEO4J_PASSWORD")

    def ignite(self) -> dict:
        ritual = {
            "operation": "seal",
            "payload": {"action": "ignite_graph_backend", "uri": self.uri},
        }
        return self.mo.interpret(ritual)


class GridGraph:
    """Handles Neo4j persistence for the MoStar Grid."""

    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self) -> None:
        self.driver.close()

    def store_seal(self, seal_json: str, label: str) -> str:
        if not seal_json:
            raise ValueError("No seal payload provided for persistence.")

        data = json.loads(seal_json)
        result = data.get("result") or {}
        payload = result.get("payload") or {}
        signature = result.get("signature") or self._derive_signature(payload)
        sealed_at = result.get("sealed_at")

        self._validate_token("label", label)
        with self.driver.session() as session:
            session.run(
                f"""
                MERGE (n:{label} {{signature: $sig}})
                SET n += $payload,
                    n.mostar_status = $status,
                    n.operation = $operation,
                    n.sealed_at = coalesce($sealed_at, n.sealed_at)
                """,
                sig=signature,
                payload=payload,
                status=data.get("status"),
                operation=data.get("operation"),
                sealed_at=sealed_at,
            )
        return signature

    def link(self, src_label: str, src_sig: str, rel_type: str, dst_label: str, dst_sig: str) -> None:
        self._validate_token("src_label", src_label)
        self._validate_token("dst_label", dst_label)
        self._validate_token("rel_type", rel_type)

        with self.driver.session() as session:
            session.run(
                f"""
                MATCH (a:{src_label} {{signature: $src_sig}})
                MATCH (b:{dst_label} {{signature: $dst_sig}})
                MERGE (a)-[r:{rel_type}]->(b)
                RETURN type(r)
                """,
                src_sig=src_sig,
                dst_sig=dst_sig,
            )

    def _derive_signature(self, payload: Dict[str, Any]) -> str:
        serialized = json.dumps(payload, sort_keys=True).encode()
        blessing = hashlib.sha256(serialized).hexdigest()[:12]
        return f"qseal:{blessing}"

    @staticmethod
    def _validate_token(name: str, value: str) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_]+", value or ""):
            raise ValueError(f"Invalid {name}: {value}")


def main() -> None:
    parser = argparse.ArgumentParser(description="MoStar Grid graph utilities.")
    subparsers = parser.add_subparsers(dest="command")

    store_parser = subparsers.add_parser("store", help="Store a MoScript seal as a node.")
    store_parser.add_argument("label", help="Label to assign to the node.")

    link_parser = subparsers.add_parser("link", help="Link two stored seals.")
    link_parser.add_argument("src_label")
    link_parser.add_argument("src_signature")
    link_parser.add_argument("rel_type")
    link_parser.add_argument("dst_label")
    link_parser.add_argument("dst_signature")

    args = parser.parse_args()

    if args.command is None:
        backend = GraphBackend()
        print(json.dumps(backend.ignite(), indent=4))
        return

    graph = GridGraph()
    try:
        if args.command == "store":
            seal_payload = sys.stdin.read().strip()
            signature = graph.store_seal(seal_payload, args.label)
            print(f"Stored {args.label} node with signature {signature}")
        elif args.command == "link":
            graph.link(
                args.src_label,
                args.src_signature,
                args.rel_type,
                args.dst_label,
                args.dst_signature,
            )
            print(
                f"Linked {args.src_label} ({args.src_signature}) "
                f"-> {args.dst_label} ({args.dst_signature}) via {args.rel_type}"
            )
    finally:
        graph.close()


if __name__ == "__main__":
    main()
