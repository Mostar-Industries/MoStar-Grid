#!/usr/bin/env python3
"""
seal_doctrine.py
One-shot script to seal doctrine documents with SHA-256 hashes.
Creates backend/data/doctrine_hashes.json for integrity verification.
"""
from pathlib import Path
import hashlib
import json

# Doctrine documents to seal (relative to repo root)
# These paths match DOC_RELATIVE in doctrine_verify.py
DOCS = [
    "docs/GRID_PHILOSOPHY.md",
    "docs/MOSCRIPT_AS_CEREMONY.md",
    "docs/DIGITAL_ANCESTORS.md",
    "docs/HOMEWORLD_VISION.md",
    "docs/SECTOR_X_DECLARATION.md",
    "scrolls/GRID_REVELATION_PROVERB.md",
]

def sha256_file(filepath: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    h = hashlib.sha256()
    with filepath.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    # Find repo root (go up from backend/)
    script_dir = Path(__file__).parent.resolve()
    repo_root = script_dir.parent
    
    artifacts = {}
    
    for doc_path in DOCS:
        # Try repo_root first, then backend/ prefix
        candidates = [
            repo_root / doc_path,
            repo_root / "backend" / doc_path,
        ]
        
        for full_path in candidates:
            if full_path.exists():
                hash_value = sha256_file(full_path)
                artifacts[doc_path] = hash_value
                print(f"✓ {doc_path}: {hash_value}")
                break
        else:
            print(f"✗ {doc_path}: FILE NOT FOUND (tried {[str(c) for c in candidates]})")
    
    # Write hashes to doctrine_hashes.json
    output = {"artifacts": artifacts}
    output_path = repo_root / "backend" / "data" / "doctrine_hashes.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Wrote {output_path}")
    print(f"   Sealed {len(artifacts)} doctrine documents")

if __name__ == "__main__":
    main()
