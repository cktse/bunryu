# Ingestion / Change Audit Trail

Append-only log of changes to the LLM-wiki, per specs.md §8.2 step 6.
**Never edit or delete existing entries — only append new ones at the bottom.**

Format: one `##` block per operation, newest at the bottom. Each block records
the date, time (HKT), the trigger, and a 1–2 sentence summary per new/updated
file. `(new)` = page created, `(upd)` = existing page modified.

> **Note on entries before 2026-07-06 17:20:** the audit trail was introduced
> after the initial seeding work below, so those entries are a **retroactive,
> summarized reconstruction** (file lists + batch summaries rather than strict
> per-file prose, and times are approximate). Full per-file granularity begins
> with the first ingest logged after this note.

---

## 2026-07-06 (approx.) — Ingest `raw/裁判員のもやもや.md` → article 「裁判員のもやもや」 (pass 1)

Retroactive summary. Initial ingest of the first inline-`[[…]]`-marked items.
- **Article (new):** `llm-wiki/articles/裁判員のもやもや.md` — essay on citizen
  participation in the judiciary; `references` + 注目語彙・文法 wired to the items below.
- **Vocabulary (new, 5):** 裁判, やがて, そもそも, 左右する, すっきり.
- **Grammar (new, 4):** ～とも～ともつかない, 必ずしも～ない, ～にしてみれば, ～に際して.
- OCR fixes applied in the article body only (raw preserved): いわ目られる→ゆがめられる,
  偏っていたとした→偏っていたとしたら.

## 2026-07-06 (approx.) — Re-ingest `raw/裁判員のもやもや.md` (pass 2, additional markers)

Retroactive summary. User added more `[[…]]` markers + two grammar points.
- **Article (upd):** 裁判員のもやもや — expanded `references`/body links/焦点リスト to full set.
- **Vocabulary (new, 16):** 導入, まじまじ, 眉を曇らせる, 持ち合わせる, 申し合わせ,
  処分, 合意, 不都合, 保つ, 下す, 意図的, 押す, 誤り, 後の祭り, もやもや, 根差す.
- **Grammar (new, 2):** 到底～ない, ～に即して.
- Inflected surface forms linked via `[[dictionary-form|surface-form]]` aliases.

## 2026-07-06 (approx.) — Re-ingest `raw/裁判員のもやもや.md` (pass 3, `[[ゆがめられる]]`)

Retroactive summary. User fixed the raw OCR typo and marked one new item.
- **Vocabulary (new, 1):** ゆがめる (ichidan-verb; passive ゆがめられる in the passage).
- **Article (upd):** 裁判員のもやもや — added `vocab-yugameru` to `references`, body
  link `[[ゆがめる|ゆがめられる]]`, and 注目語彙 entry.

## 2026-07-06 (approx.) — Ingest `raw/読み取る.md` → article 「記事の裏側」

Retroactive summary. Article title taken from the `##` heading (記事の裏側), which
differs from the raw filename (読み取る).
- **Article (new):** `llm-wiki/articles/記事の裏側.md` — essay on how news is
  reported/received; `references` + 注目語彙・文法 wired to the items below.
- **Vocabulary (new, 20):** 文字離れ, 食い止める, 身の回り, 見向きもしない, しぶしぶ,
  次第に, あまりにも, 口ごもる, 水を差す, 見逃す, 詳細, 事細か, 受け止める, 本質的,
  的外れ, 歯切れの悪さ, 突きつける, ぬけぬけ, くたくた, 実態.
- **Grammar (new, 6):** ～手前, ～いかんでは, ～かと思えば, ～といい～といい,
  ～を余儀なくされる, ～末に (from inline `[[末に]]`, classified as grammar).
- OCR fixes in article body only (raw preserved): 4道→報道, 思いを寄らぬ→思いも寄らぬ,
  ずがずが→ずかずか.

## 2026-07-06 (approx.) — Vault-wide: directory restructure

Retroactive summary. Not an ingest.
- Moved `content/raw/` → top-level `raw/`; renamed `content/` → `llm-wiki/`.
- Updated `source:` frontmatter (and メモ mentions) `content/raw/…` → `raw/…`
  across 56 generated pages.

## 2026-07-06 (approx.) — Vault-wide: `# title` lines (specs §6.5.1)

