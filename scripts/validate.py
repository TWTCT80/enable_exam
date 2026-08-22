#!/usr/bin/env python3
"""Validate the CCNA 200-301 v1.1 item bank.

Fails loudly. Exit 0 only when every check passes.

  python3 scripts/validate.py            # whole bank, all checks
  python3 scripts/validate.py --batch    # single batch: skip bank-wide quota/coverage
  python3 scripts/validate.py --batch bank/3/3.1.json
"""
from __future__ import annotations

import argparse
import difflib
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
BANK = ROOT / "bank"
BLUEPRINT = ROOT / "blueprint" / "objectives.json"

# spec: items per 100 == domain weight
QUOTA_PER_100 = {1: 20, 2: 20, 3: 25, 4: 10, 5: 15, 6: 10}
QUOTA_TOLERANCE = 1          # items, at exam scale
MAX_LETTER_SHARE = 0.32
MAX_LONGEST_CORRECT = 0.30
MAX_NO_EXHIBIT = 0.15
MIN_EXPLANATION_WORDS = 40
NEAR_DUP_RATIO = 0.85
# draganddrop is deliberately NOT supported: the runner has no keyboard-
# navigable implementation, and a drag interaction that fails on a keyboard is
# worse than none. Matching content is expressed as multi-answer instead.
VALID_TYPES = {"single", "multi"}
VALID_EXHIBIT_KINDS = {"cli_output", "config", "topology", "none"}

# stems that betray a bare-recall or definition-quiz item
BANNED_STEM_PATTERNS = [
    (re.compile(r"which of the following (is|are) true", re.I),
     "definition quiz ('which of the following is true about X')"),
    (re.compile(r"^\s*what is the (default )?(administrative distance|port number|well-known port)", re.I),
     "bare recall of a lookup-table fact"),
    (re.compile(r"^\s*which port does\b", re.I), "bare recall of a port number"),
    (re.compile(r"^\s*which command displays\b", re.I), "bare command recall"),
]

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def normalise_stem(s: str) -> str:
    s = s.lower()
    s = re.sub(r"refer to the exhibit\.?", " ", s)
    s = re.sub(r"[^a-z ]+", " ", s)      # drop digits/punctuation so reworded twins collide
    return re.sub(r"\s+", " ", s).strip()


def word_count(s: str) -> int:
    return len(re.findall(r"[A-Za-z0-9/._-]+", s))


def load_blueprint() -> dict:
    if not BLUEPRINT.exists():
        print(f"FATAL: {BLUEPRINT} missing - run step 0 first.", file=sys.stderr)
        sys.exit(2)
    doc = json.loads(BLUEPRINT.read_text())
    return {o["id"]: o for o in doc["objectives"]}


def load_items(paths: list[pathlib.Path]) -> list[tuple[pathlib.Path, dict]]:
    out = []
    for p in sorted(paths):
        try:
            data = json.loads(p.read_text())
        except json.JSONDecodeError as e:
            err(f"{p}: invalid JSON - {e}")
            continue
        items = data["items"] if isinstance(data, dict) and "items" in data else data
        if not isinstance(items, list):
            err(f"{p}: expected a list of items (or {{'items': [...]}})")
            continue
        for it in items:
            out.append((p, it))
    return out


# --- show ip route exhibit consistency ------------------------------------
PARENT_RE = re.compile(
    r"^ {6}(?P<net>\d+\.\d+\.\d+\.\d+/\d+) is (?P<var>variably )?subnetted,"
    r" (?P<subnets>\d+) subnets(?:, (?P<masks>\d+) masks)?\s*$")
CHILD_RE = re.compile(r"^(?P<code>\S(?:.{0,7}\S)?) {2,}(?P<pfx>\d+\.\d+\.\d+\.\d+/\d+)\b")


