# JLPT N1 Exam Prep Assistant — Specification

> Status: **Draft v0.3** · Last updated: 2026-07-08
> See [CLAUDE.md](bunryu/CLAUDE.md) for the high-level overview and ground rules.

## 1. Purpose

A personal assistant to prepare a single user for the **JLPT N1** exam. It
maintains an LLM-maintained wiki (the "LLM-wiki") of grammar, vocabulary, and
reading passages, tracks the user's progress, and (later) sends a daily quiz by
email. Everything is stored as human-readable markdown so the content database
doubles as an Obsidian vault.

## 2. Design Principles (from CLAUDE.md)

- **Keep it simple.** No database servers, no compiled languages, no premature
  abstraction. Files on disk are the database.
- **Reuse libraries.** Prefer well-maintained Python packages over custom code.
- **Python first**, with some JavaScript later only for display.
- **Markdown everywhere.** All docs, schema, and content are markdown so they
  stay human-editable and Obsidian-viewable.
- **Single user** to start; the design should not *prevent* multi-user later but
  must not pay for it now.

### 2.1 Language policy (important)

Because the user is studying at N1 level, explanations follow this priority so
that studying the notes is itself immersion practice:

1. **Japanese — primary.** Meanings, nuance notes, and explanations are written
   in Japanese by default (やさしい日本語で説明する).
2. **Cantonese — secondary.** Where a Japanese-only explanation risks ambiguity,
   add a Cantonese gloss (closer in heritage to Japanese than Western languages).
3. **English — last resort.** Fall back to English only when neither of the
   above conveys the point efficiently.

This policy applies to all generated/ingested content bodies (`## 意味`,
`## 例文` nuance notes, `## 関連`, etc.) and to quiz copy later. Section
**headings themselves are in Japanese** (see §6.5) to keep the vault consistent.

## 3. Scope

### In scope (current priority order)
1. Course content **schema** (this document, §6).
2. **Ingestion** of content into the LLM-wiki, via two paths:
   - **Manual article ingestion** — the `ingest article` workflow (§8), driven
     by Claude Code over hand-curated source articles in `raw/`.
   - **Web scraper** — automated seeding from an external N1 site (§9).
3. **Content linting** (§7).
4. **Progress tracker & scheduling** (§10.1).
5. **Learning aids** — deterministic vocabulary flashcards + CLI trainer (§10).

### Deferred (do not build yet)
- Daily email / quiz **generator** (§10.4).
- **AI-enriched ingest** for non-deterministic card material (§10.6).
- Any **GUI** / web dashboard (§10.6).

The learning-aids plan is detailed in §10 (near-term deterministic cards + a
future roadmap); the items listed as deferred above are not yet built. Per
CLAUDE.md, the schema and its initial seeding come first.

## 4. System Overview

```
 curated .md   ┌──────────────────────┐
 (raw/)        │  Article Ingestion   │  Claude Code reads the article, pulls
 ────────────▶ │  `ingest article`    │──┐  out [[marked]] vocab/grammar,
               └──────────────────────┘  │  writes/updates wiki pages
                                          │
 web / PDF     ┌──────────────────────┐  │
 ────────────▶ │      Scraper         │──┤  normalises external sources
               │      (Python)        │  │  into the schema
               └──────────────────────┘  │
                                          ▼
                              ┌─────────────────────┐
 manual edits ───────────────▶│  LLM-wiki           │  markdown files (Obsidian)
                              │  llm-wiki/...        │
                              └─────────┬───────────┘
                                        │ read
                              ┌─────────▼───────────┐
                              │  Progress Tracker   │  progress/progress.json
                              │  (Python)           │
                              └─────────┬───────────┘
                                        │ read
                              ┌─────────▼───────────┐
                              │ Quiz Generator      │  (DEFERRED)
                              │  + Email            │
                              └─────────────────────┘
```

## 5. Repository Layout

