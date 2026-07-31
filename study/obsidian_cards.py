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

Generation is APPEND-ONLY so the plugin's inline `<!--SR:…-->` schedule is never
clobbered: an existing note is left untouched unless explicitly --force'd.

    python study/obsidian_cards.py            # create missing notes (append-only)
    python study/obsidian_cards.py --check    # report notes whose cards drifted
    python study/obsidian_cards.py --force grammar-nisaishite ～に際して   # specific
    python study/obsidian_cards.py --force     # regenerate ALL (resets schedules!)
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
MANIFEST = FLASH / ".card-index.json"
TYPE_ORDER = {"canto": 0, "cloze": 1, "meaning": 2, "reading": 3,
              "gcloze": 4, "gmc": 5, "gerror": 6}
SR_COMMENT = re.compile(r"<!--SR:.*?-->")


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


def note_text(cards):
    kind, level = cards[0]["kind"], cards[0]["level"]
    ordered = sorted(cards, key=lambda c: (TYPE_ORDER[c["type"]], c["id"]))
    blocks = [card_block(c) for c in ordered]
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


# ---------------------------------------------------------------- driver
def group_by_item():
    cards, n_vocab, n_gram, n_art = cardgen.build()
    groups = {}
    for c in cards:
        groups.setdefault(c["item_id"], []).append(c)
    return groups, n_vocab, n_gram, n_art


def assign_sequences(groups):
    """Load/extend the stable item_id -> sequence-number manifest (per kind)."""
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    kind_of = {iid: cs[0]["kind"] for iid, cs in groups.items()}
    max_by_kind = {}
    for iid, s in manifest.items():
        k = kind_of.get(iid)
        if k:
            max_by_kind[k] = max(max_by_kind.get(k, 0), s)
    for iid in sorted(groups):
        if iid not in manifest:
            k = kind_of[iid]
            max_by_kind[k] = max_by_kind.get(k, 0) + 1
            manifest[iid] = max_by_kind[k]
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate Obsidian SR flashcard notes.")
    ap.add_argument("--check", action="store_true",
                    help="report notes whose generated cards differ from disk (no writes)")
    ap.add_argument("--force", nargs="*", default=None,
                    help="regenerate matching notes (by item-id or headword); "
                         "with no value, regenerate ALL (resets schedules)")
    args = ap.parse_args(argv)

    groups, n_vocab, n_gram, n_art = group_by_item()
    FLASH.mkdir(exist_ok=True)
    seq = assign_sequences(groups)

    def path_for(iid):
        return FLASH / f"card-{groups[iid][0]['kind']}-{seq[iid]:04d}.md"

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
    created = skipped = regen = 0
    for iid, cs in sorted(groups.items()):
        p = path_for(iid)
        text = note_text(cs)
        if p.exists():
            hit = forced is not None and (forced == [] or iid in forced
                                          or cs[0]["headword"] in forced)
            if not hit:
                skipped += 1
                continue
            print(f"⚠  regenerating {p.name} ({cs[0]['headword']}) — resets its schedule")
            regen += 1
        else:
            created += 1
        p.write_text(text, encoding="utf-8")

    print(f"\nobsidian_cards: {n_vocab} vocab + {n_gram} grammar items → {FLASH.name}/")
    print(f"  created {created}, regenerated {regen}, skipped(existing) {skipped}")
    if forced is None and skipped:
        print("  (existing notes preserved; --force <item> to regenerate, --check to audit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
