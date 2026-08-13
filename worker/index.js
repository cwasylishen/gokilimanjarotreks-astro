var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// worker/schedule.js
var SCHEDULE = {
  "stella-point-vs-uhuru-peak": "2026-07-27",
  "toilets-and-staying-clean": "2026-07-29",
  "appetite-and-eating-at-altitude": "2026-07-31",
  "climbing-kilimanjaro-solo": "2026-08-03",
  "moshi-before-and-after-your-climb": "2026-08-05",
  "serengeti-vs-ngorongoro": "2026-08-07"
};

// worker/index.js
var SLUG_RE = /\/blog\/([a-z0-9-]+)/;
function isLive(slug, now) {
  const date = SCHEDULE[slug];
  if (!date) return true;
  const ts = Date.parse(date + "T00:00:00Z");
  return Number.isNaN(ts) ? true : ts <= now;
}
__name(isLive, "isLive");
function liveInText(text, now) {
  const m = text.match(SLUG_RE);
  return !(m && !isLive(m[1], now));
}
__name(liveInText, "liveInText");
var BlogSchemaFilter = class {
  static {
    __name(this, "BlogSchemaFilter");
  }
  constructor(now) {
    this.now = now;
    this.buf = "";
  }
  text(chunk) {
    this.buf += chunk.text;
    if (!chunk.lastInTextNode) {
      chunk.remove();
      return;
    }
    let out = this.buf;
    try {
      const data = JSON.parse(this.buf);
      const nodes = Array.isArray(data) ? data : [data];
      let changed = false;
      for (const node of nodes) {
        if (node && node["@type"] === "Blog" && Array.isArray(node.blogPost)) {
          const kept = node.blogPost.filter((p) => liveInText(String(p && p.url || ""), this.now));
          if (kept.length !== node.blogPost.length) {
            node.blogPost = kept;
            changed = true;
          }
        }
      }
      if (changed) out = JSON.stringify(Array.isArray(data) ? data : nodes[0]);
    } catch (err) {
      out = this.buf;
    }
    chunk.replace(out, { html: false });
    this.buf = "";
  }
};
var index_default = {
  async fetch(request, env) {
    const url = new URL(request.url);
    const now = Date.now();
    const path = (url.pathname.replace(/\/+$/, "") || "/").replace(/\.html$/, "");
    const post = path.match(/^\/blog\/([a-z0-9-]+)$/);
    if (post && !isLive(post[1], now)) {
      const res = await env.ASSETS.fetch(new URL("/404.html", url));
      return new Response(res.body, {
        status: 404,
        headers: { "content-type": "text/html; charset=utf-8" }
      });
    }
    if (path === "/blog") {
      const res = await env.ASSETS.fetch(request);
      if (!(res.headers.get("content-type") || "").includes("text/html")) return res;
      return new HTMLRewriter().on("a.blog-card", {
        element(el) {
          if (!liveInText(el.getAttribute("href") || "", now)) el.remove();
        }
      }).on('script[type="application/ld+json"]', new BlogSchemaFilter(now)).transform(res);
    }
    if (path === "/sitemap-0.xml" || path === "/sitemap-index.xml" || path === "/llms.txt") {
      const res = await env.ASSETS.fetch(request);
      let body = await res.text();
      body = path.endsWith(".xml") ? body.replace(/<url>[\s\S]*?<\/url>/g, (block) => liveInText(block, now) ? block : "") : body.split("\n").filter((line) => liveInText(line, now)).join("\n");
      const headers = new Headers(res.headers);
      headers.delete("content-length");
      return new Response(body, { status: res.status, headers });
    }
    return env.ASSETS.fetch(request);
  }
};
export {
  index_default as default
};

