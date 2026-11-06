# SPDX-License-Identifier: Apache-2.0
# Renders a PNG (with and without a logo) and reads it back. Needs: pip install zxing-cpp pillow
# Run: python python/test_decode.py [png-from-js-test]
import io
import json
import sys
from pathlib import Path

import zxingcpp
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from deposit_qr import qr_png

uri = json.loads((Path(__file__).parent.parent / "vectors" / "uri.json").read_text())[0]["uri"]
logo = io.BytesIO()
Image.new("RGBA", (64, 64), (33, 26, 17, 255)).save(logo, "PNG")
pngs = {"plain": qr_png(uri), "logo": qr_png(uri, logo.getvalue())}
if len(sys.argv) > 1:
    pngs["js"] = Path(sys.argv[1]).read_bytes()
for name, png in pngs.items():
    found = zxingcpp.read_barcodes(Image.open(io.BytesIO(png)))
    assert found and found[0].text == uri, name
    print("decoded", name)
