from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Dict

from neo4j import GraphDatabase
from neo4j.exceptions import AuthError

CATALOG_ID = "grid_ibibio_audio_corpus"
SOURCE_NAME = "ibibio_audio_upload"
SUBGRAPH = "grid_core"
DOMAIN = "ibibio_language"
MIME_TYPE = "audio/mpeg"


def _load_env_file(env_path: Path) -> Dict[str, str]:
    if not env_path.exists():
        return {}
    values: Dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _resolve_neo4j_config() -> Dict[str, str]:
    backend_dir = Path(__file__).resolve().parents[1]
    env_values = _load_env_file(backend_dir / ".env")
    return {
        "uri": env_values.get("NEO4J_URI")
        or os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        "user": env_values.get("NEO4J_USER") or os.getenv("NEO4J_USER", "neo4j"),
        "password": env_values.get("NEO4J_PASSWORD") or os.getenv("NEO4J_PASSWORD", ""),
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class IbibioAudioGridUploader:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        self.driver.close()

    def prepare_graph(self, audio_root: Path) -> None:
        with self.driver.session() as session:
            session.run(
                "CREATE CONSTRAINT grid_data_catalog_id IF NOT EXISTS FOR (catalog:DataCatalog) REQUIRE catalog.id IS UNIQUE"
            )
            session.run(
                "CREATE CONSTRAINT source_artifact_id IF NOT EXISTS FOR (artifact:SourceArtifact) REQUIRE artifact.id IS UNIQUE"
            )
            session.run(
                "CREATE INDEX audio_asset_grid_path IF NOT EXISTS FOR (artifact:AudioAsset) ON (artifact.grid_path)"
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
                    "root": str(audio_root),
                    "source": SOURCE_NAME,
                    "subgraph": SUBGRAPH,
                    "domain": DOMAIN,
                },
            )

    def upload_audio_directory(self, audio_root: Path, repo_root: Path) -> dict:
        uploaded = 0
        linked_words = 0
        unlinked_assets = 0
        for audio_path in sorted(audio_root.glob("*.mp3")):
            metadata = self._build_metadata(audio_path, audio_root, repo_root)
            linked = self._upsert_audio_asset(metadata)
            uploaded += 1
            linked_words += linked
            if linked == 0:
                unlinked_assets += 1
        return {
            "audio_assets_uploaded": uploaded,
            "word_links_created": linked_words,
            "unlinked_audio_assets": unlinked_assets,
        }

    def _build_metadata(
        self, audio_path: Path, audio_root: Path, repo_root: Path
    ) -> dict:
        relative_path = audio_path.relative_to(repo_root)
        grid_path = Path("data") / "Ibibio_codex" / "Ibibio_audio" / audio_path.name
        return {
            "catalog_id": CATALOG_ID,
            "catalog_root": str(audio_root),
            "asset_id": f"audio_asset_{hashlib.sha256(str(relative_path).encode('utf-8')).hexdigest()[:24]}",
            "filename": audio_path.name,
            "absolute_path": str(audio_path),
            "relative_path": str(relative_path),
            "grid_path": str(grid_path).replace("\\", "/"),
            "file_url": f"file:///{str(grid_path).replace('\\', '/')}",
            "extension": audio_path.suffix.lower() or ".mp3",
            "mime_type": MIME_TYPE,
            "size_bytes": audio_path.stat().st_size,
            "content_hash": _sha256_file(audio_path),
            "source": SOURCE_NAME,
            "subgraph": SUBGRAPH,
            "domain": DOMAIN,
        }

    def _upsert_audio_asset(self, metadata: dict) -> int:
        with self.driver.session() as session:
            result = session.execute_write(self._write_audio_asset, metadata)
        return result

    @staticmethod
    def _write_audio_asset(tx, metadata: dict) -> int:
        result = tx.run(
            """
            MERGE (catalog:DataCatalog:GridCore {id: $catalog_id})
            ON CREATE SET catalog.created_at = datetime()
            SET catalog.root = $catalog_root,
                catalog.source = $source,
                catalog.subgraph = $subgraph,
                catalog.domain = $domain,
                catalog.updated_at = datetime()
            MERGE (asset:SourceArtifact:AudioAsset:GridCore {id: $asset_id})
            ON CREATE SET asset.created_at = datetime()
            SET asset.filename = $filename,
                asset.absolute_path = $absolute_path,
                asset.relative_path = $relative_path,
                asset.grid_path = $grid_path,
                asset.file_url = $file_url,
                asset.extension = $extension,
                asset.mime_type = $mime_type,
                asset.size_bytes = $size_bytes,
                asset.content_hash = $content_hash,
                asset.source = $source,
                asset.subgraph = $subgraph,
                asset.domain = $domain,
                asset.updated_at = datetime()
            MERGE (catalog)-[:PROVIDES_DATA]->(asset)
            WITH asset
            OPTIONAL MATCH (word:IbibioWord)
            WHERE word.audio_file = $filename
               OR word.audio_file = $grid_path
               OR word.audio_file ENDS WITH '/' + $filename
            WITH asset, collect(DISTINCT word) AS words
            FOREACH (word IN words | MERGE (word)-[:HAS_AUDIO_ASSET]->(asset))
            RETURN size(words) AS linked_words
            """,
            metadata,
        )
        record = result.single()
        return int(record["linked_words"]) if record else 0

    def get_stats(self) -> dict:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (asset:AudioAsset:GridCore)
                WITH count(asset) AS audio_assets
                MATCH (word:IbibioWord)
                WHERE word.audio_file IS NOT NULL AND word.audio_file <> ''
                WITH audio_assets, count(word) AS words_with_audio_property
                MATCH (word:IbibioWord)-[:HAS_AUDIO_ASSET]->(asset:AudioAsset:GridCore)
                RETURN audio_assets,
                       words_with_audio_property,
                       count(DISTINCT word) AS words_linked_to_audio_assets,
                       count(DISTINCT asset) AS linked_audio_assets
                """
            )
            record = result.single()
            return dict(record) if record else {}


def main() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    repo_root = backend_dir.parent
    audio_root = (
        backend_dir
        / "neo4j-mostar-industries"
        / "import"
        / "data"
        / "Ibibio_codex"
        / "Ibibio_audio"
    )
    if not audio_root.exists():
        raise SystemExit(f"Audio directory not found: {audio_root}")

    neo4j_config = _resolve_neo4j_config()
    if not neo4j_config["password"]:
        raise SystemExit(
            "NEO4J_PASSWORD is not configured. Set it in backend/.env or environment variables."
        )

    uploader = IbibioAudioGridUploader(
        neo4j_config["uri"],
        neo4j_config["user"],
        neo4j_config["password"],
    )
    try:
        uploader.prepare_graph(audio_root)
        summary = uploader.upload_audio_directory(audio_root, repo_root)
        stats = uploader.get_stats()
        print("🎵 IBIBIO AUDIO GRID UPLOAD")
        print(f"   audio_assets_uploaded: {summary['audio_assets_uploaded']}")
        print(f"   word_links_created: {summary['word_links_created']}")
        print(f"   unlinked_audio_assets: {summary['unlinked_audio_assets']}")
        print(f"   total_audio_assets_in_grid: {stats.get('audio_assets', 0)}")
        print(
            f"   words_linked_to_audio_assets: {stats.get('words_linked_to_audio_assets', 0)}"
        )
        print(f"   linked_audio_assets: {stats.get('linked_audio_assets', 0)}")
        print(
            f"   words_with_audio_property: {stats.get('words_with_audio_property', 0)}"
        )
    except AuthError as exc:
        raise SystemExit(
            f"Neo4j authentication failed for {neo4j_config['user']} at {neo4j_config['uri']}."
        ) from exc
    finally:
        uploader.close()


if __name__ == "__main__":
    main()
