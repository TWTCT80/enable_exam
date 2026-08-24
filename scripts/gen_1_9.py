#!/usr/bin/env python3
"""Generate bank/1/1.9.json - 'Describe IPv6 address types'.

Covers the objective's four sub-topics: unicast (global, unique local, link
local), anycast, multicast, and modified EUI-64. Describe-level, so each item
makes the candidate classify a real address out of an exhibit rather than
recall a range table.
"""
import ipaddress
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

RANGES = {
    "global": ipaddress.IPv6Network("2000::/3"),
    "ula": ipaddress.IPv6Network("fc00::/7"),
    "link_local": ipaddress.IPv6Network("fe80::/10"),
    "multicast": ipaddress.IPv6Network("ff00::/8"),
}

MAC_003 = "00:0C:29:AB:CD:EF"


def eui64(prefix, mac):
    raw = bytearray(bytes.fromhex(mac.replace(":", "").replace(".", "")))
    raw[0] ^= 0x02
    iid = bytes(raw[:3]) + b"\xff\xfe" + bytes(raw[3:])
    net = ipaddress.IPv6Network(prefix)
    return ipaddress.IPv6Address(int(net.network_address) | int.from_bytes(iid, "big"))


LL_003 = eui64("fe80::/64", MAC_003)


def _selftest():
    def where(a):
        a = ipaddress.IPv6Address(a)
        return {k for k, n in RANGES.items() if a in n}

    assert where("2001:db8:acad:1::10") == {"global"}
    assert where("fd3a:9c21:4e7b:1::10") == {"ula"}
    assert where("fe80::20c:29ff:feab:cdef") == {"link_local"}
    assert where("ff02::1") == {"multicast"}
    assert where("ff02::2") == {"multicast"}
    assert str(LL_003) == "fe80::20c:29ff:feab:cdef", LL_003
    # solicited-node multicast for 2001:db8:acad:1::1 takes the low 24 bits
    assert ipaddress.IPv6Address("ff02::1:ff00:1") in RANGES["multicast"]


_selftest()

# --- exhibits -------------------------------------------------------------

EX_001 = """Addresses observed on one segment during a survey

    Host        Address
    --------    ---------------------------
    SRV-A       2001:DB8:ACAD:1::10
    SRV-B       FD3A:9C21:4E7B:1::10
    SW-MGMT     FE80::20C:29FF:FEAB:CDEF
    (group)     FF02::1"""

EX_002 = """R2# show ipv6 interface GigabitEthernet0/0
GigabitEthernet0/0 is up, line protocol is up
  IPv6 is enabled, link-local address is FE80::21A:2BFF:FE3C:4D5E
  Global unicast address(es):
    2001:DB8:ACAD:1::1, subnet is 2001:DB8:ACAD:1::/64
  Joined group address(es):
    FF02::1
    FF02::2
    FF02::1:FF00:1
  MTU is 1500 bytes"""

EX_003 = f"""! Host NIC details
!
    Burned-in address . . . : {MAC_003.replace(':', '').lower()[:4]}.{MAC_003.replace(':', '').lower()[4:8]}.{MAC_003.replace(':', '').lower()[8:]}
    IPv6 routing  . . . . . : enabled on the segment

The interface has just been brought up and has not yet received a router
advertisement, so it has formed only its link-local address."""

EX_004 = """PC1> ipconfig

Ethernet adapter Ethernet:

   IPv6 Address. . . . . . . . . . . : 2001:DB8:ACAD:1:2C4A:9B11:78D3:5E02
   Temporary IPv6 Address. . . . . . : 2001:DB8:ACAD:1:9017:E3B2:44AC:1F65
   Link-local IPv6 Address . . . . . : FE80::2C4A:9B11:78D3:5E02
   Default Gateway . . . . . . . . . : FE80::1"""


