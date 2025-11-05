#!/usr/bin/env python3
# generate_provenance.py — cross-platform provenance generator (Windows-friendly)

from __future__ import annotations
from pathlib import Path
import os, sys, json, hashlib, datetime, platform
from typing import Dict, Any

def die(msg: str, code: int = 1) -> None:
    print(f"[FATAL] {msg}", file=sys.stderr); sys.exit(code)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""): h.update(chunk)
    return h.hexdigest()

def now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

DEFAULT_BASE = Path(__file__).resolve().parent / "data"
ENV_BASE = os.getenv("MOSTAR_PROV_BASE", "").strip().strip("'").strip('"')
BASE: Path = (Path(ENV_BASE).expanduser().resolve() if ENV_BASE else DEFAULT_BASE)

SCROLL_REL = Path("scrolls") / "GRID_REVELATION_PROVERB.md"
SCROLL = BASE / SCROLL_REL

REQUIRED_FILES: Dict[str, str] = {
    "vault_seal.json": "{}",
    "vault_patch.json": "{}",
    "GRID_ORCHESTRA.md": "# GRID_ORCHESTRA\n",
    "sha256sums.txt": "",
    "COMMIT_MESSAGE.txt": "Initial commit\n",
}
SAMPLE_SCROLL = "# GRID_REVELATION_PROVERB\n\nThis is a sample scroll content for demonstration purposes.\n"

def main() -> int:
    try:
        (BASE / "scrolls").mkdir(parents=True, exist_ok=True)
        if not SCROLL.exists(): SCROLL.write_text(SAMPLE_SCROLL, encoding="utf-8")
        for name, content in REQUIRED_FILES.items():
            p = BASE / name
            if not p.exists(): p.write_text(content, encoding="utf-8")

        sha = sha256_file(SCROLL)
        size = SCROLL.stat().st_size
        mtime = datetime.datetime.utcfromtimestamp(SCROLL.stat().st_mtime).replace(microsecond=0).isoformat() + "Z"
        now = now_iso()
        date_of_origin = now.split("T")[0]
        scroll_rel_posix = SCROLL_REL.as_posix()

        manifest = {
            "schema_version":"1.0.0","generated_at":now,
            "generator":{"name":"Code Conduit","model":"GPT-5 Thinking",
                "environment":{"python_version":platform.python_version(),"platform":platform.platform()}},
            "artifact":{"path":scroll_rel_posix,"sha256":sha,"bytes":size,"last_modified_utc":mtime,
                "license":"Kairo Covenant License v1.0","status":"Canonical — Flamebound","seal":"Woo x Mo",
                "resonance_min":0.97,"date_of_origin":date_of_origin,
                "tags":["Revelation","Cultural-Firewall","Sanctuary","Compassion-Protocol","Mostar-Grid"]},
            "provenance":{"authors":["Mo","Woo","Mostar AI"],"attestors":["Code Conduit"],
                "chain_of_custody":[{"at":now,"action":"created","by":"Code Conduit","notes":"Provenance/manifest emission"}]},
            "signatures":[
                {"type":"checksum","algorithm":"SHA-256","value":sha,"note":"Checksum is a one-way digest; not a cryptographic signature."},
                {"type":"council_cosign","status":"pending",
                 "required_keys":["Council:Mo","Council:Woo"],
                 "detached_signature_algorithms_supported":["pgp","ssh-ed25519","x509/openssl","minisign/ed25519"],
                 "detached_signature_request":"detached_signature_request.json"}
            ]
        }

        (BASE / "grid_revelation_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[ok] Created manifest: {(BASE / 'grid_revelation_manifest.json')}")

        canonical_string = "\n".join([
            "Mostar-Grid Scroll Seal Request v1",
            f"path:{scroll_rel_posix}",
            f"sha256:{sha}",
            f"bytes:{size}",
            "license:Kairo Covenant License v1.0",
            "status:Canonical — Flamebound",
            "seal:Woo x Mo",
            "resonance_min:0.97",
            f"date_of_origin:{date_of_origin}",
            f"generated_at:{now}",
        ]) + "\n"

        sigreq = {
            "schema_version":"1.0.0",
            "canonical_string": canonical_string,
            "instructions":{
                "pgp":{"detached_signature":"echo -n '<canonical_string>' | gpg --detach-sign --armor --local-user <YOUR_KEY_ID> > grid_revelation.sig.asc"},
                "ssh-ed25519":{"detached_signature":"printf '%s' '<canonical_string>' | ssh-keygen -Y sign -n mostar-grid -f ~/.ssh/id_ed25519 - > grid_revelation.sshsig"},
                "openssl_x509":{"detached_signature":"printf '%s' '<canonical_string>' | openssl dgst -sha256 -sign <private_key.pem> | openssl base64 -A > grid_revelation.sig.base64"},
                "minisign":{"detached_signature":"printf '%s' '<canonical_string>' | minisign -S -s <yourkey.minisign> -t 'Mostar Grid' -m - -x grid_revelation.minisig"}
            },
            "expected_sha256": sha,
            "notes":"Replace <...> with Council keys. Attach resulting detached signature(s) next to this request file."
        }
        (BASE / "detached_signature_request.json").write_text(json.dumps(sigreq, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[ok] Created signature request: {(BASE / 'detached_signature_request.json')}")

        airgap_text = f"""# Airgapped Integrity Manifest — GRID_REVELATION_PROVERB

Artifact: {scroll_rel_posix}
SHA-256: {sha}
Bytes: {size}
Date of Origin: {date_of_origin}
Seal: Woo x Mo
Status: Canonical — Flamebound
Resonance Minimum: ≥ 0.97
License: Kairo Covenant License v1.0

## Verify on Linux/macOS
shasum -a 256 {scroll_rel_posix}
# Expect:
# {sha}

## Verify on Windows (PowerShell)
Get-FileHash {scroll_rel_posix} -Algorithm SHA256 | Format-List
# Expect Hash:
# {sha}

## Verify with OpenSSL (any OS)
openssl dgst -sha256 {scroll_rel_posix}
# Expect:
# SHA256({scroll_rel_posix})= {sha}
"""
        (BASE / "airgapped_integrity_manifest.txt").write_text(airgap_text, encoding="utf-8")
        print(f"[ok] Created airgapped manifest: {(BASE / 'airgapped_integrity_manifest.txt')}")

        print("[summary] Done.")
        return 0
    except Exception as e:
        die(str(e)); return 1

if __name__ == "__main__":
    sys.exit(main())
