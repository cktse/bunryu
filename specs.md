# JLPT N1 Exam Prep Assistant — Specification

> Status: **Draft v0.8** · Last updated: 2026-09-05
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
- **Data minimization.** Keep a clean data lineage: store keys and look up the
  authoritative source rather than duplicating data. (Drives keeping `cards.json`
  minimal and looking the reveal up from the pages, §10.8.4.)
- **Test-driven.** Cover positive *and* negative cases; a curated fixture set
  generates a baseline to compare against (§7.1, §10.7).
- **No hardcoding; no secrets in source.** Prefer CLI args with sensible defaults;
  credentials live outside the tree in a gitignored file (§10.8.5).
- **Flag technical debt.** Trade-offs — especially backward-compatibility hacks —
  are surfaced for deliberate review, not absorbed silently.

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
5. **Learning aids** — deterministic vocabulary & grammar flashcards reviewed via
   the Obsidian SR plugin (FSRS, §10.4), plus a self-grading **daily quiz email**
   (Phase 1, §10.8).

### Deferred (do not build yet)
- **Progress-persisted quizzing / CLI trainer** over `progress.json` (§10.1,
  §10.6). The Phase-1 quiz email is built and *self-graded*; saving results back
  (the answer-capture surface) is the deferred Phase 2 (§10.8.3).
- **AI-enriched ingest** for non-deterministic card material (§10.6).
- **Web scraper** for bulk seeding (§9) — pending source selection.
- Any **GUI** / web dashboard (§10.6).

The learning-aids plan is detailed in §10 (deterministic cards + a future
roadmap). Per CLAUDE.md, the schema and its initial seeding come first.

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
                              │  llm-wiki/...       │
                              └─────────┬───────────┘
                                        │ read
                              ┌─────────▼───────────┐
                              │  Progress Tracker   │  progress/progress.json
                              │  (Python)           │
                              └─────────┬───────────┘
                                        │ read
                              ┌─────────▼───────────┐
                              │ Quiz Generator      │  Phase 1 built (§10.8);
                              │  + Email            │  progress-persisted: deferred
                              └─────────────────────┘
```

*Note:* the diagram shows the end state. Today's Phase-1 quiz email (§10.8) reads
`cards.json` (derived from `llm-wiki/` by `study/cards.py`) and the pages
directly — **not** `progress.json`; progress-persisted quizzing closes that loop
in the deferred Phase 2 (§10.8.3).

## 5. Repository Layout

```
bunryu/
├── CLAUDE.md                 # project overview & rules
├── specs.md                  # this document
├── logs.md                   # append-only ingestion/change audit trail (§8.2)
├── index.md                  # GENERATED map-of-content: every page + reading + gloss, [[links]] (§7.2; regenerated, committed)
├── raw/                      # HUMAN-CURATED source articles (input; never machine-written)
│   ├── 裁判員のもやもや.md
│   └── 読み取る.md
├── llm-wiki/                 # LLM-GENERATED content database (§6)
│   ├── grammar/              # one markdown file per grammar point
│   │   └── ～をものともせず.md
│   ├── vocabulary/           # one markdown file per vocabulary item
│   │   └── 改ざん.md
│   └── articles/             # one markdown file per ingested essay (named after title)
│       └── 裁判員のもやもや.md
├── flashcards/               # generated Obsidian SR notes: card-{vocab,grammar}-NNNN.md + .card-index.json (§10.4; committed)
├── progress/
│   └── progress.json         # card-keyed exposure history + derived urgency (§10.1; committed, atomic writes)
├── build/                    # REGENERABLE artifacts (gitignored): cards.json + daily-quiz.html (§10.3)
├── wikitools/                # Python package: tooling that operates on llm-wiki content
│   ├── __init__.py
│   ├── schema.py             # FOUNDATION — §6 schema as code (parse/split, enums, KANJI_RE/LINK_RE, suru_suffix, expected_title)
│   ├── lint.py               # stdlib-only content linter — consumes schema (§7)
│   ├── index.py              # map-of-content generator → index.md — consumes schema (§7.2)
│   ├── sources/              # one module per external web source (§9)
│   └── cli.py                # command-line entry point
├── study/                    # learning-aids code (§10)
│   ├── regen.py             # unified idempotent regeneration of all derived artifacts (§10.3)
│   ├── cards.py              # deterministic card generator → build/cards.json (§10.2–10.3)
│   ├── obsidian_cards.py     # render cards → flashcards/ Obsidian SR notes (§10.4)
│   ├── cli.py                # card viewer (MVP); interactive trainer deferred (§10.4)
│   ├── email_quiz.py         # daily CSS-interactive quiz email over build/cards.json + pages (§10.8)
│   ├── scheduler.py          # exposure + urgency scoring + read-only FSRS scan → push selection (§10.1)
│   ├── secrets.template.json # dummy-value placeholder for secrets.json (§10.8.5; committed)
│   ├── secrets.json          # real credentials grouped by service, e.g. "smtp" (§10.8.5; gitignored)
│   ├── launchd/              # LaunchAgent plist template for the daily send (§10.8.8)
│   └── prototypes/           # throwaway email-quiz prototype (§10.8.7); not a build dependency
├── tests/                    # run_lint_tests.py + test-llm-wiki/ (§7.1);
│                             #   run_cards_tests.py + cards-wiki/ + cards-baseline.json (§10.7)
└── requirements.txt
```

**`raw/` (human) vs `llm-wiki/` (LLM), kept as sibling top-level directories.**
The split makes provenance unmistakable: `raw/` holds the untouched source
articles a human curates (the essay plus any `[[...]]` markers and note
sections) and is **never machine-written**; `llm-wiki/` holds the
schema-conforming pages the assistant generates. Ingestion (§8) reads from
`raw/` and writes only under `llm-wiki/`.

**The Obsidian vault root is `bunryu/` itself** (it holds `.obsidian/`), so both
`llm-wiki/` and the generated `flashcards/` are folders inside the one vault
(that is how the SR plugin reviews the flashcards). The top level is kept tidy
because Obsidian shows it in the sidebar.

**Data tiers (what belongs where).** The layout separates content by *how it is
produced and whether it is regenerable* — the axis that decides placement and
git-tracking:

- **Authored source** (committed): `raw/` (human), `llm-wiki/` (AI), `wikitools·study·
  tests/` (code), the docs, `secrets.template.json`.
- **Code-maintained state — precious, non-regenerable** (committed): `flashcards/`
  (FSRS review schedules) and `progress/progress.json` (exposure history). Losing
  these loses real history, so writes are careful (append-only §10.4; atomic §10.1).
- **Regenerable / local** (gitignored): `build/` (rebuildable `cards.json`,
  `daily-quiz.html`) and `study/secrets.json` (a local secret). `build/` may be
  deleted anytime and rebuilt by `study/cards.py` / `study/email_quiz.py`.
- **Regenerable but committed — a deliberate exception:** `index.md` (§7.2) is
  rebuilt from `llm-wiki/` by `index.py`, but **committed** rather than gitignored
  because its value is being browsable *in place* — in Obsidian and on GitHub — as
  a map-of-content. Regenerated on every ingest / scrape and **never
  hand-edited**, it cannot drift; committing it merely spares readers a build step
  (cf. the tracked `README.md → specs.md` symlink).

`study/cards.py` writes across two tiers — the disposable `build/cards.json`
*and*, via `obsidian_cards.py`/`scheduler.py`, the precious `flashcards/` and
`progress.json` — so "generated by code" alone does not decide tracking;
**regenerability does**, and it maps to gitignored-vs-committed, with `index.md`
above the sole exception.

**One concept per file.** Each grammar point or vocabulary item is its own
markdown file under `llm-wiki/`. The filename is the headword (e.g. `改ざん.md`,
`～をものともせず.md`). This makes content greppable, diff-friendly, and
navigable in Obsidian via `[[wikilinks]]`.

**Code layering.** The Python packages depend **one way only**:
`wikitools/` ← `study/` ← `tests/`. `wikitools/schema.py` is the shared foundation
(the §6 schema as code); `wikitools/{lint,index}` and every `study/` generator
import it, so parsing/schema logic lives in exactly one place and **the validator
is never a dependency of the generators**. Tests import main modules, never the
reverse — which is also why the linter, though test-adjacent, stays a mainline
tool (§7) rather than a `tests/` module. *(CLAUDE.md tenet: modular design —
logical modules, minimal coupling, unidirectional dependencies.)*

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
| `id`         | string          | ✓   | Stable unique id — a human-readable kebab/slug (not an opaque hash; §11). Never changes once assigned. Used by progress tracker. |
| `type`       | enum            | ✓   | `vocabulary`, `grammar`, or `article`. |
| `headword`   | string          | ✓   | The term as displayed (kanji/kana for vocab; pattern for grammar; **essay title for article**). |
| `reading`    | string          | ✓   | Kana reading (furigana). Required for vocab and grammar (kanji → kana, non-kanji kept as-is, e.g. `～を目前に` → `～をもくぜんに`); n/a for article. |
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
| `accent`      | string       | ·   | Pitch-accent notation if available. In scope for N1 (§11); may be captured now even though accent/audio drills are deferred (§10.6). |

**`noun` vs `suru-verb` (サ変).** A verbal noun that also takes する — a サ変名詞
such as 確保・汚染・解決 — is **`suru-verb`**; a noun that does *not* take する
(一時・側面・倫理・飢餓) is **`noun`**. This is a per-word judgment (Japanese
language instructor role): being 漢語 does not make a word サ変. The distinction
drives the「・する」 display marker (§6.5.1, §7.2). **Suru-ness lives only in
`part_of_speech`** — never fold する into the `headword`, which stays the plain
dictionary form (= filename = `[[wikilink]]` target): headword `左右`, not
`左右する`. A lint rule enforces this (§7).

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
(body, `## 関連`, `## 例文`, article `## 本文`); §6.5.2 covers how article bodies
are otherwise wrapped.