def check_route_exhibit(tag: str, content: str) -> None:
    """Assert IOS parent/child grouping in a 'show ip route' exhibit.

    IOS groups subnets under their *classful* parent; every child must fall
    inside the parent, the declared subnet/mask counts must match what is
    printed, and 'variably' appears only when more than one mask is present.
    """
    import ipaddress

    lines = content.splitlines()
    cmd = [l for l in lines if "show ip route" in l]
    if not cmd:
        return
    # A filtered view (`show ip route static`, `| include ...`) still prints the
    # parent banner counted over the WHOLE table while listing only the matching
    # children, so the subnet/mask counts legitimately exceed what is shown.
    # Containment is still checked; the counts are not.
    filtered = not re.match(r"^\S+#\s*show ip route\s*$", cmd[0].strip())

    groups: list[tuple[int, re.Match, list[str]]] = []
    for n, line in enumerate(lines):
        m = PARENT_RE.match(line)
        if m:
            groups.append((n, m, []))
            continue
        if groups and line.startswith(" " * 9) is False and CHILD_RE.match(line):
            # child rows put the prefix at column 10 (index 9)
            cm = CHILD_RE.match(line)
            if cm.start("pfx") == 9:
                groups[-1][2].append(cm.group("pfx"))

    for n, m, kids in groups:
        net = ipaddress.ip_network(m.group("net"), strict=False)
        declared_subnets = int(m.group("subnets"))
        declared_masks = int(m.group("masks")) if m.group("masks") else 1
        variably = bool(m.group("var"))

        if not kids:
            err(f"{tag}: parent '{m.group('net')}' (line {n+1}) has no child routes")
            continue
        for k in kids:
            kn = ipaddress.ip_network(k, strict=False)
            if not (kn.subnet_of(net) if kn.version == net.version else False):
                err(f"{tag}: parent '{m.group('net')}' does not contain child '{k}' "
                    f"- IOS groups children under the classful parent")
        if filtered:
            continue
        if len(kids) != declared_subnets:
            err(f"{tag}: parent '{m.group('net')}' declares {declared_subnets} subnets "
                f"but {len(kids)} child routes are printed")
        actual_masks = len({int(k.split('/')[1]) for k in kids})
        if actual_masks != declared_masks:
            err(f"{tag}: parent '{m.group('net')}' declares {declared_masks} mask(s) "
                f"but the children use {actual_masks}")
        if variably and actual_masks < 2:
            err(f"{tag}: parent '{m.group('net')}' says 'variably subnetted' with only "
                f"one mask - IOS prints 'is subnetted, N subnets' in that case")
        if not variably and actual_masks > 1:
            err(f"{tag}: parent '{m.group('net')}' omits 'variably' but children use "
                f"{actual_masks} masks")


