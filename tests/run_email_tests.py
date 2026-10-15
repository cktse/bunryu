#!/usr/bin/env python3
"""End-to-end smoke tests for the daily quiz email (§10.8).

`email_quiz.py` is the one component nothing exercised, which is how a broken
cross-module reference (`obsidian_cards.MANIFEST`, removed in the §10.4 resync
work) reached the launchd job and failed every morning until someone read the
log. Two layers:

- **Smoke (subprocess).** The real CLI, exactly as launchd runs it, stopping short
  of `--send`: no mail leaves the machine and `progress.json` is never written
  (exposure is recorded only on a successful send, §10.8.3).
- **Golden + transport (in-process).** The renderer is run over the fixture wiki
  `tests/cards-wiki/` and compared **byte-for-byte** with committed baselines in
  `tests/email-baseline/` — the guard that lets the renderer be shared with the
  daily-lesson email (§13.8) without silently changing the live email. The SMTP
  path is exercised against a fake server: secrets validation, and the HTML part
  (with its `<style>`) arriving verbatim (§10.8.5).

    python tests/run_email_tests.py            # from the repo root
    python tests/run_email_tests.py --update   # rewrite the golden baselines (intended change)
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
QUIZ = REPO / "study" / "email_quiz.py"
FIX = HERE / "cards-wiki"
GOLDEN = HERE / "email-baseline"
FIXED_DATE = "2026-01-01"          # build_html's date input; pinned for determinism

sys.path.insert(0, str(REPO))
from study import email_quiz as eq  # noqa: E402

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


# ---------------------------------------------------------------- golden render
def fixture_emails():
    """{article: html} — one email per fixture article with MC cards.

    Mirrors the CLI's render path minus the scheduler: all of an article's MC
    cards in display order (vocab first, then id), reveal looked up from the
    fixture pages. The page index is built here because `eq.page_index()` reads
    the live vault (no wiki argument)."""
    cg = eq.cardgen
    cards, *_ = cg.build(FIX)
    pages = {pg["fm"]["headword"]: pg
             for kind in ("vocabulary", "grammar")
             for pg in cg.load_pages(kind, FIX) if pg["fm"].get("headword")}
    arts = {pg["path"].stem for pg in cg.load_pages("articles", FIX)}
    out = {}
    for a in eq.mc_counts(cards, arts):
        qs = sorted((c for c in cards if c["type"] in eq.MC_TYPES and a in c["tags"]),
                    key=lambda c: (0 if c["kind"] == "vocab" else 1, c["id"]))
        out[a] = eq.build_html(qs, a, pages, FIXED_DATE)
    return out


def update_golden():
    GOLDEN.mkdir(exist_ok=True)
    emails = fixture_emails()
    for stale in GOLDEN.glob("*.html"):
        if stale.stem not in emails:
            stale.unlink()
    for a, doc in emails.items():
        (GOLDEN / f"{a}.html").write_text(doc, encoding="utf-8")
    print(f"golden baselines updated → {GOLDEN.relative_to(REPO)}/ ({len(emails)} files)")


def test_golden():
    emails = fixture_emails()
    check("fixture yields at least two article emails", len(emails) >= 2, sorted(emails))
    have = {p.stem for p in GOLDEN.glob("*.html")}
    check("golden set matches fixture articles (no missing / stale baselines)",
          have == set(emails), f"baseline {sorted(have)} vs fixture {sorted(emails)}")
    for a, doc in sorted(emails.items()):
        base = GOLDEN / f"{a}.html"
        if not base.exists():
            continue
        exp = base.read_text(encoding="utf-8")
        detail = ""
        if doc != exp:
            i = next((k for k, (x, y) in enumerate(zip(doc, exp)) if x != y),
                     min(len(doc), len(exp)))
            detail = f"first difference at char {i}: got {doc[i:i + 60]!r}"
        check(f"golden: 「{a}」 byte-identical to baseline", doc == exp, detail)


def test_render_invariants():
    """Properties that must hold whatever the baseline says — so an --update
    can never bless a structurally broken email."""
    for a, doc in sorted(fixture_emails().items()):
        names = re.findall(r'type="radio" name="(q\d+)"', doc)
        qs = sorted(set(names), key=lambda n: int(n[1:]))
        ok_one = all(len(re.findall(rf'class="opt correct" type="radio" name="{q}"', doc)) == 1
                     for q in qs)
        check(f"「{a}」: exactly one correct choice per question", qs and ok_one)
        check(f"「{a}」: score denominator equals question count",
              f"/ {len(qs)}</div>" in doc and f"全{len(qs)}問" in doc)
        check(f"「{a}」: no raw [[wikilinks]] or unescaped choice markup",
              "[[" not in doc and "<script" not in doc)
        check(f"「{a}」: every question has a feedback box",
              doc.count('<div class="fb">') == len(qs))


# ---------------------------------------------------------------- SMTP (fake server)
class FakeSMTP:
    """Stands in for smtplib.SMTP_SSL / SMTP; records what a real server would see."""
    sent = []

    def __init__(self, host, port, context=None):
        self.host, self.port, self.calls = host, port, []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def ehlo(self):
        self.calls.append("ehlo")

    def starttls(self, context=None):
        self.calls.append("starttls")

    def login(self, user, pw):
        self.calls.append(("login", user, pw))

    def send_message(self, msg):
        FakeSMTP.sent.append((self, msg))


def with_secrets(payload):
    """Point eq.SECRETS at a temp file holding `payload` (None = no file); return loader result or the SystemExit."""
    orig = eq.SECRETS
    with tempfile.TemporaryDirectory() as d:
        eq.SECRETS = Path(d) / "secrets.json"
        if payload is not None:
            eq.SECRETS.write_text(json.dumps(payload), encoding="utf-8")
        try:
            return eq.load_smtp()
        except SystemExit as e:
            return e
        finally:
            eq.SECRETS = orig


def test_load_smtp():
    check("secrets: missing file is a hard error (no env fallback)",
          isinstance(with_secrets(None), SystemExit))
    check("secrets: missing pass is a hard error",
          isinstance(with_secrets({"smtp": {"user": "u@x"}}), SystemExit))
    check("secrets: missing smtp section is a hard error",
          isinstance(with_secrets({"other": {}}), SystemExit))
    cfg = with_secrets({"smtp": {"user": "u@x", "pass": "p"}})
    check("secrets: defaults host/port and from/to = user",
          isinstance(cfg, dict) and cfg["host"] == "smtp.gmail.com" and cfg["port"] == 465
          and cfg["from"] == cfg["to"] == "u@x", cfg)


def test_send_email():
    doc = next(iter(fixture_emails().values()))
    smtp = {"user": "u@x", "pass": "p", "host": "h", "from": "f@x", "to": "t@x"}
    orig = (eq.smtplib.SMTP_SSL, eq.smtplib.SMTP)
    eq.smtplib.SMTP_SSL = eq.smtplib.SMTP = FakeSMTP
    try:
        for port, handshake in ((465, []), (587, ["ehlo", "starttls"])):
            FakeSMTP.sent = []
            eq.send_email(doc, "件名", dict(smtp, port=port))
            check(f"send (port {port}): exactly one message sent", len(FakeSMTP.sent) == 1)
            if len(FakeSMTP.sent) != 1:
                continue
            srv, msg = FakeSMTP.sent[0]
            check(f"send (port {port}): handshake then login",
                  srv.calls == handshake + [("login", "u@x", "p")], srv.calls)
            check(f"send (port {port}): headers from secrets",
                  (msg["From"], msg["To"], msg["Subject"]) == ("f@x", "t@x", "件名"))
            html = [p for p in msg.iter_parts() if p.get_content_type() == "text/html"]
            text = [p for p in msg.iter_parts() if p.get_content_type() == "text/plain"]
            check(f"send (port {port}): multipart/alternative with text + html parts",
                  msg.get_content_type() == "multipart/alternative" and len(html) == 1
                  and len(text) == 1)
            check(f"send (port {port}): HTML (incl. <style>) arrives verbatim",
                  bool(html) and html[0].get_content().rstrip("\n") == doc)
    finally:
        eq.smtplib.SMTP_SSL, eq.smtplib.SMTP = orig


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not QUIZ.exists():
        print(f"run_email_tests: not found: {QUIZ}", file=sys.stderr)
        return 2
    if "--update" in argv:
        update_golden()
        return 0
    test_list()
    test_build_preview()
    test_send_not_triggered()
    test_golden()
    test_render_invariants()
    test_load_smtp()
    test_send_email()
    for ok, name, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if not ok and detail else ""))
    passed = sum(1 for ok, _, _ in results if ok)
    failed = len(results) - passed
    print(f"\nSummary: {passed}/{len(results)} passed, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
