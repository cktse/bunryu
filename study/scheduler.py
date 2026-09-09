#!/usr/bin/env python3
"""Card scheduler — exposure tracking, urgency scoring, read-only FSRS scan (§10.1).

Two schedulers coexist: Obsidian owns FSRS (we read its inline `<!--SR:!fsrs,…-->`
comments, never writing them); we own *exposure* (what was pushed and when). This
module blends both into a per-card **urgency** (0–100) that the push pipeline ranks
by, and persists state in a single `progress/progress.json` namespaced into
`cards` and `articles`.

State is written through an **atomic, sanity-checked** path (temp → validate →
os.replace), so a buggy batch recompute can never corrupt the precious history.

    python study/scheduler.py recompute   # refresh urgency for all pushable cards
    python study/scheduler.py status      # top cards by urgency (inspection)
"""
import argparse
import copy
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

STUDY = Path(__file__).resolve().parent
sys.path.insert(0, str(STUDY.parent))
from study import obsidian_cards as obs   # noqa: E402  (reuse card_block / canonical / SR / manifest)
from study import cards as cardgen        # noqa: E402  (REPO, CARDS_OUT)

REPO = cardgen.REPO
PROGRESS = REPO / "progress" / "progress.json"

# cards our push channels can deliver today (the email uses MC types).
PUSHABLE_TYPES = ("meaning", "gmc")

# --- urgency model (documented, tunable) -----------------------------------
WEIGHTS = {"rec": 0.4, "freq": 0.2, "fsrs": 0.4, "err": 0.0}   # sum to 1
HORIZON_DAYS = 30      # days-since-last that saturates the recency factor
FREQ_CAP = 10          # exposures that saturate the frequency factor
STAB_CAP_DAYS = 30.0   # FSRS stability treated as "solid" at/above this
FSRS_DEFAULT = 0.6     # f_fsrs when a card has no FSRS record (unlearned ⇒ urgent)
FSRS_SUBW = {"overdue": 0.5, "stability": 0.3, "difficulty": 0.2}  # sum to 1
SR_FSRS = re.compile(r"<!--SR:!fsrs,(.*?)-->")


# ---------------------------------------------------------------- helpers
def _clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def _clamp01(x):
    return _clamp(x, 0.0, 1.0)


def _days_since(iso, today):
    """today - date(iso); iso may be a date or a full timestamp."""
    return (today - date.fromisoformat(iso[:10])).days


# ---------------------------------------------------------------- FSRS read-model
def parse_sr(sr_text):
    """Parse an FSRS inline comment → dict, else None (tolerant of other formats).

    Layout (plugin-version-specific, treated positionally):
      !fsrs,<due>,<?>,<stability>,<difficulty>,<?>,<?>,<?>,<state>,<last_review>
    Only due / last_review / stability / difficulty / state are read; the rest is
    opaque. Any parse problem yields None → the card falls back to FSRS_DEFAULT."""
    m = SR_FSRS.search(sr_text or "")
    if not m:
        return None
    f = m.group(1).split(",")
    if len(f) < 4:
        return None
    try:
        out = {"due": f[0], "last_review": f[-1],
               "stability": float(f[2]), "difficulty": float(f[3])}
    except (ValueError, IndexError):
        return None
    out["state"] = int(f[7]) if len(f) > 8 and f[7].lstrip("-").isdigit() else None
    return out


def _blocks(note_text):
    """Yield each card block of a note (blank-line separated), deck tag stripped."""
    for block in re.split(r"\n[ \t]*\n", note_text.strip()):
        yield "\n".join(l for l in block.split("\n")
                        if not l.startswith("#flashcards"))


