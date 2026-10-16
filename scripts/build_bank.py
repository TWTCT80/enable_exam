#!/usr/bin/env python3
"""Assemble bank/<domain>/<objective>.json into the runner's app/bank.json.

Also writes app/bank.js, the same document as `window.BANK = {...};`. The page
loads that with a plain <script> tag, because fetch() does not work when
index.html is opened straight from disk over file://.

Refuses to build if validate.py is red, so a broken bank can never reach the
app. Pass --allow-partial while the bank is still being written; the runner
then offers practice attempts over whatever domains exist instead of a full
100-question exam.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BANK = ROOT / "bank"
BLUEPRINT = ROOT / "blueprint" / "objectives.json"
DEST = ROOT / "app" / "bank.json"
DEST_JS = ROOT / "app" / "bank.js"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-partial", action="store_true",
                    help="build even though the bank is not yet at full quota")
    args = ap.parse_args()

    mode = ["--batch"] if args.allow_partial else []
    check = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate.py"), *mode],
        capture_output=True, text=True)
    if check.returncode != 0:
        print(check.stdout)
        print("build_bank.py: refusing to build - validate.py is red.", file=sys.stderr)
        return 1

    blueprint = json.loads(BLUEPRINT.read_text())
    objectives = {
        o["id"]: {"text": o["text"], "domain": o["domain"], "verb": o["verb"],
                  "config_verify": o.get("config_verify", False)}
        for o in blueprint["objectives"]
    }

    items = []
    for path in sorted(glob.glob(str(BANK / "*" / "*.json"))):
        items.extend(json.loads(pathlib.Path(path).read_text())["items"])

    per_domain = {}
    for it in items:
        per_domain[it["domain"]] = per_domain.get(it["domain"], 0) + 1

    doc = {
        "generated": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "blueprint_version": blueprint["blueprint_version"],
        "exam": blueprint["exam"],
        "exam_minutes": blueprint["exam_minutes"],
        "retires": blueprint["retires"],
        "domains": blueprint["domains"],
        "objectives": objectives,
        "counts": {"total": len(items),
                   "per_domain": {str(k): v for k, v in sorted(per_domain.items())}},
        "complete": all(per_domain.get(d["id"], 0) >= d["items_per_100"]
                        for d in blueprint["domains"]),
        "items": items,
    }

    DEST.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
    DEST.write_text(payload)
    DEST_JS.write_text("window.BANK = " + payload + ";\n")
    kb = DEST.stat().st_size / 1024
    print(f"build_bank.py: wrote {DEST} and {DEST_JS.name} - {len(items)} items, {kb:.0f} KB")
    print(f"  per domain: {doc['counts']['per_domain']}")
    print(f"  full-exam capable: {doc['complete']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
