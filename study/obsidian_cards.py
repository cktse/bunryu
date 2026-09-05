#!/usr/bin/env python3
"""Render deterministic cards into Obsidian Spaced-Repetition notes (specs §10.4).

One note per item -> flashcards/card-{kind}-{NNNN}.md (kind = vocab | grammar),
where NNNN is a stable per-kind sequence number kept in flashcards/.card-index.json.
The filename is **answer-opaque** (the SR plugin shows the note name during
review), and the note has **no heading / no `Source:` backlink** — the link to
the llm-wiki page is embedded in each card's *answer* via `[[headword|display]]`.

Card layouts (blank-line separated; deck tag first):
  vocab   : canto / cloze / meaning(MC) / reading   (see git history / §10.2)
  grammar : gcloze `…==[[hw|surface]]==…`
            gmc    blanked sentence + 4 choices + `<br>==core = [[hw]]==`
            gerror `誤りを正しなさい： ✗ …::… ✓ … [[hw]]`

Generation is **schedule-preserving**: a changed note is rewritten in place and
each `<!--SR:…-->` schedule is re-attached to its card **by card id**, so review
history survives rewordings, reflows and redrawn MC distractors. The id↔block
mapping is the ordered card-id list recorded per note in `.card-index.json`;
nothing of ours is written into the note itself (§10.4).

    python study/obsidian_cards.py            # create + resync (safe, default)
    python study/obsidian_cards.py --check    # report notes whose cards drifted
    python study/obsidian_cards.py --force grammar-nisaishite ～に際して   # specific
    python study/obsidian_cards.py --force    # regenerate ALL (resets schedules!)
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from study import cards as cardgen  # noqa: E402

FLASH = REPO / "flashcards"
INDEX_NAME = ".card-index.json"
TYPE_ORDER = {"canto": 0, "cloze": 1, "meaning": 2, "reading": 3,
              "gcloze": 4, "gmc": 5, "gerror": 6}
SR_COMMENT = re.compile(r"<!--SR:.*?-->")
BLANK_LINE = re.compile(r"\n\s*\n")


# ---------------------------------------------------------------- rendering
def card_block(c):
    hw, rd, t = c["headword"], c["reading"], c["type"]
    if t == "reading":
        return f"{hw}::[[{hw}|{rd}]]"
    if t == "canto":
        # reuse the word display already rendered by cards.py (carries 「・する」
        # for suru-verbs, §10.2) rather than re-deriving it here
        return f"（粵）{c['front']}::[[{hw}|{c['back']}]]"
    if t in ("cloze", "gcloze"):
        return c["front"].replace("＿＿", f"==[[{hw}|{c['surface']}]]==")
    if t in ("meaning", "gmc"):
        lines = [c["front"]]
        lines += [f"{i}. {ch}" for i, ch in enumerate(c["choices"], 1)]
        lines.append(f"<br>=={c['back']} = [[{hw}]]==")
        return "\n".join(lines)
    if t == "gerror":
        return f"誤りを正しなさい： {c['front']}::{c['back']}　[[{hw}]]"
    raise ValueError(t)


def ordered_cards(cards):
    """The note's cards in written order — the order `.card-index.json` records."""
    return sorted(cards, key=lambda c: (TYPE_ORDER[c["type"]], c["id"]))


def note_text(cards, schedules=None):
    """Render the note; re-attach each card's `<!--SR:…-->` schedule if given."""
    schedules = schedules or {}
    kind, level = cards[0]["kind"], cards[0]["level"]
    blocks = []
    for c in ordered_cards(cards):
        block = card_block(c)
        sr = schedules.get(c["id"])
        if sr:
            block += "\n" + sr
        blocks.append(block)
    return f"#flashcards/{kind}/{level}\n" + "\n\n".join(blocks) + "\n"


def canonical(text):
    """Note text minus SR schedule comments (and the blank line each leaves on its
    own line), for drift comparison — so a reviewed note doesn't read as drifted."""
    out = []
    for ln in (l.rstrip() for l in SR_COMMENT.sub("", text).split("\n")):
        if ln == "" and out and out[-1] == "":
            continue                      # collapse blank runs left by stripped comments
        out.append(ln)
    return "\n".join(out).strip()


# ---------------------------------------------------------------- resync
def read_schedules(text, recorded_ids, current_ids):
    """Map card id -> its `<!--SR:…-->` comment, from a note on disk.

    Blocks are aligned to card ids by the ids recorded when the note was last
    written; with no record (first resync, or a lost sidecar) alignment falls back
    to the current order, which is how the note was generated (§10.4).
    """
    body = text.split("\n", 1)[1] if text.startswith("#flashcards") else text
    blocks = [b for b in BLANK_LINE.split(body.strip()) if b.strip()]
    ids = recorded_ids or current_ids
    schedules = {}
    for i, block in enumerate(blocks):
        m = SR_COMMENT.search(block)
        if m and i < len(ids):
            schedules[ids[i]] = m.group(0)
    return schedules