def check_item(path: pathlib.Path, it: dict, objectives: dict) -> None:
    iid = it.get("id", "<no id>")
    tag = f"{path.name}:{iid}"

    for field in ("id", "objective", "domain", "type", "select_count", "stem",
                  "exhibit", "options", "correct", "explanation", "difficulty", "skills"):
        if field not in it:
            err(f"{tag}: missing required field '{field}'")
            return

    obj = it["objective"]
    if obj not in objectives:
        err(f"{tag}: objective '{obj}' is not in objectives.json")
        return
    if it["domain"] != objectives[obj]["domain"]:
        err(f"{tag}: domain {it['domain']} does not match objective {obj} "
            f"(domain {objectives[obj]['domain']})")
    if not it["id"].startswith(f"{obj}-"):
        err(f"{tag}: id should be prefixed '{obj}-'")

    if it["type"] not in VALID_TYPES:
        err(f"{tag}: type '{it['type']}' not one of {sorted(VALID_TYPES)}")

    opts = it["options"]
    opt_ids = [o["id"] for o in opts]
    if len(opts) < 3:
        err(f"{tag}: fewer than 3 options ({len(opts)})")
    if len(set(opt_ids)) != len(opt_ids):
        err(f"{tag}: duplicate option ids {opt_ids}")

    correct = it["correct"]
    if not correct:
        err(f"{tag}: empty 'correct'")
    if not set(correct).issubset(set(opt_ids)):
        err(f"{tag}: correct {correct} is not a subset of option ids {opt_ids}")
    if it["select_count"] != len(correct):
        err(f"{tag}: select_count {it['select_count']} != len(correct) {len(correct)}")
    if it["type"] == "single" and len(correct) != 1:
        err(f"{tag}: type 'single' with {len(correct)} correct answers")
    if it["type"] == "multi":
        if len(correct) < 2:
            err(f"{tag}: type 'multi' with {len(correct)} correct answers")
        if not re.search(r"choose (two|three|four)", it["stem"], re.I):
            err(f"{tag}: multi item does not state the count ('Choose two.') in the stem")

    diff = it["difficulty"]
    if diff not in (1, 2, 3):
        err(f"{tag}: difficulty {diff} not in 1..3")

    ex = it["exhibit"]
    kind = ex.get("kind")
    if kind not in VALID_EXHIBIT_KINDS:
        err(f"{tag}: exhibit.kind '{kind}' not one of {sorted(VALID_EXHIBIT_KINDS)}")
    if kind == "none":
        if diff != 1:
            err(f"{tag}: exhibit.kind 'none' is only allowed at difficulty 1 (has {diff})")
    else:
        if not ex.get("content", "").strip():
            err(f"{tag}: exhibit.kind '{kind}' but content is empty")
        if not re.search(r"refer to the exhibit", it["stem"], re.I):
            warn(f"{tag}: has an exhibit but the stem never points to it")
        if kind == "cli_output":
            check_route_exhibit(tag, ex.get("content", ""))

    expl = it["explanation"]
    wc = word_count(expl)
    if wc < MIN_EXPLANATION_WORDS:
        err(f"{tag}: explanation is {wc} words, minimum {MIN_EXPLANATION_WORDS}")
    for oid in opt_ids:
        if oid in correct:
            continue
        # the distractor must be named explicitly, e.g. "B)" / "Option B" / " B "
        if not re.search(rf"(?<![A-Za-z]){re.escape(oid)}(?![A-Za-z])", expl):
            err(f"{tag}: explanation never addresses distractor '{oid}'")

    for pat, why in BANNED_STEM_PATTERNS:
        if pat.search(it["stem"]):
            err(f"{tag}: banned stem pattern - {why}")

    if not it["skills"]:
        err(f"{tag}: 'skills' is empty")


