#!/usr/bin/env python3
"""Generate bank/1/1.7.json - 'Describe private IPv4 addressing'.

A describe-level objective with one fact worth testing properly: where the
RFC 1918 boundaries actually fall. Every item turns on reading an address
against a range rather than reciting the ranges, and the 172.16.0.0/12
boundary - which ends at 172.31.255.255, not 172.16.255.255 - carries two of
the three items because that is where candidates actually slip.
"""
import ipaddress
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import ip_int_brief, ipint, opts  # noqa: E402

PRIVATE = [ipaddress.ip_network(n) for n in
           ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]


def is_private(addr):
    a = ipaddress.ip_network(addr, strict=False)
    return any(a.subnet_of(p) for p in PRIVATE)


# the whole point of this objective, asserted rather than assumed
assert is_private("10.14.0.0/16")
assert is_private("172.20.0.0/16")
assert not is_private("172.32.0.0/16")      # past the /12 boundary
assert is_private("172.31.255.0/24")        # last private block in that space
assert is_private("192.168.44.0/24")
assert not is_private("203.0.113.0/24") and not is_private("198.51.100.0/24")

# --- exhibits -------------------------------------------------------------

EX_001 = """Branch address blocks proposed for a new deployment

    Site            Block
    ------------    ------------------
    Manchester      10.14.0.0/16
    Leeds           172.20.0.0/16
    Bristol         172.32.0.0/16
    Cardiff         192.168.44.0/24

All four sites reach the internet through one border router."""

EX_002 = """! R2 - proposed addressing for the new data centre
!
interface GigabitEthernet0/2
 description data centre core
 ip address 172.32.10.1 255.255.255.0
 no shutdown
!

The design standard requires every internal segment to use address space
reserved for private use."""

EX_003 = ip_int_brief("BORDER1", [
    ipint("GigabitEthernet0/0", "203.0.113.2"),
    ipint("GigabitEthernet0/1", "10.8.8.1"),
    ipint("GigabitEthernet0/2", "198.51.100.7"),
    ipint("GigabitEthernet0/3", "172.32.4.1"),
])


ITEMS = [
{
  "id": "1.7-001", "objective": "1.7", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which site's block is publicly routable and therefore would not require translation at the border?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts("10.14.0.0/16", "172.20.0.0/16", "172.32.0.0/16", "192.168.44.0/24"),
  "correct": ["C"],
  "explanation": "The private space in the 172 range is 172.16.0.0/12, which runs from 172.16.0.0 to 172.31.255.255, so Bristol's 172.32.0.0/16 sits just past the end of it and is ordinary public address space. Option A falls inside 10.0.0.0/8 and is private. Option B at 172.20.0.0 sits comfortably within the /12 and is private too, which is exactly what makes the pair worth comparing. Option D falls inside 192.168.0.0/16 and is private.",
  "difficulty": 2,
  "skills": ["private-ipv4-addressing", "rfc1918-ranges", "address-range-boundary", "nat-requirement"],
},
{
  "id": "1.7-002", "objective": "1.7", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why does the proposed address fail the design standard?",
  "exhibit": {"kind": "config", "content": EX_002},
  "options": opts(
    "The private range in that space ends at 172.31.255.255.",
    "The private range in that space ends at 172.16.255.255.",
    "Addresses beginning 172.32 are reserved for multicast rather than unicast.",
    "Only 10.0.0.0/8 and 192.168.0.0/16 are private; no 172 block qualifies."),
  "correct": ["A"],
  "explanation": "The reserved block is 172.16.0.0/12, whose twelve network bits leave the second octet free to run from 16 through 31, so 172.32.10.1 falls one step outside private space and is publicly assigned. Option B stops the range at the end of 172.16, treating the /12 as though it were a /16 and shrinking the space sixteenfold. Option C confuses this with the multicast range, which begins at 224.0.0.0. Option D denies that any 172 block is private, which would make 172.16.0.0/12 itself public.",
  "difficulty": 2,
  "skills": ["private-ipv4-addressing", "rfc1918-ranges", "address-range-boundary", "prefix-length-arithmetic"],
},
{
  "id": "1.7-003", "objective": "1.7", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which interface on the border router carries an address drawn from private space?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts("GigabitEthernet0/0", "GigabitEthernet0/1", "GigabitEthernet0/2",
                  "GigabitEthernet0/3"),
  "correct": ["B"],
  "explanation": "GigabitEthernet0/1 holds 10.8.8.1, which sits inside 10.0.0.0/8 and is the only private address in the output. Option A is 203.0.113.2, a publicly assigned address. Option C is 198.51.100.7, also public. Option D is the trap: 172.32.4.1 looks like the familiar private 172 space, but private use stops at 172.31.255.255, so that address is public as well.",
  "difficulty": 1,
  "skills": ["private-ipv4-addressing", "rfc1918-ranges", "verify-ip-parameters", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "1" / "1.7.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "1.7",
    "domain": 1,
    "blueprint_version": "v1.1",
    "scope_note": ("RFC 1918 boundaries are asserted with the ipaddress module at "
                   "generation time, including that 172.16.0.0/12 ends at "
                   "172.31.255.255."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items, range assertions passed)")