```
nihongo/
├── CLAUDE.md                 # project overview & rules
├── specs.md                  # this document
├── logs.md                   # append-only ingestion/change audit trail (§8.2 step 6)
├── raw/                      # HUMAN-CURATED source articles (input; never machine-written)
│   ├── 裁判員のもやもや.md
│   └── 読み取る.md
├── llm-wiki/                 # LLM-GENERATED content database (Obsidian vault root)
│   ├── grammar/              # one markdown file per grammar point
│   │   └── ～をものともせず.md
│   ├── vocabulary/           # one markdown file per vocabulary item
│   │   └── 改ざん.md
│   └── articles/             # one markdown file per ingested essay (named after title)
│       └── 裁判員のもやもや.md
├── progress/
│   └── progress.json         # per-user review state: stats + SM-2 schedule (§10.1)
├── cards.json                # generated flashcard build artifact (§10.3; rebuildable)
├── scraper/                  # Python package (linter + web scraper + ingest helpers)
│   ├── __init__.py
│   ├── lint.py               # stdlib-only content linter (§7)
│   ├── sources/              # one module per external web source
│   └── cli.py                # command-line entry point
├── study/                    # learning-aids code (§10): card gen + scheduler + trainer
│   ├── cards.py              # deterministic card generator → cards.json (§10.2–10.3)
│   ├── schedule.py           # SM-2 scheduler, swappable (§10.1)
│   └── cli.py                # CLI flashcard trainer (§10.4)
├── tests/                    # run_tests.py + test-llm-wiki/ fixture vault (§7.1)
└── requirements.txt
```

**`raw/` (human) vs `llm-wiki/` (LLM), kept as sibling top-level directories.**
The split makes provenance unmistakable: `raw/` holds the untouched source
articles a human curates (the essay plus any `[[...]]` markers and note
sections) and is **never machine-written**; `llm-wiki/` holds the
schema-conforming pages the assistant generates. Ingestion (§8) reads from
`raw/` and writes only under `llm-wiki/`. The `llm-wiki/` tree is the Obsidian
vault root.

**One concept per file.** Each grammar point or vocabulary item is its own
markdown file under `llm-wiki/`. The filename is the headword (e.g. `改ざん.md`,
`～をものともせず.md`). This makes content greppable, diff-friendly, and
navigable in Obsidian via `[[wikilinks]]`.

## 6. Content Schema

Each content file has two parts:

1. **YAML frontmatter** — structured, machine-readable metadata. Validated.
2. **Markdown body** — human-readable explanation, examples, notes (Japanese-first
   per §2.1).

Frontmatter is the source of truth for fields the tooling needs (id, type,
level, focus, tags). The body is for the learner.

### 6.1 Common frontmatter fields (all content types)

| Field        | Type            | Req | Description |
|--------------|-----------------|-----|-------------|
| `id`         | string          | ✓   | Stable unique id, kebab/slug or hash. Never changes once assigned. Used by progress tracker. |
| `type`       | enum            | ✓   | `vocabulary`, `grammar`, or `article`. |
| `headword`   | string          | ✓   | The term as displayed (kanji/kana for vocab; pattern for grammar; **essay title for article**). |
| `reading`    | string          | ·   | Kana reading (furigana). Required for vocab; optional for grammar; n/a for article. |
| `level`      | enum            | ✓   | JLPT level: `N1` `N2` `N3` `N4` `N5`. N1 prep may include lower levels. |
| `tags`       | list[string]    | ·   | Free-form tags (theme, source, part-of-speech, etc.). |
| `source`     | string          | ·   | Where it was ingested from (URL, source filename, or citation). Empty for manual entries. |
| `created`    | date            | ✓   | ISO date the file was added. |
| `updated`    | date            | ·   | ISO date last modified. |
| `focus`      | bool            | ✓   | `true` if marked for focused drilling. Default `false`. |

### 6.2 Vocabulary-specific frontmatter

| Field         | Type         | Req | Description |
|---------------|--------------|-----|-------------|
| `part_of_speech` | enum      | ✓   | e.g. `noun`, `na-adjective`, `i-adjective`, `godan-verb`, `ichidan-verb`, `suru-verb`, `adverb`, `expression`. |
| `accent`      | string       | ·   | Pitch-accent notation if available. |

### 6.3 Grammar-specific frontmatter

| Field         | Type         | Req | Description |
|---------------|--------------|-----|-------------|
| `formation`   | string       | ✓   | How it attaches (e.g. `名詞 + をものともせず`, `動詞ます形 + っぱなし`). |
| `register`    | enum         | ·   | `formal`, `neutral`, `casual`, `literary`, `spoken`. |

### 6.4 Article-specific frontmatter

An **article** is an example essay that contains vocabulary and grammar of
interest *in natural context*. It is the project's preferred source of "examples
in use": rather than isolated sentences, a vocab/grammar item can point to an
article where it appears. One article per markdown file, **named after the essay
title** (e.g. `llm-wiki/articles/裁判員のもやもや.md`).

