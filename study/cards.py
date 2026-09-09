#!/usr/bin/env python3
"""Deterministic flashcard generator for the LLM-wiki (specs.md §10.2).

Derives cards from existing note fields by plain code — no AI, no per-card
authoring. The content page is the single source; `cards.json` is a rebuildable
build artifact. Reuses the frontmatter/body parsers from `wikitools/schema.py`.

Vocabulary cards:
  - reading / canto / meaning (MC) / cloze         (see §10.2)
Grammar cards (full-context, §10.2):
  - gcloze  : sentence with the pattern blanked -> produce it   (例文 + article)
  - gmc     : blanked sentence + 4 choices -> the pattern       (関連 distractors)
  - gerror  : a ✗ usage -> the ✓ fix (+ why)                    (## 間違いやすい点)

Every card carries `item_id` (the page id) and `kind` (vocab | grammar).

Usage:
    python study/cards.py            # build cards.json + print a summary
    python study/cards.py --sample   # also print a few example cards per type
"""

import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from wikitools import schema  # noqa: E402  (shared §6 schema primitives)

WIKI = REPO / "llm-wiki"
CARDS_OUT = REPO / "build" / "cards.json"
KANJI = schema.KANJI_RE

CANTO_START = re.compile(r"（粵[：:]")
PAREN_INNER = re.compile(r"（[^（）]*）")            # innermost full-width parens
SENT_SPLIT = re.compile(r"(?<=。)")
SUBHEADING = re.compile(r"(?m)^#{3,}\s.*$")      # `### A` labels in 本文 (§6.5.2)
PARA_SPLIT = re.compile(r"\n\s*\n")              # paragraph break = sentence break
EXAMPLE_HEAD = re.compile(r"(?m)^(?=\d+\.\s)")

VOCAB_TYPES = ("reading", "canto", "meaning", "cloze")
GRAMMAR_TYPES = ("gcloze", "gmc", "gerror")


# ---------------------------------------------------------------- loading
def load_pages(kind, wiki=WIKI):
    """Parse <wiki>/<kind>/*.md into dicts of {fm, first, sections, body}."""
    out = []
    for p in sorted((Path(wiki) / kind).glob("*.md")):
        fm, body = schema.parse_frontmatter(p.read_text(encoding="utf-8"))
        first, sections = schema.split_body(body)
        out.append({"path": p, "fm": fm, "first": first,
                    "sections": sections, "body": body})
    return out


def disp(hw, rd, pos=None):
    """Word display: 改ざん・する（かいざん・する） for a suru-verb,
    改ざん（かいざん） for a plain kanji noun, やがて for pure-kana. The 「・する」
    marker (shared with the page title §6.5.1 and the index §7.2) is derived from
    part_of_speech via schema.suru_suffix."""
    suru = schema.suru_suffix(pos)
    return f"{hw}{suru}（{rd}{suru}）" if KANJI.search(hw or "") else f"{hw}{suru}"


def base_card(page, kind):
    fm = page["fm"]
    return {
        "item_id": fm.get("id"),
        "kind": kind,
        "headword": fm.get("headword"),
        "reading": fm.get("reading"),
        "level": fm.get("level"),
        "tags": fm.get("tags", []),
    }


def honbun_sentences(sections):
    """The sentences of an article's `## 本文`, split paragraph by paragraph.

    A **paragraph break is a sentence boundary** even when the paragraph does not
    end in 「。」 — a closing quotation 「…ですよ」, a citation line, the last line
    of text A on a 統合理解 page — so no card front can straddle two paragraphs.
    Within a paragraph the §6.5.2 word-wrap is undone, and the `###` sub-headings
    of a multi-text page are dropped first (§6.5.2): they are structure, not prose.
    """
    body = sections.get("本文")
    if not body:
        return []
    out = []
    for para in PARA_SPLIT.split(SUBHEADING.sub("", body)):
        para = para.replace("\n", "")
        out += [s for s in SENT_SPLIT.split(para) if s.strip()]
    return out


def span_key(blanked):
    """Short content hash of a blanked sentence — the stable tail of a cloze id.

    Content-derived, never positional (§11.2): the rendered text carries no
    wikilink markup, so re-wrapping an article (§6.5.2) or marking another word in
    the same sentence leaves it unchanged and the card keeps its id — and with it
    its FSRS history (§10.4). Only editing *that sentence* mints a new card.
    """
    return hashlib.sha256(blanked.encode("utf-8")).hexdigest()[:8]


