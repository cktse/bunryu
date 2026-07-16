#!/usr/bin/env python3
"""Card viewer for reviewing generated flashcards (specs.md §10.4, MVP).

Builds cards fresh from `llm-wiki/` (via study/cards.py) and prints them in a
readable layout. This MVP is a *viewer* for content review — the interactive
SM-2 trainer (progress.json) comes later.

Examples:
    python study/cli.py                          # summary + how to filter
    python study/cli.py --type gmc --limit 10
    python study/cli.py --item grammar-nisaishite   # all cards for one item
    python study/cli.py --article article-haru-no-ichinichi --type cloze
    python study/cli.py --tag 春の一日 --oneline
"""

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from study import cards as cardgen  # noqa: E402

TYPES = cardgen.VOCAB_TYPES + cardgen.GRAMMAR_TYPES


def matches(c, args):
    return (
        (not args.type or c["type"] == args.type)
        and (not args.item or c["item_id"] == args.item)
        and (not args.kind or c["kind"] == args.kind)
        and (not args.article or c.get("article") == args.article)
        and (not args.level or c["level"] == args.level)
        and (not args.tag or args.tag in c.get("tags", []))
    )


def render(c):
    lines = [f"[{c['type']:7}] {c['id']}  ({c['level']})", f"  Q: {c['prompt']}"]
    if "choices" in c:
        lines.append(f"     {c['front']}")
        for i, ch in enumerate(c["choices"]):
            mark = "＊" if i == c["answer_index"] else " "
            lines.append(f"      {mark}{i + 1}. {ch}")
        lines.append(f"  A: {c['back']}")
    else:
        lines.append(f"     {c['front']}")
        extra = f"   ［surface: {c['surface']}］" if c.get("surface") else ""
        lines.append(f"  A: {c['back']}{extra}")
    return "\n".join(lines)


def render_oneline(c):
    front = c["front"].replace("\n", "／")
    if len(front) > 46:
        front = front[:45] + "…"
    return f"{c['type']:7} {front:48} → {c['back']}"


def main(argv=None):
    ap = argparse.ArgumentParser(description="View generated flashcards.")
    ap.add_argument("--type", choices=TYPES)
    ap.add_argument("--item", help="filter by item id, e.g. grammar-nisaishite")
    ap.add_argument("--kind", choices=("vocab", "grammar"))
    ap.add_argument("--article", help="filter by article id (cloze)")
    ap.add_argument("--level", help="filter by JLPT level, e.g. N1")
    ap.add_argument("--tag", help="filter by tag / article theme, e.g. 春の一日")
    ap.add_argument("--limit", type=int, default=20, help="max cards to show (default 20)")
    ap.add_argument("--oneline", action="store_true", help="compact one-line index")
    args = ap.parse_args(argv)

    cards, n_vocab, n_gram, n_art = cardgen.build()
    selected = [c for c in cards if matches(c, args)]

    any_filter = any((args.type, args.item, args.kind, args.article, args.level, args.tag))
    if not any_filter and not args.oneline:
        by_type = {t: sum(1 for c in cards if c["type"] == t) for t in TYPES}
        print(f"{len(cards)} cards from {n_vocab} vocab + {n_gram} grammar, {n_art} articles:")
        for t in TYPES:
            print(f"  {t:8} {by_type[t]}")
        print("\nFilter to review content, e.g.:")
        print("  python study/cli.py --type gmc --limit 10")
        print("  python study/cli.py --item grammar-nisaishite")
        print("  python study/cli.py --kind grammar --tag 春の一日 --oneline")
        return 0

    shown = selected[: args.limit]
    for c in shown:
        print(render_oneline(c) if args.oneline else render(c))
        if not args.oneline:
            print()
    print(f"— shown {len(shown)} of {len(selected)} matching card(s)"
          + ("; use --limit to see more" if len(selected) > len(shown) else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
