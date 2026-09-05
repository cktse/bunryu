#!/usr/bin/env python3
"""Daily email quiz — CSS-interactive, self-grading MC email (specs §10.8).

Questions come from `cards.json` (vocab `meaning` + grammar `gmc` MC cards); all
questions in one email are drawn from a single article so they share context. The
reveal (意味 with （粵）, up to 2 例文 each with （粵）) is looked up **live from the
llm-wiki pages**, reusing `cards.py` helpers — `cards.json` is never enriched
(data-minimization, §10.8.4). The email is pure CSS (no JavaScript) so it grades
itself inside Apple Mail; it is sent as raw `text/html` via SMTP (§10.8.5).

Phase 1 is self-graded only — nothing is saved back (CSS cannot capture answers).

    python study/email_quiz.py --list             # articles and their MC counts
    python study/email_quiz.py                     # build preview HTML (default article)
    python study/email_quiz.py --article そば屋の先生 -n 5 --out /tmp/quiz.html
    python study/email_quiz.py --send              # build and email via study/secrets.json
"""
import argparse
import datetime
import html
import json
import re
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path

STUDY = Path(__file__).resolve().parent
sys.path.insert(0, str(STUDY))
import cards as cardgen  # noqa: E402  (reuse load_pages, lint.LINK_RE, WIKI, REPO, CARDS_OUT)
import scheduler         # noqa: E402  (selection by urgency + exposure logging, §10.1)

REPO = cardgen.REPO
SECRETS = STUDY / "secrets.json"
PREVIEW_OUT = REPO / "build" / "daily-quiz.html"
E = html.escape
MC_TYPES = scheduler.PUSHABLE_TYPES


# ---------------------------------------------------------------- reveal (from pages)
def _unwrap_links(s):
    """[[dict|surface]] / [[dict]] -> the surface text, reusing lint.LINK_RE."""
    return cardgen.schema.LINK_RE.sub(lambda m: m.group(1).split("|")[-1], s)


def page_index():
    """headword -> page dict, for both vocabulary and grammar (via cards.load_pages)."""
    idx = {}
    for kind in ("vocabulary", "grammar"):
        for pg in cardgen.load_pages(kind):
            hw = pg["fm"].get("headword")
            if hw:
                idx[hw] = pg
    return idx


def reveal(page):
    """(意味 lines, [[jp, canto], ...]) for a page's reveal block.

    意味 kept verbatim (definition + its （粵：…）line); 例文 limited to 2, each
    paired with its （粵） sub-bullet translation if present."""
    if page is None:
        return [], []
    sec = page["sections"]
    imi = [_unwrap_links(ln.strip())
           for ln in sec.get("意味", "").strip().split("\n") if ln.strip()]
    pairs = []
    for ln in sec.get("例文", "").split("\n"):
        ln = ln.strip()
        if re.match(r"\d+\.\s", ln):                       # a numbered example sentence
            s = re.split(r"（粵", _unwrap_links(re.sub(r"^\d+\.\s*", "", ln)))[0].strip()
            if s:
                pairs.append([s, None])
        elif pairs and re.match(r"-\s*（粵", ln):           # its （粵）… translation sub-bullet
            c = re.sub(r"^-\s*（粵[：:]?）?", "", ln).strip().rstrip("）").strip()
            if c:
                pairs[-1][1] = c
    return imi, pairs[:2]


# ---------------------------------------------------------------- selection
def load_cards():
    if not cardgen.CARDS_OUT.exists():
        raise SystemExit(f"missing {cardgen.CARDS_OUT.name}: run `python study/cards.py` first.")
    return json.loads(cardgen.CARDS_OUT.read_text(encoding="utf-8"))


def article_names():
    """Article titles = the article page filenames (also used as the theme tag)."""
    return {pg["path"].stem for pg in cardgen.load_pages("articles")}


def mc_counts(cards, articles):
    """{article: (n_meaning, n_gmc)} for MC cards tagged with each article."""
    out = {}
    for a in sorted(articles):
        m = sum(1 for c in cards if c["type"] == "meaning" and a in c["tags"])
        g = sum(1 for c in cards if c["type"] == "gmc" and a in c["tags"])
        if m or g:
            out[a] = (m, g)
    return out


