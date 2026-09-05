#!/usr/bin/env python3
"""Content index generator for the LLM-wiki (specs.md §7.2).

Walks the llm-wiki/ tree and rebuilds a single human-browsable map-of-content,
index.md, at the repo root: every page as a [[wikilink]] with its reading and a
one-line gloss, grouped into 語彙 / 文法 / 記事 and sorted あいうえお. Stdlib
only; reuses schema.py's frontmatter reader. It authors nothing — every field is
read from the pages — so it can be regenerated at will and never drifts.

    python wikitools/index.py [LLM_WIKI_ROOT] [OUT]
    # defaults: ./llm-wiki  ->  ./index.md
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wikitools import schema  # noqa: E402  (shared §6 schema primitives)

# frontmatter `type` -> (section heading), in output order
SECTIONS = (("vocabulary", "語彙"), ("grammar", "文法"), ("article", "記事"))
# `## 語彙` is sub-grouped by part-of-speech into these buckets, in order (§7.2)
POS_BUCKETS = (
    ("名詞", ("noun", "suru-verb")),
    ("動詞", ("godan-verb", "ichidan-verb")),
    ("形容詞", ("na-adjective", "i-adjective")),
    ("副詞", ("adverb",)),
    ("表現", ("expression",)),
)
EDIT_NOTE = "直接編集しないでください（`wikitools/index.py` が再生成します）"


# ---------------------------------------------------------------- extraction
def first_paragraph(text):
    """Join the first blank-line-delimited paragraph into one line.

    Japanese soft-wrap is joined with no separator, reconstructing a definition
    that the page wrapped across physical lines. '' if the section is empty.
    """
    out = []
    for ln in (text or "").split("\n"):
        if ln.strip() == "":
            if out:
                break          # end of the first paragraph
            continue           # skip leading blanks
        out.append(ln.strip())
    return "".join(out)


def first_sentence(text):
    """First sentence of the first paragraph, up to and including the first 。"""
    para = first_paragraph(text)
    head, sep, _ = para.partition("。")
    return head + sep if sep else para


def gloss_for(t, sections, fm):
    """One-line gloss per §7.2: 意味 first paragraph for vocab/grammar; メモ
    first sentence for articles, falling back to a （tag・tag）list."""
    if t in ("vocabulary", "grammar"):
        return first_paragraph(sections.get("意味", ""))
    memo = first_sentence(sections.get("メモ", ""))
    if memo:
        return memo
    tags = fm.get("tags") or []
    return "（" + "・".join(tags) + "）" if tags else ""


def reading_suffix(fm):
    """`（reading）` only when it adds information — same rule as the §6.5.1
    title line: shown for kanji headwords, omitted for kana / ～… headwords.
    A suru-verb appends 「・する」 inside the paren (§7.2)."""
    hw = fm.get("headword", "")
    rd = str(fm.get("reading", "") or "")
    suru = schema.suru_suffix(fm.get("part_of_speech"))
    if rd and rd != hw and schema.KANJI_RE.search(hw):
        return f"（{rd}{suru}）"
    return ""


def row(t, fm, sections):
    hw = fm.get("headword", "")
    surface = f"[[{hw}]]{schema.suru_suffix(fm.get('part_of_speech'))}"
    link = f"{surface}{reading_suffix(fm)}"
    g = gloss_for(t, sections, fm)
    return f"- {link} — {g}" if g else f"- {link}"


# ---------------------------------------------------------------- build
def collect(root):
    """Return ({type: [(sort_reading, headword, fm, sections)]}, dates, skipped)."""
    root = Path(root)
    items = {k: [] for k, _ in SECTIONS}
    dates, skipped = [], []
    for path in sorted(root.rglob("*.md")):
        fm, body = schema.parse_frontmatter(path.read_text(encoding="utf-8"))
        t = fm.get("type")
        if t not in items:
            skipped.append(path)              # non-schema / unknown type
            continue
        fm.setdefault("headword", path.stem)  # filename is the headword
        _, sections = schema.split_body(body)
        hw = fm["headword"]
        sort_key = str(fm.get("reading", "") or "") or hw   # articles: by headword
        items[t].append((sort_key, hw, fm, sections))
        for d in ("created", "updated"):
            if fm.get(d):
                dates.append(str(fm[d]))
    return items, dates, skipped


def render(items, dates):
    total = sum(len(v) for v in items.values())
    last = max(dates) if dates else "—"
    out = ["# LLM-wiki 索引（自動生成）", "",
           f"> {EDIT_NOTE}",
           f"> 収録 {total} 項目・最終更新 {last}"]

    # 語彙 — sub-grouped by part-of-speech (§7.2); empty buckets are omitted
    vocab = items["vocabulary"]
    out += ["", f"## 語彙（{len(vocab)} 項目）"]
    for label, poss in POS_BUCKETS:
        rows = sorted((e for e in vocab if e[2].get("part_of_speech") in poss),
                      key=lambda e: (e[0], e[1]))            # あいうえお, then headword
        if not rows:
            continue
        out += ["", f"### {label}（{len(rows)} 項目）", ""]
        out += [row("vocabulary", fm, sections) for _, _, fm, sections in rows]

    # 文法・記事 — flat
    for key, title in (("grammar", "文法"), ("article", "記事")):
        rows = sorted(items[key], key=lambda e: (e[0], e[1]))
        out += ["", f"## {title}（{len(rows)} 項目）", ""]
        out += [row(key, fm, sections) for _, _, fm, sections in rows]

    return "\n".join(out) + "\n"


def build_index(root):
    """Pure builder used by tests: return (markdown, items, skipped)."""
    items, dates, skipped = collect(root)
    return render(items, dates), items, skipped


# ---------------------------------------------------------------- driver
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    root = argv[0] if argv else "./llm-wiki"
    out = argv[1] if len(argv) > 1 else "./index.md"
    if not Path(root).is_dir():
        print(f"index: no such directory: {root}", file=sys.stderr)
        return 2
    text, items, skipped = build_index(root)
    Path(out).write_text(text, encoding="utf-8")
    print(f"index: wrote {out} — "
          f"{len(items['vocabulary'])} 語彙, {len(items['grammar'])} 文法, "
          f"{len(items['article'])} 記事"
          + (f" ({len(skipped)} skipped)" if skipped else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