#### 6.5.1 Vocabulary & grammar body

The body opens with a single **level-1 title line** (`# …`), then the fixed
`##` sections. The title is derived from the frontmatter:

- If `headword` **contains any kanji**, the title is **`# headword（reading）`**
  — the reading in full-width parentheses, e.g. `# 側面（そくめん）`,
  `# 必ずしも～ない（かならずしも～ない）`.
- If `headword` **contains no kanji** (pure kana / a `～…` pattern), the title is
  just **`# headword`** — no parenthetical reading, since it would merely repeat
  the headword, e.g. `# やがて`, `# ～をものともせず`.
- **suru-verbs** (`part_of_speech: suru-verb`, §6.2) additionally carry a
  「・する」 marker: `・する` after the headword, and — when a reading is shown —
  `・する` at the end of the reading, e.g. `# 勉強・する（べんきょう・する）`,
  `# 確保・する（かくほ・する）`. A kana suru-verb (no reading shown) is just
  `# …・する`. Plain nouns take no marker (`# 一時（いちじ）`). The same rendering
  is reused verbatim in the index (§7.2) and in the flashcard word-display
  (§10.2), so a page's title, its index row, and its cards all match. Because
  `・する` is derived from `part_of_speech`, the linter's title check is POS-aware
  (§7).

**例文 sub-lines (per §2.1).** Each example sentence carries, in this order:
1. **(primary)** the Japanese note on nuance / usage;
2. **(secondary)** a translation of the sentence's meaning — **Cantonese by
   default, prefixed `（粵）`**; fall back to **English, prefixed `（英）`**, only
   when a Cantonese rendering isn't feasible.

The Japanese sentence and its Japanese nuance note remain the primary text; the
`（粵）`/`（英）` line is a secondary comprehension aid placed beneath them.

```markdown
# 側面（そくめん）

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
2. **Break at word / phrase boundaries — not only at punctuation.** Japanese has
   no spaces between words, so finding a break point takes a basic reading of the
   vocabulary and grammar. Punctuation (。、！？) is *one* good place; also break
   **between words within a sentence** whenever that evens out the lines — after a
   particle (が・を・に・は・で・と…) or a clause ending (だろうか・など・ている…).
   Example: in
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

(A `suru-verb`, so its title carries the 「・する」 marker per §6.5.1 — `改ざん`
is a サ変名詞, `改ざんする`.)

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

# 改ざん・する（かいざん・する）

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

## 7. Content Linting & Indexing

The §7 tooling builds on **`wikitools/schema.py`** — the §6 schema as code: the
stdlib frontmatter parser, the body splitter, the enum sets
(`LEVELS`/`TYPES`/`POS`/`REGISTERS`), the `KANJI_RE`/`LINK_RE` regexes, and the
title/display rules (`suru_suffix`, `expected_title`). The linter, the index
generator (§7.2), and the learning-aids generators (§10) all import it, so no
module re-implements parsing and the dependency runs one way (schema ←
everything; §5 code layering).

`wikitools/lint.py` **consumes** `schema.py` to check every page against §6. The
schema is tiny, so **use the standard library only** — no `python-frontmatter`,
`PyYAML`, or `pydantic`. `pathlib` + `re` + plain `if`s suffice; the ~30-line
hand-rolled frontmatter reader in `schema.py` replaces a YAML engine.

- **Frontmatter parse (stdlib, in `schema.py`).** Split the file on its first two `---` fences,
  then read the block line by line: `key: value` pairs, block lists (`key:`
  followed by indented `- item` lines), and inline lists (`tags: [a, b]`) into
  plain `dict`/`list`. That covers every field the schema uses — no YAML library
  needed.
- **Checks (plain `if` / `re`, no framework):**
  - All required common fields present and non-empty; `focus` parses as a bool,
    `created`/`updated` match `\d{4}-\d{2}-\d{2}`, `word_count` an int.
  - `type`-specific required fields present (vocabulary → `part_of_speech`;
    grammar → `formation`; **vocabulary & grammar → `reading`**).
  - **`reading` is kana only** — a `reading` that contains kanji is an error;
    furigana must spell the kanji out (e.g. `～を目前に` → `～をもくぜんに`, §6.1).
    This catches a `reading` mistakenly left as a copy of a kanji headword.
  - **`headword` does not end in する** for `part_of_speech` `noun`/`suru-verb` —
    suru-ness belongs in `part_of_speech`, not the headword (§6.2). Catches
    e.g. a headword `左右する` that should be `左右`. Scoped to noun/suru-verb so
    verb/expression headwords that legitimately contain する are unaffected.
  - Enum fields (`level`, `type`, `part_of_speech`, `register`) fall in
    module-level allowed sets (`frozenset` constants).
  - `id` unique across the whole `llm-wiki/` tree.
  - First body line is the `# title` per §6.5.1 (vocab/grammar) — the check is
    **POS-aware**: for a `suru-verb` the expected title carries the 「・する」
    marker (§6.5.1).
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

`lint.py` is the safety net for the whole vault, so it needs its own tests. The
approach: **run `lint.py` unchanged against a fixture vault** and compare its
output against expectations. No unit-test scaffolding, no monkeypatching — the
linter runs exactly as in production, just pointed at a different root.

- **Fixture vault: `tests/test-llm-wiki/`.** It mirrors the real vault's layout
  (`articles/`, `grammar/`, `vocabulary/` sub-folders) and is passed to the
  linter as `argv[0]`: `python wikitools/lint.py tests/test-llm-wiki`.
- **One `.md` file per case.** Each fixture file is a single **positive** example
  (a valid page that must lint clean) or **negative** example (an otherwise-valid
  page that trips exactly one rule). Cover every §7 rule with **1–2 positive and
  1–2 negative** files: required fields; `focus` bool; date format; `word_count`
  int; type-specific fields; `reading` required (vocab & grammar) + kana-only;
  `headword`-not-する (noun/suru-verb); each enum; `id` uniqueness; `# title` line
  (incl. the suru-verb 「・する」 title); `## 意味`/`## 例文` presence; ≥2
  examples; `（粵）`/`（英）` line; article `## 本文`; wikilink resolution;
  split-wikilink; code-span exclusion.
  - Keep each negative file valid in every respect **except** the one rule under
    test, so exactly the expected finding fires.
  - `id`-uniqueness (a cross-file rule) needs a **pair** of fixtures sharing an
    `id`. Positive article fixtures must link only to other fixtures that exist
    in `tests/test-llm-wiki/`, or the resolution check will (correctly) warn.
- **Runner: `tests/run_lint_tests.py`** (top-level, run from the repo root). Runs
  the linter over the fixture vault, captures the `path: [severity] message`
  output, and compares it against an **expected-results table** mapping each
  fixture to its expected finding (severity + a reason substring) or to “clean” —
  asserting the specific reason, not merely that *some* error fired. It prints a
  **pass/fail count** and exits non-zero on any mismatch, so it can gate commits
  alongside `lint-all`.

`lint.py` itself stays untouched — the fixtures are the entire test surface, and
adding a new rule means adding a positive + negative fixture and one table entry.

### 7.2 Content Index (`index.py`)

A companion stdlib scanner that turns the whole `llm-wiki/` tree into one
human-browsable **map-of-content**, `index.md`, at the repo root: every curated
item with its reading and a one-line gloss, each `[[wikilink]]`ed for drill-down
when memory fades. (It also gives the §8.4 coverage check a single digest to
eyeball for semantic near-duplicates — a bonus, not the rationale.) Like
`lint.py` it builds on `schema.py`, is **stdlib-only**, and **derives everything
from the pages** — it authors nothing, so it can be re-run at will and never
drifts.

- **Generated, never hand-maintained.** `index.md` is rebuilt from scratch on
  every run — standalone, after every ingest (§8.2), and after a scrape (§9). It
  is **committed** but **never hand-edited** (the regenerable-but-tracked
  exception in §5). Hence it cannot drift, and it always covers the *entire*
  vault, not just the latest ingest.
- **Reuses `schema.py`'s frontmatter reader** (shared with the linter) — no
  second parser.
- **Root placement is deliberate.** `index.md` sits beside `logs.md`, *outside*
  `llm-wiki/`, so the linter's `llm-wiki/` walk never tries to lint it (it is not
  a schema page).
- **Three sections, by `type`** — `## 語彙`, `## 文法`, `## 記事` — each headed
  with its item count. Splitting by type keeps it scannable and lets each section
  carry only the columns that apply (articles have no `reading` and no `## 意味`).
- **`## 語彙` is sub-grouped by part-of-speech** into `### 名詞`, `### 動詞`,
  `### 形容詞`, `### 副詞`, `### 表現` (each with its own count), to surface
  grammatical clusters — the confusable N1 adverbs together, the verbs together.
  This is a *grammatical* axis, orthogonal to the *semantic* `## 関連` graph on
  each page, so it complements rather than duplicates it. The `part_of_speech`
  → sub-heading map:
  - `noun` **and** `suru-verb` → **名詞** (suru-verbs stay with nouns, marked by
    the 「・する」 glyph below);
  - `godan-verb`, `ichidan-verb` → **動詞**;
  - `na-adjective`, `i-adjective` → **形容詞**;
  - `adverb` → **副詞**;  `expression` → **表現**.

  `## 文法` and `## 記事` stay **flat** — grammar's only groupable field
  (`register`) is too coarse, and its real similarity is functional (concession /
  emphasis / …), which lives in `## 関連`/tags (a future tag-taxonomy question,
  not POS).
