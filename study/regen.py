#!/usr/bin/env python3
"""Unified regeneration of every derived artifact (specs §10.3).

The single idempotent entry point that ingest (§8.2 step 7), scrape (§9), the
daily send (§10.8.8) and ad-hoc runs all call, so there is one regeneration path:

    build/cards.json   study/cards.py            (deterministic)
    index.md           wikitools/index.py        (deterministic)
    flashcards/        study/obsidian_cards.py   (schedule-preserving, §10.4)

Run in dependency order and unconditionally — no timestamps, no Make: the first
two are byte-identical on unchanged input, and the third resyncs in place while
carrying each card's FSRS schedule across, so re-running is always safe.

    python study/regen.py                  # everything
    python study/regen.py --only cards     # the daily send's subset
    python study/regen.py --only index --only flashcards
"""

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from study import cards as cardgen          # noqa: E402
from study import obsidian_cards            # noqa: E402
from wikitools import index as indexgen     # noqa: E402

ARTIFACTS = ("cards", "index", "flashcards")     # dependency order


def select(only=None):
    """The artifacts to rebuild, always in dependency order."""
    return [a for a in ARTIFACTS if not only or a in only]


def regen(only=None):
    """Rebuild the selected artifacts; return a non-zero code if any step failed."""
    wanted = select(only)
    rc = 0
    for name in wanted:
        print(f"── regen: {name}")
        if name == "cards":
            rc |= cardgen.main([])
        elif name == "index":
            rc |= indexgen.main([])
        else:
            rc |= obsidian_cards.main([])
    print(f"\nregen: {', '.join(wanted)} — {'OK' if rc == 0 else 'FAILED'}")
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser(description="Rebuild all derived artifacts (§10.3).")
    ap.add_argument("--only", action="append", choices=ARTIFACTS, metavar="ARTIFACT",
                    help=f"rebuild a subset (repeatable): {', '.join(ARTIFACTS)}")
    args = ap.parse_args(argv)
    return regen(args.only)


if __name__ == "__main__":
    sys.exit(main())
