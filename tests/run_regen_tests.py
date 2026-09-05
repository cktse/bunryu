#!/usr/bin/env python3
"""Tests for the schedule-preserving resync + regen driver (§10.3–10.4).

Runs `obsidian_cards.py` unchanged over a **copy** of the `tests/cards-wiki`
fixture and a throwaway deck directory (`--wiki` / `--flashcards`), so the real
`llm-wiki/` and `flashcards/` are never touched. Each case asserts one clause of
the §10.4 carry-over policy: id persists → schedule kept; card removed → schedule
dropped *and reported*; card added → fresh; `--force` → reset.

    python tests/run_regen_tests.py   # from the repo root
"""

import io
import json
import re
import shutil
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from study import obsidian_cards as oc   # noqa: E402
from study import regen                  # noqa: E402

FIXTURE = REPO / "tests" / "cards-wiki"
SR = ("<!--SR:!fsrs,2026-09-01T00:00:00.000Z,3,2.5000,5.0000000,1,1,0,1,"
      "2026-08-29T00:00:00.000Z-->")
ITEM = "vocab-dounyuu"          # 導入: canto + cloze + meaning + reading


# ---------------------------------------------------------------- helpers
def run(wiki, deck, *extra):
    """Invoke the generator exactly as the CLI does; return (rc, stdout)."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = oc.main(["--wiki", str(wiki), "--flashcards", str(deck), *extra])
    return rc, buf.getvalue()


def fresh(tmp, name):
    wiki = Path(tmp) / f"wiki-{name}"
    shutil.copytree(FIXTURE, wiki)
    return wiki, Path(tmp) / f"deck-{name}"


def manifest(deck):
    return json.loads((deck / oc.INDEX_NAME).read_text(encoding="utf-8"))


def note_path(deck, item_id=ITEM):
    return deck / f"card-vocab-{manifest(deck)['seq'][item_id]:04d}.md"


def blocks(path):
    body = path.read_text(encoding="utf-8").split("\n", 1)[1]
    return [b for b in oc.BLANK_LINE.split(body.strip()) if b.strip()]


def inject_sr(deck, card_id, item_id=ITEM):
    """Append a schedule comment to the block that holds `card_id`."""
    p = note_path(deck, item_id)
    ids = manifest(deck)["cards"][p.name]
    i = ids.index(card_id)
    bs = blocks(p)
    bs[i] = bs[i] + "\n" + SR
    header = p.read_text(encoding="utf-8").split("\n", 1)[0]
    p.write_text(header + "\n" + "\n\n".join(bs) + "\n", encoding="utf-8")


def unlink_dounyuu(wiki):
    """Drop the [[導入]] wikilink from the article body -> its cloze card vanishes."""
    art = wiki / "articles" / "裁判員のもやもや.md"
    t = art.read_text(encoding="utf-8")
    art.write_text(re.sub(r"\[\[導入(?:\|([^\]]*))?\]\]",
                          lambda m: m.group(1) or "導入", t), encoding="utf-8")


def revise_meaning(wiki):
    """Edit 導入's ## 意味 so its meaning card changes but its card id does not."""
    p = wiki / "vocabulary" / "導入.md"
    t = p.read_text(encoding="utf-8")
    p.write_text(t.replace("## 意味\n", "## 意味\nテスト用の改訂。", 1), encoding="utf-8")


# ---------------------------------------------------------------- cases
def test_create(tmp):
    wiki, deck = fresh(tmp, "create")
    rc, out = run(wiki, deck)
    notes = sorted(deck.glob("card-*.md"))
    m = manifest(deck)
    ok = (rc == 0 and len(notes) == 17 and "created 17" in out
          and set(m) == {"seq", "cards"} and len(m["seq"]) == 17
          and all(m["cards"][n.name] for n in notes))
    return ok, f"{len(notes)} notes created, manifest records seq + card ids"


def test_idempotent(tmp):
    wiki, deck = fresh(tmp, "idem")
    run(wiki, deck)
    before = {p.name: p.read_bytes() for p in deck.glob("card-*.md")}
    rc, out = run(wiki, deck)
    after = {p.name: p.read_bytes() for p in deck.glob("card-*.md")}
    ok = rc == 0 and before == after and "resynced 0" in out and "unchanged 17" in out
    return ok, "second run rewrites nothing (all 17 unchanged, byte-identical)"


def test_carry_over(tmp):
    wiki, deck = fresh(tmp, "carry")
    run(wiki, deck)
    inject_sr(deck, f"{ITEM}::meaning")
    revise_meaning(wiki)
    rc, out = run(wiki, deck)
    p = note_path(deck)
    ids = manifest(deck)["cards"][p.name]
    holder = blocks(p)[ids.index(f"{ITEM}::meaning")]
    ok = (rc == 0 and SR in holder and "テスト用の改訂" in holder
          and p.read_text(encoding="utf-8").count(SR) == 1
          and "schedule(s) dropped" not in out)
    return ok, "reworded card keeps its schedule, still on its own block"


def test_drop_reported(tmp):
    wiki, deck = fresh(tmp, "drop")
    run(wiki, deck)
    cloze = next(c for c in manifest(deck)["cards"][note_path(deck).name]
                 if "::cloze::" in c)
    inject_sr(deck, cloze)
    unlink_dounyuu(wiki)
    rc, out = run(wiki, deck)
    text = note_path(deck).read_text(encoding="utf-8")
    ok = (rc == 0 and "1 schedule(s) dropped" in out and cloze in out
          and SR not in text)
    return ok, f"removed card's schedule dropped and reported ({cloze})"


