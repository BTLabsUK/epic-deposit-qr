# epic-deposit-qr

Builds a QR code that carries an Epic Cash Epicbox address and a note. A wallet that scans it opens Send with both fields filled.

Deposits that are matched by a note are easy to get wrong when the note is typed or pasted by hand. One code removes that step. This repository is a small reference: a URI builder and a call to one QR library per language.

## Format

```
epic:<address>?message=<note>&require=message&min=<epic>&label=<text>
```

| Part | Meaning |
| --- | --- |
| `<address>` | Epicbox address: `es<50 characters>@<relay>[:port]` |
| `message` | Note, percent-encoded as UTF-8. At most 264 characters. |
| `require=message` | Asks the wallet to warn when the note is empty. The sender can still send. |
| `min` | Optional. Decimal amount in EPIC, above 0, at most 8 decimals. The wallet warns below it. The sender can still send. |
| `label` | Optional. Text shown to the sender. At most 64 characters. |

Write `message`. A reader also accepts `note` and `memo` for the same field, and ignores parameters it does not know.

The text of the code, the copy text and the link on a page are the same `epic:` string. The code is level H (about 30% of the symbol can be damaged), with a quiet zone of 4 modules. An optional logo covers about 22% of the side.

Example (made-up values):

```
epic:esWxboBPMgL4RqufRYcGUJ7t6YVWGvyuid6xRM62UkRzSb3jUcNK@epicbox.exchange.example?message=4827193065148&require=message&min=0.1&label=Deposit
```

`vectors/uri.json` holds input and expected string. Both implementations are tested against it.

## Use

JavaScript (`npm install`, library `qrcode`; in a browser, map `qrcode` to a module URL with an import map):

```js
import { depositUri, qrSvg, qrPng, qrCanvas } from './js/deposit-qr.js';

const uri = depositUri({ address, note: '4827193065148', minimum: '0.1', label: 'Deposit' });
const svg = await qrSvg(uri, logoDataUri);   // logo is optional
const png = await qrPng(uri);                // Node, no logo
await qrCanvas(canvas, uri, logoImg);        // browser, logo optional
```

PNG with a logo in Node needs an image library; this repository does not add one. Use the browser canvas, or the SVG.

Python (`pip install -r python/requirements.txt`, library `segno`; Pillow is only needed for a PNG with a logo):

```python
from deposit_qr import deposit_uri, qr_svg, qr_png

uri = deposit_uri(address, "4827193065148", minimum="0.1", label="Deposit")
svg = qr_svg(uri, logo_png_bytes)   # logo is optional
png = qr_png(uri, logo_png_bytes)
```

The input is checked: a bad address, an empty or long note, or a bad minimum raises an error. A string beyond what version 40 at level H holds is rejected by the library.

## Wallets without note support

A wallet that does not read `message` may still read the address from the string, or may refuse it. The note is then not filled, and the sender has to enter it by hand. Show the `epic:` string as text next to the code, so it can be copied, and show the note on its own as well.

## Tests

```
node js/test.js
python python/test_deposit_qr.py
python python/test_decode.py        # needs zxing-cpp and pillow; renders a PNG and reads it back
```

## Licence

Apache-2.0. See `LICENSE`.