def scan_fsrs(cards, flash_dir=None, manifest_path=None):
    """{card_id: fsrs_dict} read-only from flashcards/*.md.

    Joins via `.card-index.json`: `seq` maps item_id→NNNN, and `cards` records
    each note's card ids **in written order**, which is how blocks align to ids
    (§10.1, §10.4). Content matching is the fallback for a note with no recorded
    order — it fails exactly when a card was reworded, which is the case the
    recorded order exists to survive."""
    flash_dir = Path(flash_dir) if flash_dir else obs.FLASH
    mpath = Path(manifest_path) if manifest_path else obs.manifest_path(flash_dir)
    if not mpath.exists():
        return {}
    manifest = obs.load_manifest(mpath)      # migrates the legacy flat form
    seq, order = manifest["seq"], manifest["cards"]
    by_item = {}
    for c in cards:
        by_item.setdefault(c["item_id"], []).append(c)

    out = {}
    for item_id, n in seq.items():
        cs = by_item.get(item_id)
        if not cs:
            continue
        p = flash_dir / f"card-{cs[0]['kind']}-{int(n):04d}.md"
        if not p.exists():
            continue
        recorded = order.get(p.name)
        match = {}
        for c in cs:
            try:
                match[obs.canonical(obs.card_block(c))] = c["id"]
            except Exception:
                pass   # a card lacking render fields just won't match; skip it
        for i, block in enumerate(_blocks(p.read_text(encoding="utf-8"))):
            m = obs.SR_COMMENT.search(block)
            if not m:
                continue
            cid = (recorded[i] if recorded and i < len(recorded)
                   else match.get(obs.canonical(block)))
            fsrs = parse_sr(m.group(0))
            if cid and fsrs:
                out[cid] = fsrs
    return out


# ---------------------------------------------------------------- urgency
def _f_recency(exposure, today):
    if not exposure or not exposure.get("last"):
        return 1.0                                   # never shown ⇒ maximally urgent
    return _clamp01(_days_since(exposure["last"], today) / HORIZON_DAYS)


def _f_frequency(exposure):
    count = exposure.get("count", 0) if exposure else 0
    return _clamp01(1 - count / FREQ_CAP)


def _f_fsrs(fsrs, today):
    if not fsrs:
        return FSRS_DEFAULT
    due = fsrs.get("due")
    overdue = _days_since(due, today) if due else 0
    f_over = _clamp01(overdue / HORIZON_DAYS) if overdue > 0 else 0.0
    stab = fsrs.get("stability")
    f_stab = _clamp01(1 - stab / STAB_CAP_DAYS) if stab is not None else 0.5
    diff = fsrs.get("difficulty")
    f_diff = _clamp01((diff - 1) / 9) if diff is not None else 0.5
    return _clamp01(FSRS_SUBW["overdue"] * f_over
                    + FSRS_SUBW["stability"] * f_stab
                    + FSRS_SUBW["difficulty"] * f_diff)


def compute_urgency(exposure, fsrs, today, weights=WEIGHTS):
    """Return (score 1..100, parts) — a pure function of its inputs."""
    parts = {"rec": _f_recency(exposure, today),
             "freq": _f_frequency(exposure),
             "fsrs": _f_fsrs(fsrs, today),
             "err": 0.0}
    raw = sum(weights[k] * parts[k] for k in weights)
    score = int(round(_clamp(100 * raw, 1, 100)))
    return score, {k: round(v, 3) for k, v in parts.items()}


def recompute(cards, progress, fsrs_view, today, weights=WEIGHTS):
    """Return a new progress dict with `urgency`/`urgency_at` refreshed for every
    pushable card. Pure & idempotent: same inputs ⇒ same output."""
    new = copy.deepcopy(progress)
    new.setdefault("cards", {})
    new.setdefault("articles", {})
    iso = today.isoformat()
    for c in cards:
        if c["type"] not in PUSHABLE_TYPES:
            continue
        entry = new["cards"].setdefault(c["id"], {})
        score, parts = compute_urgency(entry.get("exposure"), fsrs_view.get(c["id"]),
                                       today, weights)
        entry["urgency"] = score
        entry["urgency_at"] = iso
        entry["parts"] = parts
    return new


# ---------------------------------------------------------------- exposure
def record_delivery(progress, card_ids, article, today, channel="email"):
    """Return a new progress dict with exposure bumped for the delivered cards and
    the featured article's last_served stamped. Touches nothing else."""
    new = copy.deepcopy(progress)
    new.setdefault("cards", {})
    new.setdefault("articles", {})
    iso = today.isoformat()
    for cid in card_ids:
        exp = new["cards"].setdefault(cid, {}).setdefault(
            "exposure", {"count": 0, "last": None, "channels": []})
        exp["count"] += 1
        exp["last"] = iso
        if channel not in exp["channels"]:
            exp["channels"].append(channel)
    art = new["articles"].setdefault(article, {"last_served": None, "count": 0})
    art["last_served"] = iso
    art["count"] += 1
    return new


