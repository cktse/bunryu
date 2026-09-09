#!/usr/bin/env python3
"""Content linter for the LLM-wiki (specs.md §7).

A **consumer** of `wikitools.schema` (the §6 schema as code): a flat script of
small functions — one per rule — each returning a list of findings. Run
`lint-all` over the whole vault:

    python -m wikitools.lint          # lint the sibling llm-wiki/ tree
    python wikitools/lint.py [ROOT]   # or point at a specific llm-wiki/ dir

Exits non-zero if any ERROR is found (WARNINGs do not fail the run).
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # repo root on path
from wikitools.schema import (  # noqa: E402  — shared schema primitives
    LEVELS, TYPES, POS, REGISTERS, KANJI_RE, LINK_RE, FrontmatterError,
    parse_frontmatter, split_body, link_target, strip_code, expected_title,
)

# ---------------------------------------------------------------- lint constants
COMMON_REQUIRED = ("id", "type", "headword", "level", "created", "focus")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EXAMPLE_RE = re.compile(r"(?m)^\d+\.\s")
CANTO_RE = re.compile(r"(?m)^\s*-\s*（(?:粵|英)）")

ERROR, WARN = "E", "W"


# ---------------------------------------------------------------- rules
def check_frontmatter(fm):
    out = []
    for f in COMMON_REQUIRED:
        if not str(fm.get(f, "")).strip():
            out.append((ERROR, f"missing required field `{f}`"))

    t = fm.get("type")
    if t not in TYPES:
        out.append((ERROR, f"`type` {t!r} not in {sorted(TYPES)}"))
    if fm.get("level") not in LEVELS:
        out.append((ERROR, f"`level` {fm.get('level')!r} not in {sorted(LEVELS)}"))
    if str(fm.get("focus")).lower() not in ("true", "false"):
        out.append((ERROR, f"`focus` must be true/false, got {fm.get('focus')!r}"))
    for d in ("created", "updated"):
        if d in fm and fm[d] and not DATE_RE.match(str(fm[d])):
            out.append((ERROR, f"`{d}` not ISO YYYY-MM-DD: {fm[d]!r}"))

    if t in ("vocabulary", "grammar") and not str(fm.get("reading", "")).strip():
        out.append((ERROR, f"{t} missing required `reading`"))
    if t == "vocabulary":
        pos = fm.get("part_of_speech")
        if pos not in POS:
            out.append((ERROR, f"`part_of_speech` {pos!r} not in {sorted(POS)}"))
    elif t == "grammar":
        if not str(fm.get("formation", "")).strip():
            out.append((ERROR, "grammar missing required `formation`"))
    elif t == "article":
        if "word_count" in fm and not str(fm["word_count"]).isdigit():
            out.append((ERROR, f"`word_count` not an int: {fm['word_count']!r}"))

    # `reading` is furigana — kana only, never contains kanji (§6.1)
    rd = str(fm.get("reading", "") or "")
    if rd and KANJI_RE.search(rd):
        out.append((ERROR, f"`reading` must be kana, contains kanji: {rd!r}"))

    # suru-ness belongs in part_of_speech, not the headword (§6.2)
    hw = str(fm.get("headword", ""))
    if t == "vocabulary" and fm.get("part_of_speech") in ("noun", "suru-verb") \
            and hw.endswith("する"):
        out.append((ERROR,
                    f"`headword` must not end in する (suru-ness is part_of_speech): {hw!r}"))

    reg = fm.get("register")
    if reg is not None and reg not in REGISTERS:
        out.append((ERROR, f"`register` {reg!r} not in {sorted(REGISTERS)}"))
    return out


def check_title_line(fm, first_line):
    exp = expected_title(fm.get("headword", ""), fm.get("reading", ""),
                         fm.get("part_of_speech"))
    if first_line.strip() != exp:
        return [(ERROR, f"title line should be {exp!r}, got {first_line.strip()!r}")]
    return []


def check_vocab_grammar_body(sections):
    out = []
    if "意味" not in sections:
        out.append((ERROR, "missing `## 意味` section"))
    ex = sections.get("例文")
    if ex is None:
        out.append((ERROR, "missing `## 例文` section"))
        return out
    blocks = [b for b in re.split(r"(?m)^(?=\d+\.\s)", ex) if EXAMPLE_RE.match(b)]
    if len(blocks) < 2:
        out.append((ERROR, f"`## 例文` needs >=2 examples, found {len(blocks)}"))
    for i, b in enumerate(blocks, 1):
        if not CANTO_RE.search(b):
            out.append((ERROR, f"例文 #{i} missing a （粵）/（英）translation line"))
    return out


def check_article_body(sections, body, valid_targets):
    out = []
    if "本文" not in sections:
        out.append((ERROR, "missing `## 本文` section"))
    for inner in LINK_RE.findall(strip_code(body)):
        tgt = link_target(inner)
        if tgt not in valid_targets:
            out.append((WARN, f"unresolved wikilink [[{tgt}]]"))
    # `## 注目語彙・文法` lists what appears in `## 本文` (§6.5.2), so every entry
    # must be linked there — an unlinked one silently costs its item a cloze card
    # from its own source article (§10.2).
    honbun = {link_target(i)
              for i in LINK_RE.findall(strip_code(sections.get("本文", "")))}
    listed = {link_target(i)
              for i in LINK_RE.findall(strip_code(sections.get("注目語彙・文法", "")))}
    for tgt in sorted(listed - honbun):
        out.append((ERROR, f"`## 注目語彙・文法` lists [[{tgt}]] but `## 本文` "
                           f"never links it"))
    return out


def check_split_links(text):
    return [(ERROR, f"wikilink split across a line break: [[{inner[:20]}…]]")
            for inner in LINK_RE.findall(strip_code(text)) if "\n" in inner]


# ---------------------------------------------------------------- driver
def lint_file(path, valid_targets):
    print('linting', path)
    text = path.read_text(encoding="utf-8")
    try:
        fm, body = parse_frontmatter(text)
    except FrontmatterError as exc:
        return [(ERROR, f"malformed YAML frontmatter: {exc}")], {}
    findings = []
    if not fm:
        return [(ERROR, "no YAML frontmatter")], fm
    findings += check_frontmatter(fm)
    findings += check_split_links(text)
    first, sections = split_body(body)
    t = fm.get("type")
    if t in ("vocabulary", "grammar"):
        findings += check_title_line(fm, first)
        findings += check_vocab_grammar_body(sections)
    elif t == "article":
        findings += check_article_body(sections, body, valid_targets)
    return findings, fm


def lint_all(root):
    root = Path(root)
    if not root.is_dir():
        print(f"lint-all: no such directory: {root}", file=sys.stderr)
        return 2
    files = sorted(root.rglob("*.md"))
    valid_targets = {p.stem for p in files}     # headword == filename stem
    ids, id_where = {}, {}
    n_err = n_warn = 0
    for path in files:
        rel = path.relative_to(root.parent)
        findings, fm = lint_file(path, valid_targets)
        # id-uniqueness (collected here, reported on the duplicate)
        pid = fm.get("id")
        if pid:
            if pid in ids:
                findings.append((ERROR, f"duplicate id `{pid}` (also {id_where[pid]})"))
            else:
                ids[pid] = path
                id_where[pid] = rel
        for sev, msg in findings:
            print(f"{rel}: [{sev}] {msg}")
            if sev == ERROR:
                n_err += 1
            else:
                n_warn += 1
    print(f"\nlint-all: {len(files)} files, {n_err} error(s), {n_warn} warning(s)")
    return 1 if n_err else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv:
        root = argv[0]
    else:
        root = "./llm-wiki"
    return lint_all(root)


if __name__ == "__main__":
    sys.exit(main())