Retroactive summary. Not an ingest.
- Added a level-1 title line to all 54 vocabulary + grammar pages:
  `# headword（reading）` when the headword contains kanji, else `# headword`.

## 2026-07-06 (approx.) — Vault-wide: Cantonese 例文 lines (specs §6.5.1 / §2.1)

Retroactive summary. Not an ingest.
- Backfilled a secondary `（粵）` translation line under every example sentence
  across all 54 vocabulary + grammar pages (108 sentences), placed after the
  primary Japanese nuance note.

## 2026-07-06 17:20 HKT — Audit trail introduced

Created `logs.md` (this file) per specs.md §8.2 step 6. No content pages changed.
Subsequent ingests will log full per-file summaries here.

## 2026-07-06 18:09 HKT — Ingest `raw/ならう.md` → article 「そば屋の先生」

First ingest logged with full per-file detail. Article title taken from the `##`
heading (そば屋の先生); differs from the raw filename (ならう). 48 new pages,
0 updated. No id collisions; all 48 article `references` resolve.

**Article (new):**
- `llm-wiki/articles/そば屋の先生.md` — essay: a foreign part-timer at a soba shop
  is scolded by the master for casual slang (マジ/めっちゃ) and realises his praise
  was a "conditional compliment"; `references` + 注目語彙・文法 wired to all items below.

**Vocabulary (new, 35):**
- `痛い目` (expression) — つらい経験；「痛い目に遭う」。
- `遭う` (godan-verb) — 災難に出くわす；会う/合う/遭う の使い分け。
- `段取り` (noun) — 物事を進める順序・手はず。
- `もたもた` (adverb) — 動作が遅く手間取るさま。
- `仕事ぶり` (noun) — 仕事の仕方・様子。
- `目に余る` (expression) — ひどくて見過ごせない。
- `どきどき` (adverb) — 緊張・不安で胸が高鳴る。
- `ましてや` (adverb) — なおさら・言うまでもなく（初回見落とし、後追加）。
- `品位` (noun) — 上品さ・品格。
- `疑う` (godan-verb) — 怪しいと思う；派生 疑わしい/疑い。
- `中途半端` (na-adj) — どっちつかずで徹底しない。
- `くれぐれも` (adverb) — 念を押す依頼・願い。
- `気に障る` (expression) — 相手の感情を害する。
- `傍ら` (noun) — すぐそば；「〜する傍ら＝一方で」も。
- `睨む` (godan-verb) — ①鋭く見る ②見当をつける。
- `手厳しい` (i-adj) — 容赦なく厳しい。
- `すらすら` (adverb) — よどみなく滑らかに進む。
- `打ち解ける` (ichidan-verb) — 心を開いて親しくなる。
- `使い勝手` (noun) — 使いやすさ・使い心地。
- `通じる` (ichidan-verb) — ①意味が伝わる ②つながる。
- `目上` (noun) — 立場が上の人；⇔目下。
- `平気` (na-adj) — ①動じない ②気にせず平然。
- `目くじらを立てる` (expression) — 些細な事をとがめる。
- `思いも寄らない` (expression) — まったく予想しない。
- `言葉遣い` (noun) — 言葉の使い方；送り仮名「遣い」。
- `がみがみ` (adverb) — うるさく叱る・小言を言う。
- `思い至る` (godan-verb) — 考えが及んで気づく。
- `境` (noun) — 分かれ目；「〜を境に」。
- `その気になる` (expression) — おだてを真に受けて舞い上がる。
- `気が緩む` (expression) — 緊張が解け油断する；自他対。
- `条件付き` (noun) — 条件が伴うこと；⇔無条件。
- `お世辞` (noun) — 心にもない褒め言葉；「お世辞にも〜ない」。
- `恥をかく` (expression) — 人前で面目を失う。
- `少しずつ` (adverb) — わずかな量を重ねて；「〜ずつ」。
- `口やかましい` (i-adj) — 小言が多くうるさい。

