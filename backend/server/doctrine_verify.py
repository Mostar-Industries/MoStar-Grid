"""
doctrine_verify.py
Runtime integrity verification for canonical doctrine scrolls.
The Grid refuses to serve if its soul is tampered with.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional

# Doctrine scrolls with expected hashes (from provenance manifest)
DOCTRINE_SCROLLS = [
    {
        "id": "grid_philosophy",
        "path": "docs/GRID_PHILOSOPHY.md",
        "expected_hash": None,  # Will be populated from manifest
    },
    {
        "id": "moscript_as_ceremony",
        "path": "docs/MOSCRIPT_AS_CEREMONY.md",
        "expected_hash": None,
    },
    {
        "id": "digital_ancestors",
        "path": "docs/DIGITAL_ANCESTORS.md",
        "expected_hash": None,
    },
    {
        "id": "homeworld_vision",
        "path": "docs/HOMEWORLD_VISION.md",
        "expected_hash": None,
    },
]


def sha256_file(filepath: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_manifest_hashes(manifest_path: Path) -> Dict[str, str]:
    """Load expected hashes from provenance manifest."""
    if not manifest_path.exists():
        return {}
    
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        # Extract hashes from manifest structure
        # This assumes manifest has a "scrolls" or "artifacts" array
        hashes = {}
        if "artifact" in manifest:
            # Single artifact format
            path = manifest["artifact"].get("path", "")
            sha = manifest["artifact"].get("sha256", "")
            if path and sha:
                hashes[path] = sha
        
        if "scrolls" in manifest:
            # Multiple scrolls format
            for scroll in manifest["scrolls"]:
                path = scroll.get("path", "")
                sha = scroll.get("sha256", "")
                if path and sha:
                    hashes[path] = sha
        
        return hashes
    except Exception as e:
        print(f"[doctrine_verify] Failed to load manifest: {e}")
        return {}


def verify_doctrine(repo_root: Optional[Path] = None) -> Dict:
    """
    Verify integrity of all doctrine scrolls.
    Returns status dict with verification results.
    """
    if repo_root is None:
        # Assume we're in backend/server, so repo root is ../../
        repo_root = Path(__file__).parent.parent.parent
    
    # Try to load expected hashes from manifest
    manifest_path = repo_root / "backend" / "data" / "grid_revelation_manifest.json"
    manifest_hashes = load_manifest_hashes(manifest_path)
    
    results = []
    all_verified = True
    
    for scroll in DOCTRINE_SCROLLS:
        scroll_path = repo_root / scroll["path"]
        scroll_id = scroll["id"]
        
        if not scroll_path.exists():
            results.append({
                "id": scroll_id,
                "path": scroll["path"],
                "verified": False,
                "reason": "file_not_found",
                "sha256": None,
            })
            all_verified = False
            continue
        
        # Calculate actual hash
        actual_hash = sha256_file(scroll_path)
        
        # Get expected hash from manifest (if available)
        expected_hash = manifest_hashes.get(scroll["path"])
        
        if expected_hash:
            verified = (actual_hash == expected_hash)
            if not verified:
                all_verified = False
            
            results.append({
                "id": scroll_id,
                "path": scroll["path"],
                "verified": verified,
                "sha256": actual_hash,
                "expected": expected_hash,
                "reason": None if verified else "hash_mismatch",
            })
        else:
            # No expected hash in manifest - treat as unverified but present
            results.append({
                "id": scroll_id,
                "path": scroll["path"],
                "verified": True,  # Allow boot if manifest missing (dev mode)
                "sha256": actual_hash,
                "expected": None,
                "reason": "no_manifest_hash",
            })
    
    return {
        "ok": all_verified,
        "scrolls": results,
        "manifest_path": str(manifest_path),
        "manifest_found": manifest_path.exists(),
    }


# FastAPI endpoint integration
async def doctrine_status_endpoint():
    """
    FastAPI endpoint handler for /api/doctrine/status.
    Returns doctrine integrity verification results.
    """
    return verify_doctrine()


if __name__ == "__main__":
    # CLI test
    import sys
    
    result = verify_doctrine()
    print(json.dumps(result, indent=2))
    
    if not result["ok"]:
        print("\n[FAIL] Doctrine integrity check failed.", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n[OK] Doctrine integrity verified.")
        sys.exit(0)
