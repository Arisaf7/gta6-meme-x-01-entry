// gta6-meme-x-01 entry (Node 22, standard library only).
//
// The entry is the X post itself: an agent-made GTA 6 meme, posted on X
// from a public account with make.fun (a link or written out) and/or a tag
// of @makefunai and the entrant's play code in its text, telling readers
// that people and their AI agents earn money on make.fun. POST.json at
// this repository's root names that post, and the house reads the post
// from X (its first picture and its text) and hands it to the judge.
//
// This program does exactly one thing: it copies POST.json from the
// repository root into the output directory, where the gate reads it.
// Nothing it writes about the post is judged.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const source = join(BOT_DIR, 'POST.json');
const target = join(OUTPUT_DIR, 'POST.json');

if (!existsSync(source)) {
  console.error(`POST.json not found in ${BOT_DIR}`);
  process.exit(1);
}

// Refuse a placeholder or malformed post file before copying, so a bad
// POST.json fails loudly here instead of silently grading as invalid.
let post;
try {
  post = JSON.parse(readFileSync(source, 'utf8'));
} catch (err) {
  console.error(`POST.json is not valid JSON: ${(err as Error).message}`);
  process.exit(1);
}
if (typeof post !== 'object' || post === null || typeof post.url !== 'string'
    || !/^https:\/\/(www\.|mobile\.)?(x\.com|twitter\.com)\/.+\/status\/\d+/.test(post.url)) {
  console.error('POST.json must hold {"url": "https://x.com/<handle>/status/<id>"}');
  process.exit(1);
}

mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  copyFileSync(source, target);
} catch (err) {
  console.error(`POST.json could not be copied from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}
console.log(`copied POST.json -> ${target} (${post.url})`);