- **Per row — every field read, never authored:**
  - **`[[headword]]`** — the drill-down wikilink (= the page filename);
  - **reading** in `（…）`, shown **only when it differs from the headword** — the
    same rule as the §6.5.1 title line (kana-only / `～…` headwords would merely
    repeat themselves, so the reading is omitted);
  - **`・する` marker for suru-verbs** (`part_of_speech: suru-verb`): `・する`
    after the `[[headword]]`, plus `・する` appended inside the reading paren when
    one is shown — e.g. `[[勉強]]・する（べんきょう・する）`,
    `[[確保]]・する（かくほ・する）`; a kana suru-verb shows `[[…]]・する` (no paren).
    Plain nouns get nothing (`[[一時]]（いちじ）`). Identical to the §6.5.1 title
    rendering, so a page's title and its index row agree; derived from
    `part_of_speech`, no data added;
  - **one-line gloss** — for vocab/grammar, the **first paragraph of `## 意味`**
    (up to the first blank line) **joined into a single line**. Joining is needed
    because that paragraph is usually soft-wrapped across two physical lines: it
    reconstructs the whole definition including the trailing `（粵：…）`, which a
    first-*line*-only rule would truncate mid-sentence. **Articles** have no 意味
    → use the **first sentence of `## メモ`** (up to the first `。`), falling back
    to a `（tag・tag）` list.
- **Deterministic order.** Within each 語彙 POS sub-group sorted by `reading`
  (あいうえお order); grammar by `reading`; articles by `headword`. A stable sort
  means unchanged input yields byte-identical output — clean git diffs, and safe
  to regenerate on every ingest.
- **Generated-file header.** The top of `index.md` is marked machine-written
  (「自動生成 — 編集しないでください」) with the generation date, so it is never
  mistaken for a hand-curated note.
- **CLI: `index.py [llm-wiki-root] [out]`** — defaults `llm-wiki/` → `index.md`
  (no hardcoding; §2).

**Tests (`tests/run_index_tests.py`).** The §7.1 fixture-vault approach reused:
run `index.py` over a small clean fixture vault and compare the emitted markdown
against a committed **golden `index.md` baseline**, asserting section order, the
語彙 POS sub-grouping (bucket order + per-bucket counts, noun+suru-verb merged),
the 「・する」 marker (suru-verb vs plain noun), per-type counts, the
reading-omission rule, gloss extraction (including the article `メモ` fallback),
and the あいうえお sort. Regenerating the baseline is the intended way to update
expectations when the format changes.

## 8. Article Ingestion (`ingest article`)

The primary seeding path for hand-curated material. Driven by Claude Code from
the prompt **`ingest article <ARTICLE.MD>`**, where `<ARTICLE.MD>` lives under
`raw/`.

Two prompts operate on a `raw/` article: the optional, read-only
**`analyze article`** (§8.4) suggests N1 items to mark, then **`ingest article`**
(§8.1–8.3) creates or updates the wiki pages.

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
     functional expressions (typically `～…` forms) → **grammar**. A marker may be
     grammar even when it appears only inline, not under a `新しい文法` section
     (e.g. `[[末に]]` → grammar `～末に`).
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
5. **Embedded quizzes.** Some sources carry quizzes as named code blocks
   (\`\`\`quiz), typically grouped under a `## 読解問題` heading. Copy the whole
   section **as-is** to the end of the new article page (the quizblock plug-in
   renders it).
6. **Lint** every created/updated file through §7 before finalizing.
7. **Regenerate derived artifacts** with **`regen.py`** (§10.3) — the single
   idempotent entry point that rebuilds `index.md`, `build/cards.json`, and
   `flashcards/` from the updated vault. Deterministic for index/cards and
   **schedule-preserving** for flashcards (§10.4), so it is safe on every ingest
   and needs no manual drift step; this mechanical refresh need not be itemized
   in the log.
8. **Append a log entry** to `logs.md` as the audit trail for this ingestion:
   date, time, and 1–2 sentences per new/updated file. Always append — never
   change existing entries.
9. **Report** what was created vs. updated, and any items needing human review.

### 8.3 Rules

- **Idempotent.** Re-ingesting the same article updates existing pages rather
  than duplicating.
- **Flag hand-edits before overwriting (git).** The vault is a git repo. Before
  overwriting an existing `llm-wiki/` page, ingest checks git for **uncommitted
  changes to that file**; if found, it **warns and asks to confirm** rather than
  clobbering — hand-edits are rare (llm-wiki is AI-owned; e.g. a manual Cantonese
  fix) and worth preserving. Only tracked files with local modifications trigger
  the prompt; new/untracked pages are created freely. The warning doubles as a
  reminder to commit before re-ingesting.
- **Preserve the source.** The `raw/` file is the human-owned input and
  is not modified by ingestion.
- **Record ambiguous classifications.** When a `[[marked]]` item's type or
  reading is ambiguous, classify to the best of current knowledge, flag it in the
  final report step (§8.2), and record the decision in `logs.md` as a durable
  footnote for future revision.
- **Use dictionary form.** Grammar/vocabulary pages created should be in dictionary form, even though actual usages linked from source articles may be in one of its variations.

### 8.4 Article Analysis (`analyze article`)

An **optional, read-only** step *before* ingestion, driven by Claude Code from
the prompt **`analyze article <ARTICLE.MD>`** (`<ARTICLE.MD>` under `raw/`). In
the role of an experienced Japanese-language instructor, it helps the user curate
N1-appropriate items — i.e. decide what to mark `[[...]]` before running
`ingest article`. It **modifies no file** (neither `raw/` nor `llm-wiki/`);
results go to the Claude Code conversation for manual review.

1. **Read** the source markdown (per §8.2 step-1) and analyze **only the main
   article body** — ignore the embedded `## 読解問題` quiz blocks and any note
   sections.
2. **Extract N1-scope items**, split into two tiers:
   - **Tier A** — frequently used, broadly applicable items: the recommended set.
   - **Tier B** — in N1 scope but more niche / lower-yield: a bounded optional
     overflow.
3. **Quality over quantity.** Exclude trivial / sub-N1 items. Rule of thumb for a
   ~600-word article (scale with length and density): **Tier A ≈ 5–10 vocabulary
   and 3–5 grammar**, plus **Tier B ≤ ~5 more** in total. The 5–10 / 3–5 budget
   is the Tier A headline — Tier B must not be used to exceed it.
4. **Per-item fields.** Report each suggested item with a fixed, actionable set:
   - **dictionary / base-form headword** (§8.3) — not the inflected surface;
   - **reading**;
   - **type** — vocabulary or grammar;
   - **one-line gloss — in Japanese** (§2.1), with a Cantonese rendering
     `（粵：…）` where it aids comprehension;
   - **location** in the article (paragraph / quoted phrase);
   - **tier** (A / B);
   - **coverage flag** — see step 5.
5. **Cross-check existing `llm-wiki/` coverage.** Resolve each item to its
   **dictionary / base form** and check whether a page already exists — matching
   on the base form, **not** the surface (e.g. 愚か**さ** → `愚か`,
   汚染**する** → `汚染`). Report coverage as one of:
   - **new headword** → the article widens coverage (breadth);
   - **existing headword** → ingest will *enhance* that page by adding this
     article as a fresh example / context (depth), per §8.2 step-3 — a positive,
     not a redundancy;
   - **near-duplicate / variant** of an existing page → recommend a **cross-link**
     rather than a new page (data-minimization tenet), e.g. `あまりに～すぎる`
     alongside an existing `あまりにも`.
6. **Reconcile with any pre-existing `[[...]]` markers.** If the source already
   carries markers (§8.2 step-2), report the **three-way diff** against the
   auto-identified set:
   - **both** (AI ∩ human) → high-confidence keep;
   - **AI-only** → suggested additions the curator may have missed;
   - **human-only** → items to double-check (possibly below N1 / niche).

   When the source has no markers yet (the common analyze-first case), this
   reduces to the plain suggestion list from steps 2–5.
7. **Overall evaluation & recommendation.** Assess the article's N1 suitability
   (writing style, register, difficulty, thematic value), then give an explicit
   **recommendation**: the proposed final set to mark, and a go / no-go on
   ingestion (weighing how much it adds vs. duplicates existing coverage).
8. **Report only — no writes, no log.** The analysis changes nothing, so — unlike
   ingest, whose §8.2 step 8 writes to `logs.md` — **nothing is logged**. §2.1's
   Japanese-first rule binds the per-item glosses (step 4); the surrounding report
   is meta scaffolding *about* study, not course content, so it is written in
   whatever language is clearest. Handoff: the user marks `[[...]]` in the source,
   then runs `ingest article` (§8.1–8.3).

## 9. Content Scraper (web seeding)

The scraper turns an external website into schema-conforming markdown files. It
complements the manual `ingest article` path for bulk seeding.

- **Pluggable sources.** Each source is a module under `wikitools/sources/`
  exposing a common interface: yield normalized records → render to markdown via
  a shared template → write to `llm-wiki/{type}/{headword}.md`.
- **Idempotent.** Re-running a source updates existing files (matched by `id`)
  rather than duplicating. Manual edits to the body should be preserved where
  feasible; at minimum, never silently overwrite without a `--force` flag.
- **Polite.** Respect `robots.txt`, rate-limit requests, cache raw HTML locally
  during development to avoid re-hitting servers.
- **Linted.** Every generated file is run through §7 linting before being
  written.
- **Derived artifacts regenerated.** After a scrape run, run **`regen.py`**
  (§10.3) — the same single regeneration path as ingest (§8.2 step 7), over the
  whole vault regardless of how its pages were created.
- Likely libraries: `requests` + `beautifulsoup4` for HTML; `markdownify` to
  convert HTML fragments; `jinja2` for the markdown template.
- **Seeding source: TBD.** A candidate N1 grammar/vocab site will be selected
  (instructor role) and documented here before implementation. Selection
  criteria: comprehensive N1 coverage, example sentences, permissive terms of
  use / robots policy, stable HTML structure.

## 10. Learning Aids (Gamification)

Turn the LLM-wiki from a reference into **active-recall practice** — flashcards,
quizzes, a daily push — with light gamification to sustain a solo learner.
Vocabulary came first, then the full-context grammar cards; **article card types
remain future** (§10.6).

Two settled decisions:

- **Card generation is 100% deterministic.** Cards are *derived* from existing
  note fields by plain code — no AI, no per-card authoring. The content page is
  the single source of truth and `cards.json` a rebuildable build artifact, so
  every future ingest is covered automatically. (AI-authored, *non-deterministic*
  card material is a **future** enhancement captured **inside the note at ingest
  time**, which keeps generation deterministic — §10.6.)
- **Cards live in a separate `flashcards/` folder, never inside content pages.**
  This preserves the raw → llm-wiki → progress separation and keeps content pages
  lint-clean and freely regeneratable. The **near-term review channel is the
  Obsidian *Spaced Repetition* plugin (FSRS)** over those notes (§10.4); a
  CLI/email channel over `progress.json` is deferred (§10.6).

Principles: stdlib-first (a generator shaped like `lint.py`), markdown stays the
source of truth, and reuse existing tools (the Obsidian SR plugin) rather than
build a scheduler now.

### 10.1 Progress tracking, urgency & scheduling

Two schedulers coexist by design; the guiding decision is **not to merge them but
to build one read-model over both, partitioning writes by owner** (§11.1):

- **Obsidian SR plugin owns FSRS** — the review schedule inside `flashcards/*.md`.
  We **read it, never write it** (§10.4).
- **We own *exposure*** — what was pushed to the learner and when, a concept
  Obsidian doesn't track; written by the delivery channels (the daily email today,
  §10.8).
