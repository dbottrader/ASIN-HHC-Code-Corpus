# ASIN-HHC Code Corpus

A unified, deduplicated collection of **code blocks** extracted from Dennis's six
AI-platform chat archives (DeepSeek, Kimi, Gemini, Grok, ChatGPT/OAI, CodePen),
spanning roughly 13 months of ASIN-HHC / CP8 work (2025-05 → 2026-10).

## What it is

Every fenced code block (``` ``` ```) from every conversation file, plus CodePen
pen sources (HTML/CSS/JS), deduplicated by SHA-256 of normalized content, with a
full provenance record for each unique block: which mirror(s), which file(s), and
the nearest section heading.

- `corpus/<lang>/<sha8>.<ext>` — one file per unique code block, shipped as
  `corpus-files.tar.gz` (extract with `tar -xzf corpus-files.tar.gz` to restore
  the `corpus/` tree; split out of the git tree for reliable upload)
- `INDEX.json` — machine-readable index: sha256, language, purpose tag, bytes,
  occurrence count, and up to 25 provenance records per block
- `stats.json` — raw per-mirror extraction stats
- `SOURCES.md` — per-mirror coverage
- `DEDUP-REPORT.md` — duplication analysis
- `tools/build_corpus.py` — the re-runnable extractor (mirrors are read-only)

## What it is NOT

This corpus is **build material, not verified evidence**. Inclusion here means "an
agent wrote or pasted this code in a chat," not "this code was tested, reviewed,
or executed." Provenance is tracked so any block can be traced back to its source
conversation; nothing here is promoted beyond what its source supports.

Evidence status across the programme stays **HOLD** until real test vectors land.
The index describes code; it does not promote code.

## Contents at a glance (2026-10-14 build)

- **3,455 unique blocks** (~11 MB) from 5,454 raw blocks
- Languages: python, javascript, html, bash, json, yaml, css, sql, jsx, markdown…
- Purpose tags: glyph, receipt, decode, gate, wallet, morphology, pen, coherence,
  moltbook, algebra, replay, fisher (keyword-classified, best-effort)
- Secrets/API keys (23) and emails/phone numbers (348) were detected and
  **excluded** from the corpus; counts are in `stats.json`

## Reproduce

```bash
python3 tools/build_corpus.py
```

Reads the six mirrors read-only; rewrites `corpus/`, `INDEX.json`, `stats.json`.

## License

MIT — see LICENSE. Equality before profits: this build material is open source.