| Field        | Type          | Req | Description |
|--------------|---------------|-----|-------------|
| `word_count` | int           | ·   | Approximate length of the Japanese body. Helps the quiz generator pick suitably-sized reading passages. |

Notes:
- The `level` field denotes the overall reading difficulty of the essay.
- `headword` holds the **essay title, taken from the source article's top `##`
  heading** (with any `[[...]]` markup stripped). The article page filename is
  this same title: `llm-wiki/articles/{title}.md`.
- **The essay title may differ from the raw source filename.** The `##` heading
  is authoritative for the headword/filename; the raw filename is recorded only
  in `source`. E.g. `raw/読み取る.md` whose heading is `## 記事の裏側`
  produces `llm-wiki/articles/記事の裏側.md` with `headword: 記事の裏側`.
- An article carries no `## 意味`/`## 例文` sections; it uses the article body
  layout in §6.5.2.

### 6.5 Markdown body structure

The body uses a fixed set of `##` headings — **in Japanese** — so it is both
human-readable and parseable by a simple heading-split. Headings appear in the
order shown; omit a section only when genuinely empty (the parser tolerates
missing optional sections). Content inside follows the language policy (§2.1):
Japanese first, Cantonese if needed, English last.

**One absolute line-break rule (all pages):** a `[[wikilink]]` — including the
aliased form `[[target|surface]]` — must never be split across a line break; it
stays wholly on one line, or Obsidian won't recognise it. This holds everywhere
(body, `## 関連`, `## 例文`, article `## 本文`). How article bodies are otherwise
wrapped is detailed in §6.5.2.

#### 6.5.1 Vocabulary & grammar body

The body opens with a single **level-1 title line** (`# …`), then the fixed
`##` sections. The title is derived from the frontmatter:

- If `headword` **contains any kanji**, the title is **`# headword（reading）`**
  — the reading in full-width parentheses, e.g. `# 改ざん（かいざん）`,
  `# 必ずしも～ない（かならずしも～ない）`.
- If `headword` **contains no kanji** (pure kana / a `～…` pattern), the title is
  just **`# headword`** — no parenthetical reading, since it would merely repeat
  the headword, e.g. `# やがて`, `# ～をものともせず`.

**例文 sub-lines (per §2.1).** Each example sentence carries, in this order:
1. **(primary)** the Japanese note on nuance / usage;
2. **(secondary)** a translation of the sentence's meaning — **Cantonese by
   default, prefixed `（粵）`**; fall back to **English, prefixed `（英）`**, only
   when a Cantonese rendering isn't feasible.

The Japanese sentence and its Japanese nuance note remain the primary text; the
`（粵）`/`（英）` line is a secondary comprehension aid placed beneath them.

```markdown
# 改ざん（かいざん）

## 意味
日本語による簡潔な定義・説明。必要なら広東語の補足、最後の手段として英語。

## 例文
1. 日本語の例文。
   - ニュアンスや使い方の注（日本語）。
   - （粵）例文の意味の広東語訳（難しければ（英）で代替）。
2. …
（CLAUDE.md により、例文は2つ以上。各例文に意味の（粵）訳〔なければ（英）〕を付す。）

## 関連
似た表現・対比する表現を [[ウィキリンク]] で結ぶ。
- [[～をよそに]] — 「Xを無視して」に近いが、より中立的。

## 間違いやすい点
- ✗ 誤った使い方 — なぜ誤りか / ✓ 正しい形。
（任意。該当なければ省略。）

## メモ
語源・覚え方・その他の補足。（任意。）
```

#### 6.5.2 Article body

**Re-flow the `## 本文` line breaks on ingest — do not copy the raw source's
wrapping.** The line breaks in `raw/` are an artifact of how the source was typed
or OCR'd and are often mid-word or uneven. When generating the article body,
re-wrap the Japanese text so that:

1. **Even, readable line length.** Lines are of similar, moderate width (aim for
   roughly 40–50 full-width characters of *rendered* text — `[[a|b]]` counts as
   its displayed surface `b`, not the markup), not a mix of very long and very
   short lines.