**Grammar (new, 13):**
- `～途端` — 「～した瞬間に（意外な事態が）」。
- `～にたえない` — ①見る/聞くに値しない ②感情を抑えきれない。
- `～極まりない` — この上なく～だ（否定的強調）。
- `～からには` — ～する以上は当然～すべきだ。
- `～ならいざ知らず` — ～なら別だが（なおさら）。
- `～を問わず` — ～に関係なく。
- `～からともなく` — いつ/どこからともなく（特定できず）。
- `～をいいことに` — ～を都合よく悪用して。
- `～にしては` — ～という基準の予想とのズレ。
- `～ことなしに` — ～せずに／～なしには。
- `～はめになる` — 望まぬ困った結果に陥る。
- `～ならまだしも` — ～ならまだ許せるが（実際はもっと）。（新しい文法欄より）
- `～ものの` — ～けれども（逆接）。（新しい文法欄より）

**Notes:** `[[途端]]`/`[[にたえない]]`/`[[極まりない]]` etc. classified as grammar
though inline-marked; inflected surface forms linked via `[[dict-form|surface]]`
aliases. OCR fixes applied to the article body only (raw preserved): もめっちゃ→めっちゃ,
そうな私に→そんな私に.

## 2026-07-06 19:02 HKT — Vault-wide: fix wikilinks split across line breaks

Not an ingest. Hard-wrapping had placed newlines inside some `[[...]]` tokens,
which Obsidian fails to parse as links. Joined every such link onto one line
(newline removed between `[[` and `]]`); no link targets/aliases changed.
- `llm-wiki/articles/そば屋の先生.md` (upd) — 5 links rejoined
  (くれぐれも, ～ならいざ知らず, ～を問わず, 通じる, ～はめになる).
- `llm-wiki/articles/記事の裏側.md` (upd) — 3 links rejoined.
Rule codified in specs.md §6.5: never split a `[[wikilink]]` across a line break.

## 2026-07-06 19:24 HKT — Vault-wide: retrofit articles to refined §6.4/§6.5.2

Not an ingest. Applied the two spec refinements (drop `references` frontmatter;
re-flow `## 本文` line breaks) to all existing article pages.
- `llm-wiki/articles/裁判員のもやもや.md` (upd) — removed `references:` block;
  re-wrapped 本文 (4 paragraphs kept; breaks only after 。、！？, none inside
  words/wikilinks; even visual width ~46).
- `llm-wiki/articles/記事の裏側.md` (upd) — removed `references:` block; 本文
  re-wrapped (4 paragraphs; visual width ~49).
- `llm-wiki/articles/そば屋の先生.md` (upd) — removed `references:` block; 本文
  re-wrapped (4 paragraphs; visual width ~46).
No content wording changed; only frontmatter (references removed) and 本文 line
wrapping. Vocabulary/grammar pages untouched (no `references`, single-line links).

## 2026-07-06 19:47 HKT — Vault-wide: re-flow article 本文 at word boundaries (§6.5.2 update)

Not an ingest. specs.md §6.5.2 was loosened to allow (and recommend) line breaks
at word/phrase boundaries — not only punctuation. Re-flowed all 3 article bodies
accordingly; breaks now fall after particles (が・は・に・と…) and clause endings
as well as 。、, giving more even rendered lines (avg ~37–38, max ~51, was ~68–79).
- `llm-wiki/articles/裁判員のもやもや.md` (upd) — 本文 re-wrapped (4 paragraphs).
- `llm-wiki/articles/記事の裏側.md` (upd) — 本文 re-wrapped (4 paragraphs).
- `llm-wiki/articles/そば屋の先生.md` (upd) — 本文 re-wrapped (4 paragraphs).
Text integrity machine-verified: stripping the new line breaks reproduces each
paragraph's exact prior characters, so only newline positions changed. 0 split
wikilinks; no `references`; paragraph breaks preserved.

## 2026-07-06 20:10 HKT — Implement `scraper/lint.py` + `lint-all` (§7)

Not an ingest. Built the stdlib-only content linter per specs.md §7 (no
python-frontmatter/PyYAML/pydantic — `pathlib` + `re` + a hand-rolled
frontmatter reader; flat functions, one per rule).
- `scraper/lint.py` (new) — checks required/typed frontmatter, enums, id
  uniqueness, `# title` line (§6.5.1), `## 意味`/`## 例文` with ≥2 examples each
  carrying a （粵）/（英）line, article `## 本文` + wikilink resolution, and the
  no-split-wikilink rule; ignores `[[…]]` shown inside code spans. Run via
  `python -m scraper.lint` (or `python scraper/lint.py [ROOT]`); exits non-zero
  on any error.
