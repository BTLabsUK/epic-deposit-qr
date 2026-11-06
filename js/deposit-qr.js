// SPDX-License-Identifier: Apache-2.0
// Epic Cash deposit QR: the `epic:` string, an SVG, and a PNG (Node) or a canvas (browser).
import QRCode from 'qrcode';

const KEY = /^es[1-9A-HJ-NP-Za-km-z]{50}@[A-Za-z0-9.-]+(:[0-9]{1,5})?$/;
const MINIMUM = /^(0|[1-9][0-9]*)(\.[0-9]{1,8})?$/;
const encode = (s) => encodeURIComponent(s).replace(/[!'()*]/g, (c) => '%' + c.charCodeAt(0).toString(16).toUpperCase());

/** `epic:<address>?message=<note>&require=message[&min=<epic>][&label=<text>]` */
export function depositUri({ address, note, minimum, label }) {
  if (!KEY.test(address)) throw new Error('address must be es<50 characters>@<relay>[:port]');
  if (!note || [...note].length > 264) throw new Error('note is required, at most 264 characters');
  let uri = `epic:${address}?message=${encode(note)}&require=message`;
  if (minimum !== undefined) {
    if (!MINIMUM.test(minimum) || !/[1-9]/.test(minimum)) throw new Error('minimum must be a decimal above 0, like "0.1"');
    uri += `&min=${minimum}`;
  }
  if (label) {
    if ([...label].length > 64) throw new Error('label is at most 64 characters');
    uri += `&label=${encode(label)}`;
  }
  return uri;
}

const OPTIONS = { errorCorrectionLevel: 'H', margin: 4 };
const TILE = 0.22; // logo tile as a share of the code's side; level H still reads

/** SVG text. `logoHref` (a data URI) goes on a white tile in the middle. */
export async function qrSvg(uri, logoHref) {
  const svg = await QRCode.toString(uri, { ...OPTIONS, type: 'svg' });
  if (!logoHref) return svg;
  const side = Number(/viewBox="0 0 (\d+)/.exec(svg)[1]);
  const tile = side * TILE, at = (side - tile) / 2, pad = tile * 0.12;
  const href = logoHref.replace(/"/g, '&quot;');
  return svg.replace('</svg>', `<rect x="${at}" y="${at}" width="${tile}" height="${tile}" fill="#fff"/>` +
    `<image x="${at + pad}" y="${at + pad}" width="${tile - 2 * pad}" height="${tile - 2 * pad}" href="${href}"/></svg>`);
}

/** PNG bytes in Node (no logo: Node has no image drawing). */
export const qrPng = (uri) => QRCode.toBuffer(uri, { ...OPTIONS, scale: 8 });

/** Browser: draws the code on `canvas`, then `logo` (an <img> that has loaded) on a white tile. */
export async function qrCanvas(canvas, uri, logo) {
  await QRCode.toCanvas(canvas, uri, { ...OPTIONS, scale: 8 });
  if (!logo) return;
  const ctx = canvas.getContext('2d'), tile = canvas.width * TILE, at = (canvas.width - tile) / 2, pad = tile * 0.12;
  ctx.fillStyle = '#fff';
  ctx.fillRect(at, at, tile, tile);
  ctx.drawImage(logo, at + pad, at + pad, tile - 2 * pad, tile - 2 * pad);
}