2. **Break at word / phrase boundaries — not only at punctuation.** Unlike
   English, Japanese has no spaces delimiting words, so choosing a break point
   requires a basic understanding of Japanese vocabulary and grammar to find a
   word boundary. Punctuation (。、！？) is *one* good place to break, but you
   should also break **between words within a sentence** whenever it gives more
   even lines — e.g. after a particle (が・を・に・は・で・と…) or after a clause
   ending (だろうか・など・ている…). Example: in
   `…[[仕事ぶり]]が[[目に余って]]叱られるのだろうかと[[どきどき]]している`, a break
   after `が`, after `だろうか`, or after `と` is all fine.
   - **It is fine to break in the middle of a word occasionally**, only when a
     line would otherwise become too long and no nearby boundary is available.
     Prefer a word boundary; a mid-word break is a last resort, not the norm.
   - **The one inviolable rule: never break inside a `[[wikilink]]`.** A wikilink
     (including `[[target|surface]]`) must stay wholly on one line (§6.5).
3. **Preserve paragraph breaks.** Blank-line paragraph breaks present in the raw
   source are meaningful and are kept: one blank line between paragraphs, matching
   the source's paragraph structure.

```markdown
## 本文
日本語の本文。複数段落の読み物（＝読解パッセージ）。

## 語釈
本文中の難語・表現の簡単な注釈（日本語中心）。（任意だが推奨。）

## 注目語彙・文法
本文に登場する学習項目を、ウィキリンクで結ぶ（これが唯一の相互参照。frontmatter の
`references` は持たない）。
- [[改ざん]] — 第1段落に登場。
- [[～をものともせず]] — 第2段落に登場。

## メモ
出典・テーマ・読解のポイント。（任意。）
```

### 6.6 Example content file — grammar

```markdown
---
id: grammar-wo-monotomosezu
type: grammar
headword: ～をものともせず
reading: ～をものともせず
level: N1
formation: 名詞 + をものともせず(に)
register: literary
tags: [perseverance, written]
source: https://example.com/n1/wo-monotomosezu
created: 2026-07-06
focus: false
---

# ～をものともせず

## 意味
困難や障害に立ち向かい、それに負けずに物事を成し遂げるさま。「～に負けないで」
の意で、逆境に立ち向かう人を称賛して使う。（粵：唔畏艱難、迎難而上。）

## 例文
1. 彼は大けがをものともせず、試合に出場した。
   - 大きな怪我にひるむことなく試合に出た、という称賛のニュアンス。
   - （粵）佢唔理會嚴重嘅傷勢，照樣落場比賽。
2. 悪天候をものともせず、登山隊は頂上を目指した。
   - 悪天候を苦にせず前進した様子を表す。
   - （粵）就算天氣咁惡劣，登山隊都繼續向山頂進發。

## 関連
- [[～をよそに]] — 「Xを無視して」。より中立・無関心のニュアンス。
- [[～にもかかわらず]] — 「Xにもかかわらず」。硬さがなく register 中立。

## 間違いやすい点
- ✗ 病気をものともせずに休んだ。— 「克服」ではなく「屈する」内容なので不自然。
  ✓ 病気をものともせず働き続けた。

## メモ
主語はふつう立派な意志を示す人物。自分自身にはあまり使わない。
```

### 6.7 Example content file — vocabulary

```markdown
---
id: vocab-kaizan
type: vocabulary
headword: 改ざん
reading: かいざん
level: N1
part_of_speech: suru-verb
tags: [crime, media, formal]
source: https://example.com/n1/kaizan
created: 2026-07-06
focus: false
---

# 改ざん（かいざん）

## 意味
文書・データ・記録などを不正に書き換えること。（粵：竄改、篡改。
English: falsification / tampering.）

## 例文
1. データの改ざんが発覚し、会社は信用を失った。
   - 不正な書き換えが明るみに出た、という文脈。
   - （粵）數據被篡改嘅事曝光，公司失去咗信譽。
2. 文書を改ざんした疑いで逮捕された。
   - 「～した疑いで」とセットでニュース文によく現れる。
   - （粵）佢因涉嫌篡改文件而被捕。

## 関連
- [[捏造]]（ねつぞう）— 何もないところから作り上げる（既存の改変とは違う）。
- [[偽造]]（ぎぞう）— 通貨・文書などの偽物を作ること。

## 間違いやすい点
- 「竄」は常用漢字外のため、ふつう「改ざん」と交ぜ書きする。

## メモ
強い否定的ニュアンス。ひそかに・不正に手を加える含み。
```

### 6.8 Example content file — article

File: `llm-wiki/articles/裁判員のもやもや.md`