- **`study/scheduler.py`** merges both into a per-card **urgency** score that the
  push pipeline ranks by. FSRS is read live and **never copied** into our store
  (*data-minimization*, §2).

**State file — `progress/progress.json`** (single, self-contained, committed —
precious, non-regenerable history), namespaced into **`cards`** (keyed by card
`id`) and **`articles`** (keyed by article title):

```json
{
  "cards": {
    "vocab-dandori::meaning": {
      "exposure": { "count": 3, "last": "2026-07-18", "channels": ["email"] },
      "urgency": 62,
      "urgency_at": "2026-07-20"
    }
  },
  "articles": {
    "そば屋の先生": { "last_served": "2026-07-18", "count": 4 }
  }
}
```

- **`exposure`** (raw history — we write on delivery): `count`, `last` (date),
  `channels`. For the email this is the *only* captured signal — the WebKit
  constraint means no pass/fail (§10.8.3).
- **`articles`** (raw history) records, per article, when it was last the email's
  subject (`last_served`) and how many times (`count`). Because a send features
  **exactly one** article, this is the authoritative rotation signal — a fact
  **not** reconstructable from card exposure alone (a card shared by two articles
  would blur a card-derived aggregate), so it is stored rather than derived.
- A channel calls `record_delivery(card_ids, article, date)` after a successful
  send; that write touches **only the delivered cards and that one article**.
- **`urgency`** (derived — batch-recomputed): a 0–100 score, materialised so the
  push path is a cheap top-N read. `urgency_at` is the compute date (staleness
  check); an optional `parts` breakdown may be emitted for tuning.
- **`review`** (deferred, SM-2): `presented`/`passed`/`failed`/`due`/`interval`/
  `ease`/`reps`, added only when a channel can *capture answers* (Phase 2,
  §10.8.3). Swappable; **FSRS** could replace it later (§10.6).

**Urgency model** — a linear combination of factors, each normalised to 0–1, with
configurable weights summing to 1, clamped to [1,100]:

```
urgency = clamp(100 · ( w_rec·f_rec + w_freq·f_freq + w_fsrs·f_fsrs + w_err·f_err ), 1, 100)
```

| Factor | 0→1 mapping | Intuition |
|---|---|---|
| `f_rec` recency | `min(days_since_last / HORIZON, 1)`; never-shown → 1.0 | longer unseen ⇒ more urgent |
| `f_freq` frequency | `1 − min(count / CAP, 1)` | under-shown ⇒ more urgent |
| `f_fsrs` (read-only) | blend of overdue-ness, `1−stability_norm`, `difficulty_norm`, `state`; **no FSRS record → configurable default** | Obsidian's view of fragility |
| `f_err` (future) | `failed / presented` | needs answer capture (Phase 2) — weight 0 today |

Weights live in a documented config dict (defaults e.g. `rec .4, freq .2, fsrs .4,
err 0`), tunable without code changes.

**FSRS read-model (read-only, not persisted), per card id** — parsed from the
inline `<!--SR:!fsrs,…-->` comments:

- Extracted: **`due`**, **`last_review`**, **`stability`**, **`difficulty`**,
  **`state`** (new / learning / review / relearning). Remaining positional fields
  are plugin-version-specific and treated as opaque; a parse failure means "no FSRS
  data" — the card falls back to the `f_fsrs` default (degrade gracefully).
- **Join:** `flashcards/.card-index.json` maps `item_id → NNNN`; within a note the
  card blocks are aligned to card ids by **reusing `obsidian_cards.py`'s renderer**
  (match by front text, not fragile block position).

> **Forward-compat — review-state adapters (not built yet).** The read-model above
> is currently Obsidian-specific. Treat it as *one adapter* behind a small seam —
> `ReviewAdapter.read(card_id) -> ReviewState | None` — so a future channel that
> owns its own scheduler (e.g. **Anki**, §10.6) can add its own adapter (reading
> `collection.anki2` when local; contributing nothing when the collection is
> remote/mobile). When more than one adapter reports a card, `f_fsrs` merges them
> under an explicit policy (e.g. most-recently-reviewed wins, or min-stability =
> most-fragile). Naming the seam now keeps that channel a drop-in rather than a
> refactor (*flag-tech-debt*, §2); the delivery side already scales, each channel
> being just another renderer over `cards.json` with `exposure.channels` logging.

**Idempotent batch recompute.** `scheduler.recompute` is a pure function of
`(exposure, fsrs_snapshot, weights, today)`: re-running the same day yields
identical scores; re-running after an Obsidian review picks up the new FSRS, still
deterministically. It rewrites every card's `urgency` (recency drifts daily for
all cards, not only delivered ones).

**Atomic, validated writes.** Because a batch recompute rewrites the whole
committed file, every save goes **temp-file → sanity-check → `os.replace`**: write
a sibling temp file, re-load and validate it (parseable JSON; the `cards`/`articles`
namespaces intact; every pre-existing card id and article still present; no entry
silently loses its `exposure` / `last_served` history; scores in [1,100]), and only
then atomically rename over `progress.json`. A failed check aborts, leaving the
original untouched. Covered by dedicated tests (§10.9).

**Selection / push.** The push pipeline runs `recompute`, picks the
**least-recently-served article** (oldest `articles[A].last_served`; never-served
articles first), then takes **top-N by `urgency`** within it. Ties broken by
`focus` → `level` → `id` for determinism. `focus` is looked up from frontmatter,
not stored per card.

Operations: `recompute` urgency, `record_delivery`, build the push queue,
(deferred) record review pass/fail, set/clear focus.

### 10.2 Card types (deterministic)

Cards are derived from existing fields — no AI. The schema doubles as card
metadata: the `（粵）` line, `part_of_speech`, the article `[[dict|surface]]`
convention, `## 関連`, and `## 間違いやすい点` each feed a card type.

**Vocabulary** (implemented):

| Card | Prompt → answer | Derived from |
|---|---|---|
| **Reading** | headword (kanji) → reading | `headword` + `reading` (skip pure-kana headwords) |
| **粵→JP production** | Cantonese gloss → the Japanese word | the `（粵）` line in `## 意味` (heritage-language recall) |
| **Meaning (MC)** | word → its meaning, 4 choices | `## 意味` as the answer; distractors sampled by matching `part_of_speech` + nearby `level` |
| **Context cloze** | sentence with the word blanked → the word | article `## 本文`: blank a `[[dict\|surface]]` span — the alias gives both the exact span to hide **and** the answer (`dict-form`). Also `例文` where the surface equals the headword verbatim. |

The **word display** — wherever the whole word is shown as prompt or answer: the
粵→JP answer, the Meaning-MC prompt, and cloze answers — reuses the shared
rendering of §6.5.1, so a card, the page title, and the index row all agree:
`改ざん・する（かいざん・する）` for a suru-verb, `改ざん（かいざん）` for a plain
kanji noun, `やがて` for kana. The **Reading** card is the deliberate exception:
its front stays the plain headword (`改ざん`), since it quizzes the kanji reading
itself and a 「・する」 there would make the expected answer ambiguous.

**Grammar** (implemented — full-context, JLPT-shaped; these three, in order gcloze/gmc/gerror):

| Card | Prompt → answer | Derived from |
|---|---|---|
| **Pattern MC (in context)** | a blanked sentence + 4 choices → the pattern | a `例文`/`本文` sentence with the pattern blanked; distractors from `## 関連` (near-synonym patterns) topped up by same-`level` patterns — mirrors the JLPT 文法 question |
| **Cloze (production)** | blanked sentence → produce the pattern | page `## 例文` (curated) and article `## 本文` (`[[pattern\|surface]]` = exact span) |
| **Error correction** | the ✗ sentence → the ✓ fix (+ why) | `## 間違いやすい点` ✗/✓ pairs |

