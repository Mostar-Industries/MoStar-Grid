from __future__ import annotations

import argparse
import csv
import io
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

BACKEND_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV_ROOT = BACKEND_ROOT / "neo4j-mostar-industries" / "import" / "data" / "csv"
DEFAULT_QUARANTINE_DIR = (
    BACKEND_ROOT / "neo4j-mostar-industries" / "import" / "staging" / "quarantine"
)
JSON_REPAIR_COLUMNS = {"api_endpoints.csv": ("input_schema", "output_schema")}
FORCED_QUARANTINE_REASONS = {
    "knowledge_graph.csv": "corrupted_rows",
    "neo4j_tasks.csv": "corrupted_rows",
    "MostarIndustries-Core.csv": "yaml_like_content",
    "ifa_framework.csv": "empty_content",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_zone_identifier(path: Path) -> bool:
    return "Zone.Identifier" in path.name


def _read_text(path: Path) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace"), "utf-8-replace"


def _detect_dialect(sample: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        return csv.excel


def _looks_like_yaml(text: str) -> bool:
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return False
    if not lines[0].rstrip().endswith(":"):
        return False
    indented_lines = sum(1 for line in lines[1:10] if line.startswith(("  ", "\t")))
    colon_lines = sum(1 for line in lines[:10] if ":" in line)
    return indented_lines >= 2 and colon_lines >= min(len(lines[:10]), 3)


def _raw_csv_warnings(text: str) -> list[str]:
    warnings: list[str] = []
    for line_number, line in enumerate(text.splitlines()[:50], start=1):
        if line.count('"') % 2 == 1:
            warnings.append(f"suspicious_quote_balance_line_{line_number}")
            break
    return warnings


def validate_csv_file(path: Path) -> dict[str, Any]:
    validation = {
        "path": str(path),
        "name": path.name,
        "valid": False,
        "reason": "",
        "row_count": 0,
        "column_count": 0,
        "null_cell_ratio": 0.0,
        "encoding": "",
        "warnings": [],
        "headers": [],
        "corruption_flag": False,
    }
    if _is_zone_identifier(path):
        validation["reason"] = "zone_identifier"
        validation["corruption_flag"] = True
        return validation

    text, encoding = _read_text(path)
    validation["encoding"] = encoding
    stripped = text.strip()
    if not stripped:
        validation["reason"] = "empty_content"
        validation["corruption_flag"] = True
        return validation

    warnings = _raw_csv_warnings(text)
    sample = text[:4096]
    dialect = _detect_dialect(sample)
    try:
        rows = list(csv.reader(io.StringIO(text), dialect=dialect))
    except csv.Error as exc:
        validation["reason"] = f"csv_parse_error:{exc}"
        validation["warnings"] = warnings
        validation["corruption_flag"] = True
        return validation

    if not rows:
        validation["reason"] = "empty_content"
        validation["warnings"] = warnings
        validation["corruption_flag"] = True
        return validation

    header = rows[0]
    validation["headers"] = header
    validation["column_count"] = len(header)
    data_rows = rows[1:]

    if len(header) == 1 and _looks_like_yaml(text):
        validation["reason"] = "yaml_like_content"
        validation["warnings"] = warnings
        validation["corruption_flag"] = True
        return validation

    if not data_rows:
        validation["reason"] = "header_only_or_empty"
        validation["warnings"] = warnings
        validation["corruption_flag"] = True
        return validation

    column_counts = {len(row) for row in data_rows}
    if len(column_counts) != 1 or next(iter(column_counts)) != len(header):
        validation["reason"] = "inconsistent_columns"
        validation["row_count"] = len(data_rows)
        validation["warnings"] = warnings
        validation["corruption_flag"] = True
        return validation

    total_cells = max(len(data_rows) * len(header), 1)
    null_cells = 0
    multiline_cells = 0
    for row in data_rows:
        for cell in row:
            if cell is None or not str(cell).strip():
                null_cells += 1
            if "\n" in str(cell) or "\r" in str(cell):
                multiline_cells += 1
    if multiline_cells:
        warnings.append(f"multiline_cells:{multiline_cells}")

    validation["valid"] = True
    validation["reason"] = "ok"
    validation["row_count"] = len(data_rows)
    validation["null_cell_ratio"] = round(null_cells / total_cells, 6)
    validation["warnings"] = warnings
    return validation


def repair_json_cell(cell: str) -> tuple[str, bool]:
    candidate = (cell or "").strip()
    if not candidate:
        return "{}", True

    attempts: list[str] = []
    normalized = (
        candidate.replace("“", '"')
        .replace("”", '"')
        .replace("’", "'")
        .replace("‘", "'")
    )
    attempts.append(normalized)
    attempts.append(normalized.replace("'", '"'))

    keyed = re.sub(
        r'([\{,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)',
        r'\1"\2"\3',
        normalized,
    )
    keyed = re.sub(r'"\s+"', '", "', keyed)
    keyed = re.sub(r',\s*([}\]])', r'\1', keyed)
    attempts.append(keyed)
    attempts.append(keyed.replace("'", '"'))

    for attempt in attempts:
        try:
            parsed = json.loads(attempt)
            return json.dumps(parsed, ensure_ascii=False, sort_keys=True), True
        except json.JSONDecodeError:
            continue

    pair_matches = re.findall(
        r'"?([A-Za-z_][A-Za-z0-9_]*)"?\s*:\s*"([^"]*)"', keyed
    )
    if pair_matches:
        repaired = {key: value for key, value in pair_matches}
        return json.dumps(repaired, ensure_ascii=False, sort_keys=True), True

    error_wrapper = {"error": "unrepairable", "original": cell}
    return json.dumps(error_wrapper, ensure_ascii=False, sort_keys=True), False


def repair_api_endpoints_file(path: Path) -> dict[str, Any]:
    report = {
        "file": path.name,
        "backup": None,
        "rows": 0,
        "repaired_cells": 0,
        "unrepairable_cells": 0,
        "changed": False,
    }
    text, encoding = _read_text(path)
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return report

    rows: list[dict[str, Any]] = []
    targets = JSON_REPAIR_COLUMNS.get(path.name, ())
    for row in reader:
        report["rows"] += 1
        for column in targets:
            value = row.get(column, "")
            if not value:
                row[column] = "{}"
                continue
            repaired, ok = repair_json_cell(value)
            if repaired != value:
                report["changed"] = True
                report["repaired_cells"] += 1
            if not ok:
                report["unrepairable_cells"] += 1
            row[column] = repaired
        rows.append(row)

    if not report["changed"]:
        return report

    backup_path = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup_path)
    report["backup"] = str(backup_path)

    with path.open("w", encoding=encoding if encoding != "utf-8-replace" else "utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return report


def cleanup_zone_identifier_files(csv_root: Path) -> list[str]:
    removed: list[str] = []
    for path in sorted(csv_root.iterdir()):
        if path.is_file() and _is_zone_identifier(path):
            path.unlink(missing_ok=True)
            removed.append(path.name)
    return removed


def quarantine_file(path: Path, quarantine_dir: Path, reason: str) -> Path:
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    target_name = path.name
    if reason == "yaml_like_content":
        target_name = f"{path.stem}.yaml"
    target = quarantine_dir / target_name
    if target.exists():
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        target = quarantine_dir / f"{path.stem}_{timestamp}{target.suffix}"
    shutil.move(str(path), str(target))
    return target


def _prepare_datasource_graph(driver: GraphDatabase.driver, csv_root: Path) -> None:
    with driver.session() as session:
        session.run(
            "CREATE CONSTRAINT IF NOT EXISTS FOR (ds:DataSource) REQUIRE ds.path IS UNIQUE"
        )
        session.run(
            "MERGE (catalog:DataCatalog:GridCore {id: $id}) "
            "SET catalog.root = $root, catalog.updated_at = datetime()",
            {"id": "grid_csv_corpus", "root": str(csv_root)},
        )


def record_datasource(
    driver: GraphDatabase.driver,
    csv_root: Path,
    record: dict[str, Any],
) -> None:
    payload = {
        "catalog_id": "grid_csv_corpus",
        "csv_root": str(csv_root),
        "path": record["path"],
        "name": record["name"],
        "status": record["status"],
        "failure_reason": record.get("failure_reason"),
        "row_count": record.get("row_count", 0),
        "column_count": record.get("column_count", 0),
        "null_cell_ratio": record.get("null_cell_ratio", 0.0),
        "corruption_flag": record.get("corruption_flag", False),
        "encoding": record.get("encoding", ""),
        "warnings": record.get("warnings", []),
        "quarantine_path": record.get("quarantine_path"),
        "last_validated": _utc_now_iso(),
    }
    with driver.session() as session:
        session.run(
            "MERGE (catalog:DataCatalog:GridCore {id: $catalog_id}) "
            "SET catalog.root = $csv_root, catalog.updated_at = datetime() "
            "MERGE (ds:DataSource:GridCore {path: $path}) "
            "SET ds.name = $name, "
            "    ds.csv_root = $csv_root, "
            "    ds.status = $status, "
            "    ds.failure_reason = $failure_reason, "
            "    ds.row_count = $row_count, "
            "    ds.column_count = $column_count, "
            "    ds.null_cell_ratio = $null_cell_ratio, "
            "    ds.corruption_flag = $corruption_flag, "
            "    ds.encoding = $encoding, "
            "    ds.warnings = $warnings, "
            "    ds.quarantine_path = $quarantine_path, "
            "    ds.last_validated = datetime($last_validated) "
            "MERGE (catalog)-[:PROVIDES_DATA]->(ds)",
            payload,
        )


def _build_datasource_record(
    path: Path,
    validation: dict[str, Any],
    status: str,
    failure_reason: str | None = None,
    quarantine_path: str | None = None,
) -> dict[str, Any]:
    return {
        "path": str(path),
        "name": path.name,
        "status": status,
        "failure_reason": failure_reason,
        "row_count": validation.get("row_count", 0),
        "column_count": validation.get("column_count", 0),
        "null_cell_ratio": validation.get("null_cell_ratio", 0.0),
        "corruption_flag": validation.get("corruption_flag", False),
        "encoding": validation.get("encoding", ""),
        "warnings": validation.get("warnings", []),
        "quarantine_path": quarantine_path,
    }


def process_csv_corpus(
    csv_root: str | Path | None = None,
    quarantine_dir: str | Path | None = None,
    *,
    repair_api_endpoints: bool = True,
    quarantine_known_bad_files: bool = True,
    quarantine_invalid_files: bool = True,
    cleanup_zone_identifiers_first: bool = False,
    track_data_sources: bool = True,
    neo4j_uri: str | None = None,
    neo4j_user: str | None = None,
    neo4j_password: str | None = None,
) -> dict[str, Any]:
    csv_root_path = Path(csv_root) if csv_root else DEFAULT_CSV_ROOT
    quarantine_path = Path(quarantine_dir) if quarantine_dir else DEFAULT_QUARANTINE_DIR
    summary = {
        "csv_root": str(csv_root_path),
        "quarantine_dir": str(quarantine_path),
        "processed_files": [],
        "valid_files": [],
        "repaired_files": [],
        "quarantined_files": [],
        "invalid_files": [],
        "zone_identifier_files": [],
        "metrics": {
            "csv_files_seen": 0,
            "csv_files_valid": 0,
            "csv_files_repaired": 0,
            "csv_files_quarantined": 0,
            "csv_invalid_remaining": 0,
            "zone_identifier_files": 0,
            "datasources_tracked": 0,
            "api_endpoint_cells_repaired": 0,
            "api_endpoint_cells_unrepairable": 0,
        },
    }

    if not csv_root_path.exists():
        summary["error"] = "csv_root_not_found"
        return summary

    if cleanup_zone_identifiers_first:
        removed = cleanup_zone_identifier_files(csv_root_path)
        summary["zone_identifier_files"].extend(removed)
        summary["metrics"]["zone_identifier_files"] = len(removed)
    else:
        ignored = [
            path.name
            for path in sorted(csv_root_path.iterdir())
            if path.is_file() and _is_zone_identifier(path)
        ]
        summary["zone_identifier_files"].extend(ignored)
        summary["metrics"]["zone_identifier_files"] = len(ignored)

    driver = None
    if track_data_sources and neo4j_uri and neo4j_user and neo4j_password:
        try:
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            _prepare_datasource_graph(driver, csv_root_path)
        except Neo4jError:
            driver = None

    try:
        for path in sorted(csv_root_path.iterdir()):
            if not path.is_file() or _is_zone_identifier(path) or path.suffix.lower() != ".csv":
                continue

            summary["metrics"]["csv_files_seen"] += 1
            summary["processed_files"].append(path.name)

            if repair_api_endpoints and path.name in JSON_REPAIR_COLUMNS:
                repair_report = repair_api_endpoints_file(path)
                if repair_report["changed"]:
                    summary["repaired_files"].append(
                        {
                            "file": path.name,
                            "backup": repair_report["backup"],
                            "repaired_cells": repair_report["repaired_cells"],
                            "unrepairable_cells": repair_report["unrepairable_cells"],
                        }
                    )
                    summary["metrics"]["csv_files_repaired"] += 1
                    summary["metrics"]["api_endpoint_cells_repaired"] += repair_report[
                        "repaired_cells"
                    ]
                    summary["metrics"]["api_endpoint_cells_unrepairable"] += repair_report[
                        "unrepairable_cells"
                    ]

            validation = validate_csv_file(path)

            forced_reason = FORCED_QUARANTINE_REASONS.get(path.name)
            if forced_reason and quarantine_known_bad_files:
                destination = quarantine_file(path, quarantine_path, forced_reason)
                summary["quarantined_files"].append(
                    {
                        "file": path.name,
                        "reason": forced_reason,
                        "destination": str(destination),
                    }
                )
                summary["metrics"]["csv_files_quarantined"] += 1
                if driver:
                    record_datasource(
                        driver,
                        csv_root_path,
                        _build_datasource_record(
                            path,
                            validation,
                            status="quarantined",
                            failure_reason=forced_reason,
                            quarantine_path=str(destination),
                        ),
                    )
                    summary["metrics"]["datasources_tracked"] += 1
                continue

            if validation["valid"]:
                summary["valid_files"].append(
                    {
                        "file": path.name,
                        "row_count": validation["row_count"],
                        "column_count": validation["column_count"],
                        "null_cell_ratio": validation["null_cell_ratio"],
                        "warnings": validation["warnings"],
                    }
                )
                summary["metrics"]["csv_files_valid"] += 1
                if driver:
                    record_datasource(
                        driver,
                        csv_root_path,
                        _build_datasource_record(path, validation, status="active"),
                    )
                    summary["metrics"]["datasources_tracked"] += 1
                continue

            if quarantine_invalid_files:
                destination = quarantine_file(path, quarantine_path, validation["reason"])
                summary["quarantined_files"].append(
                    {
                        "file": path.name,
                        "reason": validation["reason"],
                        "destination": str(destination),
                    }
                )
                summary["metrics"]["csv_files_quarantined"] += 1
                if driver:
                    record_datasource(
                        driver,
                        csv_root_path,
                        _build_datasource_record(
                            path,
                            validation,
                            status="quarantined",
                            failure_reason=validation["reason"],
                            quarantine_path=str(destination),
                        ),
                    )
                    summary["metrics"]["datasources_tracked"] += 1
            else:
                summary["invalid_files"].append(
                    {
                        "file": path.name,
                        "reason": validation["reason"],
                        "warnings": validation["warnings"],
                    }
                )
                summary["metrics"]["csv_invalid_remaining"] += 1
                if driver:
                    record_datasource(
                        driver,
                        csv_root_path,
                        _build_datasource_record(
                            path,
                            validation,
                            status="warning",
                            failure_reason=validation["reason"],
                        ),
                    )
                    summary["metrics"]["datasources_tracked"] += 1
    finally:
        if driver:
            driver.close()

    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv-root", default=str(DEFAULT_CSV_ROOT))
    parser.add_argument("--quarantine-dir", default=str(DEFAULT_QUARANTINE_DIR))
    parser.add_argument("--skip-api-repair", action="store_true")
    parser.add_argument("--skip-known-quarantine", action="store_true")
    parser.add_argument("--skip-invalid-quarantine", action="store_true")
    parser.add_argument("--cleanup-zone-identifiers", action="store_true")
    parser.add_argument("--skip-datasource-tracking", action="store_true")
    parser.add_argument("--neo4j-uri")
    parser.add_argument("--neo4j-user")
    parser.add_argument("--neo4j-password")
    args = parser.parse_args()

    result = process_csv_corpus(
        csv_root=args.csv_root,
        quarantine_dir=args.quarantine_dir,
        repair_api_endpoints=not args.skip_api_repair,
        quarantine_known_bad_files=not args.skip_known_quarantine,
        quarantine_invalid_files=not args.skip_invalid_quarantine,
        cleanup_zone_identifiers_first=args.cleanup_zone_identifiers,
        track_data_sources=not args.skip_datasource_tracking,
        neo4j_uri=args.neo4j_uri,
        neo4j_user=args.neo4j_user,
        neo4j_password=args.neo4j_password,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