```markdown
---
id: article-saibanin-moyamoya
type: article
headword: 裁判員のもやもや
level: N1
word_count: 620
tags: [reading, society, law]
source: raw/裁判員のもやもや.md
created: 2026-07-06
focus: false
---

## 本文
「裁判員制度」の導入が決まり、いったい裁判員とはどんな人が選ばれるのか…
…（本文が続く）…

## 語釈
- 眉を曇らせる — 不安や不快で表情が暗くなる。

## 注目語彙・文法
- [[裁判員]] — 第1段落に登場。
- [[～をものともせず]] — 第2段落に登場。

## メモ
テーマ：司法参加と市民感覚。読解と両項目の文脈復習に好適。
```

## 7. Content Linting

A single module `scraper/lint.py` checks that every page conforms to §6. The
schema is tiny, so **use the Python standard library only** — no third-party
packages (no `python-frontmatter`, `PyYAML`, or `pydantic`). `pathlib` + `re` +
plain `if`s are enough; a ~30-line hand-rolled frontmatter reader replaces a YAML
engine.

- **Frontmatter parse (stdlib).** Split the file on its first two `---` fences,
  then read the block line by line: `key: value` pairs, block lists (`key:`
  followed by indented `- item` lines), and inline lists (`tags: [a, b]`) into
  plain `dict`/`list`. That covers every field the schema uses — no YAML library
  needed.
- **Checks (plain `if` / `re`, no framework):**
  - All required common fields present and non-empty; `focus` parses as a bool,
    `created`/`updated` match `\d{4}-\d{2}-\d{2}`, `word_count` an int.
  - `type`-specific required fields present (vocabulary → `part_of_speech`;
    grammar → `formation`).
  - Enum fields (`level`, `type`, `part_of_speech`, `register`) fall in
    module-level allowed sets (`frozenset` constants).
  - `id` unique across the whole `llm-wiki/` tree.
  - First body line is the `# title` per §6.5.1 (vocab/grammar).
  - **vocabulary/grammar:** body has a `## 意味` and a `## 例文` with ≥2 numbered
    examples, each example carrying a `（粵）`/`（英）` line (§6.5.1).
  - **article:** body has a `## 本文`; every `[[wikilink]]` in the body /
    `## 注目語彙・文法` resolves to an existing page (unresolved = warning; §6.5).
  - No `[[wikilink]]` contains a line break, anywhere (§6.5) — a hard error.
- **CLI: `lint-all`** — walks `llm-wiki/` (the human-curated `raw/` tree is a
  sibling and is never linted), prints each finding as `path: message`, and exits
  non-zero if any error is found. Run as a pre-commit-style check and after every
  ingest/scrape.

Keep it a flat script of small functions (one per rule) returning a list of
messages; resist adding classes or a validation framework.

### 7.1 Tests for the linter

`lint.py` is the safety net for the whole vault, so it needs its own tests to
stay correct across changes. The approach is deliberately simple: **run `lint.py`
unchanged against a fixture vault** and check that its output matches what we
expect. No unit-test scaffolding, no monkeypatching — the linter is exercised
exactly as in production, just pointed at a different root.

- **Fixture vault: `tests/test-llm-wiki/`.** It mirrors the real vault's layout
  (`articles/`, `grammar/`, `vocabulary/` sub-folders) and is passed to the
  linter as `argv[0]`: `python scraper/lint.py tests/test-llm-wiki`.
- **One `.md` file per case.** Each fixture file is a single **positive** example
  (a valid page that must lint clean) or **negative** example (an otherwise-valid
  page that trips exactly one rule). Cover every §7 rule with **1–2 positive and
  1–2 negative** files: required fields; `focus` bool; date format; `word_count`
  int; type-specific fields; each enum; `id` uniqueness; `# title` line;
  `## 意味`/`## 例文` presence; ≥2 examples; `（粵）`/`（英）` line; article
  `## 本文`; wikilink resolution; split-wikilink; code-span exclusion.
  - Keep each negative file valid in every respect **except** the one rule under
    test, so exactly the expected finding fires.
  - `id`-uniqueness (a cross-file rule) needs a **pair** of fixtures sharing an
    `id`. Positive article fixtures must link only to other fixtures that exist
    in `tests/test-llm-wiki/`, or the resolution check will (correctly) warn.
