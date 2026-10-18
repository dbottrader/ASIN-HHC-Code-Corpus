#!/usr/bin/env python3
"""Build unified ASIN-HHC code corpus from six AI-platform archive mirrors.

Reads fenced code blocks from conversation .md files across the six mirrors
plus CodePen pen sources (src/index.html, src/script.js, src/style.css).
Dedupes by SHA-256 of normalized content, excludes secrets/PII, classifies
language + rough purpose, writes one file per unique block under corpus/<lang>/.
Re-runnable; mirrors are read-only.
"""
import re, hashlib, json
from pathlib import Path

WS = Path.home() / "workspace"
OUT = WS / "code-corpus"
CORPUS = OUT / "corpus"

MIRRORS = {
    "deepseek": WS / "deepseek-library" / "chats",
    "kimi": WS / "kimi-library" / "chats",
    "gemini": WS / "gemini-library" / "chats",
    "grok": WS / "grok-library" / "chats",
    "oai": WS / "oai-library",
    "codepen": WS / "codepen-library" / "pens",
}

FENCE = re.compile(r'^```([A-Za-z0-9+#._-]*)\s*\n(.*?)^```[ \t]*$', re.M | re.S)
HEADING = re.compile(r'^(#{1,6})\s+(.+)$', re.M)

SECRET_PATTERNS = [
    # OpenAI / project keys
    re.compile(r'sk-(live|test)-[A-Za-z0-9]{16,}'),
    re.compile(r'sk-proj-[A-Za-z0-9\-_]{16,}'),
    re.compile(r'sk-[A-Za-z0-9]{20,}'),
    # GitHub
    re.compile(r'ghp_[A-Za-z0-9]{20,}'),
    re.compile(r'gho_[A-Za-z0-9]{20,}'),
    re.compile(r'github_pat_[A-Za-z0-9_]{20,}'),
    # AWS / Slack / Google
    re.compile(r'AKIA[0-9A-Z]{16}'),
    re.compile(r'xox[abp]-[A-Za-z0-9-]{10,}'),
    re.compile(r'AIza[0-9A-Za-z_-]{35}'),
    # Supabase
    re.compile(r'sb_secret_[A-Za-z0-9]{16,}'),
    re.compile(r'sb_publishable_[A-Za-z0-9]{16,}'),
    # Private keys
    re.compile(r'-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    # Generic key/token assignments
    re.compile(r'["\']?api[_-]?key["\']?\s*[:=]\s*["\'][A-Za-z0-9\-_]{16,}["\']', re.I),
    re.compile(r'["\']?secret[_-]?key["\']?\s*[:=]\s*["\'][A-Za-z0-9\-_]{16,}["\']', re.I),
    re.compile(r'["\']?(client[_-]?secret|access[_-]?token|auth[_-]?token)["\']?\s*[:=]\s*["\'][A-Za-z0-9\-_.]{16,}["\']', re.I),
]
EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
PHONE_RE = re.compile(r'(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)')

EXT = {"python": "py", "javascript": "js", "typescript": "ts", "html": "html", "css": "css",
       "json": "json", "bash": "sh", "shell": "sh", "sh": "sh", "sql": "sql", "yaml": "yml",
       "yml": "yml", "markdown": "md", "md": "md", "text": "txt", "plain": "txt", "unknown": "txt",
       "jsx": "jsx", "tsx": "tsx", "rust": "rs", "go": "go", "java": "java", "c": "c", "cpp": "cpp"}

def infer_lang(content, tag):
    if tag:
        t = tag.lower().lstrip(".")
        return {"py": "python", "js": "javascript", "ts": "typescript"}.get(t, t)
    c = content.strip()
    if c.startswith("<!DOCTYPE") or c.startswith("<html") or re.search(r'</(div|html|body|script)>', c):
        return "html"
    if c.startswith("{") or c.startswith("["):
        try:
            json.loads(c); return "json"
        except Exception: pass
    if re.search(r'^\s*(import |from \w+ import|def \w+\(|class \w+[\(:])', c, re.M):
        return "python"
    if re.search(r'(function\s+\w+\s*\(|=>|const \w+\s*=|document\.|console\.log)', c):
        return "javascript"
    if re.search(r'^\s*(SELECT|INSERT|UPDATE|CREATE TABLE)\b', c, re.M | re.I):
        return "sql"
    if re.search(r'^\s*(#!/bin/(ba)?sh|echo |curl |npm |pip )', c, re.M):
        return "bash"
    if re.search(r'^\s*\w+:\s*\S', c, re.M) and "{" not in c[:50]:
        return "yaml"
    return "unknown"

PURPOSE_KEYS = [
    ("gate", ["gate", "delta717", "delta-717", "threshold"]),
    ("replay", ["replay", "test vector", "test-vector", "harness"]),
    ("morphology", ["morphology", "formation", "crabwood", "roundway"]),
    ("receipt", ["receipt", "sha256", "sha-256", "manifest", "provenance"]),
    ("wallet", ["wallet", "ledger", "token", "powp", "hcc"]),
    ("glyph", ["glyph", "anu", "sacred"]),
    ("moltbook", ["moltbook", "handshake", "heartbeat", "submolt"]),
    ("decode", ["decode", "ccd-9", "calendar", "harmonic"]),
    ("coherence", ["coherence", "resonance", "0.78"]),
    ("algebra", ["algebra", "tau", "963", "superformula"]),
    ("fisher", ["fisher", "cron", "supervis"]),
    ("pen", ["codepen"]),
]

def classify_purpose(text):
    t = text.lower()
    for purpose, keys in PURPOSE_KEYS:
        if any(k in t for k in keys):
            return purpose
    return "unknown"

def normalize(content):
    lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(l.rstrip() for l in lines).strip("\n")

def nearest_heading(text, pos):
    hs = list(HEADING.finditer(text, 0, pos))
    return hs[-1].group(2).strip()[:160] if hs else ""

def scan_markdown(mirror, fpath, blocks, stats):
    try:
        text = fpath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        stats["read_errors"] += 1; return
    stats["files_scanned"] += 1
    for m in FENCE.finditer(text):
        content = normalize(m.group(2))
        if len(re.sub(r"\s", "", content)) < 30:
            stats["too_small"] += 1; continue
        stats["blocks_found"] += 1
        if any(p.search(content) for p in SECRET_PATTERNS):
            stats["excluded_secret"] += 1; continue
        if EMAIL_RE.search(content) or PHONE_RE.search(content):
            stats["excluded_pii"] += 1; continue
        blocks.append({
            "content": content,
            "lang": infer_lang(content, m.group(1)),
            "mirror": mirror,
            "file": str(fpath.relative_to(WS)),
            "heading": nearest_heading(text, m.start()),
        })

def scan_codepen_file(srcf, pen, blocks, stats):
    try:
        content = normalize(srcf.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        stats["read_errors"] += 1; return
    stats["files_scanned"] += 1
    if len(re.sub(r"\s", "", content)) < 30:
        stats["too_small"] += 1; return
    stats["blocks_found"] += 1
    if any(p.search(content) for p in SECRET_PATTERNS):
        stats["excluded_secret"] += 1; return
    if EMAIL_RE.search(content) or PHONE_RE.search(content):
        stats["excluded_pii"] += 1; return
    lang = {"html": "html", "js": "javascript", "css": "css"}.get(
        srcf.suffix.lower().lstrip("."), "unknown")
    blocks.append({"content": content, "lang": lang, "mirror": "codepen",
                   "file": str(srcf.relative_to(WS)), "heading": f"pen: {pen.name}"})

def main():
    blocks, stats = [], {}
    for mirror, base in MIRRORS.items():
        st = {"files_scanned": 0, "blocks_found": 0, "too_small": 0,
              "excluded_secret": 0, "excluded_pii": 0, "read_errors": 0,
              "unique_blocks": 0}
        stats[mirror] = st
        if not base.exists():
            st["missing"] = True; continue
        if mirror == "codepen":
            for pen in sorted(base.iterdir()):
                for srcf in (sorted(pen.rglob("src/index.html")) +
                             sorted(pen.rglob("src/script.js")) +
                             sorted(pen.rglob("src/style.css"))):
                    scan_codepen_file(srcf, pen, blocks, st)
        elif mirror == "oai":
            for f in sorted(base.rglob("*.md")) + sorted(base.rglob("*.json")):
                scan_markdown(mirror, f, blocks, st)
        else:
            for f in sorted(base.rglob("*.md")):
                scan_markdown(mirror, f, blocks, st)

    uniq = {}
    for b in blocks:
        h = hashlib.sha256(b["content"].encode("utf-8")).hexdigest()
        if h not in uniq:
            uniq[h] = {"sha256": h, "sha8": h[:8], "lang": b["lang"],
                       "content": b["content"],
                       "purpose": classify_purpose(b["heading"] + " " + b["file"] + " " + b["content"][:2000]),
                       "bytes": len(b["content"].encode("utf-8")),
                       "occurrences": 0, "sources": []}
        u = uniq[h]
        u["occurrences"] += 1
        if len(u["sources"]) < 25:
            u["sources"].append({"mirror": b["mirror"], "file": b["file"], "heading": b["heading"]})
    for u in uniq.values():
        stats[u["sources"][0]["mirror"]]["unique_blocks"] += 1

    CORPUS.mkdir(parents=True, exist_ok=True)
    # Fail closed on short-prefix collisions (F-03). Prefer full SHA-256 filenames.
    short_map = {}
    for u in uniq.values():
        key = (u["lang"], u["sha8"])
        short_map.setdefault(key, []).append(u["sha256"])
    collisions = {k: v for k, v in short_map.items() if len(v) > 1}
    if collisions:
        raise RuntimeError(
            f"SHA-8 filename collisions detected ({len(collisions)} groups). "
            "Refusing to write; use full SHA-256 filenames."
        )
    for u in uniq.values():
        langdir = CORPUS / u["lang"]
        langdir.mkdir(exist_ok=True)
        # Full hash prevents overwrite; sha8 retained in INDEX for compatibility.
        fname = f"{u['sha256']}.{EXT.get(u['lang'], 'txt')}"
        (langdir / fname).write_text(u["content"], encoding="utf-8")
        del u["content"]
    index = sorted(uniq.values(), key=lambda u: (-u["occurrences"], u["sha8"]))
    (OUT / "INDEX.json").write_text(json.dumps(index, indent=1), encoding="utf-8")
    (OUT / "stats.json").write_text(json.dumps(stats, indent=1), encoding="utf-8")
    return index, stats

if __name__ == "__main__":
    idx, stats = main()
    print(json.dumps({"unique": len(idx),
                      "total_blocks": sum(s.get("blocks_found", 0) for s in stats.values()),
                      "stats": stats}, indent=1))
