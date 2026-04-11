from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path

from neo4j import GraphDatabase

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

_growth_protocol = importlib.import_module("core_engine.growth_protocol")
ensure_growth_constraints_sync = _growth_protocol.ensure_growth_constraints_sync


def _load_moment_module():
    module_path = BACKEND_DIR / "core_engine" / "mostar_moments_log.py"
    spec = importlib.util.spec_from_file_location("mostar_moments_log", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    moment_module = _load_moment_module()
    driver = GraphDatabase.driver(
        moment_module.NEO4J_URI,
        auth=(moment_module.NEO4J_USER, moment_module.NEO4J_PASS),
    )
    try:
        with driver.session() as session:
            ensure_growth_constraints_sync(session)
            constraints = session.run(
                """
                SHOW CONSTRAINTS YIELD labelsOrTypes, properties
                WHERE any(label IN labelsOrTypes WHERE label IN [
                    'MoStarMoment',
                    'MomentPattern',
                    'TrustProfile',
                    'LearningRule',
                    'CuriosityQuery',
                    'IntegrityViolation'
                ])
                RETURN labelsOrTypes, properties
                ORDER BY labelsOrTypes
                """
            ).data()
            duplicate_fingerprints = session.run(
                """
                MATCH (m:MoStarMoment)
                WHERE m.fingerprint IS NOT NULL
                WITH m.fingerprint AS fingerprint, count(*) AS c
                WHERE c > 1
                RETURN count(*) AS duplicate_fingerprints
                """
            ).single()["duplicate_fingerprints"]
            total_moments = session.run(
                "MATCH (m:MoStarMoment) RETURN count(m) AS total_moments"
            ).single()["total_moments"]
        print("🛡️ GROWTH PROTOCOL VALIDATION")
        print(f"   constraints_found: {len(constraints)}")
        for row in constraints:
            print(
                f"   constraint: labels={row['labelsOrTypes']}, properties={row['properties']}"
            )
        print(f"   total_moments: {total_moments}")
        print(f"   duplicate_moment_fingerprints: {duplicate_fingerprints}")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
