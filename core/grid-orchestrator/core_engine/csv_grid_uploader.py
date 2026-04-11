from __future__ import annotations

import argparse
import csv
import io
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from csv_quality import (
    DEFAULT_CSV_ROOT,
    FORCED_QUARANTINE_REASONS,
    JSON_REPAIR_COLUMNS,
    _read_text,
    repair_json_cell,
    validate_csv_file,
)

DEFAULT_BATCH_SIZE = 250
CATALOG_ID = "grid_csv_corpus"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize_key(key: str) -> str:
    normalized = key.strip()
    normalized = re.sub(r":(int|float|boolean|string)$", "", normalized)
    normalized = re.sub(r"[^0-9A-Za-z_]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "value"


def _coerce_value(key: str, value: str) -> Any:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    lowered = text.lower()
    if key.endswith(":int"):
        try:
            return int(text)
        except ValueError:
            return text
    if key.endswith(":float"):
        try:
            return float(text)
        except ValueError:
            return text
    if key.endswith(":boolean"):
        if lowered in {"true", "false"}:
            return lowered == "true"
    return text


def _load_rows(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    text, _ = _read_text(path)
    reader = csv.DictReader(io.StringIO(text))
    fieldnames = reader.fieldnames or []
    rows: list[dict[str, Any]] = []
    for row_number, row in enumerate(reader, start=1):
        cleaned_row: dict[str, Any] = {}
        payload_row: dict[str, Any] = {}
        for key, raw_value in row.items():
            source_value = raw_value
            if path.name in JSON_REPAIR_COLUMNS and key in JSON_REPAIR_COLUMNS[path.name]:
                source_value, _ = repair_json_cell(raw_value or "")
            coerced = _coerce_value(key, source_value)
            payload_row[key] = source_value if source_value is not None else ""
            if coerced is None:
                continue
            cleaned_row[_sanitize_key(key)] = coerced
        rows.append(
            {
                "row_id": f"{path.name}:{row_number}",
                "row_number": row_number,
                "properties": cleaned_row,
                "row_json": json.dumps(payload_row, ensure_ascii=False, sort_keys=True),
            }
        )
    return rows, fieldnames


def _prepare_graph(driver: GraphDatabase.driver, csv_root: Path) -> None:
    with driver.session() as session:
        session.run(
            "CREATE CONSTRAINT IF NOT EXISTS FOR (catalog:DataCatalog) REQUIRE catalog.id IS UNIQUE"
        )
        session.run(
            "CREATE CONSTRAINT IF NOT EXISTS FOR (ds:DataSource) REQUIRE ds.path IS UNIQUE"
        )
        session.run(
            "CREATE CONSTRAINT IF NOT EXISTS FOR (row:CsvRow) REQUIRE row.row_id IS UNIQUE"
        )
        session.run(
            "CREATE CONSTRAINT IF NOT EXISTS FOR (run:CsvImportRun) REQUIRE run.run_id IS UNIQUE"
        )
        session.run(
            "MERGE (catalog:DataCatalog:GridCore {id: $catalog_id}) "
            "SET catalog.root = $root, catalog.updated_at = datetime()",
            {"catalog_id": CATALOG_ID, "root": str(csv_root)},
        )


def _create_import_run(driver: GraphDatabase.driver, csv_root: Path) -> str:
    run_id = str(uuid.uuid4())
    with driver.session() as session:
        session.run(
            "CREATE (run:CsvImportRun:GridCore {run_id: $run_id, csv_root: $csv_root, started_at: datetime()})",
            {"run_id": run_id, "csv_root": str(csv_root)},
        )
    return run_id


def _mark_skipped_source(
    driver: GraphDatabase.driver,
    run_id: str,
    csv_root: Path,
    path: Path,
    validation: dict[str, Any],
    reason: str,
) -> None:
    payload = {
        "catalog_id": CATALOG_ID,
        "run_id": run_id,
        "path": str(path),
        "name": path.name,
        "csv_root": str(csv_root),
        "reason": reason,
        "row_count": validation.get("row_count", 0),
        "column_count": validation.get("column_count", 0),
        "null_cell_ratio": validation.get("null_cell_ratio", 0.0),
        "encoding": validation.get("encoding", ""),
        "warnings": validation.get("warnings", []),
    }
    with driver.session() as session:
        session.run(
            "MERGE (catalog:DataCatalog:GridCore {id: $catalog_id}) "
            "MERGE (run:CsvImportRun:GridCore {run_id: $run_id}) "
            "MERGE (ds:DataSource:GridCore {path: $path}) "
            "SET ds.name = $name, "
            "    ds.csv_root = $csv_root, "
            "    ds.status = 'skipped', "
            "    ds.failure_reason = $reason, "
            "    ds.row_count = $row_count, "
            "    ds.column_count = $column_count, "
            "    ds.null_cell_ratio = $null_cell_ratio, "
            "    ds.encoding = $encoding, "
            "    ds.warnings = $warnings, "
            "    ds.last_validated = datetime(), "
            "    ds.last_upload_attempt = datetime() "
            "MERGE (catalog)-[:PROVIDES_DATA]->(ds) "
            "MERGE (run)-[:SKIPPED_SOURCE]->(ds)",
            payload,
        )


def _upsert_source(
    driver: GraphDatabase.driver,
    run_id: str,
    csv_root: Path,
    path: Path,
    validation: dict[str, Any],
    fieldnames: list[str],
    uploaded_row_count: int,
) -> None:
    payload = {
        "catalog_id": CATALOG_ID,
        "run_id": run_id,
        "path": str(path),
        "name": path.name,
        "dataset": path.stem,
        "csv_root": str(csv_root),
        "row_count": validation.get("row_count", uploaded_row_count),
        "column_count": validation.get("column_count", len(fieldnames)),
        "null_cell_ratio": validation.get("null_cell_ratio", 0.0),
        "encoding": validation.get("encoding", ""),
        "warnings": validation.get("warnings", []),
        "headers": fieldnames,
        "uploaded_row_count": uploaded_row_count,
    }
    with driver.session() as session:
        session.run(
            "MERGE (catalog:DataCatalog:GridCore {id: $catalog_id}) "
            "MERGE (run:CsvImportRun:GridCore {run_id: $run_id}) "
            "MERGE (ds:DataSource:GridCore {path: $path}) "
            "SET ds.name = $name, "
            "    ds.dataset = $dataset, "
            "    ds.csv_root = $csv_root, "
            "    ds.status = 'uploaded', "
            "    ds.failure_reason = null, "
            "    ds.row_count = $row_count, "
            "    ds.column_count = $column_count, "
            "    ds.null_cell_ratio = $null_cell_ratio, "
            "    ds.encoding = $encoding, "
            "    ds.warnings = $warnings, "
            "    ds.headers = $headers, "
            "    ds.uploaded_row_count = $uploaded_row_count, "
            "    ds.last_validated = datetime(), "
            "    ds.last_uploaded = datetime() "
            "MERGE (catalog)-[:PROVIDES_DATA]->(ds) "
            "MERGE (run)-[:IMPORTED_SOURCE]->(ds)",
            payload,
        )


def _upload_batch(
    driver: GraphDatabase.driver,
    source_path: Path,
    rows: list[dict[str, Any]],
) -> None:
    with driver.session() as session:
        session.run(
            "MATCH (ds:DataSource:GridCore {path: $path}) "
            "UNWIND $rows AS row "
            "MERGE (record:CsvRow:GridCore {row_id: row.row_id}) "
            "SET record += row.properties, "
            "    record.source_path = $path, "
            "    record.source_name = $source_name, "
            "    record.dataset = $dataset, "
            "    record.row_number = row.row_number, "
            "    record.row_json = row.row_json, "
            "    record.updated_at = datetime() "
            "MERGE (ds)-[:HAS_ROW]->(record)",
            {
                "path": str(source_path),
                "source_name": source_path.name,
                "dataset": source_path.stem,
                "rows": rows,
            },
        )


def upload_csv_corpus(
    csv_root: str | Path,
    neo4j_uri: str,
    neo4j_user: str,
    neo4j_password: str,
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> dict[str, Any]:
    csv_root_path = Path(csv_root)
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    summary = {
        "csv_root": str(csv_root_path),
        "uploaded_files": [],
        "skipped_files": [],
        "metrics": {
            "csv_files_seen": 0,
            "csv_files_uploaded": 0,
            "csv_files_skipped": 0,
            "rows_uploaded": 0,
        },
    }
    try:
        _prepare_graph(driver, csv_root_path)
        run_id = _create_import_run(driver, csv_root_path)
        summary["run_id"] = run_id
        for path in sorted(csv_root_path.iterdir()):
            if not path.is_file() or path.suffix.lower() != ".csv":
                continue
            summary["metrics"]["csv_files_seen"] += 1
            validation = validate_csv_file(path)
            forced_reason = FORCED_QUARANTINE_REASONS.get(path.name)
            if forced_reason:
                _mark_skipped_source(driver, run_id, csv_root_path, path, validation, forced_reason)
                summary["skipped_files"].append({"file": path.name, "reason": forced_reason})
                summary["metrics"]["csv_files_skipped"] += 1
                continue
            if not validation["valid"]:
                _mark_skipped_source(
                    driver,
                    run_id,
                    csv_root_path,
                    path,
                    validation,
                    validation["reason"],
                )
                summary["skipped_files"].append(
                    {"file": path.name, "reason": validation["reason"]}
                )
                summary["metrics"]["csv_files_skipped"] += 1
                continue
            rows, fieldnames = _load_rows(path)
            _upsert_source(driver, run_id, csv_root_path, path, validation, fieldnames, len(rows))
            for start in range(0, len(rows), batch_size):
                _upload_batch(driver, path, rows[start : start + batch_size])
            summary["uploaded_files"].append(
                {"file": path.name, "rows_uploaded": len(rows), "column_count": len(fieldnames)}
            )
            summary["metrics"]["csv_files_uploaded"] += 1
            summary["metrics"]["rows_uploaded"] += len(rows)
        with driver.session() as session:
            session.run(
                "MATCH (run:CsvImportRun:GridCore {run_id: $run_id}) "
                "SET run.completed_at = datetime(), "
                "    run.csv_files_uploaded = $csv_files_uploaded, "
                "    run.csv_files_skipped = $csv_files_skipped, "
                "    run.rows_uploaded = $rows_uploaded",
                {
                    "run_id": run_id,
                    "csv_files_uploaded": summary["metrics"]["csv_files_uploaded"],
                    "csv_files_skipped": summary["metrics"]["csv_files_skipped"],
                    "rows_uploaded": summary["metrics"]["rows_uploaded"],
                },
            )
    finally:
        driver.close()
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv-root", default=str(DEFAULT_CSV_ROOT))
    parser.add_argument("--neo4j-uri", required=True)
    parser.add_argument("--neo4j-user", required=True)
    parser.add_argument("--neo4j-password", required=True)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    args = parser.parse_args()
    result = upload_csv_corpus(
        csv_root=args.csv_root,
        neo4j_uri=args.neo4j_uri,
        neo4j_user=args.neo4j_user,
        neo4j_password=args.neo4j_password,
        batch_size=args.batch_size,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
