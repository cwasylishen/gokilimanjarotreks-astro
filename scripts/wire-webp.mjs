// Phase 1: wrap <img src="/images/X.jpg"> in <picture> with a WebP source
// where public/images/X.webp exists and the img is not already inside a picture.
import { readdirSync, readFileSync, writeFileSync, existsSync, statSync } from 'fs';
import { join } from 'path';

const walk = (d) => readdirSync(d).flatMap((f) => {
  const p = join(d, f);
  return statSync(p).isDirectory() ? walk(p) : p.endsWith('.astro') ? [p] : [];
});

let wrapped = 0, skipped = [];
for (const file of walk('src')) {
  let src = readFileSync(file, 'utf8');
  const re = /<img\s[^>]*src="(\/images\/[^"]+\.jpg)"[^>]*>/g;
  let out = '';
  let last = 0;
  let m;
  let changed = false;
  while ((m = re.exec(src))) {
    const jpg = m[1];
    const webp = jpg.replace(/\.jpg$/, '.webp');
    const before = src.slice(Math.max(0, m.index - 200), m.index);
    out += src.slice(last, m.index);
    last = m.index + m[0].length;
    const inPicture = /<picture[^>]*>(?:(?!<\/picture>)[\s\S])*$/.test(before);
    if (!existsSync(join('public', webp.slice(1)))) {
      skipped.push(`${file}: no webp for ${jpg}`);
      out += m[0];
    } else if (inPicture) {
      skipped.push(`${file}: already in <picture>: ${jpg}`);
      out += m[0];
    } else {
      out += `<picture><source type="image/webp" srcset="${webp}">${m[0]}</picture>`;
      wrapped++;
      changed = true;
    }
  }
  out += src.slice(last);
  if (changed) writeFileSync(file, out);
}
console.log('wrapped', wrapped);
console.log(skipped.join('\n'));
