#!/usr/bin/env python3
"""Generate bank/6/6.7.json - 'Recognize components of JSON-encoded data'.

Objects, arrays, key/value pairs and the scalar types. Every payload in this
file is parsed with json.loads() at generation time, and the deliberately
broken one in 003 is asserted to FAIL parsing - so the item cannot ship
claiming a syntax error that does not exist, or a valid document that does.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

DEVICE = {
    "device": {
        "hostname": "R1",
        "management": {"address": "10.9.9.1", "protocol": "https", "port": 443},
        "interfaces": [
            {"name": "GigabitEthernet0/0", "enabled": True,
             "addresses": ["10.1.1.1/30"]},
            {"name": "GigabitEthernet0/1", "enabled": False, "addresses": []},
        ],
        "location": None,
    }
}

BROKEN = """{
  "hostname": "SW1",
  "vlans": [10, 20, 30],
  "uplink": {
    "name": "GigabitEthernet0/1",
    "trunk": True
  }
}"""


def _selftest():
    doc = json.loads(json.dumps(DEVICE))
    ifs = doc["device"]["interfaces"]
    assert len(ifs) == 2
    assert ifs[1]["enabled"] is False and ifs[1]["addresses"] == []
    assert isinstance(ifs[0]["addresses"], list) and len(ifs[0]["addresses"]) == 1
    assert doc["device"]["location"] is None
    # 003 must genuinely be invalid JSON, and valid once True is lower-cased
    try:
        json.loads(BROKEN)
        raise AssertionError("BROKEN parsed; the item claims a fault that is absent")
    except json.JSONDecodeError:
        pass
    json.loads(BROKEN.replace("True", "true"))


_selftest()

PAYLOAD = json.dumps(DEVICE, indent=2)

EX_A = "GET /api/v1/device HTTP/1.1 returned the following body:\n\n" + PAYLOAD
EX_003 = ("A colleague hand-wrote this file and the parser rejects it.\n\n"
          + BROKEN)


ITEMS = [
{
  "id": "6.7-001", "objective": "6.7", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does the payload record about the second entry in the interfaces array?",
  "exhibit": {"kind": "config", "content": EX_A},
  "options": opts(
    "It is enabled and carries a single address.",
    "It is disabled but still carries a single address.",
    "It is enabled and carries no addresses at all.",
    "It is disabled and carries no addresses at all."),
  "correct": ["D"],
  "explanation": "The second object in the array sets enabled to false and gives addresses an empty pair of brackets, so both readings point the same way: the interface is down and holds nothing. Option A describes the first entry instead, which is the ordinary wrong-element read when arrays are indexed by eye. Option B takes the correct enabled value but the wrong address list. Option C reverses both fields at once.",
  "difficulty": 2,
  "skills": ["json", "json-arrays", "json-objects", "read-correct-row"],
},
{
  "id": "6.7-002", "objective": "6.7", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What kind of JSON value does addresses hold on the first interface?",
  "exhibit": {"kind": "config", "content": EX_A},
  "options": opts(
    "An object, because it groups related settings together.",
    "An array holding one string.",
    "A string that happens to contain a prefix length.",
    "A number, written in the dotted form addresses use."),
  "correct": ["B"],
  "explanation": "Square brackets mark an array and the single element inside them is quoted, so this is an array containing one string, which is why an interface with no addresses shows empty brackets rather than being absent. Option A describes braces, which JSON uses for objects such as management. Option C ignores the brackets and would leave no way to hold a second address. Option D calls a quoted value a number, and JSON numbers are never quoted.",
  "difficulty": 2,
  "skills": ["json", "json-arrays", "json-data-types", "json-strings"],
},
{
  "id": "6.7-003", "objective": "6.7", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why does the parser reject this document?",
  "exhibit": {"kind": "config", "content": EX_003},
  "options": opts(
    "The vlans array may not hold bare numbers; each value needs quoting.",
    "An object cannot be nested inside another object in JSON.",
    "JSON booleans are written true and false, in lower case.",
    "The last key in an object must be followed by a trailing comma."),
  "correct": ["C"],
  "explanation": "JSON spells its booleans entirely in lower case, so True is not a keyword the parser recognises and the document fails at that line; the capitalised form comes from Python and is a frequent slip when a file is written by hand. Option A is wrong because unquoted numbers are exactly how JSON expresses them. Option B is contradicted by the uplink object, which nests legitimately. Option D inverts the rule, since a trailing comma is itself invalid.",
  "difficulty": 3,
  "skills": ["json", "json-syntax", "json-data-types", "troubleshoot-json"],
},
{
  "id": "6.7-004", "objective": "6.7", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. How many interface objects does this payload describe?",
  "exhibit": {"kind": "config", "content": EX_A},
  "options": opts("Two", "One", "Four", "None; interfaces holds an object"),
  "correct": ["A"],
  "explanation": "The interfaces array holds two brace-delimited objects, one per interface, each with its own name, enabled flag and address list. Option B counts only the first. Option C counts the key/value pairs inside one object rather than the objects themselves. Option D misreads the square brackets as braces, and the difference matters: an array can grow to hold more interfaces where a single object could not.",
  "difficulty": 1,
  "skills": ["json", "json-arrays", "json-objects", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "6" / "6.7.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "6.7",
    "domain": 6,
    "blueprint_version": "v1.1",
    "scope_note": ("Every payload is parsed with json.loads() at generation time, and "
                   "the broken one is asserted to fail parsing."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items, JSON parse self-test passed)")