def check_bank_wide(items: list[tuple[pathlib.Path, dict]], objectives: dict,
                    batch: bool) -> None:
    n = len(items)
    if n == 0:
        err("no items found")
        return

    # --- answer-key balance -------------------------------------------------
    letters = Counter()
    for _, it in items:
        for c in it.get("correct", []):
            letters[c] += 1
    total_keys = sum(letters.values())
    for letter, count in sorted(letters.items()):
        share = count / total_keys
        if share > MAX_LETTER_SHARE:
            err(f"answer-key imbalance: '{letter}' is {share:.1%} of keys "
                f"({count}/{total_keys}), limit {MAX_LETTER_SHARE:.0%}")

    # --- longest-option tell ------------------------------------------------
    # A *strictly* longest correct answer is the real tell: a length-picker has a
    # unique option to point at. An exact tie with a distractor gives that
    # heuristic nothing to choose between, so it is tracked but not failed.
    strict_hits = 0
    joint_hits = 0
    weighted = 0.0
    considered = 0
    for _, it in items:
        opts = it.get("options", [])
        correct = it.get("correct", [])
        if len(opts) < 2 or not correct:
            continue
        considered += 1
        lens = {o["id"]: len(o["text"]) for o in opts}
        distractors = [v for k, v in lens.items() if k not in correct]
        if not distractors:
            continue
        longest = max(lens.values())
        n_opts = len(lens)          # NOT n: that is the bank-wide item count
        k = sum(1 for v in lens.values() if v == longest)
        if k == n_opts:
            # every option the same length: "pick the longest" narrows nothing
            continue
        best_correct = max(lens[c] for c in correct if c in lens)
        if best_correct < longest:
            continue
        # Weight by how much the tie actually narrows the guess. Picking among
        # k longest gives 1/k against a 1/n baseline, so the advantage scales
        # as (n/k - 1)/(n - 1): 1.0 when the key is uniquely longest, ~0 when
        # nearly every option ties. A flat half-hit over-penalised 3-way ties
        # between same-length addresses and under-penalised 2-way ties.
        w = (n_opts / k - 1) / (n_opts - 1)
        if k == 1:
            strict_hits += 1
        else:
            joint_hits += 1
        weighted += w
    if considered:
        # A strictly-longest key is a full hit. An exact tie with a distractor
        # still narrows a length-picker's guess (2 of n rather than 1 of n), so
        # it counts half rather than nothing.
        score = weighted / considered
        if score > MAX_LONGEST_CORRECT:
            err(f"length tell: weighted longest-answer score {score:.1%} exceeds "
                f"{MAX_LONGEST_CORRECT:.0%} "
                f"({strict_hits} strictly longest, {joint_hits} tied, "
                f"of {considered} items)")

    # --- exhibitless share --------------------------------------------------
    none_ct = sum(1 for _, it in items if it.get("exhibit", {}).get("kind") == "none")
    share = none_ct / n
    if share > MAX_NO_EXHIBIT:
        err(f"exhibit.kind 'none' is {share:.1%} of items ({none_ct}/{n}), "
            f"limit {MAX_NO_EXHIBIT:.0%}")

    # --- duplicate / near-duplicate stems -----------------------------------
    norm = [(it.get("id"), normalise_stem(it.get("stem", ""))) for _, it in items]
    seen: dict[str, str] = {}
    for iid, s in norm:
        if s in seen:
            err(f"duplicate stem: {iid} is identical to {seen[s]} after normalisation")
        else:
            seen[s] = iid
    for i in range(len(norm)):
        for j in range(i + 1, len(norm)):
            a, b = norm[i][1], norm[j][1]
            if not a or not b or a == b:
                continue
            if abs(len(a) - len(b)) / max(len(a), len(b)) > 0.35:
                continue
            r = difflib.SequenceMatcher(None, a, b).ratio()
            if r > NEAR_DUP_RATIO:
                err(f"near-duplicate stems ({r:.2f}): {norm[i][0]} vs {norm[j][0]}")

    # --- difficulty mix (advisory) -----------------------------------------
    dm = Counter(it.get("difficulty") for _, it in items)
    mix = {d: dm.get(d, 0) / n for d in (1, 2, 3)}
    target = {1: 0.25, 2: 0.55, 3: 0.20}
    for d in (1, 2, 3):
        if abs(mix[d] - target[d]) > 0.12:
            warn(f"difficulty mix: {mix[d]:.0%} at level {d}, target {target[d]:.0%}")

    multi_share = sum(1 for _, it in items if it.get("type") == "multi") / n
    if multi_share > 0.15:
        warn(f"multi-answer items are {multi_share:.0%} of the bank, target ~10%")

    if batch:
        return

    # --- domain quotas ------------------------------------------------------
    per_domain = Counter(it.get("domain") for _, it in items)
    exams = n / 100
    for d, per100 in QUOTA_PER_100.items():
        expected = per100 * exams
        got = per_domain.get(d, 0)
        if abs(got - expected) > QUOTA_TOLERANCE * exams:
            err(f"domain {d}: {got} items, quota {expected:.0f} "
                f"(tolerance +/-{QUOTA_TOLERANCE * exams:.0f})")

    # --- objective coverage -------------------------------------------------
    per_obj = Counter(it.get("objective") for _, it in items)
    for oid in objectives:
        if per_obj.get(oid, 0) == 0:
            err(f"objective {oid} has zero items")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", type=pathlib.Path)
    ap.add_argument("--batch", action="store_true",
                    help="skip bank-wide quota and objective-coverage checks")
    args = ap.parse_args()

    objectives = load_blueprint()
    paths = args.paths or sorted(BANK.rglob("*.json"))
    if not paths:
        print("FATAL: no item files found under bank/", file=sys.stderr)
        return 2

    items = load_items(paths)
    for path, it in items:
        check_item(path, it, objectives)
    check_bank_wide(items, objectives, args.batch)

    scope = "batch" if args.batch else "full bank"
    print(f"validate.py ({scope}): {len(items)} items from {len(paths)} file(s)")

    for w in warnings:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  FAIL  {e}")

    if errors:
        print(f"\nFAILED with {len(errors)} error(s).")
        return 1
    print(f"\nOK ({len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
