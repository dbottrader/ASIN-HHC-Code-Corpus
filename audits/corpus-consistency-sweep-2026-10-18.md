# ASIN-HHC Code Corpus Consistency Sweep — 2026-10-18

**Status:** OBSERVED + TESTED (detector unit probes); corpus-wide content scan NOT YET EXECUTED.  
**Scope:** Review of public `README.md`, `stats.json`, `SOURCES.md`, `DEDUP-REPORT.md`, and `tools/build_corpus.py` in `dbottrader/ASIN-HHC-Code-Corpus`. No corpus files were modified. No secret values were collected or published.

## Findings

### F-01 — Secret detector misses common token formats (TESTED, reproducible)

The current `SECRET_PATTERNS` in `tools/build_corpus.py` detect classic `ghp_` GitHub tokens and AWS `AKIA...` access-key IDs, but synthetic format probes returned **no match** for:
- OpenAI project-key prefix `sk-proj-` followed by a sufficiently long token body.
- Supabase secret-key prefix `sb_secret_` followed by a sufficiently long token body.
- GitHub fine-grained PAT prefix `github_pat_` followed by a sufficiently long token body.

The same probes did match `ghp_`, `AKIA...`, and a PEM private-key header. These were synthetic format strings only, not real credentials.

**Impact:** the published exclusion count (23 secret-pattern matches) does not establish that the corpus is free of credentials. The three missed formats are concrete false-negative cases in the current detector.

**Remediation:** add format-specific patterns for current provider prefixes and generic high-entropy credential assignments; add positive and negative regression fixtures; scan only for matches and emit redacted file/block identifiers, never token contents. Treat a match as quarantine/review, not proof a credential is live.

### F-02 — Reported duplication rate mixes exclusions with repeats (REPRODUCIBLE arithmetic)

Published `stats.json` / `SOURCES.md` report:
- Raw extracted blocks: 5,454
- Too-small blocks dropped: 145
- Secret-pattern exclusions: 23
- Email/phone-pattern exclusions: 348
- Unique included blocks: 3,455

After the stated pre-dedup filters, the candidate set is 5,454 − 145 − 23 − 348 = **4,938**. Relative to that candidate set, duplicates are 4,938 − 3,455 = **1,483**, or **30.0%**. The published report computes (5,454 − 3,455) / 5,454 = **36.7%**, which counts all excluded and too-small blocks as if they were repeats. The 36.6% figure is therefore not a clean deduplication rate under the documented pipeline.

**Remediation:** publish separate metrics: raw blocks, too-small drops, secret/PII exclusions, post-filter candidates, unique included blocks, and duplicate occurrences. Define the duplicate rate denominator explicitly.

### F-03 — 8-hex-character filenames are weaker than the full SHA-256 dedup key (DESIGN RISK)

The builder deduplicates by full SHA-256 but writes files as `<sha8>.<ext>` (first 32 bits). A short-prefix collision can overwrite a different block even when the full hashes differ; the index can then point at two records whose on-disk filename collides.

**Remediation:** use the full SHA-256 as the filename or check all short-prefix collisions and fail closed before writing. Add a fixture that forces a prefix collision and verifies no overwrite occurs.

### F-04 — Corpus build is not self-contained in the public repository (REPRODUCIBILITY GAP)

The builder hard-codes source mirrors under `~/workspace/*-library` and writes to `~/workspace/code-corpus`. Those paths are environment-specific and not supplied by the repository itself. The README's `python3 tools/build_corpus.py` command only reproduces the build when the private/local mirror layout already exists.

**Remediation:** accept explicit input/output paths and a manifest of source roots; validate missing roots; add a sanitized fixture dataset and CI test that reproduces counts/hashes without private archives.

### F-05 — Purpose classification is ordered substring matching (KNOWN MISCLASSIFICATION RISK)

`classify_purpose` returns the first purpose whose keyword appears in the heading, path, or first 2,000 content characters. Generic terms such as `token`, `ledger`, `threshold`, `sacred`, or `calendar` can override the actual subject because category priority is hard-coded.

**Remediation:** record all matching labels with evidence spans, or use an explicit precedence/ multi-label policy; measure per-category precision on a manually labeled sample before treating tags as authoritative.

## Evidence accounting

- **OBSERVED:** the five published source artifacts and their contents were retrieved from the public repository.
- **TESTED:** synthetic probes against the detector patterns demonstrated false negatives for `sk-proj-`, `sb_secret_`, and `github_pat_`; positive controls matched `ghp_`, `AKIA...`, and a private-key header.
- **REPRODUCED:** the count arithmetic in F-02.
- **NOT EXECUTED:** no full scan of all 3,455 stored blocks or the Hugging Face dataset is claimed in this report; the raw corpus archive and dataset contents still need to be fetched and scanned to quantify actual missed exposures and category errors.
- **No credentials or personal contact details are reproduced here.**

## Next executable step

Fetch the published corpus archive and the Hugging Face dataset into a read-only audit workspace; verify archive/index counts and full hashes; run expanded secret/PII detectors plus duplicate-prefix and category checks; emit only redacted findings and per-category counts. Quarantine only confirmed risky blocks after preserving a private, access-controlled audit receipt.