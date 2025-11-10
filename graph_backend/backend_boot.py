#!/usr/bin/env python3
"""
🧩 Graph Backend – Boot
------------------------
Handles Neo4j initialization and graph seeding.
"""

from core_engine.moscript_engine import MoScriptEngine
import os, json

class GraphBackend:
    def __init__(self, uri=None, user="neo4j", password=None):
        self.mo = MoScriptEngine()
        self.uri = uri or os.getenv("NEO4J_URI")
        self.user = user
        self.password = password or os.getenv("NEO4J_PASSWORD")

    def ignite(self):
        ritual = {"operation": "seal", "payload": {"action": "ignite_graph_backend", "uri": self.uri}}
        return self.mo.interpret(ritual)

if __name__ == "__main__":
    backend = GraphBackend()
    print(json.dumps(backend.ignite(), indent=4))