# ---------------------------------------------------------------- HTML
CSS = """
body{margin:0;padding:0;background:#eceff1;
 font-family:-apple-system,'Hiragino Sans','Hiragino Kaku Gothic ProN',sans-serif;
 -webkit-text-size-adjust:100%;}
.wrap{max-width:600px;margin:0 auto;background:#fff;counter-reset:score;}
.hd{background:#1f6feb;color:#fff;padding:20px 22px;}
.hd h1{margin:0;font-size:19px;font-weight:700;}
.hd p{margin:6px 0 0;font-size:13px;opacity:.9;}
.body{padding:8px 22px 24px;}
.q{border-top:1px solid #eee;padding:18px 0 6px;}
.qn{font-size:12px;color:#1f6feb;font-weight:700;letter-spacing:.05em;}
.qt{font-size:16px;font-weight:600;margin:4px 0 12px;line-height:1.5;}
/* hide the actual inputs; the label is the tap target */
.opt,.sub{position:absolute;left:-9999px;opacity:0;}
.lbl{display:block;border:1.5px solid #d0d7de;border-radius:10px;
 padding:11px 14px;margin:7px 0;font-size:15px;line-height:1.45;color:#24292f;}
.opt:checked+.lbl{border-color:#1f6feb;background:#eaf2ff;}
/* one feedback box per question, hidden until 答え合わせ */
.fb{display:none;margin:8px 0 4px;padding:12px 14px;border-radius:10px;
 background:#f6f8fa;font-size:14px;line-height:1.6;}
.v{font-weight:700;} .v-ok{color:#1a7f37;} .v-no{color:#cf222e;}
.v-ok,.v-no{display:none;}
.expl{margin-top:6px;}
.expl .imi{color:#57606a;margin-top:4px;}
.expl .rei{margin:6px 0 0;padding-left:18px;}
.expl .rc{color:#8a94a6;font-size:13px;margin:1px 0 4px;}
.subbtn{display:block;text-align:center;background:#1f6feb;color:#fff;
 font-size:16px;font-weight:700;padding:14px;border-radius:10px;margin:22px 0 6px;}
.score{display:none;text-align:center;font-size:20px;font-weight:800;
 color:#1f6feb;padding:10px 0 4px;}
.num::before{content:counter(score);}
.foot{color:#8b949e;font-size:12px;text-align:center;padding:14px 0 4px;line-height:1.6;}
/* ===== after 答え合わせ is tapped ===== */
#sub:checked~.body .q .fb{display:block;}
#sub:checked~.body .score{display:block;}
/* mark the correct choice, and tint any wrong pick */
#sub:checked~.body .correct+.lbl{border-color:#1a7f37;background:#e6f4ea;}
#sub:checked~.body .correct+.lbl::after{content:' ✓';color:#1a7f37;font-weight:700;}
#sub:checked~.body .wrong:checked+.lbl{border-color:#cf222e;background:#ffebe9;}
#sub:checked~.body .wrong:checked+.lbl::after{content:' ✕';color:#cf222e;font-weight:700;}
/* single box: verdict resolves by correctness; explanation always shows */
#sub:checked~.body .correct:checked~.fb{background:#e6f4ea;}
#sub:checked~.body .wrong:checked~.fb{background:#fff5f5;}
#sub:checked~.body .correct:checked~.fb .v-ok{display:inline;}
#sub:checked~.body .wrong:checked~.fb .v-no{display:inline;}
/* score: count each correctly-answered question */
#sub:checked~.body .correct:checked+.lbl{counter-increment:score;}
"""


def render_q(i, c, pages):
    ans = c.get("back") or c["choices"][c["answer_index"]]
    qtext = c.get("front") or c.get("headword")
    kind_ja = "語彙" if c["kind"] == "vocab" else "文型"
    rows = [f'<div class="q"><div class="qn">問 {i}　{kind_ja}</div>',
            f'<div class="qt">{E(qtext)}</div>']
    for j, ch in enumerate(c["choices"]):
        cls = "correct" if ch == ans else "wrong"
        oid = f"q{i}o{j}"
        rows.append(f'<input class="opt {cls}" type="radio" name="q{i}" id="{oid}">'
                    f'<label class="lbl" for="{oid}">{E(ch)}</label>')
    imi, rei = reveal(pages.get(c["headword"]))
    imi_html = "<br>".join(E(x) for x in imi)
    imi_block = f'<div class="imi">{imi_html}</div>' if imi_html else ""
    lis = ""
    for jp, canto in rei:
        cc = f'<div class="rc">（粵）{E(canto)}</div>' if canto else ""
        lis += f"<li>{E(jp)}{cc}</li>"
    rei_block = f'<ol class="rei">{lis}</ol>' if lis else ""
    rows.append(
        '<div class="fb">'
        '<span class="v v-ok">✓ 正解！</span>'
        '<span class="v v-no">✕ 復習：</span>'
        f'<div class="expl">{imi_block}{rei_block}</div>'
        '</div>')
    rows.append('</div>')
    return "\n".join(rows)


def build_html(qs, article, pages, today):
    """Render the email from an already-selected list of cards (see main → scheduler)."""
    body = "\n".join(render_q(i + 1, c, pages) for i, c in enumerate(qs))
    doc = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>今日の復習クイズ</title>
<style>{CSS}</style></head>
<body>
<div class="wrap">
 <input class="sub" type="checkbox" id="sub">
 <div class="hd"><h1>今日の復習クイズ</h1>
   <p>「{E(article)}」より　全{len(qs)}問　—　選んで下の「答え合わせ」を押してください</p></div>
 <div class="body">
{body}
 <label class="subbtn" for="sub">答え合わせ　✓</label>
 <div class="score">スコア　<span class="num"></span> / {len(qs)}</div>
 <p class="foot">採点・解説はすべてこのメール内（Apple Mail）で表示されます。<br>
   回答は保存されません（フェーズ1・自己採点）。</p>
 </div>
