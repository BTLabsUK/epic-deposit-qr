// SPDX-License-Identifier: Apache-2.0
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { depositUri, qrPng, qrSvg } from './deposit-qr.js';

for (const { uri, ...input } of JSON.parse(readFileSync(new URL('../vectors/uri.json', import.meta.url)))) {
  assert.equal(depositUri(input), uri);
}
const uri = JSON.parse(readFileSync(new URL('../vectors/uri.json', import.meta.url)))[0].uri;
assert.throws(() => depositUri({ address: 'bad', note: '1' }));
assert.throws(() => depositUri({ address: 'x', note: '' }));
assert.match(await qrSvg(uri), /^<svg/);
assert.match(await qrSvg(uri, 'data:image/png;base64,AAAA'), /<image /);
const png = await qrPng(uri);
if (process.argv[2]) (await import('node:fs')).writeFileSync(process.argv[2], png);
console.log('js ok');
