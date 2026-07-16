#!/usr/bin/env python3
"""Snapshot test for study/cards.py (specs.md §10.7).

Runs `cards.py` as a **subprocess** over the fixture wiki `tests/cards-wiki/`,
writing its cards JSON to a temp file (`--out`), then compares that file against
the committed baseline `tests/cards-baseline.json`. This exercises the whole
program — arg parsing → build → JSON serialization → file output — as a black
box, not just the `build()` function. Passes iff identical; on a mismatch it
lists the NEW / MISSING / CHANGED card ids and exits non-zero.

    python tests/run_cards_tests.py            # compare against the baseline
    python tests/run_cards_tests.py --update   # rewrite the baseline (intended change)
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FIX = HERE / "cards-wiki"
BASELINE = HERE / "cards-baseline.json"
CARDS_PY = REPO / "study" / "cards.py"


def run_cards(out_path):
    """Invoke `cards.py --wiki cards-wiki --out <out_path>`; raise on failure."""
    r = subprocess.run(
        [sys.executable, str(CARDS_PY), "--wiki", str(FIX), "--out", str(out_path)],
        cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"cards.py exited {r.returncode}")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    if "--update" in argv:
        run_cards(BASELINE)
        print(f"baseline updated → {BASELINE.relative_to(REPO)}")
        return 0

    if not BASELINE.exists():
        print("run_cards_tests: no baseline; run with --update first", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "cards.json"
        run_cards(out)
        got = json.loads(out.read_text(encoding="utf-8"))
    expected = json.loads(BASELINE.read_text(encoding="utf-8"))

    if got == expected:
        print(f"PASS  cards.py: {len(got)} cards match baseline")
        return 0

    exp = {c["id"]: c for c in expected}
    gotm = {c["id"]: c for c in got}
    print(f"FAIL  cards.py output differs from baseline (baseline {len(expected)}, got {len(got)}):")
    for cid in sorted(set(exp) | set(gotm)):
        if cid not in gotm:
            print(f"  MISSING  {cid}")
        elif cid not in exp:
            print(f"  NEW      {cid}")
        elif exp[cid] != gotm[cid]:
            print(f"  CHANGED  {cid}")
    print("\n(re-run with --update if the change is intended)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
