#!/usr/bin/env python3
"""Tests for study/scheduler.py (specs §10.9). Stdlib only, like §7.1 / §10.7.

Three surfaces: the pure urgency computation, the tolerant FSRS parser + join,
and the atomic / sanity-checked write. Prints PASS/FAIL per case and exits
non-zero on any failure.

    python tests/run_scheduler_tests.py     # from the repo root
"""
import json
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from study import scheduler as s          # noqa: E402
from study import obsidian_cards as obs   # noqa: E402

TODAY = date(2026, 7, 20)
RESULTS = []


def check(name, cond):
    RESULTS.append((bool(cond), name))


def expect_raise(name, fn):
    try:
        fn()
        RESULTS.append((False, name + " (expected raise, none)"))
    except Exception:
        RESULTS.append((True, name))


# ---------------------------------------------------------------- urgency
def test_urgency():
    # never-shown, no FSRS: .4*1 + .2*1 + .4*0.6 = 0.84 -> 84
    score, parts = s.compute_urgency(None, None, TODAY)
    check("never-shown card scores 84", score == 84)
    check("never-shown recency factor = 1", parts["rec"] == 1.0)

    # fully-known solid card: seen today, count=CAP, strong FSRS -> clamps to 1
    solid_exp = {"count": s.FREQ_CAP, "last": TODAY.isoformat(), "channels": ["email"]}
    solid_fsrs = {"due": (TODAY + timedelta(days=30)).isoformat(),
                  "last_review": TODAY.isoformat(), "stability": 60.0, "difficulty": 1.0,
                  "state": 2}
    low, _ = s.compute_urgency(solid_exp, solid_fsrs, TODAY)
    check("recent+frequent+solid card scores 1", low == 1)

    # ordering: never-shown > long-unseen > recent (no FSRS, isolate recency/freq)
    never, _ = s.compute_urgency(None, None, TODAY)
    old = {"count": 1, "last": (TODAY - timedelta(days=20)).isoformat(), "channels": []}
    recent = {"count": 1, "last": (TODAY - timedelta(days=1)).isoformat(), "channels": []}
    s_old, _ = s.compute_urgency(old, None, TODAY)
    s_recent, _ = s.compute_urgency(recent, None, TODAY)
    check("never > long-unseen > recent", never > s_old > s_recent)

    # FSRS: an overdue, low-stability, high-difficulty card outranks a fresh one
    # with identical exposure.
    exp = {"count": 2, "last": (TODAY - timedelta(days=5)).isoformat(), "channels": []}
    fragile = {"due": (TODAY - timedelta(days=10)).isoformat(), "last_review": "x",
               "stability": 1.0, "difficulty": 9.0, "state": 3}
    fresh = {"due": (TODAY + timedelta(days=20)).isoformat(), "last_review": "x",
             "stability": 60.0, "difficulty": 1.0, "state": 2}
    check("fragile FSRS outranks fresh FSRS",
          s.compute_urgency(exp, fragile, TODAY)[0] > s.compute_urgency(exp, fresh, TODAY)[0])

    # missing FSRS falls back to default (> a solid FSRS, same exposure)
    check("missing FSRS ranks above solid FSRS",
          s.compute_urgency(exp, None, TODAY)[0] > s.compute_urgency(exp, fresh, TODAY)[0])


def test_recompute_idempotent():
    cards = [{"id": "vocab-x::meaning", "item_id": "vocab-x", "type": "meaning",
              "kind": "vocab", "level": "N1", "tags": ["A"]},
             {"id": "grammar-y::gmc", "item_id": "grammar-y", "type": "gmc",
              "kind": "grammar", "level": "N1", "tags": ["A"]},
             {"id": "vocab-x::reading", "item_id": "vocab-x", "type": "reading",
              "kind": "vocab", "level": "N1", "tags": ["A"]}]   # not pushable
    p0 = {"cards": {}, "articles": {}}
    p1 = s.recompute(cards, p0, {}, TODAY)
    p2 = s.recompute(cards, p1, {}, TODAY)
    check("recompute scores only pushable types", set(p1["cards"]) ==
          {"vocab-x::meaning", "grammar-y::gmc"})
    check("recompute is idempotent", p1 == p2)


# ---------------------------------------------------------------- FSRS parse + join
def test_parse_sr():
    good = ("<!--SR:!fsrs,2026-07-16T06:45:00.143Z,0,1.2931,5.11217071,"
            "1,1,0,0,2026-07-16T06:39:00.143Z-->")
    f = s.parse_sr(good)
    check("parse_sr extracts fields",
          f and f["due"].startswith("2026-07-16") and abs(f["stability"] - 1.2931) < 1e-6
          and abs(f["difficulty"] - 5.11217071) < 1e-6 and f["state"] == 0
          and f["last_review"].endswith("06:39:00.143Z"))
    check("parse_sr rejects malformed", s.parse_sr("<!--SR:!fsrs,only-->") is None)
    check("parse_sr ignores non-FSRS (SM-2)", s.parse_sr("<!--SR:!2026-01-01,3,250-->") is None)
    check("parse_sr handles empty", s.parse_sr("") is None)