Locating the pattern span to blank:

- **Article `## 本文`** — the `[[pattern|surface]]` alias gives the **exact span**
  (fully reliable, as for vocab cloze).
- **Page `## 例文`** — the pattern is plain text; find its contiguous **core**
  (headword minus `～`). Reliable for *contiguous* patterns (~32/38). For split /
  呼応 patterns (`必ずしも～ない`, `～とも～ともつかない`, `～といい～といい`,
  `到底～ない`, `～ことはあっても`, `～からといって～というものではない`) blank the
  distinctive fragment(s); where detection is unreliable, skip that pattern's
  `例文`-cloze (it still gets MC / error-correction where those apply).

Deferred grammar cards (§10.6): meaning-recognition, `formation` (attachment
rules), and reading (kanji-bearing patterns only). **No 粵→pattern card** —
grammar meanings are abstract and often shared, so producing the exact pattern
from a Cantonese gloss is ambiguous.

### 10.3 Storage & data flow

```
llm-wiki/**                 (content — never modified)
   │   study/cards.py        (stdlib; deterministic)
   ▼
build/cards.json            (build artifact: derived cards; rebuildable)
   │
   ├── study/obsidian_cards.py ─▶ flashcards/card-*.md   (Obsidian SR channel; §10.4)
   ├── study/email_quiz.py ─▶ daily quiz email (reveal looked up from pages; §10.8)
   └── (deferred) CLI trainer + progress-persisted quizzing over progress.json (§10.1, §10.6)
```

- `study/cards.py` walks `llm-wiki/` and emits `cards.json`; content pages are
  never touched.
- **Cards go into a separate `flashcards/` folder — not inline in content pages.**
  The Obsidian SR plugin reviews them there (§10.4). We deliberately do **not**
  embed cards/scheduling inline in `llm-wiki/` pages: that would re-mix the
  raw/llm-wiki/progress layers, clutter the reflowed layout, and — given how often
  we regenerate the vault (renames, title lines, `（粵）` backfill, reflows) — risk
  **wiping review history**. A separate folder gives Obsidian-as-a-channel while
  content stays clean and `lint-all` (which walks only `llm-wiki/`) ignores it.
- **`cards.json` is regenerated whenever the vault changes** — a step of ingest
  (§8.2 step 7) and scrape (§9), and again by the daily send before it reads the
  file (§10.8.8) — so the card bank never lags the pages. `email_quiz.py` **reads
  `build/cards.json` from disk and does not rebuild it**, so that freshness is
  what makes newly-ingested items appear in the quiz.

**Unified regeneration (`study/regen.py`).** All three derived artifacts are
rebuilt by **one idempotent entry point**, which ingest (§8.2), scrape (§9), the
daily send (§10.8.8), and ad-hoc runs all call — so there is a single
regeneration path. It runs `cards.py` (→ `build/cards.json`), `index.py` (→
`index.md`), and `obsidian_cards.py` (→ `flashcards/`) in dependency order.
`regen.py --only {cards,index,flashcards}` selects a subset (the daily send uses
`--only cards`).

- **No timestamps, no Make.** `cards.json` and `index.md` are deterministic
  (byte-identical on unchanged input — verified by their exact-match test
  baselines), so they are regenerated **unconditionally**: correct-by-construction,
  zero git churn, and none of the mtime-staleness hazards that an iCloud-synced
  vault (files evicted/re-materialised) and git checkouts (mtimes reset to "now")
  would introduce. Flashcards are made safe to regenerate unconditionally by the
  **schedule-preserving resync** (§10.4). §11 records why a Make/mtime dependency
  graph was rejected.
- **Incremental only if ever needed.** Should the vault grow large enough that
  full regeneration is slow (thousands of pages — not near), add a **content-hash
  manifest** (compare source hashes, stdlib, iCloud-safe) — never mtime. YAGNI
  for now.

### 10.4 Delivery channels

**Near-term — Obsidian Spaced Repetition (FSRS).** Cards are exported as separate
notes the mainstream Obsidian *Spaced Repetition* plugin reviews (FSRS enabled in
its settings). Design:

- `study/obsidian_cards.py` reads `cards.json` and writes **one note per item**
  into a top-level **`flashcards/`** folder — a sibling of `llm-wiki/` inside the
  same vault (`bunryu/` is the vault root). Content pages are never touched.
  Vocabulary → `card-vocab-{NNNN}.md`, deck `#flashcards/vocab/{level}`; grammar →
  `card-grammar-{NNNN}.md`, deck `#flashcards/grammar/{level}`. Same rules for
  both: answer-opaque filename, no heading/backlink, the `[[item]]` context link
  embedded in each card's answer, append-only generation.
- **Regenerated via `regen.py`, schedule-preserving.** Regeneration (§10.3)
  creates notes for new items **and resyncs drifted notes in place while carrying
  over their FSRS schedules** (below), so it is non-destructive and safe to run on
  every ingest/scrape — no `--check`-then-manual-`--force` dance.
- **Schedule-preserving resync.** The FSRS schedule lives inline as a
  `<!--SR:!fsrs,…-->` comment the plugin reads and writes in the note itself (the
  note *is* the database; there is no external store). On resync,
  `obsidian_cards.py` regenerates a note's card blocks but **re-attaches each
  existing schedule to its card**, matched by a **stable card id** (carried in a
  marker invisible to Obsidian). Policy:
  - card id **persists** → schedule carried over — correct for the common changes
    (display tweaks like 「・する」, reflows, reclassifications);
  - card **removed** (its block no longer generated) → its schedule is dropped,
    and the drop is **reported**;
  - card **added** → starts fresh (no schedule).

  Matching is by **id, not content**, so a *reworded* card keeps its review
  history by design. **`--force`** remains the explicit escape hatch to **reset**
  a note's schedules when a card has changed enough to count as new. (Build note:
  the id marker's non-interference with the SR plugin's own card-boundary parsing
  must be verified when implemented; until then, append-only creation +
  `--check`/manual `--force` is the interim behavior.)

For example, study/cli.py generates the following quizzes for the vocab 挟む:
```
bunryu % python ./study/cli.py --vocab vocab-hasamu
[canto  ] vocab-hasamu::canto  (N2)
  Q: この意味の言葉は何ですか？
     夾住、夾喺中間、插入
  A: 挟む（はさむ）

[cloze  ] vocab-hasamu::cloze::article-haru-no-ichinichi::2  (N2)
  Q: 空欄に入る語は？
     ドアの脇に立って、書類カバンを器用に両足で＿＿、書類に熱心に目を通している。
  A: 挟む（はさむ）   ［surface: 挟み］

[meaning] vocab-hasamu::meaning  (N2)
  Q: 意味は？
     挟む（はさむ）
       1. ある状態を変えずに維持し続ける
       2. 数量・程度が多くなる・強くなる
      ＊3. ①二つのものの間に物を入れて押さえる
       3. 感動・驚き・呆然などで、その場にずっと立ったまま動けないでいる
  A: ①二つのものの間に物を入れて押さえる

[reading] vocab-hasamu::reading  (N2)
  Q: 読みは？
     挟む
  A: はさむ

— shown 4 of 4 matching card(s)
```

These render into `flashcards/card-vocab-NNNN.md` in SR-plugin syntax below,
where `NNNN` is the sequence number assigned to that vocab. The filename must not
contain the word — the plugin shows the note name as part of the deck during
review — and for the same reason neither may headings, tags, or backlinks that
name the item.

```
\#flashcards/vocab/<level>

canton:
（粵）<sentence>::[[<dict wikilinks>|<headword> (<reading>)]]

article:
<sentence contains cloze ==[[<dict wikilinks>|surface]]== rest of sentence>
ドアの脇に立って、書類カバンを器用に両足で==[[挟む|挟み]]==、書類に熱心に目を通している。

MC:
<headword> (<reading>)
1. <choice 1>
2. <choice 2>
3. <choice 3>
4. <choice 4>
<br>==<correct choice> = [[<dict wikilinks>]]==

Yomi:
<headword>::[[<dict wikilinks>|<reading>]]
```

For the same example vocab, the corresponding flashcard is:
```
\#flashcards/vocab/N2
（粵）夾住、夾喺中間、插入::[[挟む|挟む（はさむ）]]

ドアの脇に立って、書類カバンを器用に両足で==[[挟む|挟み]]==、書類に熱心に目を通している。

挟む（はさむ）
1. ある状態を変えずに維持し続ける
2. 数量・程度が多くなる・強くなる
3. 二つのものの間に物を入れて押さえる
4. 感動・驚き・呆然などで、その場にずっと立ったまま動けないでいる
<br>==二つのものの間に物を入れて押さえる = [[挟む]]==

挟む::[[挟む|はさむ]]
```

- Filename **`card-vocab-{NNNN}.md`** — an **answer-opaque** sequence number
  (stable `vocab_id → NNNN` mapping in `flashcards/.card-index.json`), because the
  SR plugin shows the note name during review. For the same reason the note has
  **no heading and no `Source:` backlink** — those would reveal the word. The link
  to the llm-wiki page is embedded in each card's **answer** (`[[headword|display]]`),
  so context is one click away only *after* the card is flipped.