ITEMS = [
{
  "id": "1.9-001", "objective": "1.9", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which address is a unique local address, routable inside the organisation but never across the internet?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts("2001:DB8:ACAD:1::10", "FE80::20C:29FF:FEAB:CDEF", "FF02::1",
                  "FD3A:9C21:4E7B:1::10"),
  "correct": ["D"],
  "explanation": "Unique local addresses come from FC00::/7 and are written in practice beginning FD, so FD3A:9C21:4E7B:1::10 is the one that routes within the organisation while being filtered at its edge. Option A begins with 2001 and falls in 2000::/3, the global unicast space that is routable across the internet. Option B begins FE80 and is link-local, which cannot be routed off its own link at all. Option C begins FF and is a multicast group address rather than a unicast address for any single host.",
  "difficulty": 2,
  "skills": ["ipv6-address-types", "unique-local-address", "global-unicast", "address-range-boundary"],
},
{
  "id": "1.9-002", "objective": "1.9", "domain": 1, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Which two of the joined groups would an ordinary IPv6 host join as well, not only a router? (Choose two.)",
  "exhibit": {"kind": "cli_output", "content": EX_002},
  "options": opts("FF02::1", "FF02::2", "FE80::21A:2BFF:FE3C:4D5E",
                  "FF02::1:FF00:1", "2001:DB8:ACAD:1::1"),
  "correct": ["A", "D"],
  "explanation": "FF02::1 is the all-nodes group, which every IPv6 interface joins whatever its role, and FF02::1:FF00:1 is the solicited-node group derived from the low-order bits of the interface's own unicast address, which hosts and routers alike use for neighbour discovery. Option B is the all-routers group and marks this interface as a router's. Option C is the link-local unicast address rather than a group. Option E is the global unicast address, also not a group.",
  "difficulty": 2,
  "skills": ["ipv6-address-types", "multicast", "solicited-node-multicast", "all-nodes-group"],
},
{
  "id": "1.9-003", "objective": "1.9", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which link-local address does this interface form for itself?",
  "exhibit": {"kind": "config", "content": EX_003},
  "options": opts(
    "FE80::20C:29FF:FEAB:CDEF",
    "FE80::C:29FF:FEAB:CDEF",
    "FE80::20C:29FE:FFAB:CDEF",
    "FE80::20C:29FF:FECD:EFAB"),
  "correct": ["A"],
  "explanation": "A link-local address is FE80 followed by an interface identifier built by modified EUI-64: the MAC splits into 000C29 and ABCDEF, FFFE goes between them, and the seventh bit of the first byte inverts so 00 becomes 02. Option B leaves the first byte uninverted and then drops its leading digit, losing the 02 entirely. Option C writes the inserted value as FEFF instead of FFFE. Option D rotates the final three octets of the MAC rather than keeping their order.",
  "difficulty": 3,
  "skills": ["ipv6-address-types", "modified-eui-64", "link-local-address", "ul-bit-inversion"],
},
{
  "id": "1.9-004", "objective": "1.9", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which address would this host use as the source when contacting a server elsewhere on the internet?",
  "exhibit": {"kind": "cli_output", "content": EX_004},
  "options": opts(
    "FE80::2C4A:9B11:78D3:5E02",
    "FE80::1",
    "2001:DB8:ACAD:1:9017:E3B2:44AC:1F65",
    "2001:DB8:ACAD:1:2C4A:9B11:78D3:5E02"),
  "correct": ["C"],
  "explanation": "A host with both a stable and a temporary global address prefers the temporary one as the source for connections it starts outward, which is what the privacy extension exists to do, so the 9017 address is used. Option D is the stable global address and serves inbound connections rather than outbound ones. Option A is link-local and cannot leave the segment. Option B is link-local too and belongs to the router, appearing here only as the default gateway.",
  "difficulty": 1,
  "skills": ["ipv6-address-types", "global-unicast", "temporary-address", "verify-ip-parameters"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "1" / "1.9.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "1.9",
    "domain": 1,
    "blueprint_version": "v1.1",
    "scope_note": ("Address-type ranges and the EUI-64 derivation are asserted with "
                   "the ipaddress module in _selftest() rather than recalled."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items, address-type self-test passed)")
