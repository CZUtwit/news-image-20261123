// Entry for news-image-20261123 (Node 22, standard library only).
//
// The picture lives in this repository as entry.png: one image summing up
// the world news of Monday 23 November 2026, drawn by tools/make_image.py
// (pure Pillow, no network). This program only copies it to the output
// directory, so both grader runs write exactly the same bytes.
//
// Local run:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const target = join(outDir, 'entry.png');
const source = new URL('./entry.png', import.meta.url);

copyFileSync(source, target);

const written = statSync(target);
if (written.size === 0) {
  throw new Error('entry.png came out empty');
}