- **Append-only / idempotent generation** protects review history: a note is
  written only if it does not already exist; existing notes (carrying the
  plugin's inline `<!--SR:…-->` schedule) are never rewritten. Future ingests add
  only new notes. `--check` reports content drift without overwriting; `--force
  <vocab>` regenerates one note deliberately (resets that note's schedule, with a
  warning) — same philosophy as the ingest git-flag (§8.3).
- The plugin owns scheduling (FSRS, stored inline in `flashcards/` notes); those
  notes are **committed** — review history is precious. Chose the mainstream
  plugin over the SR-Recall fork for maintenance; can switch later.

**Built — daily quiz email (§10.8).** A self-grading, CSS-interactive quiz email
over `cards.json` (with the reveal looked up from the pages) is implemented; it
adds the multiple-choice + push-delivery channel. It is **self-graded (Phase 1)**
— results are not yet persisted.

**Still deferred — CLI trainer & progress-persisted quizzing (§10.6).** A stdlib
CLI trainer and result-persistence over `progress.json` (SM-2, §10.1) remain
planned; persistence needs the Phase-2 answer-capture surface (§10.8.3). Running
that alongside Obsidian-SR means two schedulers — reconcile then. `study/cli.py`
today is a read-only card *viewer* for content review, not yet a review session.

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
- **Remaining grammar cards** — meaning-recognition, `formation`, reading (the
  full-context MC / cloze / error-correction set is near-term, §10.2) — and
  **article card types**.
- **CLI trainer & progress-persisted quizzing** over `cards.json` +
  `progress.json` (SM-2, §10.1). The daily quiz **email** is already built and
  self-graded (§10.8); what remains deferred is a stdlib CLI trainer and
  **persisting results** (the Phase-2 answer-capture surface, §10.8.3), which adds
  a second scheduler alongside Obsidian-SR — reconcile then. FSRS could later
  replace SM-2 (Obsidian already uses FSRS).
- **Anki export channel.** A renderer `cards.json → .apkg`/CSV, sibling to
  `obsidian_cards.py` — stable card ids double as Anki note GUIDs so re-exports
  update in place. Likely **export-only** first (Anki's review state stays in its
  own collection); reading it back would add an Anki `ReviewAdapter` and a merge
  policy for `f_fsrs` (§10.1). Logged via `exposure.channels`.
- **Web dashboard** with the constellation view; **audio / TTS** listening cards
  (pitch-accent / audio are in scope for N1, but the drills are deferred — §11
  resolved).
- **Any GUI** remains deferred.

### 10.7 Tests for the card generator

`study/cards.py` is deterministic (sorted output, seeded distractors), so it is
tested by **snapshot**: build cards over a small fixture wiki and assert they
match a saved baseline. Standard library only (like §7.1) — no `pytest`.

- **Fixture wiki: `tests/cards-wiki/`** — a **separate** directory from
  `tests/test-llm-wiki/` (which holds deliberately-malformed pages for lint's
  negative tests and is unusable here). It mirrors the real layout
  (`vocabulary/`, `grammar/`, `articles/`) and holds a **representative subset of
  real, well-formed pages** copied from `llm-wiki/`, **plus one article whose
  `[[wikilinks]]` resolve to the included items** (this is what drives cloze /
  gcloze). Chosen to exercise every card type and the tricky cases:
  - *vocab* — a kanji headword (reading), a pure-kana one (no reading), a
    nested-paren `（粵：（風）…）` gloss (canto balanced-paren, §cards `_balanced_paren`),
    a `①`-sense definition (marker stripping), and enough items for the meaning-MC
    distractor pool;
  - *grammar* — a contiguous pattern (gcloze + gmc + gerror), a split/呼応 pattern
    (例文-cloze via the leading fragment, no MC), a bracketing pattern with a ✗/✓
    pair (gerror only), an inline `✗ … ✓ …` mistake, and the 0-card
    `～といい～といい` gap.
- **`cards.py` change (input/output decoupled):** two independent flags —
  `--wiki` (input root, default `llm-wiki/`) and `--out` (output path, default
  `build/cards.json`); the program always writes to `--out`. Guard: **`--wiki`
  requires `--out`**, so reading a test wiki can't silently overwrite the real
  `build/cards.json`. `build()` still accepts a wiki argument for internal use;
  other callers are unaffected.
- **Baseline: `tests/cards-baseline.json`** — the expected cards JSON, committed,
  produced by `cards.py` itself. Regenerated deliberately with `--update` when a
  `cards.py` change is intended.
- **Runner: `tests/run_cards_tests.py`** (top-level, run from the repo root):
  invokes `cards.py --wiki tests/cards-wiki --out <tmp>` as a **subprocess**, then
  JSON-loads that temp file and compares to the baseline — exercising the whole
  program (arg parsing → build → serialization → file output), not just `build()`.
  **Passes iff identical**, else prints which card ids are NEW / MISSING / CHANGED
  and exits non-zero. `python tests/run_cards_tests.py --update` rewrites the
  baseline (via the same CLI path).

`cards.py` stays otherwise unchanged; the fixture + baseline are the test surface,
so adding or altering a card type means re-running `--update` and eyeballing the diff.

### 10.8 Daily Email Quiz

A second delivery channel (alongside the Obsidian SR notes of §10.4): a **daily,
bite-size, self-grading quiz email**. Prototype proven end-to-end — the
interactive quiz renders and grades **inside iPhone Mail** with no external
browser. This section documents the design and data flow; the generator lives in
`study/email_quiz.py` (promoted from the prototype under `study/prototypes/`).

**10.8.1 Design goals & target clients**

- **One article per email** — the 5–8 questions are all drawn from a single
  source article, so they read in a shared context (§10 theme `tags`). The article
  is chosen by **least-recently-served rotation**, and the questions within it are
  the **highest-`urgency`** cards, both from the scheduler (§10.1).
- **Bite-size** — **5 questions** by default (tunable; 8 is the comfortable
  ceiling before the expanded email feels long). Vocabulary ≈60 %, grammar the
  rest.
- **Multiple-choice only** — MC is the one format that self-grades with no
  server and no JavaScript (see 10.8.2).
- **Self-contained** — answer, submit, score, and the reveal of explanations all
  happen *inside* the one email. Nothing links out; nothing is required to load.
- **Target clients, in priority order:**
  1. **iPhone Mail (primary, must-support).**
  2. **macOS Mail (secondary).**
  3. Web/HTML front-ends like Gmail (nice-to-have).

  Apple Mail (iOS + macOS) is **WebKit-based** — the most CSS-capable mail
  renderer — which is what makes the in-email interactivity possible. Outside
  WebKit (e.g. Gmail web strips `<style>`) the email **degrades gracefully** to a
  static, still-readable quiz. We design for Apple Mail and accept the fallback.

**10.8.2 Interactivity — pure CSS, no JavaScript**

**No mail client runs JavaScript** (Apple Mail included), so the quiz is built
entirely from CSS that WebKit honours:

- Each choice is a hidden `radio`/`checkbox` `<input>` + a `<label>` tap target;
  selecting checks the input (`:checked`) and highlights the label.
- **答え合わせ (submit)** is one checkbox toggle; `#sub:checked ~ …` sibling
  selectors then reveal every question's feedback at once.
- **Score** uses a **CSS counter**: each correctly-answered question does
  `counter-increment`, and the score line prints `counter(score)` — e.g.
  「スコア 4 / 5」.
- Per-question **verdict** resolves by correctness (`.correct:checked` → ✓ 正解！,
  `.wrong:checked` → ✕ 復習：); the **explanation always shows** after submit.

This is intricate, WebKit-specific CSS; **the source of truth for "does it
render" is a real send to Apple Mail**, not a browser preview (Mail's sanitizer
is stricter than Safari). Verified on iPhone Mail via the SMTP path (10.8.5).

**10.8.3 Persistence — exposure yes, results no (Phase 1)**

CSS can compute and reveal, but **cannot send data anywhere** (that needs JS, and
mail `<form>` POST is unreliable/stripped). So the two kinds of state differ:

- **Results (grades) are not captured.** The quiz is self-graded in-email; *how*
  the user answered never leaves the email. The email says so plainly.
- **Exposure *is* recorded.** After a successful send the channel logs which cards
  went out to `progress/progress.json` via `scheduler.record_delivery` (§10.1).
  This needs no feedback from the email — it is a delivery log — and it drives the
  urgency-based selection so the daily email **rotates coverage** instead of
  repeating.
- **Deferred (Phase 2+):** capturing which answers were picked requires a
  **companion surface** (a tiny local page / CLI) that the email links to, writing
  a `review` record to `progress.json` (§10.1) — never the SR plugin's inline
  schedule (replicating FSRS state is fragile). Open question, §11.

> Do **not** attempt in-email *answer* capture — it is not achievable with
> CSS-only mail. Exposure logging is server-side (at send), so it is unaffected.

**10.8.4 Data flow — questions from `cards.json`, reveal from the pages**

The quiz **reuses the existing deterministic pipeline** and adds no duplicated
data (data-minimization, §2 tenets):

```
llm-wiki/**  ──cards.py──▶  build/cards.json    (§10.3; the question bank)
                                 │                         ▲ read-only
   flashcards/*.md (FSRS) ──┐    │                         │
   progress.json (exposure)─┴──▶ study/scheduler.py ──▶ urgency (§10.1)
                                 │
                                 ▼
                        study/email_quiz.py
                                 │  ├─ scheduler picks the least-recently-served
                                 │  │     article, then its top-N MC cards by urgency
                                 │  │     (vocab `meaning` + grammar `gmc`)
                                 │  └─ for each item, looks up its page in
                                 │        llm-wiki/{vocabulary,grammar}/<headword>.md
                                 │        for the REVEAL: 意味 (with （粵）) + 2 例文
                                 │        (each with its （粵） line)
                                 ▼
                 text/html email ──SMTP──▶ iPhone Mail
                                 │
                                 └─ on success: scheduler.record_delivery(card_ids, article)
                                       updates exposure + article last_served (§10.1)
```