- **Runner: `tests/run_tests.py`** (top-level, run from the repo root). It runs
  the linter over the fixture vault, captures the `path: [severity] message`
  output, and compares it against an **expected-results table** — a mapping of
  each fixture file to its expected finding (severity + a reason substring) or
  to “clean”. Assert the specific reason, not merely that *some* error occurred.
  The runner tallies and prints a **pass/fail count** summary and exits non-zero
  if any fixture's actual result differs from expected, so it can gate commits
  alongside `lint-all`.

`lint.py` itself stays untouched — the fixtures are the entire test surface, and
adding a new rule means adding a positive + negative fixture and one table entry.

## 8. Article Ingestion (`ingest article`)

The primary seeding path for hand-curated material. Driven by Claude Code from
the prompt **`ingest article <ARTICLE.MD>`**, where `<ARTICLE.MD>` lives under
`raw/`.

### 8.1 Source article format

A curated source file in `raw/`:
- The **bulk of the file is the Japanese article** to be added to the LLM-wiki.
- **Vocabulary and grammar of interest are marked inline with `[[...]]`**
  (e.g. `[[改ざん]]`, `[[～をものともせず]]`).
- The file **may contain linked note sections** below the article that give
  extra explanation for specific items; these inform the generated wiki pages.

### 8.2 Ingestion steps

1. **Read** the source markdown from the given path. The **essay title is the
   source's top `##` heading** (`[[...]]` markup stripped); it becomes the
   article `headword` and article filename (§6.4), which **may differ from the
   raw source filename**.
2. **Extract** every `[[...]]` marker as an item of interest. **Markers are
   type-agnostic** — a `[[...]]` may enclose either vocabulary or grammar.
3. For each marked item:
   - **Classify it as `vocabulary` or `grammar`** and determine its reading/POS
     (or `formation`/`register`). Judge by nature, not by any note-list heading:
     content words and set expressions → **vocabulary**; grammatical patterns /
     functional expressions (typically `～…` forms) → **grammar**. A marker may
     be grammar even when it appears only inline and not under a `新しい文法`
     section (e.g. `[[末に]]` → grammar `～末に`).
   - Use the **dictionary/base form** as the headword even when the inline usage
     is inflected (§8.3); link the surface form in the article body via an
     Obsidian alias, `[[dictionary-form|surface-form]]`.
   - **Create** a new page under `llm-wiki/{vocabulary|grammar}/{headword}.md`
     following the §6 schema, *or* **update** the existing page (matched by
     `id`/headword) — e.g. add this article to its examples/related links.
   - Populate the body Japanese-first per §2.1, using any linked note sections
     from the source for nuance.
4. **Create the article page** under `llm-wiki/articles/{title}.md` (title = the
   step-1 `##` heading):
   - `## 本文` = the Japanese article (with `[[...]]` markers preserved as
     wikilinks so Obsidian cross-links to the item pages), **re-wrapped per §6.5.2**
     (even line length, no breaks inside words/wikilinks, paragraph breaks kept).
   - `## 注目語彙・文法` list = the extracted items as wikilinks (no `references`
     frontmatter — the wikilinks are the sole cross-reference; §6.4).
   - `source` = the `raw/...` path.
5. **Lint** every created/updated file through §7 before finalizing.
6. **Add new log entry** to logs.md to audit trail changes made as part of this ingestion, include date, time, summary of the changes to each file (1-2 sentences per new/updated file) -- always add to the logs.md, never change existing log entries.
7. **Report** what was created vs. updated, and any items needing human review.

### 8.3 Rules

- **Idempotent.** Re-ingesting the same article updates existing pages rather
  than duplicating; never silently clobber hand-edited bodies without a `--force`
  equivalent (or an explicit heads-up when run interactively).
- **Preserve the source.** The `raw/` file is the human-owned input and
  is not modified by ingestion.
- **Use dictionary form.** Grammar/vocabulary pages created should be in dictionary form, even though actual usages linked from source articles may be in one of its variations.

## 9. Content Scraper (web seeding)

The scraper turns an external website into schema-conforming markdown files. It
complements the manual `ingest article` path for bulk seeding.

- **Pluggable sources.** Each source is a module under `scraper/sources/`
  exposing a common interface: yield normalized records → render to markdown via
  a shared template → write to `llm-wiki/{type}/{headword}.md`.
- **Idempotent.** Re-running a source updates existing files (matched by `id`)
  rather than duplicating. Manual edits to the body should be preserved where
  feasible; at minimum, never silently overwrite without a `--force` flag.
