#!/usr/bin/env python3
"""Test the linter by running it, unchanged, over the fixture vault (§7.1).

Runs `wikitools/lint.py` against `tests/test-llm-wiki/`, captures its
`path: [severity] message` output, and compares each fixture's actual findings
against the EXPECTED table below. Prints a pass/fail summary and exits non-zero
on any mismatch.

    python tests/run_lint_tests.py   # from the repo root
"""

import io
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from wikitools import lint  # noqa: E402

FIX = Path(__file__).resolve().parent / "test-llm-wiki"

E, W = "E", "W"

# fixture (relative to test-llm-wiki/) -> expected finding (severity, reason
# substring) for a negative case, or None for a positive case (must lint clean).
EXPECTED = {
    # vocabulary — positives
    "vocabulary/見本.md": None,
    "vocabulary/やがて.md": None,
    "vocabulary/neg-dup-a.md": None,          # first of the dup pair: clean
    # vocabulary — negatives
    "vocabulary/neg-missing-id.md": (E, "missing required field `id`"),
    "vocabulary/neg-focus.md": (E, "`focus` must be true/false"),
    "vocabulary/neg-date.md": (E, "`created` not ISO"),
    "vocabulary/neg-level.md": (E, "`level`"),
    "vocabulary/neg-type.md": (E, "`type`"),
    "vocabulary/neg-pos.md": (E, "`part_of_speech`"),
    "vocabulary/neg-missing-reading.md": (E, "vocabulary missing required `reading`"),
    "vocabulary/neg-title.md": (E, "title line should be"),
    "vocabulary/neg-missing-imi.md": (E, "missing `## 意味`"),
    "vocabulary/neg-missing-reibun.md": (E, "missing `## 例文`"),
    "vocabulary/neg-few-examples.md": (E, ">=2 examples"),
    "vocabulary/neg-missing-canto.md": (E, "missing a （粵）"),
    "vocabulary/neg-no-frontmatter.md": (E, "no YAML frontmatter"),
    "vocabulary/neg-split-link.md": (E, "split across a line break"),
    "vocabulary/neg-dup-b.md": (E, "duplicate id"),
    "vocabulary/pos-suru.md": None,                                    # suru-verb title, clean
    "vocabulary/neg-suru-title.md": (E, "・する"),                      # suru title missing ・する
    "vocabulary/neg-headword-suru.md": (E, "must not end in する"),
    # grammar
    "grammar/～に際して.md": None,
    "grammar/neg-missing-formation.md": (E, "grammar missing required `formation`"),
    "grammar/neg-register.md": (E, "`register`"),
    "grammar/neg-missing-reading.md": (E, "grammar missing required `reading`"),
    "grammar/neg-kanji-reading.md": (E, "`reading` must be kana"),
    # articles
    "articles/pos-article.md": None,
    "articles/neg-missing-honbun.md": (E, "missing `## 本文`"),
    "articles/neg-unresolved.md": (W, "unresolved wikilink"),
    "articles/neg-word-count.md": (E, "`word_count` not an int"),
}

LINE_RE = re.compile(r"^test-llm-wiki/(?P<path>.+\.md): \[(?P<sev>[EW])\] (?P<msg>.*)$")


def run_linter():
    """Run lint.py over the fixture vault; return {fixture_path: [(sev, msg)]}."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        lint.main([str(FIX)])            # lint.py unchanged, argv[0] = fixtures
    findings = {}
    for line in buf.getvalue().splitlines():
        m = LINE_RE.match(line)
        if m:
            findings.setdefault(m["path"], []).append((m["sev"], m["msg"]))
    return findings


def main():
    if not FIX.is_dir():
        print(f"run_lint_tests: fixture vault not found: {FIX}", file=sys.stderr)
        return 2
    findings = run_linter()
    on_disk = {str(p.relative_to(FIX)) for p in FIX.rglob("*.md")}

    results = []
    for fx in sorted(set(EXPECTED) | on_disk):
        got = findings.get(fx, [])
        if fx not in EXPECTED:
            results.append((False, fx, f"fixture on disk but not in EXPECTED (got {got})"))
        elif fx not in on_disk:
            results.append((False, fx, "listed in EXPECTED but file missing"))
        elif EXPECTED[fx] is None:
            ok = got == []
            results.append((ok, fx, "clean" if ok else f"expected clean, got {got}"))
        else:
            sev, sub = EXPECTED[fx]
            ok = any(s == sev and sub in m for s, m in got)
            results.append((ok, fx, f"[{sev}] …{sub}…" if ok else
                            f"expected [{sev}] containing '{sub}', got {got}"))

    for ok, fx, why in results:
        print(f"{'PASS' if ok else 'FAIL'}  {fx}  — {why}")
    passed = sum(1 for ok, _, _ in results if ok)
    failed = len(results) - passed
    print(f"\nSummary: {passed}/{len(results)} passed, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
