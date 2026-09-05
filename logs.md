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

## 2026-07-20 — Feature: card scheduler, urgency & exposure (§10.1, §10.9)

Not an ingest. New `study/scheduler.py` — a read-model over two schedulers, per
the design agreed in specs §10.1.
- **Read-model, not a merge.** Obsidian owns FSRS (read-only for us); we own
  *exposure*. `scheduler.py` blends both into a per-card **urgency** (0–100, tunable
  linear model: recency + frequency + FSRS-fragility, +future error-rate).
- **`progress/progress.json`** — single committed file, namespaced `cards`
  (`exposure` + derived `urgency`) + `articles` (`last_served`, the rotation
  signal). **Atomic sanity-checked writes** (temp → validate → `os.replace`): the
  validator rejects dropping a card *with exposure*, regressed exposure, dropped
  articles, or out-of-range scores, leaving the original intact; urgency-only
  entries are regenerable and may be dropped. Committed as an empty skeleton.
- **FSRS read-only scan** parses the plugin's `<!--SR:!fsrs,…-->` comments
  (due/last_review/stability/difficulty/state), joining block→card-id by **content
  match** (reusing `obsidian_cards.card_block`/`canonical`) — 68/167 pushable cards
  matched in the live vault. Tolerant: unknown formats → "no FSRS data".
- **`email_quiz.py` wired to it:** selection is now least-recently-served article
  + top-N by urgency; `record_delivery` logs exposure only on a successful
  `--send` (preview is side-effect-free). Rotation verified (3 sends → 3 distinct
  articles).
- **Tests:** `tests/run_scheduler_tests.py` (24) — pure urgency, FSRS parse+join,
  atomic-write safety. All suites green: lint 25/25, cards 58, scheduler 24/24.

## 2026-07-27 — Housekeeping: build/ for regenerable artifacts + spec fixes

Not an ingest. File-location cleanup delineating data tiers (specs §5).
- **New `build/` (gitignored)** collects the two regenerable artifacts —
  `cards.json` (was repo root) and `daily-quiz.html` (was `study/`). Updated
  `cards.py` `CARDS_OUT`, `email_quiz.py` `PREVIEW_OUT` (+ `mkdir` on write),
  `prototypes/gen_email.py`, and `.gitignore` (`build/`). Consumers via
  `cardgen.CARDS_OUT` followed automatically; regenerated into `build/`, verified
  pipeline + all suites (25/58/24). Precious state (`flashcards/`,
  `progress/progress.json`) deliberately left in place.
- **Spec §5 rewrite:** documented the three data tiers (authored source /
  code-maintained precious state / regenerable) and the regenerability-vs-tracking
  mapping. **Fixed a bug:** §5 said `llm-wiki/` was the Obsidian vault root, but
  `.obsidian/` is at `bunryu/` — the vault root is `bunryu/` (so the SR plugin sees
  `flashcards/`); corrected to match §10.4.
- Note: the daily launchd send has been running for real — `progress.json` shows a
  full week of article rotation (all 5 articles), preserved intact through the move.

## 2026-07-30 — Ingest: raw/哲学の目的.md (article + 10 items)

Ingested the Tsuchiya Kenji essay per §8. All 11 pages **new** (no updates).
- **`llm-wiki/articles/哲学の目的.md`** (new) — article page (word_count ≈ 560).
  `## 本文` re-wrapped per §6.5.2, `[[...]]` markers preserved as wikilinks; the
  `<u>…</u>①②` reference markers and the source citation line kept for the quiz.
  First-ever use of §8.2 step 5: the `## 読解問題` section's three ```quiz``` blocks
  (quizblock plugin) copied to the page end.
- **Vocabulary (6, new):** [[あくまでも]] (adv), [[手っ取り早い]] (i-adj),
  [[探究]] (noun), [[厳密]] (na-adj), [[思い込み]] (noun), [[確信]] (noun).
