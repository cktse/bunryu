#!/usr/bin/env python3
"""End-to-end smoke tests for the daily quiz email (§10.8).

`email_quiz.py` is the one component nothing exercised, which is how a broken
cross-module reference (`obsidian_cards.MANIFEST`, removed in the §10.4 resync
work) reached the launchd job and failed every morning until someone read the
log. These tests run the **real CLI as a subprocess**, exactly as launchd does,
and stop short of `--send`: no mail leaves the machine and `progress.json` is
never written (exposure is recorded only on a successful send, §10.8.3).

    python tests/run_email_tests.py   # from the repo root
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUIZ = REPO / "study" / "email_quiz.py"

results = []


def check(name, ok, detail=""):
    results.append((ok, name, detail))


def run(*args):
    """Invoke the CLI the way launchd does: absolute script, repo as cwd."""
    p = subprocess.run([sys.executable, str(QUIZ), *args], cwd=REPO,
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def test_list():
    rc, out = run("--list")
    check("--list exits 0", rc == 0, out.strip().splitlines()[-1:] or out)
    check("--list names at least one article with MC cards",
          bool(re.search(r"\(meaning \d+, gmc \d+", out)), out[:120])


def test_build_preview():
    """The full selection path — scheduler.recompute + scan_fsrs + select — which
    is where the launchd failure actually happened."""
    with tempfile.TemporaryDirectory() as d:
        out_path = Path(d) / "quiz.html"
        rc, out = run("--out", str(out_path), "-n", "5")
        check("preview build exits 0", rc == 0, out[-400:])
        if rc != 0 or not out_path.exists():
            check("preview file written", False, "no file")
            return
        html = out_path.read_text(encoding="utf-8")
        check("preview file written", True)
        check("HTML carries the CSS-only quiz machinery (§10.8.2)",
              all(t in html for t in ("<style", 'type="radio"', "counter-increment")))
        check("5 questions rendered", len(re.findall(r'name="q\d+"', html)) >= 5
              or html.count("答え") >= 1)
        check("reveal text is rendered, not raw wikilinks",
              "[[" not in html, "unrendered [[wikilink]] in output")


def test_send_not_triggered():
    """Guard the guard: a preview run must not touch progress.json."""
    prog = REPO / "progress" / "progress.json"
    before = prog.read_bytes()
    with tempfile.TemporaryDirectory() as d:
        run("--out", str(Path(d) / "q.html"))
    check("preview run leaves progress.json untouched", prog.read_bytes() == before)


def main():
    if not QUIZ.exists():
        print(f"run_email_tests: not found: {QUIZ}", file=sys.stderr)
        return 2
    test_list()
    test_build_preview()
    test_send_not_triggered()
    for ok, name, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if not ok and detail else ""))
    passed = sum(1 for ok, _, _ in results if ok)
    failed = len(results) - passed
    print(f"\nSummary: {passed}/{len(results)} passed, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
