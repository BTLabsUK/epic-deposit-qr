# SPDX-License-Identifier: Apache-2.0
# Run: python python/test_deposit_qr.py
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from deposit_qr import deposit_uri, qr_png, qr_svg

VECTORS = json.loads((Path(__file__).parent.parent / "vectors" / "uri.json").read_text())

for v in VECTORS:
    args = {k: v[k] for k in ("address", "note", "minimum", "label") if k in v}
    assert deposit_uri(**args) == v["uri"], v["uri"]
for bad in (("bad", "1"), (VECTORS[0]["address"], "")):
    try:
        deposit_uri(*bad)
    except ValueError:
        continue
    raise AssertionError(bad)
assert qr_svg(VECTORS[0]["uri"]).startswith("<svg")
assert qr_png(VECTORS[0]["uri"])[:4] == b"\x89PNG"
print("python ok")