def _render_blank(sentence, target_match):
    """Render a sentence: target link -> ＿＿, other links -> their surface text."""
    parts, last = [], 0
    for m in schema.LINK_RE.finditer(sentence):
        parts.append(sentence[last:m.start()])
        parts.append("＿＿" if m.span() == target_match.span()
                     else m.group(1).split("|")[-1])
        last = m.end()
    parts.append(sentence[last:])
    return "".join(parts)


# ---------------------------------------------------------------- vocabulary
def _balanced_paren(text, start):
    """Content of the （…） whose opening `（` is at index `start`, honouring nested
    full-width parens. Returns (content, end_index_of_matching_close)."""
    depth, i = 0, start
    while i < len(text):
        if text[i] == "（":
            depth += 1
        elif text[i] == "）":
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i
        i += 1
    return text[start + 1:], len(text)          # unbalanced: take the rest


def parse_imi(imi_text):
    """Return (japanese_definition, cantonese_gloss_or_None) from a ## 意味 body.

    Handles a （粵：…）gloss that itself contains parentheses, e.g. （粵：（風）呼呼聲。）,
    by matching the balanced closing `）` rather than the first one.
    """
    canto = None
    m = CANTO_START.search(imi_text)
    if m:
        inner, _ = _balanced_paren(imi_text, m.start())   # from the outer （ of （粵
        inner = inner[len("粵："):]                        # drop the 粵： label
        g = re.split(r"English[：:]|英[：:]", inner)[0]
        canto = g.replace("\n", "").strip().strip("。、 ")

    jp = imi_text                                          # drop ALL parentheticals,
    prev = None                                            # innermost-first for nesting
    while prev != jp:
        prev, jp = jp, PAREN_INNER.sub("", jp)
    jp = jp.replace("\n", "").strip().split("。")[0].strip()  # first sentence
    jp = re.sub(r"^[①-⑳]\s*", "", jp)                     # drop a leading sense marker
    return jp, canto


def reading_cards(vocab):
    cards = []
    for v in vocab:
        hw = v["fm"].get("headword", "")
        if not KANJI.search(hw):
            continue                                     # pure kana: nothing to test
        c = base_card(v, "vocab")
        c.update(id=f"{c['item_id']}::reading", type="reading",
                 prompt="読みは？", front=hw, back=v["fm"].get("reading"))
        cards.append(c)
    return cards


def canto_cards(vocab):
    cards = []
    for v in vocab:
        _, canto = parse_imi(v["sections"].get("意味", ""))
        if not canto:
            continue                                     # no Cantonese gloss to prompt from
        c = base_card(v, "vocab")
        c.update(id=f"{c['item_id']}::canto", type="canto",
                 prompt="この意味の言葉は何ですか？", front=canto,
                 back=disp(c["headword"], c["reading"], v["fm"].get("part_of_speech")))
        cards.append(c)
    return cards


def meaning_cards(vocab):
    """4-choice MC: word -> definition. Distractors: same POS first, then any."""
    defs = {}
    for v in vocab:
        jp, _ = parse_imi(v["sections"].get("意味", ""))
        if jp:
            defs[v["fm"]["id"]] = jp
    cards = []
    for v in vocab:
        vid = v["fm"]["id"]
        answer = defs.get(vid)
        if not answer:
            continue
        pos = v["fm"].get("part_of_speech")
        rng = random.Random(vid)                         # reproducible distractors
        same = [defs[o["fm"]["id"]] for o in vocab
                if o["fm"]["id"] != vid and o["fm"].get("part_of_speech") == pos
                and defs.get(o["fm"]["id"])]
        other = [defs[o["fm"]["id"]] for o in vocab
                 if o["fm"]["id"] != vid and o["fm"].get("part_of_speech") != pos
                 and defs.get(o["fm"]["id"])]
        rng.shuffle(same); rng.shuffle(other)
        distractors, seen = [], {answer}
        for d in same + other:
            if d not in seen:
                distractors.append(d); seen.add(d)
            if len(distractors) == 3:
                break
        if len(distractors) < 3:
            continue                                     # not enough to form an MC
        choices = [answer] + distractors
        rng.shuffle(choices)
        c = base_card(v, "vocab")
        c.update(id=f"{vid}::meaning", type="meaning", prompt="意味は？",
                 front=disp(c["headword"], c["reading"], v["fm"].get("part_of_speech")),
                 choices=choices, answer_index=choices.index(answer), back=answer)
        cards.append(c)
    return cards


