# SPDX-License-Identifier: Apache-2.0
"""Epic Cash deposit QR: the `epic:` string, an SVG and a PNG. Needs segno; a logo needs Pillow too."""
import base64
import io
import re
from urllib.parse import quote

import segno

KEY = re.compile(r"es[1-9A-HJ-NP-Za-km-z]{50}@[A-Za-z0-9.-]+(:[0-9]{1,5})?")
MINIMUM = re.compile(r"(0|[1-9][0-9]*)(\.[0-9]{1,8})?")
TILE = 0.22  # logo tile as a share of the code's side; level H still reads


def deposit_uri(address, note, minimum=None, label=None):
    """`epic:<address>?message=<note>&require=message[&min=<epic>][&label=<text>]`"""
    if not KEY.fullmatch(address):
        raise ValueError("address must be es<50 characters>@<relay>[:port]")
    if not note or len(note) > 264:
        raise ValueError("note is required, at most 264 characters")
    uri = f"epic:{address}?message={quote(note, safe='')}&require=message"
    if minimum is not None:
        if not MINIMUM.fullmatch(minimum) or not re.search("[1-9]", minimum):
            raise ValueError('minimum must be a decimal above 0, like "0.1"')
        uri += f"&min={minimum}"
    if label:
        if len(label) > 64:
            raise ValueError("label is at most 64 characters")
        uri += f"&label={quote(label, safe='')}"
    return uri


def qr(uri):
    return segno.make(uri, error="h", micro=False)


def qr_svg(uri, logo_png=None):
    """SVG text. `logo_png`: PNG bytes, put on a white tile in the middle."""
    out = io.BytesIO()
    qr(uri).save(out, kind="svg", scale=1, border=4, xmldecl=False, nl=False, light="#fff")
    svg = out.getvalue().decode()
    side = int(re.search(r'width="(\d+)', svg).group(1))
    svg = svg.replace("<svg ", f'<svg viewBox="0 0 {side} {side}" ', 1)  # lets CSS resize it
    if logo_png is None:
        return svg
    tile = side * TILE
    at, pad = (side - tile) / 2, tile * 0.12
    href = "data:image/png;base64," + base64.b64encode(logo_png).decode()
    return svg.replace("</svg>", f'<rect x="{at}" y="{at}" width="{tile}" height="{tile}" fill="#fff"/>'
                       f'<image x="{at + pad}" y="{at + pad}" width="{tile - 2 * pad}" height="{tile - 2 * pad}" href="{href}"/></svg>')


def qr_png(uri, logo_png=None, scale=8):
    """PNG bytes. `logo_png`: PNG bytes, put on a white tile in the middle (needs Pillow)."""
    out = io.BytesIO()
    qr(uri).save(out, kind="png", scale=scale, border=4)
    if logo_png is None:
        return out.getvalue()
    from PIL import Image
    img = Image.open(io.BytesIO(out.getvalue())).convert("RGB")
    out = io.BytesIO()
    tile = int(img.width * TILE)
    at, pad = (img.width - tile) // 2, tile * 12 // 100
    img.paste("white", (at, at, at + tile, at + tile))
    logo = Image.open(io.BytesIO(logo_png)).convert("RGBA").resize((tile - 2 * pad,) * 2)
    img.paste(logo, (at + pad, at + pad), logo)
    img.save(out, format="PNG")
    return out.getvalue()