def test_scan_join():
    """A note block is matched to its card id by content, and its SR parsed."""
    c = {"id": "vocab-z::meaning", "item_id": "vocab-z", "type": "meaning",
         "kind": "vocab", "level": "N1", "headword": "改ざん", "reading": "かいざん",
         "front": "改ざん（かいざん）", "choices": ["書き換え", "捏造", "偽造", "改良"],
         "answer_index": 0, "back": "書き換え", "tags": ["A"]}
    sr = "<!--SR:!fsrs,2026-07-16T00:00:00.000Z,0,3.0,4.0,1,1,0,2,2026-07-10T00:00:00.000Z-->"
    with tempfile.TemporaryDirectory() as d:
        flash = Path(d)
        (flash / ".card-index.json").write_text(json.dumps({"vocab-z": 1}), encoding="utf-8")
        note = obs.note_text([c]).rstrip() + "\n" + sr + "\n"
        (flash / "card-vocab-0001.md").write_text(note, encoding="utf-8")
        got = s.scan_fsrs([c], flash_dir=flash, manifest_path=flash / ".card-index.json")
    check("scan_fsrs joins block→card id by content (legacy flat manifest)",
          "vocab-z::meaning" in got and abs(got["vocab-z::meaning"]["stability"] - 3.0) < 1e-9)


def test_scan_current_manifest_and_default_path():
    """The shape `obsidian_cards` actually writes today — `{"seq":…,"cards":…}` —
    joined by the recorded card order, and reached through the module's own
    `manifest_path()` default rather than an explicit argument. Both are what the
    daily send uses, and neither was covered before (the launchd break of
    2026-09-09)."""
    c = {"id": "vocab-z::meaning", "item_id": "vocab-z", "type": "meaning",
         "kind": "vocab", "level": "N1", "headword": "改ざん", "reading": "かいざん",
         "front": "改ざん（かいざん）", "choices": ["書き換え", "捏造", "偽造", "改良"],
         "answer_index": 0, "back": "書き換え", "tags": ["A"]}
    sr = "<!--SR:!fsrs,2026-07-16T00:00:00.000Z,0,7.5,4.0,1,1,0,2,2026-07-10T00:00:00.000Z-->"
    with tempfile.TemporaryDirectory() as d:
        flash = Path(d)
        obs.save_manifest(obs.manifest_path(flash),
                          {"seq": {"vocab-z": 1},
                           "cards": {"card-vocab-0001.md": ["vocab-z::meaning"]}})
        # a *reworded* card: content matching would fail, the recorded order must not
        note = obs.note_text([c]).rstrip().replace("改良", "改訂") + "\n" + sr + "\n"
        (flash / "card-vocab-0001.md").write_text(note, encoding="utf-8")
        got = s.scan_fsrs([c], flash_dir=flash)          # manifest_path defaults
    check("scan_fsrs reads the current manifest shape via manifest_path()",
          "vocab-z::meaning" in got)
    check("scan_fsrs joins a reworded card by recorded order",
          got.get("vocab-z::meaning", {}).get("stability") == 7.5)


# ---------------------------------------------------------------- atomic write
def _seed(path):
    data = {"cards": {"a::meaning": {"exposure": {"count": 2, "last": "2026-07-10",
                                                  "channels": ["email"]}, "urgency": 50},
                      "b::gmc": {"urgency": 30}},
            "articles": {"Art": {"last_served": "2026-07-10", "count": 1}}}
    s.save_progress(data, path)
    return data


def test_atomic_write():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "progress.json"
        seeded = _seed(path)
        check("valid save round-trips", s.load_progress(path) == seeded)

        # record_delivery bumps only the delivered card + the article
        upd = s.record_delivery(s.load_progress(path), ["a::meaning"], "Art", TODAY)
        s.save_progress(upd, path)
        back = s.load_progress(path)
        check("record_delivery bumps delivered card",
              back["cards"]["a::meaning"]["exposure"]["count"] == 3
              and back["cards"]["a::meaning"]["exposure"]["last"] == TODAY.isoformat())
        check("record_delivery preserves other card",
              back["cards"]["b::gmc"]["urgency"] == 30)
        check("record_delivery stamps article",
              back["articles"]["Art"]["last_served"] == TODAY.isoformat()
              and back["articles"]["Art"]["count"] == 2)

        # a bad update is rejected and the original file is left intact
        before = path.read_bytes()
        drop = {"cards": {"b::gmc": {"urgency": 30}}, "articles": {"Art": {"last_served": "2026-07-10"}}}
        expect_raise("save rejects dropping a card WITH exposure",
                     lambda: s.save_progress(drop, path))     # a::meaning has exposure
        regress = json.loads(before)
        regress["cards"]["a::meaning"]["exposure"]["count"] = 0
        expect_raise("save rejects regressed exposure", lambda: s.save_progress(regress, path))
        bad_u = json.loads(before)
        bad_u["cards"]["a::meaning"]["urgency"] = 200
        expect_raise("save rejects out-of-range urgency", lambda: s.save_progress(bad_u, path))
        drop_art = json.loads(before)
        del drop_art["articles"]["Art"]
        expect_raise("save rejects dropped article", lambda: s.save_progress(drop_art, path))

        check("original file byte-for-byte intact after rejects", path.read_bytes() == before)
        check("no leftover .tmp file", not (path.with_name(path.name + ".tmp")).exists())

        # an urgency-only entry (no exposure) is regenerable and MAY be dropped
        keep = s.load_progress(path)
        ok_drop = {"cards": {"a::meaning": keep["cards"]["a::meaning"]},  # exposure kept
                   "articles": keep["articles"]}
        s.save_progress(ok_drop, path)                        # drops b::gmc (urgency-only)
        check("urgency-only card may be dropped", "b::gmc" not in s.load_progress(path)["cards"])


def main():
    test_urgency()
    test_recompute_idempotent()
    test_parse_sr()
    test_scan_join()
    test_scan_current_manifest_and_default_path()
    test_atomic_write()
    for ok, name in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    passed = sum(1 for ok, _ in RESULTS if ok)
    failed = len(RESULTS) - passed
    print(f"\nSummary: {passed}/{len(RESULTS)} passed, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