- **Grammar (4, new):** [[～わけではない]] and [[～わけでもない]] (cross-linked
  part-negation pair — source marked both distinctly), [[いかに～べきか]],
  [[～しかない]] (dictionary forms; article links them via aliases, e.g.
  `[[～しかない|言うしかありません]]`, `[[いかに～べきか|いかに生きるべきか]]`).
- **Lint:** clean — 192 files, 0 errors, 0 warnings.
- **Items needing human review (footnotes):**
  1. **Title has no top `##` heading.** Unlike other raw files, this source starts
     with body text; headword/filename taken as `哲学の目的` (the `<u>…</u>①`
     phrase + raw filename) rather than a `##` heading.
  2. **OCR fixes in the quiz text (raw left untouched per §8.3).** Corrected three
     garbled runs in the copied quiz blocks: `無意いみおもじんせいおく味` →
     `無意味`; `ことがりゆうせいかい理由` → `ことが理由`; `もっといせいかい最も`
     → `最も`. The raw source still contains these; worth fixing there too.
  3. **Tilde normalization.** Raw used a wave dash `〜` (U+301C) in `いかに〜べきか`;
     normalized to the vault's fullwidth `～` (U+FF5E) so the wikilink resolves.

## 2026-07-31 — Ingest: raw/食料安全保障.md (article + 18 items)

Ingested the Yamaguchi Hidemasa editorial (食環境科学入門) per §8. All 19 pages
**new** (no updates); first ingest to run the new §8.2 step-3 `index.md`
regeneration.
- **`llm-wiki/articles/食料安全保障.md`** (new) — article page (word_count ≈ 600).
  `## 本文` re-wrapped per §6.5.2, all 18 `[[…]]` markers preserved; `<u>…</u>①②`
  reference markers + citation kept. Source's three `（注）` moved into `## 語釈`.
  The `## 読解問題` block's three ```quiz``` blocks copied verbatim (§8.2 step 5).
- **Vocabulary (14, new):** [[飽食]] [[確保]] [[側面]] [[飢餓]] [[到来]] [[倫理]]
  [[円滑]] [[志向]] [[せめて]] [[粗食]] [[禁欲]] [[汚染]] [[愚か]] [[再考]].
- **Grammar (4, new):** [[～を目前に]] [[～てまで]] [[～こそ]] [[～とともに]]
  (dictionary form; article links inflected surfaces via aliases, e.g.
  `[[～てまで|捨ててまで]]`, `[[～を目前に|目前に]]`, `[[～こそ|こそ]]`).
