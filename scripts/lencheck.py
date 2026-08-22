#!/usr/bin/env python3
"""Report option-length balance per item, so the longest-answer tell gets caught
while drafting instead of at validation.

    python3 scripts/lencheck.py bank/1/1.1.json bank/1/1.2.json
    python3 scripts/lencheck.py              # whole bank

Prints only the items where the key is longest or joint-longest, with the
weight each contributes, and the resulting score against the 30% limit.
"""
import glob
import json
import pathlib
import sys

LIMIT = 0.30


def weight(item):
    """Same measure validate.py applies: how much 'pick the longest' narrows
    the guess. 1.0 when the key is uniquely longest, 0 when every option ties."""
    lens = {o["id"]: len(o["text"]) for o in item["options"]}
    correct = item["correct"]
    longest = max(lens.values())
    n = len(lens)
    k = sum(1 for v in lens.values() if v == longest)
    if k == n:
        return 0.0, k
    if max(lens[c] for c in correct) < longest:
        return 0.0, k
    return (n / k - 1) / (n - 1), k


def main() -> int:
    paths = sys.argv[1:] or sorted(glob.glob("bank/*/*.json"))
    items = [i for p in paths for i in json.loads(pathlib.Path(p).read_text())["items"]]
    if not items:
        print("no items found", file=sys.stderr)
        return 2

    total = 0.0
    flagged = []
    for it in items:
        w, k = weight(it)
        total += w
        if w > 0:
            lens = {o["id"]: len(o["text"]) for o in it["options"]}
            flagged.append((w, it["id"], k, lens, it["correct"]))

    flagged.sort(reverse=True)
    for w, iid, k, lens, correct in flagged:
        tag = "STRICT" if k == 1 else f"tie/{k} "
        print(f"  {tag} {iid:<10} w={w:.2f}  {lens}  key={correct}")

    score = total / len(items)
    verdict = "OK" if score <= LIMIT else "OVER LIMIT"
    print(f"\n{len(items)} items | longest-answer score {score:.1%} "
          f"(limit {LIMIT:.0%}) | {verdict}")
    return 0 if score <= LIMIT else 1


if __name__ == "__main__":
    sys.exit(main())
