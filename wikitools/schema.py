#!/usr/bin/env python3
"""The LLM-wiki content schema, as code (specs.md §6).

Foundation module — the frontmatter parser, the body splitter, the schema's enum
sets, the shared regexes, and the title/display rules. Depends on nothing else in
the project; its one third-party dependency is `yaml12` (YAML 1.2), which parses
the `---` block.

It is imported by the linter (§7), the index generator (§7.2), and the
learning-aids generators (§10), so parsing/schema logic lives in exactly one
place and the dependency runs one way — schema ← everything (CLAUDE.md: modular
design, minimal coupling, unidirectional dependencies; specs §5 code layering).
"""

import re

import yaml12

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
class FrontmatterError(ValueError):
    """A page has a `---` block, but it is not valid YAML (reported by §7 lint)."""


def parse_frontmatter(text):
    """Return (frontmatter_dict, body_str). dict is {} if no frontmatter.

    The `---` block is parsed as **YAML 1.2** (`yaml12`), so values keep their
    natural types: `focus: false` -> bool, `word_count: 620` -> int,
    `tags: [a, b]` -> list[str]. Dates stay strings (YAML 1.2 has no timestamp
    type), which is what the §7 `YYYY-MM-DD` check expects.
    """
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not m:
        return {}, text
    try:
        data = yaml12.parse_yaml(m.group(1))
    except Exception as exc:                      # malformed YAML — caller reports
        raise FrontmatterError(str(exc)) from exc
    if data is None:                              # empty block
        return {}, m.group(2)
    if not isinstance(data, dict):
        raise FrontmatterError("frontmatter block is not a mapping")
    return data, m.group(2)


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
