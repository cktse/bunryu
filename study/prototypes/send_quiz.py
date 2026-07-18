#!/usr/bin/env python3
"""Send the prototype quiz as a real text/html email via SMTP.

Sends the raw MIME verbatim, so the <head><style> block (which the CSS-only
interactivity depends on) reaches the recipient intact — unlike Gmail's
compose/API path, which strips it (specs §10.8.5).

Credentials load ONLY from `study/secrets.json` (gitignored; copy
`study/secrets.template.json` and fill it in). No environment-variable fallback,
by design: a mandatory local file avoids silently picking up SMTP_* left in the
shell by an unrelated session. Values live under the "smtp" key:

  { "smtp": { "user": ..., "pass": ..., "host": ..., "port": ...,
              "from": ..., "to": ... } }

`pass` is a provider APP PASSWORD, not the account password.
"""
import ssl
import json
import smtplib
from email.message import EmailMessage
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent      # study/
SECRETS = STUDY / "secrets.json"


def load_smtp():
    """SMTP config from study/secrets.json['smtp']. secrets.json is mandatory."""
    if not SECRETS.exists():
        raise SystemExit(
            f"missing {SECRETS}: copy study/secrets.template.json to "
            "study/secrets.json and fill in the smtp values.")
    cfg = json.loads(SECRETS.read_text(encoding="utf-8")).get("smtp", {})
    user, pw = cfg.get("user"), cfg.get("pass")
    if not user or not pw:
        raise SystemExit("smtp.user and smtp.pass are required in study/secrets.json.")
    return {
        "user": user,
        "pass": pw,
        "host": cfg.get("host", "smtp.gmail.com"),
        "port": int(cfg.get("port", 465)),
        "from": cfg.get("from") or user,
        "to": cfg.get("to") or user,
    }


s = load_smtp()
html_file = STUDY / "prototypes" / "email-quiz-prototype.html"
html = html_file.read_text(encoding="utf-8")

msg = EmailMessage()
msg["From"] = s["from"]
msg["To"] = s["to"]
msg["Subject"] = "今日の復習クイズ（試作 #1）"
msg.set_content("HTMLメール対応のクライアント（Apple Mail）でご覧ください。"
                "選択して「答え合わせ」を押すと、その場で採点・解説が表示されます。")
msg.add_alternative(html, subtype="html")

ctx = ssl.create_default_context()
if s["port"] == 465:
    with smtplib.SMTP_SSL(s["host"], s["port"], context=ctx) as srv:
        srv.login(s["user"], s["pass"])
        srv.send_message(msg)
else:
    with smtplib.SMTP(s["host"], s["port"]) as srv:
        srv.ehlo()
        srv.starttls(context=ctx)
        srv.login(s["user"], s["pass"])
        srv.send_message(msg)

print(f"sent → {s['to']}  (from {s['from']} via {s['host']}:{s['port']}, {len(html)} bytes html)")
