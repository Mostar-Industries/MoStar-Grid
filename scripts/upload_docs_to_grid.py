from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from neo4j import GraphDatabase
from neo4j.exceptions import AuthError

CATALOG_ID = "grid_import_docs_corpus"
SOURCE_NAME = "docs_dir_upload"
SUBGRAPH = "grid_core"
DOMAIN = "mostar_docs"
CHUNK_SIZE = 1400
TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".rst",
    ".yaml",
    ".yml",
    ".json",
    ".csv",
    ".tsv",
    ".xml",
}


def _load_env_file(env_path: Path) -> dict[str, str]:
    if not env_path.exists():
        return {}
    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _resolve_neo4j_config() -> dict[str, str]:
    backend_dir = Path(__file__).resolve().parents[1]
    env_values = _load_env_file(backend_dir / ".env")
    return {
        "uri": env_values.get("NEO4J_URI")
        or os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        "user": env_values.get("NEO4J_USER") or os.getenv("NEO4J_USER", "neo4j"),
        "password": env_values.get("NEO4J_PASSWORD") or os.getenv("NEO4J_PASSWORD", ""),
    }


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _text_chunks(text: str, size: int) -> list[str]:
    if not text:
        return []
    return [text[i : i + size] for i in range(0, len(text), size)]


def _build_json_structure(
    artifact_id: str, value: Any
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    nodes: list[dict[str, Any]] = []
    rels: list[dict[str, Any]] = []

    def walk(
        current: Any, path: str, depth: int, key: str | None, index: int | None
    ) -> str:
        node_key = hashlib.sha256(
            f"{artifact_id}|{path}".encode("utf-8", errors="ignore")
        ).hexdigest()[:24]
        base = {
            "id": f"json_{node_key}",
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
        scalar_text = (
            current
            if isinstance(current, str)
            else json.dumps(current, ensure_ascii=False)
        )
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


def _extract_docx_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            xml_bytes = archive.read("word/document.xml")
    except Exception:
        return ""
    try:
        root = ElementTree.fromstring(xml_bytes)
    except ElementTree.ParseError:
        return ""
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", namespace):
        parts = [
            node.text for node in paragraph.findall(".//w:t", namespace) if node.text
        ]
        if parts:
            paragraphs.append("".join(parts))
    return "\n".join(paragraphs)


def _extract_pdf_text(path: Path) -> str:
    for module_name in ("pypdf", "PyPDF2"):
        try:
            module = __import__(module_name, fromlist=["PdfReader"])
            reader = module.PdfReader(str(path))
            pages = []
            for page in reader.pages:
                text = page.extract_text() or ""
                if text:
                    pages.append(text)
            return "\n".join(pages)
        except Exception:
            continue
    return ""


def _load_file_payload(
    path: Path,
) -> tuple[str, str, list[dict[str, Any]], list[dict[str, Any]], str | None]:
    extension = path.suffix.lower()
    structure_nodes: list[dict[str, Any]] = []
    structure_rels: list[dict[str, Any]] = []
    root_id: str | None = None
    if extension in TEXT_EXTENSIONS:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if extension == ".json":
            try:
                parsed = json.loads(text)
                artifact_id = f"artifact_{hashlib.sha256(str(path).encode('utf-8', errors='ignore')).hexdigest()[:16]}"
                structure_nodes, structure_rels, root_id = _build_json_structure(
                    artifact_id, parsed
                )
                return text, "json_parsed", structure_nodes, structure_rels, root_id
            except Exception:
                return text, "json_parse_failed_raw_only", [], [], None
        return text, "text_chunked", [], [], None
    if extension == ".docx":
        text = _extract_docx_text(path)
        return text, "docx_text_extracted" if text else "docx_raw_only", [], [], None
    if extension == ".pdf":
        text = _extract_pdf_text(path)
        return text, "pdf_text_extracted" if text else "pdf_raw_only", [], [], None
    return "", "raw_only", [], [], None


class DocsGridUploader:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        self.driver.close()

    def prepare_graph(self, docs_root: Path) -> None:
        with self.driver.session() as session:
            session.run(
                "CREATE CONSTRAINT grid_data_catalog_id IF NOT EXISTS FOR (catalog:DataCatalog) REQUIRE catalog.id IS UNIQUE"
            )
            session.run(
                "CREATE CONSTRAINT source_artifact_id IF NOT EXISTS FOR (artifact:SourceArtifact) REQUIRE artifact.id IS UNIQUE"
            )
            session.run(
                "CREATE INDEX source_artifact_relative_path IF NOT EXISTS FOR (artifact:SourceArtifact) ON (artifact.relative_path)"
            )
            session.run(
                "MERGE (catalog:DataCatalog:GridCore {id: $catalog_id}) "
                "SET catalog.root = $root, "
                "    catalog.source = $source, "
                "    catalog.subgraph = $subgraph, "
                "    catalog.domain = $domain, "
                "    catalog.updated_at = datetime()",
                {
                    "catalog_id": CATALOG_ID,
                    "root": str(docs_root),
                    "source": SOURCE_NAME,
                    "subgraph": SUBGRAPH,
                    "domain": DOMAIN,
                },
            )

    def upload_docs_directory(self, docs_root: Path, repo_root: Path) -> dict[str, int]:
        files = sorted(
            path
            for path in docs_root.iterdir()
            if path.is_file() and "Zone.Identifier" not in path.name
        )
        uploaded = 0
        chunked = 0
        structured = 0
        for file_path in files:
            metadata, chunk_rows, structure_nodes, structure_rels, root_row = (
                self._build_payload(file_path, repo_root)
            )
            self._upsert_document(
                metadata, chunk_rows, structure_nodes, structure_rels, root_row
            )
            uploaded += 1
            if chunk_rows:
                chunked += 1
            if structure_nodes:
                structured += 1
        return {
            "files_uploaded": uploaded,
            "files_with_chunks": chunked,
            "files_with_structure": structured,
        }

    def _build_payload(
        self, file_path: Path, repo_root: Path
    ) -> tuple[
        dict[str, Any],
        list[dict[str, Any]],
        list[dict[str, Any]],
        list[dict[str, Any]],
        dict[str, str] | None,
    ]:
        relative_path = file_path.relative_to(repo_root)
        artifact_id = f"artifact_{hashlib.sha256(str(relative_path).encode('utf-8')).hexdigest()[:16]}"
        text, parse_status, structure_nodes, structure_rels, root_id = (
            _load_file_payload(file_path)
        )
        if structure_nodes:
            for node in structure_nodes:
                node["artifact_id"] = artifact_id
        mime_type = (
            mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        )
        metadata = {
            "catalog_id": CATALOG_ID,
            "catalog_root": str(file_path.parent),
            "artifact_id": artifact_id,
            "filename": file_path.name,
            "absolute_path": str(file_path),
            "relative_path": str(relative_path),
            "grid_path": str(relative_path).replace("\\", "/"),
            "file_url": f"file:///{str(relative_path).replace('\\', '/')}",
            "extension": file_path.suffix.lower() or "<none>",
            "mime_type": mime_type,
            "size_bytes": file_path.stat().st_size,
            "content_hash": _sha256_file(file_path),
            "parse_status": parse_status,
            "chunk_count": len(_text_chunks(text, CHUNK_SIZE)),
            "root_node_id": root_id,
            "source": SOURCE_NAME,
            "subgraph": SUBGRAPH,
            "domain": DOMAIN,
        }
        chunk_rows = [
            {
                "id": f"chunk_{artifact_id}_{index}",
                "artifact_id": artifact_id,
                "chunk_index": index,
                "text": chunk,
                "text_length": len(chunk),
                "content_hash": _sha256_text(chunk),
                "source": SOURCE_NAME,
                "subgraph": SUBGRAPH,
                "domain": DOMAIN,
            }
            for index, chunk in enumerate(_text_chunks(text, CHUNK_SIZE))
        ]
        root_row = {"artifact_id": artifact_id, "root_id": root_id} if root_id else None
        return metadata, chunk_rows, structure_nodes, structure_rels, root_row

    def _upsert_document(
        self,
        metadata: dict[str, Any],
        chunk_rows: list[dict[str, Any]],
        structure_nodes: list[dict[str, Any]],
        structure_rels: list[dict[str, Any]],
        root_row: dict[str, str] | None,
    ) -> None:
        with self.driver.session() as session:
            session.execute_write(
                self._write_document,
                metadata,
                chunk_rows,
                structure_nodes,
                structure_rels,
                root_row,
            )

    @staticmethod
    def _write_document(
        tx,
        metadata: dict[str, Any],
        chunk_rows: list[dict[str, Any]],
        structure_nodes: list[dict[str, Any]],
        structure_rels: list[dict[str, Any]],
        root_row: dict[str, str] | None,
    ) -> None:
        tx.run(
            """
            MERGE (catalog:DataCatalog:GridCore {id: $catalog_id})
            ON CREATE SET catalog.created_at = datetime()
            SET catalog.root = $catalog_root,
                catalog.source = $source,
                catalog.subgraph = $subgraph,
                catalog.domain = $domain,
                catalog.updated_at = datetime()
            MERGE (artifact:SourceArtifact:DocumentAsset:GridCore {id: $artifact_id})
            ON CREATE SET artifact.created_at = datetime()
            SET artifact.filename = $filename,
                artifact.absolute_path = $absolute_path,
                artifact.relative_path = $relative_path,
                artifact.grid_path = $grid_path,
                artifact.file_url = $file_url,
                artifact.extension = $extension,
                artifact.mime_type = $mime_type,
                artifact.size_bytes = $size_bytes,
                artifact.content_hash = $content_hash,
                artifact.parse_status = $parse_status,
                artifact.chunk_count = $chunk_count,
                artifact.root_node_id = $root_node_id,
                artifact.source = $source,
                artifact.subgraph = $subgraph,
                artifact.domain = $domain,
                artifact.updated_at = datetime()
            MERGE (catalog)-[:PROVIDES_DATA]->(artifact)
            """,
            metadata,
        )
        if chunk_rows:
            tx.run(
                """
                UNWIND $rows AS row
                MERGE (chunk:ArtifactChunk:GridCore {id: row.id})
                SET chunk.chunk_index = row.chunk_index,
                    chunk.text = row.text,
                    chunk.text_length = row.text_length,
                    chunk.content_hash = row.content_hash,
                    chunk.source = row.source,
                    chunk.subgraph = row.subgraph,
                    chunk.domain = row.domain
                WITH row, chunk
                MATCH (artifact:SourceArtifact:GridCore {id: row.artifact_id})
                MERGE (artifact)-[:HAS_CHUNK]->(chunk)
                """,
                rows=chunk_rows,
            )
        if structure_nodes:
            tx.run(
                """
                UNWIND $rows AS row
                MERGE (node:StructuredContentNode:GridCore {id: row.id})
                SET node.artifact_id = row.artifact_id,
                    node.path = row.path,
                    node.depth = row.depth,
                    node.key = row.key,
                    node.list_index = row.list_index,
                    node.node_kind = row.node_kind,
                    node.scalar_type = row.scalar_type,
                    node.value_preview = row.value_preview,
                    node.value_length = row.value_length,
                    node.child_count = row.child_count,
                    node.source = $source,
                    node.subgraph = $subgraph,
                    node.domain = $domain
                """,
                rows=structure_nodes,
                source=SOURCE_NAME,
                subgraph=SUBGRAPH,
                domain=DOMAIN,
            )
        if root_row:
            tx.run(
                """
                MATCH (artifact:SourceArtifact:GridCore {id: $artifact_id})
                MATCH (root:StructuredContentNode:GridCore {id: $root_id})
                MERGE (artifact)-[:HAS_ROOT]->(root)
                """,
                artifact_id=root_row["artifact_id"],
                root_id=root_row["root_id"],
            )
        if structure_rels:
            tx.run(
                """
                UNWIND $rows AS row
                MATCH (parent:StructuredContentNode:GridCore {id: row.parent_id})
                MATCH (child:StructuredContentNode:GridCore {id: row.child_id})
                MERGE (parent)-[rel:HAS_CHILD]->(child)
                SET rel.edge_kind = row.edge_kind,
                    rel.edge_key = row.edge_key,
                    rel.edge_index = row.edge_index
                """,
                rows=structure_rels,
            )

    def get_stats(self) -> dict[str, int]:
        with self.driver.session() as session:
            record = session.run(
                """
                MATCH (catalog:DataCatalog:GridCore {id: $catalog_id})-[:PROVIDES_DATA]->(artifact:DocumentAsset:GridCore)
                WITH count(DISTINCT artifact) AS document_assets
                OPTIONAL MATCH (artifact:DocumentAsset:GridCore {source: $source})-[:HAS_CHUNK]->(chunk:ArtifactChunk:GridCore)
                WITH document_assets, count(DISTINCT chunk) AS chunks
                OPTIONAL MATCH (artifact:DocumentAsset:GridCore {source: $source})-[:HAS_ROOT]->(root:StructuredContentNode:GridCore)
                RETURN document_assets, chunks, count(DISTINCT root) AS rooted_documents
                """,
                catalog_id=CATALOG_ID,
                source=SOURCE_NAME,
            ).single()
            return (
                dict(record)
                if record
                else {"document_assets": 0, "chunks": 0, "rooted_documents": 0}
            )


def main() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    repo_root = backend_dir.parent
    docs_root = backend_dir / "neo4j-mostar-industries" / "import" / "docs"
    if not docs_root.exists():
        raise SystemExit(f"Docs directory not found: {docs_root}")
    neo4j_config = _resolve_neo4j_config()
    if not neo4j_config["password"]:
        raise SystemExit(
            "NEO4J_PASSWORD is not configured. Set it in backend/.env or environment variables."
        )
    uploader = DocsGridUploader(
        neo4j_config["uri"],
        neo4j_config["user"],
        neo4j_config["password"],
    )
    try:
        uploader.prepare_graph(docs_root)
        summary = uploader.upload_docs_directory(docs_root, repo_root)
        stats = uploader.get_stats()
        print("📚 DOCS GRID UPLOAD")
        print(f"   files_uploaded: {summary['files_uploaded']}")
        print(f"   files_with_chunks: {summary['files_with_chunks']}")
        print(f"   files_with_structure: {summary['files_with_structure']}")
        print(f"   total_document_assets_in_grid: {stats.get('document_assets', 0)}")
        print(f"   total_document_chunks_in_grid: {stats.get('chunks', 0)}")
        print(f"   rooted_documents_in_grid: {stats.get('rooted_documents', 0)}")
    except AuthError as exc:
        raise SystemExit(
            f"Neo4j authentication failed for {neo4j_config['user']} at {neo4j_config['uri']}."
        ) from exc
    finally:
        uploader.close()


if __name__ == "__main__":
    main()
