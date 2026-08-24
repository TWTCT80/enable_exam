#!/usr/bin/env python3
"""Replace one item block in a generator with new text, in place.

Used to raise the multi-answer share without disturbing anything else: each
replacement sits on the same objective and carries the same difficulty as the
item it displaces, so domain quotas, per-objective counts and the difficulty
mix all come out unchanged.

    from swap_item import replace_item
    replace_item("scripts/gen_1_4.py", "1.4-002", NEW_BLOCK)

NEW_BLOCK is the item dict as source text, starting at '{' and ending at '},'.
"""
import pathlib
import re
import sys


def replace_item(gen_path: str, item_id: str, new_block: str) -> None:
    p = pathlib.Path(gen_path)
    src = p.read_text()

    start_marker = '\n{\n  "id": "%s"' % item_id
    start = src.find(start_marker)
    if start < 0:
        raise SystemExit(f"{gen_path}: item {item_id} not found")
    start += 1                                    # keep the preceding newline

    # item blocks close with '},' on a line of their own at column 0
    end = src.find("\n},\n", start)
    if end < 0:
        raise SystemExit(f"{gen_path}: no closing brace found for {item_id}")
    end += len("\n},\n")

    block = new_block.rstrip()
    if not block.endswith(","):
        block += ","
    p.write_text(src[:start] + block + "\n" + src[end:])


def exhibit_var(gen_path: str, item_id: str) -> str:
    """Report which exhibit variable an item currently uses, for reuse."""
    src = pathlib.Path(gen_path).read_text()
    start = src.find('"id": "%s"' % item_id)
    if start < 0:
        return "?"
    m = re.search(r'"content": (\w+)', src[start:start + 900])
    return m.group(1) if m else "inline"


if __name__ == "__main__":
    print(exhibit_var(sys.argv[1], sys.argv[2]))
