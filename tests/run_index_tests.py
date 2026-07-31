#!/usr/bin/env python3
"""Test the index generator against a fixture vault (specs.md §7.2).

Same golden-baseline approach as §7.1: run `scraper/index.py` over the clean
fixture vault `tests/index-wiki/` and compare its markdown to the committed
baseline `tests/index-baseline.md`, plus targeted property checks for the rules
that matter (section order, counts, reading-omission, あいうえお sort, 意味
paragraph-join, article メモ / tags gloss). Prints a pass/fail summary and exits
non-zero on any mismatch.

    python tests/run_index_tests.py            # from the repo root
    python scraper/index.py tests/index-wiki tests/index-baseline.md  # regen baseline

Regenerating the baseline (right-hand command) is the intended way to update
expectations when the format deliberately changes.
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from scraper import index  # noqa: E402

FIX = Path(__file__).resolve().parent / "index-wiki"
BASELINE = Path(__file__).resolve().parent / "index-baseline.md"


def checks(text):
    """Return [(ok, name, detail)] for each property under test."""
    def has(s):
        return s in text

    def order(a, b, c):
        return text.index(a) < text.index(b) < text.index(c)

    out = []

    # 1. golden byte-identical
    if BASELINE.exists():
        exp = BASELINE.read_text(encoding="utf-8")
        out.append((text == exp, "golden byte-identical",
                    "matches baseline" if text == exp else "differs from baseline"))
    else:
        out.append((False, "golden byte-identical", "baseline missing — run the regen command"))

    # 2. section order 語彙 -> 文法 -> 記事
    out.append((order("## 語彙", "## 文法", "## 記事"),
                "section order 語彙→文法→記事", ""))

    # 3. per-type counts + total
    out.append((has("## 語彙（3 項目）") and has("## 文法（1 項目）")
                and has("## 記事（2 項目）") and has("収録 6 項目"),
                "per-type counts + total", "3/1/2, total 6"))

    # 4. reading shown for kanji headword
    out.append((has("[[改ざん]]（かいざん）") and has("[[相槌]]（あいづち）"),
                "reading shown for kanji", "改ざん / 相槌"))

    # 5. reading omitted for kana headword
    out.append((has("[[やがて]] —") and not has("[[やがて]]（"),
                "reading omitted for kana", "やがて"))

    # 6. grammar (～…) reading omitted
    out.append((has("[[～ものの]] —") and not has("[[～ものの]]（"),
                "reading omitted for ～ grammar", "～ものの"))

    # 7. あいうえお sort within 語彙
    out.append((order("[[相槌]]", "[[改ざん]]", "[[やがて]]"),
                "あいうえお sort", "相槌<改ざん<やがて"))

    # 8. 意味 paragraph-join (not first-line-only): line-2 text + inline 粵 kept
    out.append((has("多く悪い意味で用いる。（粵：篡改、竄改。）"),
                "意味 paragraph joined (＋inline 粵)", "改ざん gloss"))

    # 9. article gloss = first メモ sentence (二文目 dropped)
    out.append((has("テーマ：索引生成の確認。") and not has("二文目"),
                "article メモ first sentence", "テスト記事"))

    # 10. article tags fallback when no メモ
    out.append((has("[[タグ記事]] — （reading・fallback）"),
                "article tags fallback", "タグ記事"))

    # 11. generated-file header (edit note + 最終更新)
    out.append((has(index.EDIT_NOTE) and has("最終更新 2026-07-30"),
                "generated-file header", ""))

    return out


def main():
    if not FIX.is_dir():
        print(f"run_index_tests: fixture vault not found: {FIX}", file=sys.stderr)
        return 2
    text, _, _ = index.build_index(str(FIX))
    results = checks(text)
    for ok, name, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ""))
    passed = sum(1 for ok, _, _ in results if ok)
    failed = len(results) - passed
    print(f"\nSummary: {passed}/{len(results)} passed, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