- **Polite.** Respect `robots.txt`, rate-limit requests, cache raw HTML locally
  during development to avoid re-hitting servers.
- **Linted.** Every generated file is run through §7 linting before being
  written.
- Likely libraries: `requests` + `beautifulsoup4` for HTML; `markdownify` to
  convert HTML fragments; `jinja2` for the markdown template.
- **Seeding source: TBD.** A candidate N1 grammar/vocab site will be selected
  (instructor role) and documented here before implementation. Selection
  criteria: comprehensive N1 coverage, example sentences, permissive terms of
  use / robots policy, stable HTML structure.

## 10. Learning Aids (Gamification)

The goal is to turn the LLM-wiki from a reference into **active-recall practice** —
flashcards, quizzes, a daily push — with light gamification to sustain a solo
learner. **Start with vocabulary**; grammar and article cards come later (§10.6).

Two design decisions are settled:

- **Card generation is 100% deterministic.** Cards are *derived* from existing
  note fields by plain code — no AI, no per-card authoring. The content page is
  the single source of truth; `cards.json` is a rebuildable build artifact, so it
  works automatically for every future ingest. (AI-authored, *non-deterministic*
  card material is a **future** enhancement captured **inside the note at ingest
  time**, which keeps generation deterministic — see §10.6.)
- **Cards and scheduling live in sidecar artifacts, never inside content pages.**
  This preserves the raw → llm-wiki → progress separation, keeps pages lint-clean
  and freely regeneratable, and avoids coupling to any one flashcard tool.

Principles: stdlib-first (a generator shaped like `lint.py`), markdown stays the
source of truth, reuse a simple well-known SRS algorithm.

### 10.1 Progress Tracker & scheduling

Per-user review state lives in `progress/progress.json`, keyed by content `id`:

```json
{
  "vocab-kaizan": {
    "presented": 3,
    "passed": 2,
    "failed": 1,
    "last_seen": "2026-07-08",
    "due": "2026-07-11",
    "interval": 3,
    "ease": 2.5,
    "reps": 2,
    "focus": false
  }
}
```

- Scheduling uses **SM-2** (simple, ~40 lines): `interval`/`ease`/`reps`/`due`
  update on each pass/fail. The scheduler is a small **swappable** module so
  **FSRS** can replace it later (§10.6) without touching callers.
- `focus` is mirrored from / written back to the content file frontmatter (the
  content file stays the source of truth for `focus`; `progress.json` for stats).
  Focus items form a priority / leech deck.
- Operations: build the **due queue**, record pass/fail, update the schedule,
  set/clear focus.
- MVP keys by content `id` (one schedule per word); per-card-type scheduling is a
  possible later refinement.

### 10.2 Card types (vocabulary, deterministic)

All four are derivable from existing fields **because the schema was designed for
it** — the `（粵）` line, `part_of_speech`, and the article `[[dict|surface]]`
convention each double as card metadata:

| Card | Prompt → answer | Derived from |
|---|---|---|
| **Reading** | headword (kanji) → reading | `headword` + `reading` (skip pure-kana headwords) |
| **粵→JP production** | Cantonese gloss → the Japanese word | the `（粵）` line in `## 意味` (heritage-language recall) |
| **Meaning (MC)** | word → its meaning, 4 choices | `## 意味` as the answer; distractors sampled by matching `part_of_speech` + nearby `level` |
| **Context cloze** | sentence with the word blanked → the word | article `## 本文`: blank a `[[dict\|surface]]` span — the alias gives both the exact span to hide **and** the answer (`dict-form`). Also `例文` where the surface equals the headword verbatim. |

### 10.3 Storage & data flow

```
llm-wiki/**                 (content — never modified)
   │   study/cards.py        (stdlib; deterministic)
   ▼
cards.json                  (build artifact: derived cards; delete & rebuild anytime)
   │   + progress/progress.json  (§10.1 scheduling/stats)
   ▼
delivery engine → CLI / email / …  (§10.4)
```

- `study/cards.py` walks `llm-wiki/` and emits `cards.json`; content pages are
  never touched.
- **Why not store cards inline via an Obsidian SR plugin** (considered and
  rejected for now): the popular *Spaced Repetition* plugin writes scheduling
  comments (`<!--SR:…-->`) into the notes and needs `::` / `==` markup inline.
  That would re-mix the raw/llm-wiki/progress layers, clutter the reflowed
  layout, cap card types at the plugin's model, and — given how often we
  regenerate the vault (renames, title lines, `（粵）` backfill, reflows) — risk
  **colliding with or wiping review history**. Since the content page already *is*
  the single source (cards are derived), inline storage buys little; Obsidian as a
  channel is instead a future *export* target (§10.6).

