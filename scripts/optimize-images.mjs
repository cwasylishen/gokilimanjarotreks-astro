// Phase 1 image tooling: generate WebP variants, gallery thumbnails, and
// recompress oversized originals. Uses sharp from Astro's dependency tree.
// Run: node scripts/optimize-images.mjs
import sharp from 'sharp';
import { readdirSync, statSync, existsSync, renameSync, unlinkSync } from 'fs';
import { join } from 'path';

const IMG = 'public/images';
const GAL = join(IMG, 'gallery');
const MAX_W = 1600;
const BIG = 250 * 1024;

const log = (...a) => console.log(...a);

async function recompress(path) {
  const st = statSync(path);
  if (st.size <= BIG) return false;
  const meta = await sharp(path).metadata();
  const tmp = path + '.tmp';
  let p = sharp(path).rotate();
  if ((meta.width || 0) > MAX_W) p = p.resize({ width: MAX_W });
  await p.jpeg({ quality: 80, mozjpeg: true }).toFile(tmp);
  if (statSync(tmp).size < st.size) {
    renameSync(tmp, path);
    log('recompressed', path, `${(st.size / 1024) | 0}K -> ${(statSync(path).size / 1024) | 0}K`);
    return true;
  }
  unlinkSync(tmp);
  return false;
}

async function toWebp(jpg, webp, width) {
  let p = sharp(jpg).rotate();
  if (width) p = p.resize({ width, withoutEnlargement: true });
  await p.webp({ quality: 78 }).toFile(webp);
  log('wrote', webp, `${(statSync(webp).size / 1024) | 0}K`);
}

// 1. Top-level: recompress big jpgs, generate missing webp for wired prefixes
const wiredPrefixes = ['route-', 'page-hero-', 'dest-', 'daytrip-', 'nelson', 'testimonials-bg', 'hero-mobile', 'hero-tablet', 'hero.'];
for (const f of readdirSync(IMG)) {
  const full = join(IMG, f);
  if (!f.endsWith('.jpg') || !statSync(full).isFile()) continue;
  await recompress(full);
  if (wiredPrefixes.some((p) => f.startsWith(p))) {
    const webp = full.replace(/\.jpg$/, '.webp');
    if (!existsSync(webp)) await toWebp(full, webp);
  }
}

// 2. Gallery: recompress originals, refresh webp pair if jpg shrank, make 600px thumbs
for (const f of readdirSync(GAL)) {
  if (!f.endsWith('.jpg') || f.endsWith('-thumb.jpg')) continue;
  const jpg = join(GAL, f);
  const shrank = await recompress(jpg);
  const webp = jpg.replace(/\.jpg$/, '.webp');
  if (shrank || !existsSync(webp)) await toWebp(jpg, webp);
  const thumbW = jpg.replace(/\.jpg$/, '-thumb.webp');
  const thumbJ = jpg.replace(/\.jpg$/, '-thumb.jpg');
  if (!existsSync(thumbW)) await toWebp(jpg, thumbW, 600);
  if (!existsSync(thumbJ)) {
    await sharp(jpg).rotate().resize({ width: 600, withoutEnlargement: true }).jpeg({ quality: 80, mozjpeg: true }).toFile(thumbJ);
    log('wrote', thumbJ);
  }
}
log('done');