def cloze_cards(articles, vocab_by_headword):
    """Blank a [[dict|surface]] span in an article sentence; answer = dict-form."""
    cards = []
    for art in articles:
        aid = art["fm"]["id"]
        for sent in honbun_sentences(art["sections"]):
            if "[[" not in sent:
                continue
            for m in schema.LINK_RE.finditer(sent):
                v = vocab_by_headword.get(schema.link_target(m.group(1)))
                if not v:
                    continue                             # grammar link or unknown: skip
                front = _render_blank(sent, m).strip()
                if "＿＿" not in front:
                    continue
                c = base_card(v, "vocab")
                c.update(
                    id=f"{v['fm']['id']}::cloze::{aid}::{span_key(front)}", type="cloze",
                    prompt="空欄に入る語は？", front=front,
                    back=disp(c["headword"], c["reading"], v["fm"].get("part_of_speech")),
                    surface=m.group(1).split("|")[-1], article=aid)
                cards.append(c)
    return cards


# ---------------------------------------------------------------- grammar
def example_sentences(sections):
    """The sentence line of each numbered 例文 block."""
    out = []
    for block in EXAMPLE_HEAD.split(sections.get("例文", "")):
        m = re.match(r"\s*\d+\.\s*(.+)", block)
        if m:
            out.append(m.group(1).strip())
    return out


def contiguous_core(headword):
    """Pattern core for a contiguous pattern (only leading/trailing ～), else None."""
    parts = [p for p in headword.split("～") if p]
    return parts[0] if len(parts) == 1 else None


def blank_target(headword):
    """String to blank in a 例文: the contiguous core, or a distinctive leading
    fragment of a split pattern (必ずしも, 到底, からといって). None if unreliable."""
    core = contiguous_core(headword)
    if core:
        return core
    parts = [p for p in headword.split("～") if p]
    lead = parts[0] if parts else ""
    if lead and (KANJI.search(lead) or len(lead) >= 4):
        return lead
    return None


def related_cores(sections):
    """Distractor pattern cores from ## 関連 wikilinks."""
    cores = []
    for inner in schema.LINK_RE.findall(sections.get("関連", "")):
        core = inner.split("|")[0].replace("～", "").strip()
        if core:
            cores.append(core)
    return cores


def parse_mistake(sections):
    """(wrong, correct, reason) from a ## 間違いやすい点 with a ✗/✓ pair, else None.

    Handles full-sentence pairs (✗ … 。 / ✓ … 。) and short inline pairs on one
    line (✗ …phrase… ✓ …phrase…). Reason: an inline `— …` if present, else the
    explanation text preceding the ✗."""
    sec = sections.get("間違いやすい点", "")
    xm = re.search(r"✗\s*(.+?)\s*(?=。|✓|\n|$)", sec)
    vm = re.search(r"✓\s*(.+?)\s*(?=。|\n|$)", sec)
    if not (xm and vm):
        return None
    rm = re.search(r"[—―\-]\s*(.+?)(?=。|\n|$)", sec[xm.end():vm.start()])
    reason = (rm.group(1).strip() if rm else
              sec[:xm.start()].strip().lstrip("-").strip().replace("\n", " "))
    return xm.group(1).strip(), vm.group(1).strip(), reason


def grammar_context(grammar, articles):
    """[(blanked_sentence, surface, source)] where the pattern can be blanked:
    articles give an exact [[hw|surface]] span; 例文 give a core/fragment match."""
    hw = grammar["fm"]["headword"]
    cands = []
    for art in articles:
        aid = art["fm"]["id"]
        for sent in honbun_sentences(art["sections"]):
            for m in schema.LINK_RE.finditer(sent):
                if schema.link_target(m.group(1)) == hw:
                    blanked = _render_blank(sent, m).strip()
                    if "＿＿" in blanked:
                        cands.append((blanked, m.group(1).split("|")[-1],
                                      f"{aid}::{span_key(blanked)}"))
    tgt = blank_target(hw)
    if tgt:
        for sent in example_sentences(grammar["sections"]):
            idx = sent.find(tgt)
            if idx != -1:
                blanked = sent[:idx] + "＿＿" + sent[idx + len(tgt):]
                cands.append((blanked, tgt, f"例文::{span_key(blanked)}"))
    return cands


def grammar_cloze_cards(grammar, articles):
    hw = grammar["fm"]["headword"]
    cards = []
    for blanked, surface, src in grammar_context(grammar, articles):
        c = base_card(grammar, "grammar")
        c.update(id=f"{c['item_id']}::gcloze::{src}", type="gcloze",
                 prompt="空欄に入る文型は？", front=blanked, surface=surface,
                 back=disp(hw, grammar["fm"].get("reading")))
        cards.append(c)
    return cards


