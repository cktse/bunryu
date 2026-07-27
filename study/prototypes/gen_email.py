#!/usr/bin/env python3
"""PROTOTYPE ONLY — build a self-contained CSS-interactive quiz email.

Targets Apple Mail (iOS/macOS, WebKit): NO JavaScript. Selecting a choice,
tapping 答え合わせ, the score, and the per-question reveal are all pure CSS
(:checked + sibling selectors + counters). Self-graded; nothing is saved.

    python prototypes/gen_email.py [N]      # N questions (default 5)
"""
import json, re, html, sys, math
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent   # study/prototypes/ -> repo root
ART = "そば屋の先生"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 5
E = html.escape

cards = json.load(open(REPO / "build" / "cards.json"))


def pick(tp, n):
    got = [c for c in cards if c["type"] == tp and ART in c["tags"]]
    got.sort(key=lambda c: c["id"])
    return got[:n]


def page_content(kind, headword):
    """Look up the item's llm-wiki page for the reveal: the full 意味 section
    (definition + （粵：…）line) verbatim, plus up to 2 例文 sentences."""
    d = "vocabulary" if kind == "vocab" else "grammar"
    p = REPO / "llm-wiki" / d / f"{headword}.md"
    if not p.exists():
        return [], []
    txt = p.read_text(encoding="utf-8")
    imi = []
    m = re.search(r"## 意味\n(.+?)(?:\n## |\Z)", txt, re.S)
    if m:
        # keep every non-empty 意味 line verbatim — the definition AND the
        # （粵：…）line, which for grammar sits on its own line below it.
        imi = [ln.strip() for ln in m.group(1).strip().split("\n") if ln.strip()]
    rei = []   # list of [jp_sentence, cantonese_or_None]
    m = re.search(r"## 例文\n(.+?)(?:\n## |\Z)", txt, re.S)
    if m:
        for ln in m.group(1).split("\n"):
            ln = ln.strip()
            if re.match(r"\d+\.\s", ln):                  # a numbered example sentence
                s = re.sub(r"^\d+\.\s*", "", ln)
                s = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", s)   # [[a|b]] -> b
                s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)            # [[a]]   -> a
                s = re.split(r"（粵", s)[0].strip()                  # drop inline （粵…）if any
                if s:
                    rei.append([s, None])
            elif rei and re.match(r"-\s*（粵", ln):        # its （粵）… translation sub-bullet
                c = re.sub(r"^-\s*（粵[：:]?）?", "", ln).strip().rstrip("）").strip()
                if c:
                    rei[-1][1] = c
    return imi, rei[:2]


# ~60% vocab, remainder grammar
nv = math.ceil(N * 0.6)
qs = pick("meaning", nv) + pick("gmc", N - nv)
for c in qs:
    c["imi"], c["rei"] = page_content(c["kind"], c["headword"])

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


def render_q(i, c):
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
    imi_html = "<br>".join(E(x) for x in c.get("imi", []))
    imi = f'<div class="imi">{imi_html}</div>' if imi_html else ""
    rei = ""
    for jp, canto in c.get("rei", []):
        cc = f'<div class="rc">（粵）{E(canto)}</div>' if canto else ""
        rei += f"<li>{E(jp)}{cc}</li>"
    reihtml = f'<ol class="rei">{rei}</ol>' if rei else ""
    rows.append(
        '<div class="fb">'
        '<span class="v v-ok">✓ 正解！</span>'
        '<span class="v v-no">✕ 復習：</span>'
        f'<div class="expl">{imi}{reihtml}</div>'
        '</div>')
    rows.append('</div>')
    return "\n".join(rows)


body = "\n".join(render_q(i + 1, c) for i, c in enumerate(qs))
doc = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>今日の復習クイズ</title>
<style>{CSS}</style></head>
<body>
<div class="wrap">
 <input class="sub" type="checkbox" id="sub">
 <div class="hd"><h1>今日の復習クイズ</h1>
   <p>「{E(ART)}」より　全{len(qs)}問　—　選んで下の「答え合わせ」を押してください</p></div>
 <div class="body">
{body}
 <label class="subbtn" for="sub">答え合わせ　✓</label>
 <div class="score">スコア　<span class="num"></span> / {len(qs)}</div>
 <p class="foot">これは試作メールです。回答は保存されません。<br>
   採点・解説はすべてこのメール内（Apple Mail）で完結します。</p>
 </div>
</div>
</body></html>"""

out = Path(__file__).parent / "email-quiz-prototype.html"
out.write_text(doc, encoding="utf-8")
print(f"wrote {out.relative_to(REPO)}  ({len(qs)} questions, {len(doc)} bytes)")
