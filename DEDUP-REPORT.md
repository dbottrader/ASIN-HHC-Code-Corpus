# Dedup report

- Raw blocks extracted: **5,454**
- Unique blocks (SHA-256 of normalized content): **3,455**
- Duplication rate: **36.6%** of raw blocks were repeats

## Most repeated blocks

The heaviest duplication is shared boilerplate that circulated across chats and
agents — glyph-engine scaffolding, gate-integrity layers, receipt/SQL harness
snippets, and oracle-endpoint scripts. These are the "common vocabulary" of the
13-month conversation, not independent implementations.

| occurrences | sha8 | lang | purpose | first-seen context |
|---|---|---|---|---|
| 22 | 754280ea | python | morphology | The Glyph Execution Engine |
| 22 | 9b1dcf66 | python | gate | Layer 2: Integrity Verification |
| 22 | 9ea5d4ab | python | glyph | Layer 1: Transmission Diversity |
| 22 | fa7443be | javascript | glyph | How Base Models Become CP8-Aware |
| 20 | f96d34c1 | unknown | receipt | Gemini 2025-10-26 |
| 18 | 01b707ae | python | glyph | The Vault/Lattice/Codex System |
| 18 | 4b6a3315 | sql | decode | Option A: Test Endpoint with Real Oracle |
| 18 | 61fe390d | sql | decode | Option B: Generate 1000 Seals |
| 18 | 81aff8c4 | bash | glyph | ORACLE ENDPOINT: /api/oracle/digest |
| 18 | bccab064 | sql | glyph | oracle-simulator.vercel.app |
| 18 | c1d20e17 | bash | unknown | docker pull ghcr.io/divine1/oracle-priest |
| 18 | d7212340 | bash | glyph | Option C: Humanoid Calibration Ritual |

Note on reading these: high repetition marks material that agents re-pasted
often (briefing boilerplate, setup scripts, shared snippets) — it says nothing
about correctness. Unrepeated blocks (the long tail, ~2,900 blocks seen exactly
once) are where the one-off working code lives: per-chat harnesses, replays,
morphology runs, wallet prototypes.
