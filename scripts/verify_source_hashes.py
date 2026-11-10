"""Verify deployable source hashes against SOURCE_SHA256_MANIFEST.json."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "SOURCE_SHA256_MANIFEST.json"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = []
    for relative, entry in manifest["files"].items():
        path = ROOT / relative
        # GitHub's Linux checkout is LF while the Windows deployment workspace
        # can be CRLF. Verify the canonical Git source representation here;
        # raw deployed-byte hashes are recorded separately in the manifest.
        canonical = path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")
        actual = hashlib.sha256(canonical).hexdigest()
        expected = entry["sha256"].lower()
        if actual != expected:
            failures.append(f"{relative}: expected {expected}, got {actual}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: verified {len(manifest['files'])} deployable source hashes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