- **`cards.json` drives the questions** and stays **minimal** — it holds only
  flashcard Q&A (front, choices, answer, back). It is **not** enriched with
  explanations. (Deliberately rejected: bundling 意味/例文/canto onto every card —
  it duplicates page data across a word's ~4 cards, risks drift, and violates
  data-minimization. See §11.)
- **The reveal is looked up live from the llm-wiki page** — the single source of
  truth for 意味 (incl. its `（粵）` gloss) and 例文 (incl. each example's `（粵）`
  translation). The generator reuses `cards.py` helpers (`load_pages` and
  `lint.LINK_RE`) rather than re-implementing page loading / wikilink parsing.
- Consequence: `cards.py` and `cards.json` are **unchanged** by this channel.

**10.8.5 Delivery — SMTP (`smtplib`), raw MIME**

- Send via **`smtplib`** as a `multipart/alternative` message (plain-text
  fallback + the `text/html` part). The **raw HTML is transmitted verbatim**, so
  the `<head><style>` block the interactivity depends on arrives intact.
- **The Gmail API / compose path is unusable here** — it strips `<head><style>`
  on send, which flattens the quiz to static. Confirmed during prototyping. SMTP
  is the channel we use.
- **Credentials via a gitignored `study/secrets.json`** — a file grouping
  related secrets by service; SMTP lives under an `smtp` key
  (`user` / `pass` / `host` / `port` / `from` / `to`), where `pass` is a provider
  **app password**, not the account password. `smtp.gmail.com:465` (implicit SSL)
  is the default; `587` STARTTLS supported.
  - **The file is mandatory — no environment-variable fallback.** Ambient env
    risks silently picking up `SMTP_*` left by an unrelated session (or an
    injected value); an explicit local file is more predictable and safer.
    Missing file / missing `user`/`pass` → hard error.
  - **`secrets.json` is never committed** (`.gitignore`, bare name so it is ignored
    at any depth). A **`secrets.template.json` with dummy values IS committed** as
    the format placeholder — copy it to `secrets.json` and fill in real values. New
    service secrets get their own top-level key (e.g. add `"openai": {…}`), keeping
    the top-level tree clean; both files live in `study/` beside the code that reads them.
  - **Never hardcode credentials in source.** If a secret ever lands in a tracked
    file, rotate it at the provider.
- Scheduling the *daily* send (cron / launchd) is a later step; the near-term
  deliverable is the generator + manual send.

**10.8.6 Reveal content & length**

- Per question, after submit: a single feedback box — verdict (✓ 正解！/ ✕ 復習：)
  then the explanation (shown regardless of correctness): the item's **意味 with
  its `（粵）` gloss**, and up to **2 例文, each with its `（粵）` translation**.
- Length is roughly ~2 phone screens to answer and ~3.5 screens fully expanded at
  5 questions; that scales with the question count, which is why 8 is the ceiling.

**10.8.7 Status**

- **Prototype proven** on iPhone Mail via SMTP (interactivity, scoring, reveal
  with Cantonese all working). Prototype artifacts kept under `study/prototypes/`
  (`gen_email.py`, `send_quiz.py`) for reference; not a build dependency.
- **Implemented — `study/email_quiz.py`:** reads questions from `cards.json`,
  looks up the reveal from the pages via `cards.py` helpers (`load_pages`,
  `lint.LINK_RE`), builds the email, and sends via SMTP (`study/secrets.json`).
  CLI: `--list` (articles + MC counts), `--article`, `-n/--num` (default 5),
  `--out` (preview HTML, default `build/daily-quiz.html`, gitignored), `--send`.
  Subject carries the date. Verified byte-identical question output to the approved
  prototype.
- **In progress — scheduler integration (§10.1):** selection moves from the
  initial "most-MC-cards, id-sorted" default to the scheduler's
  least-recently-served article + top-N-by-urgency, with `record_delivery`
  updating exposure after a send (`--send`). `--article` still overrides.
- **Next:** the daily send scheduler (10.8.8), then the Phase-2 companion capture
  surface (10.8.3).

**10.8.8 Daily scheduling (macOS `launchd`)**

The send runs **once per day** on a personal MacBook that may be **off or asleep**
at any given moment, so `cron` is unsuitable (deprecated on macOS; a job scheduled
for a time the machine was off simply never runs — no catch-up). A **`launchd`
LaunchAgent** drives it, combining triggers with an idempotent guard so they
collapse to exactly one send per day:

- **`StartCalendarInterval`** (default **07:00** local) — fires at the set time; if
  the Mac is *asleep* then, `launchd` runs it on the next wake.
- **`RunAtLoad`** — fires at login / boot: the **catch-up** path for when the Mac
  was *off* at 07:00 and opened later in the day.
- **Idempotent `--once-daily` guard** — `email_quiz.py --send --once-daily` checks
  `progress.json` and **exits without sending if any article was already served
  today** (an exposure logged today). Because exposure is written **only on a
  successful send** (§10.8.3), a failed attempt (e.g. no network right after wake)
  leaves the day "unsent", so the next wake/login **retries** — self-healing, with
  no lost or duplicate days.
- **Fresh card bank before each send** — the daily run **rebuilds `build/cards.json`
  before reading it**, so the quiz is correct-by-construction even if a page was
  hand-edited without a re-ingest (which is what would otherwise leave `cards.json`
  stale — §10.3). This is the *read-time* guard complementing ingest's *write-time*
  regeneration (§8.2 step 7); `cards.py` is cheap and deterministic, so re-running
  it daily is free insurance. Implementation: the send runs **`regen.py --only
  cards`** (§10.3) — or, equivalently, `email_quiz.py` rebuilds `cards.json` on
  start (it already imports `cards.py`), needing no wrapper or plist change —
  ordered **after** the `--once-daily` guard, so an already-sent day skips the
  rebuild too.

A **LaunchAgent** (per-user, `~/Library/LaunchAgents/`), *not* a LaunchDaemon: the
send needs the logged-in user's `study/secrets.json`, network, and repo path.
`StandardOutPath` / `StandardErrorPath` capture a run log. A ready-to-load plist
template lives at `study/launchd/`; loading it (`launchctl bootstrap`/`load`) is a
manual, per-machine step since it touches `~/Library`.

Behavior matrix: awake → runs at 07:00; asleep → on wake; off then opened → at
login; already sent today → skipped; failed send → retried next trigger.

### 10.9 Tests for the scheduler

`study/scheduler.py` mixes pure computation (urgency) with careful I/O (the
atomic, validated write), so both are tested — stdlib only (like §7.1, §10.7):

- **Urgency computation — pure-function tests.** `recompute` is a pure function of
  `(exposure, fsrs_snapshot, weights, today)`; feed crafted inputs and assert exact
  scores and ordering: never-shown ranks above long-unseen above recent; a
  low-stability / overdue FSRS card outranks a fresh one; a missing FSRS record
  falls back to the default; **idempotence** — running twice with the same inputs
  changes nothing.
- **FSRS parser — fixture tests.** Parse real `<!--SR:!fsrs,…-->` strings into
  `due`/`last_review`/`stability`/`difficulty`/`state`; a malformed / unknown-shape
  comment yields "no FSRS data" rather than an error. Include the block→card-id join
  (a small `flashcards/` fixture + `.card-index.json`).
- **Atomic write — correctness & safety tests.** Exercise the temp-file →
  sanity-check → `os.replace` path: a valid update lands; an update that would
  **drop a card id or article**, lose an entry's `exposure` / `last_served`, or
  produce an out-of-range score is **rejected, leaving the original file
  byte-for-byte intact**; an interrupted write never leaves a partial
  `progress.json` (only the temp file). `record_delivery` bumps only the delivered
  cards and the one featured article, preserving every other entry.

A top-level `tests/run_scheduler_tests.py` runner exits non-zero on any mismatch,
gating alongside the lint and cards suites.

## 11. Decisions & Open Questions

**Resolved:**

- **`id` scheme** — human-readable slug (not opaque hash), which stays short and
  clean. Lint enforces uniqueness; disambiguate homophone collisions with a short
  qualifier (e.g. `vocab-au` for 遭う vs. `vocab-au-meet` for 会う).
- **Re-ingestion vs. hand-edits** — before overwriting an existing `llm-wiki/`
  page, ingest checks git for uncommitted changes to that file and **warns /
  asks to confirm** before clobbering (§8.3). Hand-edits are rare (llm-wiki is
  AI-owned; e.g. a manual Cantonese correction). The warning doubles as a nudge
  to commit before re-ingesting.
- **Pitch-accent & audio** — in scope for N1. Pitch-accent can be captured now via
  the optional `accent` field (§6.2); audio/TTS drills are deferred (§10.6).
- **Ambiguous `[[marked]]` items** — ingest classifies to the best of current
  knowledge and **flags** the call in the final report step (§8.2), recording it
  in `logs.md` as the durable footnote for future revision (§8).
- **`build/cards.json`** — gitignored (rebuildable build artifact). `progress.json`
  stays **tracked** — it is precious, non-regenerable review history.
- **Scheduling granularity** — one schedule per word for now (§10.1).
- **Flashcard delivery** — near-term channel is the **mainstream Obsidian
  *Spaced Repetition* plugin (FSRS)**, reviewing generated notes in a separate
  top-level `flashcards/` folder (never inside content pages). Chosen over the
  SR-Recall fork for maintenance; can switch later. The daily quiz **email** is a
  second, built channel (§10.8); a CLI trainer and progress-persisted quizzing
  remain deferred (§10.4, §10.6).
- **Flashcard notes** — one per item, `card-vocab-{NNNN}.md` /
  `card-grammar-{NNNN}.md` (answer-opaque sequence; the plugin shows the note name
  during review, so no headword / heading / backlink). The llm-wiki link is
  embedded in each card's **answer**. **Committed** (review history is precious);
  generation is **append-only** to preserve the plugin's inline schedule.