- First run over `llm-wiki/` surfaced one real violation, now fixed:
  - `llm-wiki/grammar/～ならいざ知らず.md` (upd) — title line was `# ～ならいざ知らず`
    but the headword contains kanji, so corrected to
    `# ～ならいざ知らず（～ならいざしらず）` per §6.5.1.
- Vault now lints clean: 105 files, 0 errors, 0 warnings.

## 2026-07-06 21:01 HKT — Implement lint.py test suite (§7.1)

Not an ingest. Built the fixture-vault test suite per specs.md §7.1 — runs
`lint.py` unchanged over a crafted vault and compares findings to expectations.
- `tests/test-llm-wiki/` (new) — 25 fixture pages mirroring the vault layout
  (`vocabulary/`, `grammar/`, `articles/`); each is one positive (lints clean)
  or negative (trips exactly one rule) example covering every §7 rule, incl. a
  dup-`id` pair and an unresolved-link warning. Kept under `tests/`, so
  `lint-all` (which targets `llm-wiki/`) never sees these deliberately-malformed
  files.
- `tests/run_tests.py` (new) — runs `lint.main([test-llm-wiki])`, parses the
  `path: [sev] message` output, and checks each fixture against an
  expected-results table (specific severity + reason substring, or “clean”).
  Prints a pass/fail summary; exits non-zero on mismatch. Run from repo root:
  `python tests/run_tests.py`.
- Result: 25/25 pass, exit 0. `lint.py` itself was not modified.

## 2026-07-06 21:47 HKT — Ingest `raw/第二課 いたわる.md` → article 「春の一日」

Article title from the `##` heading (春の一日); differs from the raw filename
(第二課 いたわる). 43 new pages, 0 updated. No `references` frontmatter (§6.4);
本文 wrapped at word boundaries (§6.5.2). Vault lints clean afterward
(148 files, 0 errors, 0 warnings).

**Article (new):** `llm-wiki/articles/春の一日.md` — essay: an older narrator is
shown small, unforced kindnesses by two young strangers on a bus and train, and
reflects on how consideration (いたわり) enriches society across generations.

**Vocabulary (new, 35):** 思い当たる, 上ずる, 席を空ける, 鳴き声, 耳を澄ます,
ぽかぽか, 勘違い, 最中, たまたま, 譲る, いかにも, ほやほや, 脇, 器用, 挟む,
目を通す, 出向く, 席を立つ, 向かう, 気配, 擦れ違う, 会釈, さりげない, 振る舞い,
じんわり, 胸にしみる, 見ず知らず, もってのほか, いたわり, よぼよぼ, ぎすぎす,
とげ, ひいては, 潤い, こつこつ.

**Grammar (new, 7):** それにしても, ～ずにはいられない, ～ないでもない,
～からといって～というものではない, ～めく (from inline `[[めいた]]`),
～からして (from `[[からして]]`), ～にもまして (from `[[にもまして]]`).

**Notes:** the 新しい文法 list's 4th entry「〜からといって、〜というものではない」
was created as a single combined grammar page (inline `[[というものではない]]`
aliases to it). Inflected surface forms linked via `[[dict-form|surface]]`
aliases. No OCR fixes needed (clean source).

## 2026-07-08 16:00 HKT — Ingest `raw/第一課 しる.md` → article 「初めての雪」

Article title from the `##` heading (初めての雪); differs from the raw filename
(第一課 しる). 33 new pages, 0 updated. No `references` frontmatter (§6.4); 本文
wrapped at word boundaries (§6.5.2). Vault lints clean afterward (181 files,
0 errors, 0 warnings).

**Article (new):** `llm-wiki/articles/初めての雪.md` — essay: someone raised in a
warm climate sees snow for the first time, moves from wonder at its beauty to
awareness of its harshness/danger, and reflects that knowledge gained online is
only partial next to lived experience.

**Vocabulary (new, 26):** やれやれ, 伸びをする, ひらひら, そこそこ, 飛び出す,
かけら, めがける, 手のひら, 何とも, 思いにとらわれる, みるみる, 増す, 立ち尽くす,
飽きる, きらきら, すがすがしい, まるっきり, きゅっきゅっ, そっと, ヒューヒュー,
後を絶たない, 押しつぶす, 身を潜める, つくづく, 思い知る, 一面的.

**Grammar (new, 6):** ～ことなく, ～たところで, ～限り, ～ことはあっても (from the
新しい文法 list); ～かのようだ (from inline `[[かのような]]`); ～を通して (from
inline `[[通して]]`).