def grammar_mc_cards(grammar, articles, level_cores):
    hw = grammar["fm"]["headword"]
    core = contiguous_core(hw)                 # clean choices only for contiguous patterns
    if not core:
        return []
    # the blanked span must equal the choice (the core), so inserting a choice
    # reconstructs the sentence — skip article spans like を[[…|通して]] (surface
    # ≠ core) that would double a particle. 例文 spans blank the whole core.
    ctx = next((blanked for blanked, surface, _ in grammar_context(grammar, articles)
                if surface == core), None)
    if ctx is None:
        return []
    rng = random.Random(grammar["fm"]["id"])
    rel = [c for c in related_cores(grammar["sections"]) if c != core]
    fill = [c for c in level_cores.get(grammar["fm"]["level"], []) if c != core and c not in rel]
    rng.shuffle(rel); rng.shuffle(fill)
    distractors, seen = [], {core}
    for d in rel + fill:
        if d not in seen:
            distractors.append(d); seen.add(d)
        if len(distractors) == 3:
            break
    if len(distractors) < 3:
        return []
    choices = [core] + distractors
    rng.shuffle(choices)
    c = base_card(grammar, "grammar")
    c.update(id=f"{c['item_id']}::gmc", type="gmc",
             prompt="空欄に入る文型を選びなさい：", front=ctx,
             choices=choices, answer_index=choices.index(core), back=core)
    return [c]


def grammar_error_cards(grammar):
    parsed = parse_mistake(grammar["sections"])
    if not parsed:
        return []
    wrong, correct, reason = parsed
    c = base_card(grammar, "grammar")
    c.update(id=f"{c['item_id']}::gerror", type="gerror",
             prompt="誤りを正しなさい：", front=f"✗ {wrong}",
             back=(f"{reason}　" if reason else "") + f"✓ {correct}")
    return [c]


# ---------------------------------------------------------------- driver
def build(wiki=WIKI):
    vocab = load_pages("vocabulary", wiki)
    grammar = load_pages("grammar", wiki)
    articles = load_pages("articles", wiki)
    by_headword = {v["fm"].get("headword"): v for v in vocab}

    cards = (reading_cards(vocab) + canto_cards(vocab)
             + meaning_cards(vocab) + cloze_cards(articles, by_headword))

    level_cores = {}
    for g in grammar:
        core = contiguous_core(g["fm"]["headword"])
        if core:
            level_cores.setdefault(g["fm"]["level"], []).append(core)
    for g in grammar:
        cards += grammar_cloze_cards(g, articles)
        cards += grammar_mc_cards(g, articles, level_cores)
        cards += grammar_error_cards(g)

    # content-hashed cloze ids can only collide on an identical blanked sentence
    # (the same sentence twice in one article); disambiguate deterministically.
    seen = {}
    for c in cards:
        seen[c["id"]] = n = seen.get(c["id"], 0) + 1
        if n > 1:
            c["id"] = f"{c['id']}-{n}"

    cards.sort(key=lambda c: (c["type"], c["id"]))       # stable output
    return cards, len(vocab), len(grammar), len(articles)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate the flashcard JSON from the LLM-wiki.")
    ap.add_argument("--sample", action="store_true", help="print example cards per type")
    ap.add_argument("--wiki", help="wiki root to read from (default llm-wiki/)")
    ap.add_argument("--out", help="path to write the cards JSON to (default cards.json)")
    args = ap.parse_args(argv)
    if args.wiki and not args.out:      # input & output are independent; guard the footgun
        ap.error("--wiki requires --out (refusing to overwrite the real cards.json from another wiki)")

    cards, n_vocab, n_gram, n_art = build(args.wiki or WIKI)

    by_type = {}
    for c in cards:
        by_type[c["type"]] = by_type.get(c["type"], 0) + 1
    print(f"cards.py: {n_vocab} vocab, {n_gram} grammar, {n_art} articles -> {len(cards)} cards")
    for t in VOCAB_TYPES + GRAMMAR_TYPES:
        print(f"  {t:8} {by_type.get(t, 0)}")

    out = Path(args.out) if args.out else CARDS_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"written: {out}")

    if args.sample:
        for t in VOCAB_TYPES + GRAMMAR_TYPES:
            ex = next((c for c in cards if c["type"] == t), None)
            if ex:
                print(f"\n--- sample [{t}] ---")
                print(json.dumps(ex, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