- **`index.md`** regenerated (§7.2): now 158 語彙 / 46 文法 / 7 記事.
- **Lint:** clean — 211 files, 0 errors, 0 warnings.
- **Notes / human-review footnotes:**
  1. **Punctuation normalized.** Source body used full-width commas `，` (U+FF0C);
     normalized to `、` in `## 本文` / `## 語釈` for consistency with the rest of
     the vault (and this file's own quiz blocks). Quiz blocks copied as-is, so a
     couple of `，` remain inside them by design.
  2. **`～を目前に` reading fixed at lint.** First wrote `reading: ～を目前に`
     (headword copy); the linter correctly rejected it because 目前 is kanji, so
     the §6.5.1 title needs the kana reading — corrected to `～をもくぜんに`
     (title `# ～を目前に（～をもくぜんに）`).
  3. **`～を目前に` marked focus** (`focus: true`) in Obsidian during ingest;
     preserved.
  4. **`あまりに～すぎる` deliberately not ingested** — the ①-referenced phrase is
     discontiguous and a near-duplicate of existing `あまりにも`; left for a future
     cross-link rather than a new page (data-minimization).

## 2026-07-31 — Feature: suru-verb 「・する」 display + POS-grouped index

Not an ingest. Surfaces サ変 (suru-verb) items distinctly and groups the index
by part-of-speech. Spec updated first (§6.2, §6.5.1, §7, §7.1, §7.2).
- **Convention (§6.2):** a サ変名詞 (verbal noun taking する) is `suru-verb`; a
  noun that does not is `noun`. Suru-ness lives **only** in `part_of_speech` —
  never in `headword`.
- **Display (§6.5.1, §7.2):** suru-verbs render `勉強・する（べんきょう・する）` in
  both the page `# title` and the index row (shared `lint.suru_suffix`). `index.py`
  now sub-groups `## 語彙` by POS into 名詞/動詞/形容詞/副詞/表現 (noun+suru-verb →
  名詞); 文法/記事 stay flat.
- **Lint (§7):** title check is POS-aware (expects 「・する」 for suru-verbs); new
  rule — `headword` must not end in する for noun/suru-verb.
- **Content migration (14 pages):** reclassified 8 noun→suru-verb (確保・汚染・
  到来・志向・探究・確信・再考・禁欲); retitled 5 already-suru pages (会釈・処分・
  勘違い・合意・導入); renamed `左右する`→`左右` (headword/reading/title/filename)
  and aliased its 2 wikilinks in 裁判員のもやもや.md to `[[左右|左右する]]`.
- **Tests/baselines:** lint fixtures +3 (suru title ±, headword-する) → 30/30;
  index fixtures +3 (動詞/形容詞/表現) + 改ざん→suru-verb, baseline regenerated →
  14/14. cards (58) unaffected — its fixture vault is separate; scheduler 24/24.
  Full vault lint clean (211/0/0). `build/cards.json`/`index.md` regenerated.
- **Flashcards (follow-up):** applied the 「・する」 display to the Obsidian SR
  channel too. `cards.py` `disp()` is POS-aware; `obsidian_cards.py` canto card
  now reuses the rendered `c['back']` (dropped its duplicate `disp` + dead `lint`
  import); §6.5.1/§10.2 note flashcards as a third surface (Reading card exempt).
  Cards fixture `左右する`→`左右` (mirrors the vault rename); cards baseline
  updated. **Full flashcards resync** (`obsidian_cards.py --force`): 28 created +
  175 regenerated, 0 drift — this **reset 28 local pilot FSRS schedules** (OK'd,
  pilot phase). Root-caused the drift to ingestion never regenerating
  cards.json/flashcards (spec gap, §8.2 — under review).

## 2026-07-31 — Refactor: scraper/ → wikitools/ + extract schema.py

Not an ingest. Fixes a layering smell (the linter doubled as the shared parsing
library) and a misnamed package (specs §5 code-layering; CLAUDE.md modular-design
tenet).
- **New `wikitools/schema.py`** — the §6 schema as code (foundation):
  `parse_frontmatter`, `split_body`, `link_target`, `strip_code`,
  `KANJI_RE`/`LINK_RE`, enum sets, `suru_suffix`, `expected_title`. Depends on
  nothing.
- **`git mv scraper/ → wikitools/`** (renames preserved): `lint.py` is now a pure
  **consumer** of `schema`; `index.py` imports `schema` (not lint). `study/cards.py`
  imports `schema` and **no longer imports the validator at all**; `email_quiz.py`
  uses `cardgen.schema.LINK_RE`. Test runners import `wikitools.{lint,index}`.
- **One-way layering now holds:** `wikitools/` ← `study/` ← `tests/`.
- `index.py` `EDIT_NOTE` updated (the `index.md` header now cites
  `wikitools/index.py`); index baseline regenerated; cards baseline unchanged.
- **Verified:** lint 30/30, index 14/14, cards 58, scheduler 24/24; real-vault
  lint 211/0/0 via `wikitools/lint.py`; `index.md` + `build/cards.json` regenerated.

## 2026-09-05 — Ingest 地域をまわって考えたこと（小熊英二）/c embedded quizzes

`ingest article raw/地域をまわって考えたこと.md` (§8). 10 marked items, **all new
headwords** — no existing page needed enhancing.
- **New article `llm-wiki/articles/地域をまわって考えたこと.md`** — 本文 re-wrapped
  per §6.5.2 (~40–50 全角/line, breaks at particle/clause boundaries, wikilinks
  intact), 原文注1–7 folded into `## 語釈`, 注目語彙・文法 split 語彙/文法, and the
  source's `## 読解問題` (4 `quiz` blocks) copied verbatim to the end. `word_count`
  888 computed from the rendered 本文.
- **New vocabulary (9)**: `暗黙のうちに` (expression), `対極` (noun), `往々にして`
  (adverb), `懐疑的` (na-adj), `卑下` (**suru-verb**), `経緯` (noun), `壊滅`
  (**suru-verb**), `煩雑` (na-adj), `異なる` (godan-verb, N2 — 基本語だが本文の
  対比の軸なので採録).
- **New grammar (1)**: `とはいえ` — 文頭用法（本文）と接続用法の両方を記載。
  Named without the `～` prefix, matching the sentence-initial 接続詞 precedent
  (`それにしても`, which already carried a dangling `[[とはいえ]]` link — now
  resolved).
- **Source markup corrected on the way in** (raw is untouched, §8.3): the source
  marked `[[卑下する|卑下]]`; per §6.2 suru-ness lives in `part_of_speech`, so the
  page is `卑下` (`suru-verb`, title 「卑下・する（ひげ・する）」) and the body links
  plain `[[卑下]]`.
- **Ambiguous classifications recorded** (§8.3): `往々にして` → `adverb` (a set
  副詞句; `expression` was the alternative); `暗黙のうちに` → `expression` rather
  than a bare `暗黙` noun, since the fixed 「〜のうちに」 phrase is the N1 item;
  `異なる` levelled **N2**, not N1.
- **No `##` title heading in the source** — §8.2 step 1 takes the essay title from
  the top `##` heading, but this source starts straight into 本文. Fell back to the
  raw filename (＝出典の書名) for both `headword` and the article filename; noted in
  the page's `## メモ`. Worth a spec sentence for the heading-less case.
- **Verified:** real-vault lint **222 files, 0 error(s), 0 warning(s)**; suites
  lint 30/30, index 14/14, cards 58, scheduler 24/24. Regenerated `index.md`
  (167 語彙 / 47 文法 / 8 記事) and `build/cards.json` (783 cards);
  `obsidian_cards.py` created the **10 new flashcard notes** (append-only,
  203 existing notes untouched).
- **Flashcard drift, root cause found — left unfixed by design.** After this
  ingest `obsidian_cards.py --check` reports **174 drifted notes**; measured
  against the same vault with the 10 new pages removed it is **0**. So the drift
  is not stale generation — the MC distractors (`meaning` / `gmc`) are sampled
  from the **whole-vault pool** (`random.Random(item_id)` seeds *which* draw, but
  the pool is global), so **any** ingest reshuffles distractors vault-wide. The
  §10.4 schedule-preserving resync (`regen.py` + stable card ids) is still
  **unimplemented** — the only lever today is `--force`, which would **reset all
  174 FSRS schedules**. Not run: the on-disk distractors are still valid, and
  review history outweighs distractor freshness. Two candidate fixes for the
  §10.4 work: implement the id-matched resync, or make distractor draws depend
  only on a stable per-item neighbourhood so the pool stops being global.

## 2026-09-05 — schema.py: hand-rolled frontmatter reader → yaml12 (YAML 1.2)

Not an ingest. `yaml12` became available; adopted it **only** where it simplifies
(specs §7, §11.1; CLAUDE.md reuse-libraries tenet).
- **`wikitools/schema.py`** — `parse_frontmatter` drops the ~30-line hand-rolled
  reader for a single `yaml12.parse_yaml` call (~6 lines). Values now carry real
  types (`focus`→bool, `word_count`→int, `tags`→list[str]); dates stay strings,
  since YAML 1.2 has no timestamp type, so the §7 `YYYY-MM-DD` check is
  unaffected. New `FrontmatterError` for a `---` block that is not valid YAML.
- **`wikitools/lint.py`** — catches `FrontmatterError` and reports
  `malformed YAML frontmatter: …`. This is a **new rule**, not just a port: the
  old reader silently skipped lines it could not parse, so broken YAML was the
  one breakage class the linter could not see.
- **New negative fixture** `tests/test-llm-wiki/vocabulary/neg-bad-yaml.md`
  (unterminated `[`) + its `EXPECTED` entry; lint suite 30 → **31 cases**.
- **New `requirements.txt`** (the file specs §5 already listed but that did not
  exist): pins `py-yaml12>=0.1.0`, the project's sole runtime dependency.
- **Equivalence checked before switching:** parsed all **272** pages
  (llm-wiki 222 + both fixture vaults) with the old and new readers — 271
  identical, 0 differing, 0 parse errors (the 272nd is the no-frontmatter
  fixture).
- **Verified:** lint 31/31, index 14/14, cards 58, scheduler 24/24; real-vault
  lint 222/0/0; regenerated `build/cards.json` and `index.md` are
  **byte-identical** to before the change.
- **Specs updated** (§5 tree, §7 parse rule + stdlib-only claim, §7.1 fixture
  list, §11.1 decision record incl. the compiled-wheel trade-off).

## 2026-09-05 — Implement §10.3 regen.py + §10.4 schedule-preserving resync

Not an ingest. Closes §12 near-term item 3; spec critiqued and amended first
(two mechanisms in §10.4/§10.1 conflicted — see below).

**Spec changes made before coding**
- **§10.4 resync mechanism changed: inline id marker → sidecar.** The spec had
  each card carry "a stable card id in a marker invisible to Obsidian", hedged by
  a build note that its non-interference with the SR plugin's card-boundary
  parsing "must be verified when implemented". Replaced with the id↔block mapping
  recorded **outside** the note, in `.card-index.json` (`{"seq": …, "cards":
  {note: [card_id, …]}}`). Nothing of ours is written into a note, so the plugin
  cannot be confused by it, and `.card-index.json` was already precious state
  (losing it renumbers every note) — no new risk class.
- **§10.1's join was inconsistent with §10.4** — it aligned FSRS blocks to card
  ids "by front text", which fails for exactly the case the resync exists for (a
  card whose front changed). Both now name the one sidecar.
- **New §11.2 gap: cloze ids embed a position** (`::cloze::{article}::{n}` is the
  wikilink ordinal, `::gcloze::{article}::{n}` the sentence ordinal), so editing
  an article renumbers them and the resync reads that as remove + add. Recorded,
  reported at runtime rather than silent, and promoted to §12 near-term item 3
  (fix before real FSRS history accumulates; it churns the §10.7 baseline).
- **§10.2's "global distractor pool" gap (logged 2026-09-05) is dissolved, not
  worked around**: MC distractors are redrawn vault-wide on every ingest, but the
  *card id* is unchanged, so the resync rewrites those blocks and keeps their
  schedules.

**Code**
- **New `study/regen.py`** — one idempotent entry point running `cards.py` →
  `index.py` → `obsidian_cards.py` in dependency order, in-process. `--only
  {cards,index,flashcards}` is repeatable; `select()` is a pure helper so the
  ordering is testable.
- **`study/obsidian_cards.py` — append-only → schedule-preserving.** A changed
  note is now rewritten in place with each `<!--SR:…-->` re-attached to its card
  by id (blocks aligned via the recorded id list; positional fallback when a note
  has no record). Unchanged notes are left byte-identical. Dropped schedules are
  reported with their card id. `--force [item…]` keeps its reset meaning.
  Added `--wiki` / `--flashcards` with a `--wiki` requires `--flashcards` guard
  (mirrors `cards.py` §10.7), which is what lets the tests run without touching
  the real deck. Manifest migrates the legacy flat `{item_id: NNNN}` form,
  preserving the sequence numbers that name every note.
- **New `tests/run_regen_tests.py`** — 9 cases over a *copy* of `tests/cards-wiki`
  and a throwaway deck: create; idempotence (byte-identical re-run); carry-over on
  a reworded card; drop reported when a card disappears (removing the `[[導入]]`
  link kills its cloze card); added card starts fresh; `--force` resets;
  `--wiki`-without-`--flashcards` guard; legacy-manifest migration; `--only`
  ordering.

**Verified:** lint 31/31, index 14/14, cards 58, scheduler 24/24, **regen 9/9**.
Live run: `regen.py` rebuilt `cards.json` + `index.md` (both unchanged) and
**resynced 174 notes / 39 unchanged**; `--check` now reports **0 drifted**; a
second `regen.py` reports **0 resynced, 213 unchanged** (idempotent).
Note the 174 rewrites cost nothing: **0 of 213 notes carried an FSRS schedule**
(the 28 pilot schedules were reset on 2026-07-31 and nothing has been reviewed
since), so the resync landed with no history at stake.

## 2026-09-05 — Content-derived cloze/gcloze card ids (§10.4, §11.2 closed)

Not an ingest. Removes the last positional coupling in the card ids, so the
§10.4 resync can actually keep review history across a re-ingest.
- **`study/cards.py`** — new `span_key(blanked)` = first 8 hex of
  `sha256(blanked sentence)`. Ids become `…::cloze::{article}::{h}` and
  `…::gcloze::{article}::{h}` (`例文::{h}` for example-derived gcloze), replacing
  the wikilink ordinal / sentence ordinal. The hash input is the **rendered**
  blanked sentence — `_render_blank` has already resolved other wikilinks to
  surface text — so re-wrapping an article (§6.5.2) or marking another word in the
  same sentence leaves the id untouched. `build()` gained a deterministic `-2`
  suffix for the only possible collision (the same blanked sentence twice in one
  article).
- **`tests/run_regen_tests.py`** — new case `cloze_id_survives_reingest`
  simulates a re-ingest (re-wrap a line **and** insert `[[制度]]` before an
  existing cloze target in the same sentence — both of which used to renumber the
  id) and asserts the ids are unchanged *and* an injected FSRS schedule is still
  attached afterwards. Suite 9 → **10 cases**.
- **`tests/cards-baseline.json`** regenerated via `--update` (deliberate, §10.7):
  30 lines, all id strings plus the re-sort they cause — **no card content
  changed** (verified by comparing the full card bag ignoring ids: 783 = 783,
  identical).

**Obsidian-visible impact — checked, and it is layout-only.** Same 783 cards,
same text, same decks, same note filenames. **14 of 213 notes** had their blocks
re-ordered within the note (block order is by `(type, id)`, and the ids changed);
the other 199 are byte-identical. Nothing was mis-attached: **0 notes carry an
FSRS schedule** and `progress.json` holds **0 cloze/gcloze keys** (only `meaning`
+ `gmc`), so this migration — the one time ids *had* to churn — cost no history.
Reviewing is unaffected either way: the SR plugin schedules each card
independently of its position in the note. Residual cosmetic churn (editing a
sentence can move its block) is recorded as a §11.2 note rather than fixed, since
avoiding it means carrying a per-item ordinal on every card.

**Verified:** lint 31/31, index 14/14, cards 58, scheduler 24/24, regen 10/10;
`regen.py` → 14 resynced / 199 unchanged / 0 schedules dropped; `--check` 0
drifted; second run 0 resynced / 213 unchanged; `index.md` and `progress.json`
untouched.