# ---------------------------------------------------------------- selection
def article_last_served(progress, article):
    return progress.get("articles", {}).get(article, {}).get("last_served")


def _urgency(progress, cid):
    return progress.get("cards", {}).get(cid, {}).get("urgency", 0)


def select(mc_cards, article_set, progress, n, today, article=None, focus_ids=()):
    """Pick the least-recently-served article, then its top-N cards by urgency.

    `mc_cards` = pushable cards; `article_set` = valid article titles. Returns
    (chosen_article, [cards]). Pure over its inputs (testable)."""
    pools = {}
    for c in mc_cards:
        for a in (t for t in c.get("tags", []) if t in article_set):
            pools.setdefault(a, []).append(c)
    if not pools:
        return None, []
    if article is not None:
        if article not in pools:
            return article, []
        chosen = article
    else:                                            # least-recently-served; never first
        chosen = min(sorted(pools),
                     key=lambda a: article_last_served(progress, a) or "")
    ranked = sorted(
        pools[chosen],
        key=lambda c: (-_urgency(progress, c["id"]),
                       0 if c["item_id"] in focus_ids else 1,
                       c["level"], c["id"]))
    return chosen, ranked[:n]


# ---------------------------------------------------------------- persistence
def load_progress(path=PROGRESS):
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault("cards", {})
        data.setdefault("articles", {})
        return data
    return {"cards": {}, "articles": {}}


def sanity_check(old, new):
    """Raise ValueError if `new` would lose history or hold bad data vs `old`."""
    if not (isinstance(new, dict) and isinstance(new.get("cards"), dict)
            and isinstance(new.get("articles"), dict)):
        raise ValueError("progress.json must have dict `cards` and `articles`")
    for cid, oe in old.get("cards", {}).items():
        oexp = oe.get("exposure")
        if not oexp:
            continue                       # urgency-only entry is regenerable; may be dropped
        nexp = new["cards"].get(cid, {}).get("exposure")
        if not nexp:
            raise ValueError(f"exposure history dropped: {cid}")
        if nexp.get("count", 0) < oexp.get("count", 0):
            raise ValueError(f"exposure history regressed: {cid}")
    for a, oa in old.get("articles", {}).items():
        na = new["articles"].get(a)
        if na is None:
            raise ValueError(f"article dropped: {a}")
        if oa.get("last_served") and not na.get("last_served"):
            raise ValueError(f"article last_served lost: {a}")
    for cid, e in new["cards"].items():
        u = e.get("urgency")
        if u is not None and not (1 <= u <= 100):
            raise ValueError(f"urgency out of range for {cid}: {u}")


def save_progress(data, path=PROGRESS):
    """Atomic write: temp → sanity-check against the current file → os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    old = load_progress(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        reloaded = json.loads(tmp.read_text(encoding="utf-8"))   # must round-trip
        sanity_check(old, reloaded)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    os.replace(tmp, path)


# ---------------------------------------------------------------- CLI
def _load_cards():
    if not cardgen.CARDS_OUT.exists():
        raise SystemExit(f"missing {cardgen.CARDS_OUT.name}: run `python study/cards.py` first.")
    return json.loads(cardgen.CARDS_OUT.read_text(encoding="utf-8"))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Card scheduler (§10.1).")
    ap.add_argument("cmd", choices=["recompute", "status"], help="action")
    ap.add_argument("-n", "--num", type=int, default=20, help="status: rows to show")
    args = ap.parse_args(argv)

    cards = _load_cards()
    mc = [c for c in cards if c["type"] in PUSHABLE_TYPES]
    today = date.today()
    progress = recompute(mc, load_progress(), scan_fsrs(cards), today)

    if args.cmd == "recompute":
        save_progress(progress)
        print(f"recomputed urgency for {len(mc)} pushable cards → {PROGRESS.name}")
        return 0

    rows = sorted(mc, key=lambda c: -_urgency(progress, c["id"]))[:args.num]
    for c in rows:
        e = progress["cards"].get(c["id"], {})
        exp = e.get("exposure", {})
        print(f"  {_urgency(progress, c['id']):3d}  {c['id']:<32} "
              f"seen×{exp.get('count', 0)} last={exp.get('last', '—')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