def test_added_starts_fresh(tmp):
    wiki, deck = fresh(tmp, "added")
    unlink_dounyuu(wiki)                       # generate without the cloze card
    run(wiki, deck)
    inject_sr(deck, f"{ITEM}::meaning")
    shutil.rmtree(wiki)                        # restore the link -> card comes back
    shutil.copytree(FIXTURE, wiki)
    rc, out = run(wiki, deck)
    p = note_path(deck)
    ids = manifest(deck)["cards"][p.name]
    bs = blocks(p)
    added = [b for i, b in enumerate(bs) if "::cloze::" in ids[i]]
    ok = (rc == 0 and added and all(SR not in b for b in added)
          and SR in bs[ids.index(f"{ITEM}::meaning")])
    return ok, "new card starts with no schedule; the kept one is undisturbed"


def reingest_article(wiki):
    """Simulate a re-ingest of the article: re-wrap a line (§6.5.2) and mark one
    more word *before* an existing cloze target in the same sentence — the two
    edits that used to renumber positional cloze ids (§11.2)."""
    art = wiki / "articles" / "裁判員のもやもや.md"
    t = art.read_text(encoding="utf-8")
    t = t.replace("「[[裁判]]員制度」", "「[[裁判]]員[[制度]]」", 1)   # shifts the old ordinal
    art.write_text(t.replace("が決まり、", "が決まり、\n", 1), encoding="utf-8")


def test_cloze_id_survives_reingest(tmp):
    wiki, deck = fresh(tmp, "reingest")
    run(wiki, deck)
    p = note_path(deck)
    before = [c for c in manifest(deck)["cards"][p.name] if "::cloze::" in c]
    inject_sr(deck, before[0])
    reingest_article(wiki)
    rc, out = run(wiki, deck)
    after = [c for c in manifest(deck)["cards"][p.name] if "::cloze::" in c]
    holder = blocks(p)[manifest(deck)["cards"][p.name].index(before[0])]
    ok = (rc == 0 and after == before and SR in holder
          and "schedule(s) dropped" not in out)
    return ok, "reflow + a new marker in the same sentence keep the cloze id (and its schedule)"


def test_ab_subheadings_change_no_card(tmp):
    """A 統合理解 page labels its texts `### A` / `### B` inside 本文 (§6.5.2);
    those lines are structure, so no card may change when they are added."""
    from study import cards as cardgen
    wiki, _ = fresh(tmp, "ab")
    before = cardgen.build(wiki)[0]
    art = wiki / "articles" / "裁判員のもやもや.md"
    t = art.read_text(encoding="utf-8")
    t = t.replace("## 本文\n", "## 本文\n### A\n", 1)
    head, _, rest = t.partition("\n\n")                  # label the 2nd paragraph B
    art.write_text(head + "\n\n### B\n" + rest, encoding="utf-8")
    after = cardgen.build(wiki)[0]
    fronts = [c.get("front", "") for c in after]
    ok = (after == before and not any(f.lstrip().startswith("#") for f in fronts))
    return ok, "### A / ### B labels are stripped before sentence splitting"


def test_force_resets(tmp):
    wiki, deck = fresh(tmp, "force")
    run(wiki, deck)
    inject_sr(deck, f"{ITEM}::meaning")
    rc, out = run(wiki, deck, "--force", ITEM)
    ok = rc == 0 and SR not in note_path(deck).read_text(encoding="utf-8") and "reset 1" in out
    return ok, "--force <item> discards that note's schedules"


def test_wiki_requires_flashcards(tmp):
    wiki, _ = fresh(tmp, "guard")
    buf = io.StringIO()
    try:
        with redirect_stdout(buf), redirect_stderr(buf):   # argparse usage text
            oc.main(["--wiki", str(wiki)])
        return False, "expected SystemExit, none raised"
    except SystemExit as e:
        return e.code == 2, "a test wiki cannot write into the real deck"


def test_legacy_manifest(tmp):
    wiki, deck = fresh(tmp, "legacy")
    deck.mkdir(parents=True)
    (deck / oc.INDEX_NAME).write_text(json.dumps({ITEM: 42}), encoding="utf-8")
    rc, out = run(wiki, deck)
    m = manifest(deck)
    ok = (rc == 0 and m["seq"][ITEM] == 42 and (deck / "card-vocab-0042.md").exists()
          and set(m) == {"seq", "cards"})
    return ok, "flat {item: NNNN} manifest migrates, sequence numbers preserved"


def test_regen_select(_tmp):
    ok = (regen.select() == list(regen.ARTIFACTS)
          and regen.select(["cards"]) == ["cards"]
          and regen.select(["flashcards", "cards"]) == ["cards", "flashcards"])
    return ok, "--only filters but keeps dependency order"


CASES = [test_create, test_idempotent, test_carry_over, test_drop_reported,
         test_added_starts_fresh, test_cloze_id_survives_reingest,
         test_ab_subheadings_change_no_card, test_force_resets,
         test_wiki_requires_flashcards, test_legacy_manifest, test_regen_select]


def main():
    if not FIXTURE.is_dir():
        print(f"run_regen_tests: fixture wiki not found: {FIXTURE}", file=sys.stderr)
        return 2
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        for case in CASES:
            name = case.__name__.removeprefix("test_")
            try:
                ok, why = case(tmp)
            except Exception as exc:                       # a crash is a failure
                ok, why = False, f"{type(exc).__name__}: {exc}"
            results.append((ok, name, why))
    for ok, name, why in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  — {why}")
    passed = sum(1 for ok, _, _ in results if ok)
    failed = len(results) - passed
    print(f"\nSummary: {passed}/{len(results)} passed, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