### 10.4 Delivery channels

- **MVP — CLI trainer** (stdlib): validates the card types and SRS with real
  reps; fastest feedback. Reads `cards.json` + `progress.json`.
- **Daily email / quiz** (next): the *same engine* selects due items (biased to
  `focus` + low pass-rate), renders a Japanese-first (§2.1) quiz email, and
  records results back to `progress.json`. Delivery mechanism TBD (SMTP / API);
  user email on file: cktse_jp@yahoo.co.jp.
- **Obsidian-SR / web** (future, §10.6).

### 10.5 Gamification mechanics (design intent)

- **Mastery ladder** per word: New → Seen → Reading-OK → Producing →
  Nuance-solid → 🏆 Mastered; harder card types unlock as the SM-2 interval grows.
- **Streaks + daily goal** (e.g. 10 reviews + 3 new); **XP** weighted by card
  difficulty (production / nuance > recognition).
- **Focus / leech deck** from the `focus` flag.
- **Thematic constellations**: the article-theme `tags` let a mastered set
  "light up" its source article — per-article progress bars and achievements that
  tie vocabulary back to reading.
- **Weekly boss / reading-boss** quiz: re-read the source article, cloze-quizzed
  in situ.

### 10.6 Future roadmap (not near-term)

Explicitly deferred:

- **AI-enriched ingest.** Extend `ingest article` (§8) to author *non-deterministic*
  card material **into the note** as structured fields — nuance-duel cards (which
  `関連` near-synonym fits a crafted sentence), higher-quality MC distractors,
  error-spot items from `間違いやすい点`. The AI value is captured once, at ingest,
  and stored in the page; **card generation stays 100% deterministic**.
- **Grammar & article card types** (vocabulary first).
- **FSRS** scheduler swap (§10.1).
- **Obsidian-SR export**: generate a separate `review/` folder from `cards.json`
  using the *SR-Recall* fork (scheduling kept in its own JSON), so Obsidian
  becomes a channel **without** touching content pages.
- **Web dashboard** with the constellation view; **audio / TTS** listening cards
  (see the audio open question, §11).
- **Any GUI** remains deferred.

## 11. Open Questions

1. Which external site(s) to scrape for seeding? (instructor role to research) <- postponed
2. `id` scheme — human-readable slug vs. opaque hash? (draft uses readable slug) <- prefer human-readable slug instead of opaque hash which can be excessively long and hence ugly
3. How aggressively should re-ingestion/re-scraping preserve hand-edited body text? <- should flag if a llm-wiki note was manually edited before overwriting content -- this should be rare as llm-wiki is owned by AI, e.g. manual correction of typos in cantonese which is AI's weaker languages
4. Pitch-accent and audio: in scope for N1 prep, or out? <- in scope for N1 prep, deferred to later implementation phase for now
5. When a `[[marked]]` item is ambiguous (vocab vs. grammar, or reading unknown),
   should ingestion guess and flag, or pause for human confirmation? <- evaluate to the best of AI's knowledge and flag (suggest to leave decision as footnote for future reference)
6. `cards.json` — committed (diffable, portable) or gitignored (pure build
   artifact)? Draft treats it as rebuildable, leaning gitignored <- gitignored for now
7. Scheduling granularity — one schedule per word, or per (word, card-type)?
   Draft starts per-word (§10.1). <- per word for now

## 12. Next Steps

**Done so far:** schema (§6); `lint.py` + `lint-all` + fixture tests (§7, §7.1);
the `ingest article` workflow (§8) with 5 articles seeded; the learning-aids plan
(§10).

**Near-term — learning aids, vocabulary-first (§10):**
1. `study/cards.py` — deterministic card generator → `cards.json` (§10.2–10.3).
2. `study/schedule.py` — SM-2 scheduler over `progress/progress.json` (§10.1).
3. `study/cli.py` — CLI flashcard trainer to validate the card types with real
   reps (§10.4).

**After that:**
4. Daily email / quiz on the same engine (§10.4).
5. Select and document the web seeding source (§9); implement the first source.
6. Roadmap items (§10.6): AI-enriched ingest, Obsidian-SR export, FSRS, grammar
   cards, web dashboard.
