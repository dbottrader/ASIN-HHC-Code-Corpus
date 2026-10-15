# Sources

Per-mirror extraction coverage for the 2026-10-14 build. "Unique" counts blocks
whose first-seen source was that mirror (dedup is global, so a block counts once).

| mirror | files scanned | blocks found | too small | excluded: secrets | excluded: emails/phones | unique blocks |
|---|---|---|---|---|---|---|
| deepseek (116 chats) | 116 | 1,883 | 31 | 5 | 80 | 1,267 |
| gemini (829 chats) | 829 | 1,604 | 56 | 0 | 100 | 1,077 |
| grok (334 chats) | 334 | 1,519 | 48 | 17 | 68 | 781 |
| codepen (367 pens, src files) | 455 | 445 | 10 | 1 | 97 | 330 |
| oai (17 md/json docs) | 17 | 3 | 0 | 0 | 3 | 0 |
| kimi (66 chats) | 66 | 0 | 0 | 0 | 0 | 0 |
| **total** | **1,817** | **5,454** | **145** | **23** | **348** | **3,455** |

Notes:

- **kimi**: 66 conversations, zero fenced code blocks. Kimi's chats in this
  archive are detailed summaries, not working sessions — recorded, not a gap in
  the extractor.
- **oai**: the OAI mirror holds documents and DMT originals rather than chat
  transcripts; its 3 fenced blocks all contained contact details and were
  excluded under the no-PII rule.
- **codepen**: scanned `src/index.html`, `src/script.js`, `src/style.css` per pen
  (dist/ copies and READMEs excluded to avoid duplicates).
- **excluded**: 23 blocks matched secret/API-key patterns; 348 matched email or
  phone patterns (many CodePen pens carry `mailto:`/contact placeholders). Counts
  are preserved in `stats.json`; contents are not.
- Blocks under 30 non-whitespace characters (e.g. single shell commands) were
  dropped as noise.
