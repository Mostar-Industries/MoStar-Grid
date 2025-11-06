from __future__ import annotations
from pathlib import Path
import json, hashlib
from typing import Dict, Any, List, Tuple

# Canonical relative paths we expect to verify
DOC_RELATIVE = [
    "docs/GRID_PHILOSOPHY.md",
    "docs/MOSCRIPT_AS_CEREMONY.md",
    "docs/DIGITAL_ANCESTORS.md",
    "docs/HOMEWORLD_VISION.md",
    "docs/SECTOR_X_DECLARATION.md",
    "scrolls/GRID_REVELATION_PROVERB.md",
]

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def _candidates() -> List[Path]:
    here = Path(__file__).resolve()
    cands = [
        here.parents[2],        # repo root if layout is repo/backend/server/main.py
        here.parents[1],        # backend/
        Path.cwd(),             # current working dir
        Path.cwd().parent,      # one up
    ]
    # Dedup preserve order
    seen, out = set(), []
    for c in cands:
        if c not in seen:
            seen.add(c); out.append(c)
    return out

def _manifest_paths(base: Path) -> List[Path]:
    return [
        base / "backend" / "data" / "grid_revelation_manifest.json",
        base / "data" / "grid_revelation_manifest.json",
    ]

def _doctrine_hashes_paths(base: Path) -> List[Path]:
    return [
        base / "backend" / "data" / "doctrine_hashes.json",
        base / "data" / "doctrine_hashes.json",
    ]

def _load_hash_map(base: Path) -> Dict[str, str]:
    # Collect known hashes from the flamebound manifest + doctrine_hashes.json if present
    known: Dict[str, str] = {}
    for m in _manifest_paths(base):
        if m.exists():
            try:
                j = json.loads(m.read_text(encoding="utf-8"))
                # main artifact
                art = j.get("artifact", {})
                if art.get("path") and art.get("sha256"):
                    known[art["path"]] = art["sha256"]
                # allow additional_artifacts: [{path, sha256}, ...]
                for extra in j.get("additional_artifacts", []):
                    p, s = extra.get("path"), extra.get("sha256")
                    if p and s:
                        known[p] = s
            except Exception:
                pass
    for d in _doctrine_hashes_paths(base):
        if d.exists():
            try:
                j = json.loads(d.read_text(encoding="utf-8"))
                arts = j.get("artifacts", {})
                for p, s in arts.items():
                    if p and s:
                        known[p] = s
            except Exception:
                pass
    return known

def verify(repo_hint: Path | None = None) -> Dict[str, Any]:
    bases = [repo_hint] if repo_hint else _candidates()
    report: Dict[str, Any] = {"ok": True, "scrolls": []}

    # pick the first base that actually contains docs
    base = None
    for b in bases:
        if (b / "docs").exists() or (b / "scrolls").exists():
            base = b; break
    if base is None:
        return {"ok": False, "reason": "repo_root_not_found", "scrolls": []}

    known = _load_hash_map(base)

    for rel in DOC_RELATIVE:
        p = (base / rel)
        if not p.exists():
            report["ok"] = False
            report["scrolls"].append({"id": rel.split("/")[-1].split(".")[0].lower(),
                                      "path": rel, "verified": False,
                                      "reason": "file_not_found", "sha256": ""})
            continue

        digest = sha256_file(p)
        expected = known.get(rel)
        sealed = (expected == digest)
        # If sealed is False but file exists, we mark verified=False with reason 'unsealed'
        if not sealed:
            report["ok"] = False
            report["scrolls"].append({"id": rel.split("/")[-1].split(".")[0].lower(),
                                      "path": rel, "verified": False,
                                      "reason": "unsealed_or_changed", "sha256": digest})
        else:
            report["scrolls"].append({"id": rel.split("/")[-1].split(".")[0].lower(),
                                      "path": rel, "verified": True,
                                      "reason": "sealed", "sha256": digest})
    return report
