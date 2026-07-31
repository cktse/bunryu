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

    def order(*xs):
        idx = [text.index(x) for x in xs]
        return idx == sorted(idx)

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

    # 3. 語彙 POS sub-bucket order
    out.append((order("### 名詞", "### 動詞", "### 形容詞", "### 副詞", "### 表現"),
                "POS bucket order", "名詞→動詞→形容詞→副詞→表現"))

    # 4. per-bucket + per-type counts + total
    out.append((has("## 語彙（6 項目）") and has("### 名詞（2 項目）")
                and has("### 動詞（1 項目）") and has("### 形容詞（1 項目）")
                and has("### 副詞（1 項目）") and has("### 表現（1 項目）")
                and has("## 文法（1 項目）") and has("## 記事（2 項目）")
                and has("収録 9 項目"),
                "bucket/type counts + total", "名詞2 …, 語彙6, total 9"))

    # 5. suru-verb shows the ・する marker (surface + reading)
    out.append((has("[[改ざん]]・する（かいざん・する）"),
                "・する marker on suru-verb", "改ざん"))

    # 6. plain noun gets no ・する; reading shown for kanji
    out.append((has("[[相槌]]（あいづち）") and not has("[[相槌]]・する"),
                "plain noun: reading, no ・する", "相槌"))

    # 7. noun + suru-verb merged into 名詞 (both before 動詞)
    out.append((order("### 名詞", "[[相槌]]", "[[改ざん]]", "### 動詞"),
                "noun+suru-verb merged in 名詞", ""))

    # 8. reading omitted for kana headword
    out.append((has("[[やがて]] —") and not has("[[やがて]]（"),
                "reading omitted for kana", "やがて"))

    # 9. grammar (～…) reading omitted
    out.append((has("[[～ものの]] —") and not has("[[～ものの]]（"),
                "reading omitted for ～ grammar", "～ものの"))

    # 10. あいうえお sort within 名詞
    out.append((order("[[相槌]]", "[[改ざん]]"),
                "あいうえお sort in 名詞", "相槌<改ざん"))

    # 11. 意味 paragraph-join (not first-line-only): line-2 text + inline 粵 kept
    out.append((has("多く悪い意味で用いる。（粵：篡改、竄改。）"),
                "意味 paragraph joined (＋inline 粵)", "改ざん gloss"))

    # 12. article gloss = first メモ sentence (二文目 dropped)
    out.append((has("テーマ：索引生成の確認。") and not has("二文目"),
                "article メモ first sentence", "テスト記事"))

    # 13. article tags fallback when no メモ
    out.append((has("[[タグ記事]] — （reading・fallback）"),
                "article tags fallback", "タグ記事"))

    # 14. generated-file header (edit note + 最終更新)
    out.append((has(index.EDIT_NOTE) and has("最終更新"),
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