# ---------------------------------------------------------------- manifest
def load_manifest(path):
    """Return {"seq": {item_id: NNNN}, "cards": {note_name: [card_id, …]}}.

    Migrates the original flat `{item_id: NNNN}` file in place on first read —
    the sequence numbers are precious (they name every note on disk).
    """
    if not path.exists():
        return {"seq": {}, "cards": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data and all(isinstance(v, int) for v in data.values()):
        return {"seq": data, "cards": {}}            # legacy flat format
    return {"seq": data.get("seq", {}), "cards": data.get("cards", {})}


def save_manifest(path, manifest):
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def assign_sequences(manifest, groups):
    """Extend the stable item_id -> sequence-number map (per kind); never reassign."""
    seq = manifest["seq"]
    kind_of = {iid: cs[0]["kind"] for iid, cs in groups.items()}
    max_by_kind = {}
    for iid, s in seq.items():
        k = kind_of.get(iid)
        if k:
            max_by_kind[k] = max(max_by_kind.get(k, 0), s)
    for iid in sorted(groups):
        if iid not in seq:
            k = kind_of[iid]
            max_by_kind[k] = max_by_kind.get(k, 0) + 1
            seq[iid] = max_by_kind[k]
    return seq


# ---------------------------------------------------------------- driver
def group_by_item(wiki=None):
    cards, n_vocab, n_gram, n_art = (cardgen.build(Path(wiki)) if wiki
                                     else cardgen.build())
    groups = {}
    for c in cards:
        groups.setdefault(c["item_id"], []).append(c)
    return groups, n_vocab, n_gram, n_art


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate Obsidian SR flashcard notes.")
    ap.add_argument("--check", action="store_true",
                    help="report notes whose generated cards differ from disk (no writes)")
    ap.add_argument("--force", nargs="*", default=None,
                    help="regenerate matching notes (by item-id or headword), "
                         "discarding their schedules; with no value, ALL notes")
    ap.add_argument("--wiki", help="wiki root to read from (default llm-wiki/)")
    ap.add_argument("--flashcards", help="deck directory to write (default flashcards/)")
    args = ap.parse_args(argv)

    if args.wiki and not args.flashcards:
        ap.error("--wiki requires --flashcards (refusing to write a test wiki "
                 "into the real deck)")

    flash = Path(args.flashcards) if args.flashcards else FLASH
    groups, n_vocab, n_gram, n_art = group_by_item(args.wiki)
    flash.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest(flash / INDEX_NAME)
    seq = assign_sequences(manifest, groups)

    def path_for(iid):
        return flash / f"card-{groups[iid][0]['kind']}-{seq[iid]:04d}.md"

    if args.check:
        drifted = []
        for iid, cs in groups.items():
            p = path_for(iid)
            if p.exists() and canonical(note_text(cs)) != canonical(p.read_text(encoding="utf-8")):
                drifted.append(p.name)
        for name in sorted(drifted):
            print(f"DRIFT  {name}")
        print(f"\n--check: {len(drifted)} note(s) drifted"
              + ("" if drifted else " — all in sync"))
        return 1 if drifted else 0

    forced = args.force            # None | [] (all) | [ids/headwords]
    created = unchanged = resynced = reset = 0
    dropped = []                   # (note, card_id) whose schedule no longer has a card
    for iid, cs in sorted(groups.items()):
        p = path_for(iid)
        current_ids = [c["id"] for c in ordered_cards(cs)]
        recorded_ids = manifest["cards"].get(p.name)   # order the note was last written in
        manifest["cards"][p.name] = current_ids

        if not p.exists():
            p.write_text(note_text(cs), encoding="utf-8")
            created += 1
            continue

        old = p.read_text(encoding="utf-8")
        hit = forced is not None and (forced == [] or iid in forced
                                      or cs[0]["headword"] in forced)
        if hit:
            print(f"⚠  regenerating {p.name} ({cs[0]['headword']}) — resets its schedule")
            p.write_text(note_text(cs), encoding="utf-8")
            reset += 1
            continue

        schedules = read_schedules(old, recorded_ids, current_ids)
        text = note_text(cs, schedules)
        for cid in schedules:
            if cid not in current_ids:
                dropped.append((p.name, cid))
        if text == old:
            unchanged += 1
            continue
        p.write_text(text, encoding="utf-8")
        resynced += 1

    save_manifest(flash / INDEX_NAME, manifest)

    print(f"\nobsidian_cards: {n_vocab} vocab + {n_gram} grammar items → {flash.name}/")
    print(f"  created {created}, resynced {resynced}, unchanged {unchanged}, reset {reset}")
    if dropped:
        print(f"  {len(dropped)} schedule(s) dropped (card no longer generated):")
        for name, cid in sorted(dropped):
            print(f"    {name}: {cid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