**Notes:** classified `[[通して]]`→grammar ～を通して and `[[かのような]]`→grammar
～かのようだ (functional patterns); `[[限り]]`→grammar ～限り (in the 新しい文法
list). Lint caught one title-rule slip during finalize — `～ことはあっても.md`
title was `# ～ことはあっても（～ない）`; corrected to `# ～ことはあっても` per
§6.5.1 (no-kanji headword → no parenthetical). No OCR fixes (clean source; only
within-line spacing normalized on reflow).

## 2026-07-08 22:20 HKT — Re-ingest `raw/裁判員のもやもや.md` → repair only (Obsidian link mangling)

Re-ingestion requested. §8.3 git check: target files committed/clean (no
hand-edits to clobber). Content was **idempotent** — all 23 inline markers + 6
新しい文法 items already have pages; nothing new to create.
- Only substantive diff: **3 wikilinks in `llm-wiki/articles/裁判員のもやもや.md`
  had been auto-rewritten by Obsidian to full vault paths** after the
  `nihongo`→`bunryu` rename — `[[bunryu/llm-wiki/vocabulary/やがて]]` (×2) and
  `[[bunryu/llm-wiki/grammar/～に際して]]` (×1). Restored to `[[やがて]]` /
  `[[～に際して]]`. Only non-aliased links were affected; `[[dict|surface]]`
  links were untouched.
- Impact: the mangled `[[やがて]]` link had been **silently dropping やがて's
  cloze card** from the generated deck (link_target no longer matched a
  headword); fixing it restored the card.
- Lint before fix: 181 files, 0 errors, **3 warnings** (linter caught the
  unresolved links); after fix: **0 errors, 0 warnings**.
- Mitigation recommended: set Obsidian *New link format = Shortest path* and
  *Automatically update internal links = Off*; the linter's unresolved-link
  warning is the safety net if it recurs.

## 2026-07-09 13:11 HKT — Obsidian flashcard channel (§10.4): `study/obsidian_cards.py` + `flashcards/`