- **Grammar card set** — build the **full-context, JLPT-shaped** three first
  (§10.2): pattern MC-in-context (distractors from `## 関連`), cloze production
  (`例文` + article), and error-correction (`## 間違いやすい点`). Meaning /
  formation / reading cards deferred; no 粵→pattern card.
- **Daily email quiz** (§10.8) — a **self-grading CSS-interactive** MC email,
  Apple-Mail-first, **5 questions from one article**. Questions come from
  `cards.json` (vocab `meaning` + grammar `gmc`); the reveal is **looked up live
  from the llm-wiki pages** (意味 + `（粵）`, 2 例文 + `（粵）`) — `cards.json` is
  **not** enriched (*data-minimization* tenet, §2). Delivered by **`smtplib` (raw
  MIME)**, not the Gmail API (which strips `<style>`). Credentials load from a
  **mandatory, gitignored `study/secrets.json`** (no env fallback), with a
  committed dummy-value template (*no-secrets-in-source* tenet, §2). Phase 1
  captures **exposure** (a send-side delivery log) but **not results** (CSS can't
  capture answers); save-back of grades needs a Phase-2 companion surface (§10.8.3).
- **Card scheduler & urgency** (§10.1) — the two schedulers are reconciled by a
  **read-model, not a merge**: Obsidian owns FSRS (we read it only), we own
  *exposure*, and `study/scheduler.py` blends both into a per-card **urgency**
  (0–100, tunable linear model) that the push pipeline ranks by. State is a single
  `progress/progress.json` namespaced into `cards` (raw `exposure` + derived
  `urgency`) and `articles` (per-article `last_served`, the rotation signal); the
  daily full-file recompute is protected by **atomic, sanity-checked writes**
  (temp → validate → `os.replace`) plus tests (§10.9), rather than a second file.
  FSRS is never copied (*data-minimization*, §2).

### 11.1 How key decisions evolved

A record of the questions that shaped the design, so the rationale survives where
the code no longer shows the paths not taken.

- **Card generation: AI vs. deterministic.** Considered authoring cards with an
  LLM for richer distractors/nuance. Chose **100% deterministic** generation from
  existing note fields: it is reproducible, testable (§10.7), and free for every
  future ingest. AI value is instead deferred to *ingest time*, written **into the
  note**, so generation stays deterministic (§10.6). *(Keep-it-simple; test-driven.)*
- **Where flashcards live.** Considered embedding cards/scheduling inline in the
  content pages. Rejected: it re-mixes the raw→llm-wiki→progress layers and, since
  the vault is regenerated often, would risk **wiping review history**. Cards live
  in a separate `flashcards/` folder, generated **append-only** so the SR plugin's
  inline schedule is never clobbered (§10.3–10.4).
- **Flashcard scheduler: build vs. reuse.** Considered writing an SM-2 scheduler
  now. Chose to **reuse the mainstream Obsidian SR plugin (FSRS)** near-term and
  defer our own `progress.json`/SM-2 to the CLI/email channel — avoids building a
  scheduler before it is needed. *(Reuse-libraries.)* The two-scheduler overlap is
  a known reconciliation item.
- **Email interactivity & transport.** The daily quiz went through three dead ends
  before the working path: pasting HTML into Mail's composer (rich-text editor
  strips the `<style>`), then the Gmail API/compose path (also strips
  `<head><style>`). The answer was **raw `text/html` over SMTP**, which Apple Mail
  (WebKit) renders with full CSS-only interactivity. The definitive test is a real
  send to iPhone Mail, not a browser preview (§10.8.2, §10.8.5).
- **`cards.json`: minimal vs. enriched.** Considered bundling 意味/例文/`（粵）`
  onto every card so the email needn't touch the pages. Rejected: it duplicates
  page data across a word's ~4 cards and risks drift. The email instead **looks the
  reveal up from the pages** at send time. *(Data-minimization; flag-tech-debt.)*
- **Secrets handling.** An early prototype hardcoded an SMTP app password, then
  moved to env vars. Settled on a **mandatory gitignored `secrets.json` with a
  committed template** and **no env fallback** — an explicit local file is more
  predictable than ambient env that a stray session could inject (§10.8.5).
  *(No-secrets-in-source.)*
- **Two schedulers, and where urgency lives.** With Obsidian-FSRS already owning
  review scheduling, considered building a parallel scheduler that duplicates its
  state. Chose instead a **read-model over both** — read FSRS live, own only
  *exposure* — feeding a materialised **urgency** score (§10.1). On storage,
  weighed a separate rebuildable `urgency.json` (isolate the daily full-file
  recompute from precious history) against one self-contained file; chose **one
  `progress.json`** because it is written on every delivery anyway, with **atomic,
  sanity-checked writes** as the safeguard instead of a second file. *(Reuse;
  data-minimization; flag-tech-debt.)*
- **Regeneration: idempotent driver, not Make/mtime.** Drift (stale `index.md`,
  `cards.json`, flashcards after ingests) prompted considering a **Make**- or
  **mtime-dependency** build graph ("rebuild iff upstream newer"). Rejected for
  this project: the vault is **iCloud-synced** (eviction/re-materialisation and
  cross-device sync rewrite mtimes unpredictably) and **git checkouts reset mtimes**
  — so mtime is an unreliable staleness signal; the repo/vault paths contain
  **spaces and Japanese**, which Make prerequisites handle badly; and it adds a
  non-Python build DSL. Decisively, the artifacts are **cheap and deterministic**,
  so there is no rebuild cost to optimise — unconditional regeneration is
  correct-by-construction with zero churn. Chose a **single idempotent
  `regen.py`** all flows call, plus **schedule-preserving** flashcard resync so
  even the one stateful artifact is safe to rebuild anytime (§10.3–10.4). Incremental
  rebuilds, if ever needed, would use a **content-hash manifest**, never mtime.
  *(Keep-it-simple; reuse; data-lineage.)*

### 11.2 Known gaps & smaller opportunities

Beyond the roadmap (§10.6), these are the smaller known gaps in the current build:

- **No answer capture yet.** The quiz email is self-graded; results are not saved
  (Phase 2, §10.8.3). Designing the companion capture surface is the main open
  question below.
- **Grammar coverage gaps.** `例文`-cloze is skipped for split/呼応 patterns where
  span detection is unreliable, and one bracketing pattern (`～といい～といい`)
  currently yields **0 cards** (§10.2, §10.7). Acceptable, but revisitable.
- **Urgency model is unvalidated.** The linear weights (§10.1) are a reasonable
  first guess, not tuned against outcomes; with no answer capture yet, there is no
  feedback signal to fit them. Revisit once results land (Phase 2).
- **FSRS parser is version-coupled.** It reads the current plugin's inline field
  layout; a plugin format change would silently drop to "no FSRS data" (safe, but
  degraded) until the parser is updated (§10.1).

**Open:**

1. Which external site(s) to scrape for seeding (§9)? — postponed (instructor
   role to research).
2. **Phase-2 answer capture (§10.8.3).** What is the companion surface that records
   quiz results back to `progress.json` — a tiny local page, a CLI re-entry, or a
   mailto/deep-link? Constrained by the fact that CSS-only email cannot post data.

## 12. Next Steps

**Done so far:**
- Schema (§6); `lint.py` + `lint-all` + fixture tests (§7, §7.1).
- The `ingest article` workflow (§8) with 8 articles seeded.
- Learning-aids pipeline (§10): `study/cards.py` → `cards.json` (+ snapshot tests,
  §10.7), `study/cli.py` viewer, `study/obsidian_cards.py` → **vocabulary and
  grammar** flashcards in `flashcards/` (append-only).
- Daily quiz email (§10.8): `study/email_quiz.py` (questions from `cards.json`,
  reveal from the pages, `smtplib` send via a gitignored `study/secrets.json`),
  proven interactive on iPhone Mail.
- Content index (§7.2): `wikitools/index.py` → `index.md` (+ fixture tests), and the
  suru-verb 「・する」 display shared across page titles, index, and flashcards
  (§6.2, §6.5.1, §7.2, §10.2).

**Near-term:**
1. **Card scheduler (§10.1, §10.9)** — `study/scheduler.py`: exposure tracking +
   read-only FSRS scan + urgency scoring, with atomic sanity-checked writes to
   `progress/progress.json` and its test suite. Wire `email_quiz.py` selection to
   least-recently-served article + top-N-by-urgency, and `record_delivery` on send.
2. **Daily send scheduler** — `launchd` LaunchAgent (07:00, RunAtLoad catch-up) +
   `email_quiz.py --once-daily` idempotent guard (§10.8.8).
3. **Unified regeneration (§10.3–10.4)** — `study/regen.py` (one idempotent entry
   point rebuilding `index.md` + `build/cards.json` + `flashcards/`), plus the
   **schedule-preserving** flashcard resync in `obsidian_cards.py` (re-attach
   `<!--SR:…-->` by card id). Point ingest (§8.2 step 7), scrape (§9), and the
   daily send (`--only cards`, §10.8.8) at it; have `email_quiz.py` rebuild
   `cards.json` on start. Fixes the derived-artifact drift (stale card bank →
   new items missing from the quiz).
4. Select and document the **web seeding source** (§9); implement the first source.

**After that:**
5. **Phase-2 answer capture** — companion surface writing quiz results to
   `progress.json` (§10.8.3, open question §11).
6. CLI trainer + progress-persisted quizzing over `progress.json` (§10.1, §10.6).
7. Roadmap items (§10.6): AI-enriched ingest, remaining article card types,
   web dashboard, audio / TTS.
