from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path("/home/idona/MoStar/MoStar-Grid/backend/neo4j-mostar-industries/import/data/scripts")
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Mostar123"
CHUNK_SIZE = 1400
BATCH_SIZE = 80


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def cypher_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r")


def to_cypher(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and (math.isinf(value) or math.isnan(value)):
            return "null"
        return repr(value)
    if isinstance(value, str):
        return f"'{cypher_escape(value)}'"
    if isinstance(value, list):
        return "[" + ", ".join(to_cypher(item) for item in value) + "]"
    if isinstance(value, dict):
        parts: list[str] = []
        for key, item in value.items():
            safe_key = key if key.replace("_", "").isalnum() and not key[0].isdigit() else f"`{key}`"
            parts.append(f"{safe_key}: {to_cypher(item)}")
        return "{" + ", ".join(parts) + "}"
    return to_cypher(str(value))


def run_cypher(query: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".cypher", delete=False, encoding="utf-8") as handle:
        handle.write(query)
        temp_path = handle.name
    try:
        result = subprocess.run(
            ["cypher-shell", "-u", NEO4J_USER, "-p", NEO4J_PASSWORD, "-f", temp_path],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        return result.stdout
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass


def query_total_nodes() -> int:
    output = run_cypher("MATCH (n) RETURN count(n) AS total;")
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.isdigit():
            return int(stripped)
    raise RuntimeError(f"Unable to parse total node count from output: {output}")


def batches(rows: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [rows[i : i + size] for i in range(0, len(rows), size)]


def write_rows(query_template: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    for batch in batches(rows, BATCH_SIZE):
        literal = "[\n" + ",\n".join(to_cypher(row) for row in batch) + "\n]"
        run_cypher(query_template.replace("$ROWS", literal))


def text_chunks(text: str, size: int) -> list[str]:
    if not text:
        return [""]
    return [text[i : i + size] for i in range(0, len(text), size)]


def build_json_structure(artifact_id: str, value: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    nodes: list[dict[str, Any]] = []
    rels: list[dict[str, Any]] = []

    def walk(current: Any, path: str, depth: int, key: str | None, index: int | None) -> str:
        node_id = sha(f"{artifact_id}|{path}")[:24]
        base = {
            "id": f"json_{node_id}",
            "artifact_id": artifact_id,
            "path": path,
            "depth": depth,
            "key": key,
            "list_index": index,
        }
        if isinstance(current, dict):
            node = {
                **base,
                "node_kind": "object",
                "scalar_type": None,
                "value_preview": None,
                "value_length": None,
                "child_count": len(current),
            }
            nodes.append(node)
            for child_key, child_value in current.items():
                child_path = f"{path}.{child_key}" if path else child_key
                child_id = walk(child_value, child_path, depth + 1, child_key, None)
                rels.append(
                    {
                        "parent_id": node["id"],
                        "child_id": child_id,
                        "edge_kind": "key",
                        "edge_key": child_key,
                        "edge_index": None,
                    }
                )
            return node["id"]
        if isinstance(current, list):
            node = {
                **base,
                "node_kind": "array",
                "scalar_type": None,
                "value_preview": None,
                "value_length": None,
                "child_count": len(current),
            }
            nodes.append(node)
            for child_index, child_value in enumerate(current):
                child_path = f"{path}[{child_index}]"
                child_id = walk(child_value, child_path, depth + 1, None, child_index)
                rels.append(
                    {
                        "parent_id": node["id"],
                        "child_id": child_id,
                        "edge_kind": "index",
                        "edge_key": None,
                        "edge_index": child_index,
                    }
                )
            return node["id"]
        scalar_text = current if isinstance(current, str) else json.dumps(current, ensure_ascii=False)
        node = {
            **base,
            "node_kind": "scalar",
            "scalar_type": type(current).__name__,
            "value_preview": scalar_text[:500],
            "value_length": len(scalar_text),
            "child_count": 0,
        }
        nodes.append(node)
        return node["id"]

    root_id = walk(value, "root", 0, None, None)
    return nodes, rels, root_id


def ingest_file(file_path: Path) -> dict[str, Any]:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    rel_path = str(file_path.relative_to(SCRIPTS_DIR.parent.parent.parent.parent))
    artifact_id = f"artifact_{sha(str(file_path))[:16]}"
    file_hash = sha(text)
    extension = file_path.suffix.lower() or "<none>"
    parse_status = "raw_only"
    root_id = None
    structure_nodes: list[dict[str, Any]] = []
    structure_rels: list[dict[str, Any]] = []

    if extension == ".json":
        try:
            parsed = json.loads(text)
            parse_status = "json_parsed"
            structure_nodes, structure_rels, root_id = build_json_structure(artifact_id, parsed)
        except Exception:
            parse_status = "json_parse_failed_raw_only"

    artifact_row = {
        "id": artifact_id,
        "filename": file_path.name,
        "absolute_path": str(file_path),
        "relative_path": rel_path,
        "extension": extension,
        "size_bytes": file_path.stat().st_size,
        "content_hash": file_hash,
        "parse_status": parse_status,
        "chunk_count": len(text_chunks(text, CHUNK_SIZE)),
        "root_node_id": root_id,
        "created_at": "datetime()",
        "source": "scripts_dir_ingest",
        "subgraph": "grid_core",
        "domain": "mostar_grid",
    }

    chunk_rows: list[dict[str, Any]] = []
    for idx, chunk in enumerate(text_chunks(text, CHUNK_SIZE)):
        chunk_rows.append(
            {
                "id": f"chunk_{artifact_id}_{idx}",
                "artifact_id": artifact_id,
                "chunk_index": idx,
                "text": chunk,
                "text_length": len(chunk),
                "content_hash": sha(chunk),
                "source": "scripts_dir_ingest",
                "subgraph": "grid_core",
                "domain": "mostar_grid",
            }
        )

    write_rows(
        """
UNWIND $ROWS AS row
MERGE (a:SourceArtifact:GridCore {id: row.id})
SET a.filename = row.filename,
    a.absolute_path = row.absolute_path,
    a.relative_path = row.relative_path,
    a.extension = row.extension,
    a.size_bytes = row.size_bytes,
    a.content_hash = row.content_hash,
    a.parse_status = row.parse_status,
    a.chunk_count = row.chunk_count,
    a.root_node_id = row.root_node_id,
    a.source = row.source,
    a.subgraph = row.subgraph,
    a.domain = row.domain;
""",
        [artifact_row],
    )

    write_rows(
        """
UNWIND $ROWS AS row
MERGE (c:ArtifactChunk:GridCore {id: row.id})
SET c.chunk_index = row.chunk_index,
    c.text = row.text,
    c.text_length = row.text_length,
    c.content_hash = row.content_hash,
    c.source = row.source,
    c.subgraph = row.subgraph,
    c.domain = row.domain
WITH row, c
MATCH (a:SourceArtifact:GridCore {id: row.artifact_id})
MERGE (a)-[:HAS_CHUNK]->(c);
""",
        chunk_rows,
    )

    write_rows(
        """
UNWIND $ROWS AS row
MERGE (n:StructuredContentNode:GridCore {id: row.id})
SET n.artifact_id = row.artifact_id,
    n.path = row.path,
    n.depth = row.depth,
    n.key = row.key,
    n.list_index = row.list_index,
    n.node_kind = row.node_kind,
    n.scalar_type = row.scalar_type,
    n.value_preview = row.value_preview,
    n.value_length = row.value_length,
    n.child_count = row.child_count,
    n.source = 'scripts_dir_ingest',
    n.subgraph = 'grid_core',
    n.domain = 'mostar_grid';
""",
        structure_nodes,
    )

    if root_id:
        write_rows(
            """
UNWIND $ROWS AS row
MATCH (a:SourceArtifact:GridCore {id: row.artifact_id})
MATCH (r:StructuredContentNode:GridCore {id: row.root_id})
MERGE (a)-[:HAS_ROOT]->(r);
""",
            [{"artifact_id": artifact_id, "root_id": root_id}],
        )

    write_rows(
        """
UNWIND $ROWS AS row
MATCH (p:StructuredContentNode:GridCore {id: row.parent_id})
MATCH (c:StructuredContentNode:GridCore {id: row.child_id})
MERGE (p)-[rel:HAS_CHILD]->(c)
SET rel.edge_kind = row.edge_kind,
    rel.edge_key = row.edge_key,
    rel.edge_index = row.edge_index;
""",
        structure_rels,
    )

    return {
        "file": file_path.name,
        "artifact_id": artifact_id,
        "parse_status": parse_status,
        "chunks": len(chunk_rows),
        "structure_nodes": len(structure_nodes),
        "structure_rels": len(structure_rels),
    }


def main() -> None:
    files = sorted(
        path
        for path in SCRIPTS_DIR.iterdir()
        if path.is_file() and "Zone.Identifier" not in path.name
    )
    before = query_total_nodes()
    print(f"START_NODES={before}")
    print(f"FILES_TO_INGEST={len(files)}")
    for file_path in files:
        pre = query_total_nodes()
        summary = ingest_file(file_path)
        post = query_total_nodes()
        delta = post - pre
        print(
            json.dumps(
                {
                    "file": summary["file"],
                    "parse_status": summary["parse_status"],
                    "chunks": summary["chunks"],
                    "structure_nodes": summary["structure_nodes"],
                    "structure_rels": summary["structure_rels"],
                    "nodes_before": pre,
                    "nodes_after": post,
                    "delta": delta,
                },
                ensure_ascii=False,
            )
        )
    final_total = query_total_nodes()
    print(f"FINAL_NODES={final_total}")
    print(f"TOTAL_DELTA={final_total - before}")


if __name__ == "__main__":
    main()
