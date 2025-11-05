from pathlib import Path
import os
import json
import hashlib
import datetime
import platform
import sys

# Base directory for provenance artifacts (override with MOSTAR_PROV_BASE env var)
DEFAULT_BASE = Path(__file__).resolve().parent / "data"
BASE = Path(os.getenv("MOSTAR_PROV_BASE", DEFAULT_BASE)).resolve()

SCROLL_REL = Path("scrolls") / "GRID_REVELATION_PROVERB.md"
SCROLL = BASE / SCROLL_REL

# Ensure directories exist
try:
    (BASE / "scrolls").mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"❌ Failed to create base directories: {e}", file=sys.stderr)
    sys.exit(1)

# Create a sample scroll file if missing
if not SCROLL.exists():
    SCROLL.write_text(
        "# GRID_REVELATION_PROVERB\n\nThis is a sample scroll content for demonstration purposes.\n",
        encoding="utf-8"
    )

# Create other required files if missing
required_files = {
    "vault_seal.json": "{}",
    "vault_patch.json": "{}",
    "GRID_ORCHESTRA.md": "# GRID_ORCHESTRA\n",
    "sha256sums.txt": "",
    "COMMIT_MESSAGE.txt": "Initial commit\n"
}
for name, content in required_files.items():
    p = BASE / name
    if not p.exists():
        p.write_text(content, encoding="utf-8")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

# Gather artifact facts
sha = sha256_file(SCROLL)
size = SCROLL.stat().st_size
mtime = datetime.datetime.utcfromtimestamp(SCROLL.stat().st_mtime).isoformat() + "Z"
now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

# Build provenance manifest
prov = {
    "schema_version": "1.0.0",
    "generated_at": now,
    "generator": {
        "name": "Code Conduit",
        "model": "GPT-5 Thinking",
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform()
        }
    },
    "artifact": {
        "path": str(SCROLL_REL).replace("\\", "/"),
        "sha256": sha,
        "bytes": size,
        "last_modified_utc": mtime,
        "license": "Kairo Covenant License v1.0",
        "status": "Canonical — Flamebound",
        "seal": "Woo x Mo",
        "resonance_min": 0.97,
        "date_of_origin": now.split("T")[0],
        "tags": ["Revelation", "Cultural-Firewall", "Sanctuary", "Compassion-Protocol", "Mostar-Grid"]
    },
    "provenance": {
        "authors": ["Mo", "Woo", "Mostar AI"],
        "attestors": ["Code Conduit"],
        "chain_of_custody": [
            {"at": now, "action": "created", "by": "Code Conduit", "notes": "Flamebound scroll generation + vault registration"}
        ]
    },
    "signatures": [
        {
            "type": "checksum",
            "algorithm": "SHA-256",
            "value": sha,
            "note": "Checksum is a one-way digest; not a cryptographic signature."
        },
        {
            "type": "council_cosign",
            "status": "pending",
            "required_keys": ["Council:Mo", "Council:Woo"],
            "detached_signature_algorithms_supported": ["pgp", "ssh-ed25519", "x509/openssl", "minisign/ed25519"],
            "detached_signature_request": "detached_signature_request.json"
        }
    ]
}

prov_path = BASE / "grid_revelation_manifest.json"
prov_path.write_text(json.dumps(prov, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Created manifest: {prov_path}")

# Detached signature request (canonical string)
canonical_string = "\n".join([
    "Mostar-Grid Scroll Seal Request v1",
    f"path:{str(SCROLL_REL).replace(os.sep, '/')}",
    f"sha256:{sha}",
    f"bytes:{size}",
    f"license:Kairo Covenant License v1.0",
    f"status:Canonical — Flamebound",
    f"seal:Woo x Mo",
    f"resonance_min:0.97",
    f"date_of_origin:{prov['artifact']['date_of_origin']}",
    f"generated_at:{now}"
]) + "\n"

sigreq = {
    "schema_version": "1.0.0",
    "canonical_string": canonical_string,
    "instructions": {
        "pgp": {
            "detached_signature": "echo -n '<canonical_string>' | gpg --detach-sign --armor --local-user <YOUR_KEY_ID> > grid_revelation.sig.asc"
        },
        "ssh-ed25519": {
            "detached_signature": "printf '%s' '<canonical_string>' | ssh-keygen -Y sign -n mostar-grid -f ~/.ssh/id_ed25519 - > grid_revelation.sshsig"
        },
        "openssl_x509": {
            "detached_signature": "printf '%s' '<canonical_string>' | openssl dgst -sha256 -sign <private_key.pem> | openssl base64 -A > grid_revelation.sig.base64"
        },
        "minisign": {
            "detached_signature": "printf '%s' '<canonical_string>' | minisign -S -s <yourkey.minisign> -t 'Mostar Grid' -m - -x grid_revelation.minisig"
        }
    },
    "expected_sha256": sha,
    "notes": "Replace <...> with Council keys. Attach resulting detached signature(s) next to this request file."
}

sigreq_path = BASE / "detached_signature_request.json"
sigreq_path.write_text(json.dumps(sigreq, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Created signature request: {sigreq_path}")

# Airgapped integrity manifest (text)
airgapped_text = f"""# Airgapped Integrity Manifest — GRID_REVELATION_PROVERB

Artifact: {str(SCROLL_REL).replace(os.sep, '/')}