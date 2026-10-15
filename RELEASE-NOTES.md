# ASIN-HHC Code Corpus — release notes (2026-10-14)

13 months of AI-agent working code, compiled into one open-source corpus.

## What this is

Every code block from 13 months of ASIN-HHC / CP8 working sessions across six
AI platforms — DeepSeek, Gemini, Grok, ChatGPT, Kimi, and CodePen — extracted,
deduplicated, and published as build material under the MIT license.

- **3,455 unique code blocks** (~11 MB), from 5,454 raw blocks across 1,817 files
- **Full provenance**: every block traces back to its source conversation
- **Languages**: Python, JavaScript, HTML, Bash, JSON, YAML, CSS, SQL, JSX and more
- **Coverage**: gate/algebra replay harnesses, morphology engines, receipt and
  provenance tooling, wallet/ledger prototypes, glyph engines, decode harnesses,
  Moltbook handshake tooling, 367 CodePen builds

## What this is not

Build material, not verified evidence. Inclusion means "an agent wrote this in
a chat" — not "this was tested or reviewed." Findings stay HOLD until real test
vectors land. No block in this corpus has been independently replayed under the
current tau_hard = 0.25 or coherence-function requirements. Secrets, API keys, emails, and phone numbers were detected and
excluded (371 blocks).

## Links

- Corpus repo: (link on publish)
- Reproduce it: `python3 tools/build_corpus.py` — mirrors are read-only, the
  extractor is deterministic

Equality before profits: the code is open. Build on it.

#ASINHHC #CP8 #OpenSource #AIAgents #BuildInPublic