Not an ingest / not an llm-wiki change. Implemented the near-term delivery
channel per specs §10.4.
- `study/obsidian_cards.py` (new) — renders `cards.json` → one Obsidian SR note
  per vocab at `flashcards/card-{headword}.md` (deck tag `#flashcards/vocab/{level}`,
  `Source: [[headword]]` backlink, SR-syntax lines: reading/canto/meaning `::`
  recall + `==surface==` cloze). **Append-only** (never rewrites an existing note,
  so the plugin's inline `<!--SR:…-->` schedule is safe); `--check` audits drift,
  `--force [id/headword…]` regenerates deliberately.
- Generated **138 flashcard notes** (untracked; to be committed — review history
  is precious). `lint-all` unaffected (181 files, 0/0; `flashcards/` is outside
  `llm-wiki/`).
- Bug fixed at the root in `study/cards.py`: the `（粵：…）` gloss could wrap across
  lines, leaving a newline inside the `canto` card (split the SR line and tripped
  `--check`). `parse_imi` now strips newlines from the gloss; `cards.json`
  regenerated (0 canto newlines), flashcards regenerated, `--check` clean.

## 2026-07-10 14:09 HKT — Flashcard format overhaul (§10.4 feedback)

Not an ingest / not an llm-wiki change. Reworked the Obsidian flashcard format per
user feedback in specs §10.4; overwrote all 138 notes (no meaningful schedules yet).
- **Answer-opaque filenames**: `card-{headword}.md` → `card-vocab-{NNNN}.md` with a
  stable `vocab_id → NNNN` manifest at `flashcards/.card-index.json`. The plugin
  shows the note name during review, so it must not reveal the word.
- **No heading / no `Source:` backlink** (they'd reveal the answer). The llm-wiki
  link is embedded in each card's **answer** via `[[headword|display]]` instead.
- **Card layouts** (SR syntax): canto `（粵）gloss::[[hw|hw（reading）]]`; cloze
  `…==[[hw|surface]]==…`; **meaning MC** as a cloze block (`hw（reading）` + 4
  numbered choices + `<br>==correct = [[hw]]==`); reading `hw::[[hw|reading]]`
  (kanji only). Leading sense-marker `①` stripped from definitions (`cards.py`).
- `study/obsidian_cards.py` rewritten: manifest-based sequence filenames, new
  `note_text`/`card_block`, full-text drift `--check`; append-only preserved.
- Regenerated: 138 notes, `--check` clean, lint unaffected (181, 0/0). specs §5,
  §10.4, §11 reconciled to the new naming/format.

## 2026-07-10 16:35 HKT — Fix: canto gloss with nested parentheses (bug report)

Not an ingest. `parse_imi` extracted the `（粵：…）` gloss with a non-greedy regex
that stopped at the **first** `）`, so a gloss containing its own parens truncated —
e.g. ヒューヒュー `（粵：（風）呼呼聲、咻咻咁吹。）` yielded only `（風`.
- `study/cards.py`: replaced the regex with **balanced depth-counting**
  (`_balanced_paren`) to find the matching `）`; also made the jp-definition
  parenthetical stripping **nesting-safe** (iterative innermost removal).
- Regenerated `cards.json`; `--check` flagged **29** drifted flashcards
  (20 canto corrections + 6 meaning cards whose distractor pool shifted + 3
  structural). `--force`-regenerated all 138 (no schedules yet); `--check` clean.
- Note: MC distractors are sampled from the global def pool, so a single content
  edit can ripple to unrelated meaning cards — acceptable now (pre-review), but a
  candidate for more stable distractor selection later.

## 2026-07-13 18:20 HKT — Grammar flashcards (§10.2/§10.4)

Not an ingest. Implemented the three full-context grammar card types.
- `study/cards.py`: added `gcloze` (pattern blanked → produce it; from `例文`
  core-match + article `[[pattern|surface]]`), `gmc` (blanked sentence + 4 choices
  from `## 関連` + same-level fill; contiguous patterns only), and `gerror`
  (✗/✓ from `## 間違いやすい点`, incl. short inline pairs). Span detection:
  `blank_target` uses the contiguous core, or a distinctive leading fragment
  (必ずしも/到底/からといって) for split patterns. Generic rename `vocab_id → item_id`
  + `kind` (vocab|grammar); output is unchanged for vocab cards.
- `study/obsidian_cards.py`: per-kind sequence filenames `card-grammar-{NNNN}.md`,
  deck `#flashcards/grammar/{level}`, grammar `card_block`s.
- `study/cli.py`: `--item`/`--kind` filters; renders grammar types.
- Result: 638 cards (127 grammar: 86 gcloze + 31 gmc + 10 gerror). Generated
  **37 grammar notes** (append-only; 138 vocab notes skipped). `lint-all` 181,0/0.
- **Append-only proved its worth:** the vocab notes already carry real
  `<!--SR:!fsrs,…-->` review schedules — they were correctly preserved.
- Fixed a `--check` false-positive: `canonical()` now collapses the blank line a
  stripped SR comment leaves, so reviewed notes don't read as drifted.
- Coverage gap (1/38): `～といい～といい` gets 0 cards (bracketing pattern, not in any
  article, no distinctive fragment, no ✗/✓ pair) — acceptable for now.

## 2026-07-15 16:28 HKT — Tests for cards.py (§10.7) + rename lint runner

Not an ingest.
- Renamed `tests/run_tests.py` → `tests/run_lint_tests.py` (git mv; parallel to
  the new cards runner); updated its docstring/error string and specs §5/§7.1.
- `study/cards.py`: `load_pages`/`build` take a **wiki-root override** (default
  `llm-wiki/`); `main --wiki` prints the summary but **does not write cards.json**
  (a first cut clobbered the real artifact — fixed).
- `tests/cards-wiki/` (new) — fixture wiki: 9 vocab + 6 grammar + 1 article
  copied from `llm-wiki/`, chosen to hit every card type and edge case
  (nested-paren 粵 ヒューヒュー, ①-sense 挟む, split 必ずしも～ない, bracketing
  ～とも～ともつかない, 0-card ～といい～といい, article gcloze via ～に即して).
- `tests/cards-baseline.json` (new, committed) — expected `build(cards-wiki)`
  output (47 cards). `tests/run_cards_tests.py` (new) rebuilds and compares;
  PASS iff identical, else lists NEW/MISSING/CHANGED ids and exits non-zero;
  `--update` rewrites the baseline.
- Verified: snapshot PASS (47), negative test (mutating a reading) correctly
  fails and pinpoints the 5 affected cards; lint suite 25/25; real `cards.json`
  (638) and `lint-all` (181, 0/0) intact.

## 2026-07-16 12:24 HKT — cards.py test: redesign per design review (§10.7)

Not an ingest. Cleaned up the design flagged in review.
- **Decoupled input/output** in `cards.py`: replaced the inelegant "write
  cards.json iff no `--wiki`" conditional with independent `--wiki` (input,
  default `llm-wiki/`) and `--out` (output, default `cards.json`); it always
  writes to `--out`. Guard: **`--wiki` requires `--out`** (argparse error, exit 2)
  so a test wiki can't overwrite the real `cards.json`.
- **Runner is now a true black box:** `tests/run_cards_tests.py` invokes
  `cards.py --wiki cards-wiki --out <tmp>` as a **subprocess**, JSON-loads the temp
  file, and diffs against the baseline — exercising arg parsing → build →
  serialization → file output (not just the `build()` import). `--update` writes
  the baseline via the same CLI path.
- Verified: snapshot PASS (47); guard exits 2; a non-card-field edit (register)
  still PASSes (confirms it compares output, not inputs); lint 25/25; real
  `cards.json` (638) + `lint-all` (181, 0/0) intact. specs §10.7 updated.

## 2026-07-16 12:47 HKT — Fix: gmc double-particle bug + regression coverage

Not an ingest. User-reported bug: `～を通して` gmc front `…インターネットを＿＿…`
with choice `を通して` doubled the particle (`…をを通して…`).
- Cause: gmc used the first context, which could be an **article span whose
  surface ≠ the pattern core** — e.g. `を[[～を通して|通して]]` (surface `通して`,
  particle `を` outside the link) while the choice is the core `を通して`.
- Fix (`study/cards.py grammar_mc_cards`): gmc now requires a context where the
  **blanked span equals the choice (the core)** — the `例文` always blanks the
  whole core. gmc 31→29 (`～めく`, `～かのようだ` had only surface≠core contexts →
  correctly lose gmc; `～を通して` keeps it via 例文).
- Regression coverage: added `～を通して`, `初めての雪`, `～末に`, `～ものの` to
  `tests/cards-wiki/` so `～を通して` gets a gmc; baseline now 58 cards. Confirmed
  that reverting the fix fails the test (CHANGED `grammar-wo-tooshite::gmc`).
- Real flashcards: 3 grammar notes drifted; regenerated `～めく` (no schedule).
  `～かのようだ` + `～を通して` carry FSRS schedules — regeneration pending user
  decision (per-note --force resets the whole note's schedule).
- Both suites pass (cards 58, lint 25/25).

## 2026-07-18 — Feature: daily email quiz (§10.8)

Not an ingest. New delivery channel: a daily, self-grading, CSS-interactive MC
quiz email that grades itself **inside Apple Mail** (no JavaScript).
- **Prototype → proven on iPhone Mail.** Pure-CSS interactivity (`:checked` +
  sibling selectors + a counter score) survives Apple Mail's sanitizer. Findings:
  copy-paste into Mail's composer strips it; Gmail API/compose strips
  `<head><style>`; **only raw `text/html` via SMTP** delivers it intact.
  Prototype kept under `study/prototypes/` (`gen_email.py`, `send_quiz.py`).
- **Design (specs §10.8):** 5 questions from one article (shared context);
  MC-only; questions from `cards.json` (vocab `meaning` + grammar `gmc`); the
  reveal (意味 + （粵）, 2 例文 + （粵）) is **looked up live from the llm-wiki
  pages** — `cards.json` stays minimal (rejected enriching it: duplication /
  drift / data-minimization). Phase 1 self-graded, **no persistence** (CSS can't
  capture answers).
- **Credentials:** `study/secrets.json` (gitignored), grouped by service under an
  `smtp` key; committed `study/secrets.template.json` placeholder. **Mandatory
  file, no env fallback** (avoids stray `SMTP_*` from other sessions).
- **Implemented `study/email_quiz.py`** — reuses `cards.py` `load_pages` /
  `lint.LINK_RE` (no re-implemented page parsing); CLI `--list` / `--article` /
  `-n` / `--out` / `--send`. Byte-identical question output to the approved
  prototype; both suites still pass (cards 58, lint 25/25).
