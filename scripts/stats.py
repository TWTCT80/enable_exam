#!/usr/bin/env python3
"""Coverage and difficulty report for the item bank.

    python3 scripts/stats.py                 # full report
    python3 scripts/stats.py --domain 3      # one domain
    python3 scripts/stats.py --json          # machine-readable

Reports what validate.py enforces plus what it only warns about, so a drift in
difficulty mix or a thinly covered objective is visible before it becomes a
failure.
"""
from __future__ import annotations

import argparse
import glob
import json
import pathlib
import sys
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLUEPRINT = ROOT / "blueprint" / "objectives.json"
DIFFICULTY_TARGET = {1: 0.25, 2: 0.55, 3: 0.20}
LETTER_LIMIT = 0.32
LENGTH_LIMIT = 0.30


def load():
    bp = json.loads(BLUEPRINT.read_text())
    items = []
    for path in sorted(glob.glob(str(ROOT / "bank" / "*" / "*.json"))):
        items.extend(json.loads(pathlib.Path(path).read_text())["items"])
    return bp, items


def length_weight(item):
    """The longest-answer advantage, as validate.py and lencheck.py measure it."""
    if item["type"] == "draganddrop":
        return 0.0              # a target mapping has nothing to pick by length
    lens = {o["id"]: len(o["text"]) for o in item["options"]}
    longest = max(lens.values())
    n = len(lens)
    k = sum(1 for v in lens.values() if v == longest)
    if k == n or max(lens[c] for c in item["correct"]) < longest:
        return 0.0
    return (n / k - 1) / (n - 1)


def bar(share, width=24):
    filled = round(share * width)
    return "#" * filled + "." * (width - filled)


def report(bp, items, only_domain=None):
    if only_domain:
        items = [i for i in items if i["domain"] == only_domain]
    n = len(items)
    if not n:
        print("no items", file=sys.stderr)
        return 2

    objectives = {o["id"]: o for o in bp["objectives"]}
    per_obj = Counter(i["objective"] for i in items)
    per_dom = Counter(i["domain"] for i in items)
    exams = sum(per_dom.values()) / 100

    w = 74
    print("=" * w)
    print(f"  {bp['exam']} {bp['blueprint_version']} item bank"
          f"{'' if not only_domain else f'  -  domain {only_domain} only'}")
    print(f"  {n} items   |   blueprint retires {bp['retires']}")
    print("=" * w)

    # ---- domains ---------------------------------------------------------
    print("\nDOMAIN COVERAGE")
    print(f"  {'':<4}{'domain':<34}{'items':>6}{'quota':>7}{'  ':<2}{'share':>7}")
    for d in bp["domains"]:
        if only_domain and d["id"] != only_domain:
            continue
        got = per_dom.get(d["id"], 0)
        quota = round(d["items_per_100"] * exams) if not only_domain else got
        flag = "  " if got == quota else " !"
        print(f"  {d['id']}.0 {d['name']:<34}{got:>6}{quota:>7}{flag:<2}"
              f"{got / n:>6.1%}  {bar(got / n, 18)}")

    # ---- objectives ------------------------------------------------------
    print("\nOBJECTIVE COVERAGE          (* = configure and verify)")
    empty = []
    for oid, o in objectives.items():
        if only_domain and o["domain"] != only_domain:
            continue
        got = per_obj.get(oid, 0)
        if got == 0:
            empty.append(oid)
        star = "*" if o.get("config_verify") else " "
        text = o["text"][:44]
        diffs = Counter(i["difficulty"] for i in items if i["objective"] == oid)
        mix = "/".join(str(diffs.get(d, 0)) for d in (1, 2, 3))
        print(f"  {star}{oid:<6}{text:<46}{got:>3} items   d {mix}")
    if empty:
        print(f"\n  UNCOVERED: {', '.join(empty)}")

    # ---- difficulty ------------------------------------------------------
    print("\nDIFFICULTY MIX")
    diffs = Counter(i["difficulty"] for i in items)
    for d in (1, 2, 3):
        share = diffs.get(d, 0) / n
        target = DIFFICULTY_TARGET[d]
        delta = share - target
        note = "" if abs(delta) <= 0.12 else "   <- outside tolerance"
        print(f"  level {d}  {diffs.get(d, 0):>4}  {share:>6.1%}  "
              f"(target {target:.0%}, {delta:+.1%}){note}")
        print(f"           {bar(share)}")

    # ---- answer key ------------------------------------------------------
    print("\nANSWER KEY")
    letters = Counter(c for i in items if i["type"] != "draganddrop" for c in i["correct"])
    total_keys = sum(letters.values())
    for letter, count in sorted(letters.items()):
        share = count / total_keys
        note = "   <- over limit" if share > LETTER_LIMIT else ""
        print(f"  {letter}  {count:>4}  {share:>6.1%}  {bar(share)}{note}")

    # ---- tells and shape -------------------------------------------------
    print("\nITEM SHAPE")
    score = sum(length_weight(i) for i in items) / n
    kinds = Counter(i["exhibit"]["kind"] for i in items)
    multi = sum(1 for i in items if i["type"] == "multi")
    none_ct = kinds.get("none", 0)
    print(f"  longest-answer score   {score:>6.1%}   (limit {LENGTH_LIMIT:.0%})")
    print(f"  exhibitless items      {none_ct / n:>6.1%}   (limit 15%)")
    print(f"  multi-answer items     {multi / n:>6.1%}   (target ~10%)")
    print(f"  exhibit kinds          " +
          ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())))

    # ---- skills ----------------------------------------------------------
    skills = Counter(s for i in items for s in i["skills"])
    print(f"\nSKILL TAGS   {len(skills)} distinct across {n} items")
    print("  most exercised:")
    for skill, count in skills.most_common(8):
        print(f"    {count:>4}  {skill}")
    singletons = [s for s, c in skills.items() if c == 1]
    print(f"  tagged once only: {len(singletons)}")

    print()
    return 0


def as_json(bp, items):
    objectives = {o["id"]: o for o in bp["objectives"]}
    per_obj = Counter(i["objective"] for i in items)
    n = len(items)
    doc = {
        "generated_from": str(BLUEPRINT.relative_to(ROOT)),
        "blueprint_version": bp["blueprint_version"],
        "total": n,
        "per_domain": {str(d["id"]): sum(1 for i in items if i["domain"] == d["id"])
                       for d in bp["domains"]},
        "per_objective": {oid: per_obj.get(oid, 0) for oid in objectives},
        "uncovered_objectives": [o for o in objectives if per_obj.get(o, 0) == 0],
        "difficulty": {str(d): sum(1 for i in items if i["difficulty"] == d)
                       for d in (1, 2, 3)},
        "answer_key": dict(Counter(c for i in items if i["type"] != "draganddrop" for c in i["correct"])),
        "exhibit_kinds": dict(Counter(i["exhibit"]["kind"] for i in items)),
        "multi_items": sum(1 for i in items if i["type"] == "multi"),
        "longest_answer_score": round(
            sum(length_weight(i) for i in items) / n, 4),
        "distinct_skills": len({s for i in items for s in i["skills"]}),
    }
    print(json.dumps(doc, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", type=int, choices=range(1, 7))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    bp, items = load()
    return as_json(bp, items) if args.json else report(bp, items, args.domain)


if __name__ == "__main__":
    sys.exit(main())
