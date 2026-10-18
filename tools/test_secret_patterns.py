#!/usr/bin/env python3
"""Regression fixtures for SECRET_PATTERNS (F-01).

Runs without private mirrors. Synthetic tokens only — never real credentials.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_corpus import SECRET_PATTERNS

POSITIVE = [
    ("openai_legacy", "sk-abcdefghijklmnopqrstuvwxyz012345"),
    ("openai_proj", "sk-proj-abcdefghijklmnopqrstuvwxyz0123456789"),
    ("github_classic", "ghp_abcdefghijklmnopqrstuvwxyz012345"),
    ("github_fine", "github_pat_11AAAAAAAABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghij"),
    ("aws", "AKIAIOSFODNN7EXAMPLE"),
    ("supabase_secret", "sb_secret_abcdefghijklmnopqrstuv"),
    ("pem", "-----BEGIN RSA PRIVATE KEY-----\nMIIE"),
]

NEGATIVE = [
    ("short_sk", "sk-short"),
    ("url", "https://example.com/sk-proj-docs"),
    ("comment", "# no secret here"),
]

def matches(text: str) -> bool:
    return any(p.search(text) for p in SECRET_PATTERNS)

def main() -> int:
    failed = []
    for name, sample in POSITIVE:
        if not matches(sample):
            failed.append(f"POSITIVE miss: {name}")
    for name, sample in NEGATIVE:
        if matches(sample):
            failed.append(f"NEGATIVE false positive: {name}")
    if failed:
        print("FAIL")
        for f in failed:
            print(" ", f)
        return 1
    print("PASS: all positive fixtures matched; negatives clean")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