</div>
</body></html>"""
    return doc


# ---------------------------------------------------------------- send
def load_smtp():
    """SMTP config from study/secrets.json['smtp']. Mandatory; no env fallback (§10.8.5)."""
    if not SECRETS.exists():
        raise SystemExit(f"missing {SECRETS}: copy study/secrets.template.json to "
                         "study/secrets.json and fill in the smtp values.")
    cfg = json.loads(SECRETS.read_text(encoding="utf-8")).get("smtp", {})
    if not cfg.get("user") or not cfg.get("pass"):
        raise SystemExit("smtp.user and smtp.pass are required in study/secrets.json.")
    cfg.setdefault("host", "smtp.gmail.com")
    cfg.setdefault("port", 465)
    cfg["from"] = cfg.get("from") or cfg["user"]
    cfg["to"] = cfg.get("to") or cfg["user"]
    return cfg


def send_email(html_doc, subject, smtp):
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = smtp["from"], smtp["to"], subject
    msg.set_content("HTMLメール対応のクライアント（Apple Mail）でご覧ください。"
                    "選択して「答え合わせ」を押すと、その場で採点・解説が表示されます。")
    msg.add_alternative(html_doc, subtype="html")
    ctx = ssl.create_default_context()
    port = int(smtp["port"])
    if port == 465:
        with smtplib.SMTP_SSL(smtp["host"], port, context=ctx) as srv:
            srv.login(smtp["user"], smtp["pass"])
            srv.send_message(msg)
    else:
        with smtplib.SMTP(smtp["host"], port) as srv:
            srv.ehlo()
            srv.starttls(context=ctx)
            srv.login(smtp["user"], smtp["pass"])
            srv.send_message(msg)


# ---------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description="Daily CSS-interactive quiz email (§10.8).")
    ap.add_argument("--article", help="article title to draw from (default: least-recently-served)")
    ap.add_argument("-n", "--num", type=int, default=5, help="number of questions (default 5)")
    ap.add_argument("--out", help="write the HTML to this path (default: preview file)")
    ap.add_argument("--send", action="store_true", help="email it via study/secrets.json")
    ap.add_argument("--once-daily", action="store_true",
                    help="no-op if an email was already sent today (idempotent; for launchd §10.8.8)")
    ap.add_argument("--list", action="store_true", help="list articles and MC counts, then exit")
    args = ap.parse_args(argv)

    cards = load_cards()
    arts = article_names()
    counts = mc_counts(cards, arts)

    if args.list:
        for a in sorted(counts):
            m, g = counts[a]
            print(f"  {a}\t(meaning {m}, gmc {g}, total {m + g})")
        return 0

    today = datetime.date.today()

    # Idempotent daily guard (§10.8.8): skip if any article was already served
    # today. Exposure is written only on a successful send, so a failed attempt
    # leaves the day unsent and the next launchd trigger retries.
    if args.once_daily:
        served = scheduler.load_progress().get("articles", {}).values()
        if any(a.get("last_served") == today.isoformat() for a in served):
            print(f"--once-daily: already sent today ({today.isoformat()}); nothing to do.")
            return 0

    # Scheduler: refresh urgency (exposure + read-only FSRS), then select the
    # least-recently-served article and its top-N cards by urgency (§10.1).
    mc = [c for c in cards if c["type"] in scheduler.PUSHABLE_TYPES]
    progress = scheduler.recompute(mc, scheduler.load_progress(),
                                   scheduler.scan_fsrs(cards), today)
    article, chosen = scheduler.select(mc, arts, progress, args.num, today,
                                       article=args.article)
    if not chosen:
        raise SystemExit(
            f"no MC cards for article 「{article}」." if article
            else "no article has MC cards; run `python study/cards.py` first.")
    chosen.sort(key=lambda c: (0 if c["kind"] == "vocab" else 1, c["id"]))  # display order

    pages = page_index()
    doc = build_html(chosen, article, pages, today.isoformat())
    subject = f"今日の復習クイズ（{today.isoformat()}）"

    if args.send:
        smtp = load_smtp()
        send_email(doc, subject, smtp)
        # only on a successful send: log exposure (delivery) and persist (§10.8.3)
        progress = scheduler.record_delivery(progress, [c["id"] for c in chosen],
                                             article, today)
        scheduler.save_progress(progress)
        print(f"sent → {smtp['to']}  「{article}」 {len(chosen)}問  (exposure logged)")
    out = Path(args.out) if args.out else (None if args.send else PREVIEW_OUT)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(doc, encoding="utf-8")
        print(f"wrote {out}  「{article}」 {len(chosen)}問, {len(doc)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
