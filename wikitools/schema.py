#!/usr/bin/env python3
"""The LLM-wiki content schema, as code (specs.md §6).

Foundation module — the frontmatter parser, the body splitter, the schema's enum
sets, the shared regexes, and the title/display rules. Standard library only; it
depends on nothing else in the project.

It is imported by the linter (§7), the index generator (§7.2), and the
learning-aids generators (§10), so parsing/schema logic lives in exactly one
place and the dependency runs one way — schema ← everything (CLAUDE.md: modular
design, minimal coupling, unidirectional dependencies; specs §5 code layering).
"""

import re

# ---------------------------------------------------------------- schema vocab
LEVELS = frozenset({"N1", "N2", "N3", "N4", "N5"})
TYPES = frozenset({"vocabulary", "grammar", "article"})
POS = frozenset({
    "noun", "na-adjective", "i-adjective", "godan-verb", "ichidan-verb",
    "suru-verb", "adverb", "expression",
})
REGISTERS = frozenset({"formal", "neutral", "casual", "literary", "spoken"})

KANJI_RE = re.compile(r"[㐀-䶿一-鿿々]")
LINK_RE = re.compile(r"\[\[(.*?)\]\]", re.S)          # inner text (may span \n)


# ---------------------------------------------------------------- parsing
def parse_frontmatter(text):
    """Return (frontmatter_dict, body_str). dict is {} if no frontmatter.

    Hand-rolled — handles `key: value`, inline lists `[a, b]`, and block
    lists (`key:` then indented `- item` lines). No YAML engine.
    """
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not m:
        return {}, text
    block, body = m.group(1), m.group(2)
    data = {}
    cur_list_key = None
    for line in block.split("\n"):
        if not line.strip():
            continue
        if cur_list_key and re.match(r"\s*-\s+", line):
            data[cur_list_key].append(re.sub(r"^\s*-\s+", "", line).strip())
            continue
        cur_list_key = None
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val == "":
            data[key] = []            # possible block list; items follow
            cur_list_key = key
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [x.strip() for x in inner.split(",")] if inner else []
        else:
            data[key] = val
    return data, body


def split_body(body):
    """Return (first_nonempty_line, {section_title: text})."""
    lines = body.split("\n")
    first = next((l for l in lines if l.strip()), "")
    sections, cur, buf = {}, None, []
    for l in lines:
        if l.startswith("## "):
            if cur is not None:
                sections[cur] = "\n".join(buf)
            cur, buf = l[3:].strip(), []
        elif cur is not None:
            buf.append(l)
    if cur is not None:
        sections[cur] = "\n".join(buf)
    return first, sections


def link_target(inner):
    """`target|surface` -> target ; `x` -> x."""
    return inner.split("|", 1)[0].strip()


def strip_code(text):
    """Drop fenced and inline code spans so `[[…]]` shown as literal code
    (e.g. in メモ) is not mistaken for a real wikilink."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`]*`", "", text)


# ---------------------------------------------------------------- title / display
def suru_suffix(pos):
    """The 「・する」 display marker for サ変 (suru-verb) items; '' otherwise.
    Shared by the page title (§6.5.1), the index (§7.2), and the flashcards
    (§10.2)."""
    return "・する" if pos == "suru-verb" else ""


def expected_title(headword, reading, pos=None):
    """The `# title` line derived from the schema fields (§6.5.1)."""
    suru = suru_suffix(pos)
    if KANJI_RE.search(headword) and reading:
        return f"# {headword}{suru}（{reading}{suru}）"
    return f"# {headword}{suru}"
