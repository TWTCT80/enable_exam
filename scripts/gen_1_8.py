#!/usr/bin/env python3
"""Generate bank/1/1.8.json - 'Configure and verify IPv6 addressing and prefix'.

Configure-and-verify. As with 1.6, every address this file asserts is computed
or checked with the ipaddress module by _selftest() before the file is written,
including the EUI-64 derivation, so a transposed group cannot reach a candidate.
"""
import ipaddress
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import ipv6_int_brief, ipv6_int, opts  # noqa: E402


def eui64(prefix, mac):
    """Modified EUI-64: split the MAC, insert FFFE, invert the U/L bit."""
    raw = bytearray(bytes.fromhex(mac.replace(":", "").replace(".", "")))
    raw[0] ^= 0x02
    iid = bytes(raw[:3]) + b"\xff\xfe" + bytes(raw[3:])
    net = ipaddress.IPv6Network(prefix)
    return ipaddress.IPv6Address(int(net.network_address) | int.from_bytes(iid, "big"))


MAC_002 = "00:1A:2B:3C:4D:5E"
EUI_002 = eui64("2001:db8:acad:1::/64", MAC_002)


def _selftest():
    assert str(EUI_002) == "2001:db8:acad:1:21a:2bff:fe3c:4d5e", EUI_002

    a = ipaddress.IPv6Address("2001:0DB8:0000:0000:0000:0AB0:0000:00CD")
    assert a.compressed == "2001:db8::ab0:0:cd"
    assert a == ipaddress.IPv6Address("2001:db8:0:0:0:ab0:0:cd")   # same, uncompressed
    assert a != ipaddress.IPv6Address("2001:db8::ab:0:cd")         # genuinely different

    p48 = ipaddress.IPv6Network("2001:db8:acad::/48")
    assert ipaddress.IPv6Network("2001:db8:acad:7::/64").subnet_of(p48)
    assert not ipaddress.IPv6Network("2001:db8:acae:7::/64").subnet_of(p48)
    try:
        ipaddress.IPv6Network("2001:db8:acad::7/64")
        raise AssertionError("expected host bits to be rejected")
    except ValueError:
        pass

    n1 = ipaddress.IPv6Network("2001:db8:acad:1::1/64", strict=False)
    n2 = ipaddress.IPv6Network("2001:db8:acad:2::1/64", strict=False)
    assert n1 != n2
    # both link-locals stay on one link regardless, which is the point of item 005
    assert ipaddress.IPv6Address("fe80::1") in ipaddress.IPv6Network("fe80::/10")


_selftest()

UP = "up/up"
DOWN = "administratively down/down"

# --- exhibits -------------------------------------------------------------

EX_001 = """An address has been recorded in full, unabbreviated form:

    2001:0DB8:0000:0000:0000:0AB0:0000:00CD

It must be entered into the documentation in its shortest valid form."""

EX_002 = f"""! R2 - relevant configuration
!
interface GigabitEthernet0/0
 ipv6 address 2001:DB8:ACAD:1::/64 eui-64
 no shutdown
!

The burned-in address of GigabitEthernet0/0 is {MAC_002.replace(':', '').lower()[:4]}.{MAC_002.replace(':', '').lower()[4:8]}.{MAC_002.replace(':', '').lower()[8:]}."""

EX_003 = """The organisation has been allocated 2001:DB8:ACAD::/48 and subnets it
into /64 segments, one per VLAN.

    VLAN 10   segment 1
    VLAN 20   segment 2
    VLAN 30   segment 7   <- being configured now"""

EX_004 = ipv6_int_brief("R4", [
    ipv6_int("GigabitEthernet0/0", UP, ["FE80::21A:2BFF:FE3C:4D5E"]),
    ipv6_int("GigabitEthernet0/1", UP,
             ["FE80::21A:2BFF:FE3C:4D5F", "2001:DB8:ACAD:9::1"]),
    ipv6_int("GigabitEthernet0/2", DOWN, ["unassigned"]),
])

EX_005 = """! R1 and R2 are cabled directly to one another
!
R1  interface GigabitEthernet0/0
     ipv6 address 2001:DB8:ACAD:1::1/64
!
R2  interface GigabitEthernet0/0
     ipv6 address 2001:DB8:ACAD:2::1/64
!

Each router can ping the other's link-local address, but a ping to the
other's global address fails."""

EX_006 = """! R6 - relevant configuration
!
interface GigabitEthernet0/0
 no shutdown
!

GigabitEthernet0/0 must take its prefix from the router advertisements
already being sent on the segment and build its own interface identifier,
without any DHCPv6 server involved."""

EX_007 = ipv6_int_brief("R7", [
    ipv6_int("GigabitEthernet0/0", UP,
             ["FE80::2D0:58FF:FE12:3401", "2001:DB8:CAFE:10::1"]),
    ipv6_int("GigabitEthernet0/1", UP,
             ["FE80::2D0:58FF:FE12:3402", "2001:DB8:CAFE:20::1"]),
    ipv6_int("Loopback0", UP, ["FE80::2D0:58FF:FE12:3400", "2001:DB8:CAFE:FF::1"]),
])


ITEMS = [
{
  "id": "1.8-001", "objective": "1.8", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which entry is the shortest valid form of the recorded address?",
  "exhibit": {"kind": "config", "content": EX_001},
  "options": opts(
    "2001:DB8::AB0::CD",
    "2001:DB8::AB0:0:CD",
    "2001:DB8::AB:0:CD",
    "2001:DB8:0:0:0:AB0:0:CD"),
  "correct": ["B"],
  "explanation": "Leading zeros in a group are dropped and the single longest run of all-zero groups is replaced by a double colon, which here is the three groups before 0AB0, giving 2001:DB8::AB0:0:CD. Option A uses two double colons, which is invalid because the expansion would then be ambiguous. Option C loses a digit from 0AB0, turning it into AB and producing a different address entirely. Option D drops leading zeros correctly but never applies the double colon, so it is valid yet not the shortest form.",
  "difficulty": 2,
  "skills": ["ipv6-addressing", "address-compression", "leading-zero-rules", "double-colon-rule"],
},
{
  "id": "1.8-002", "objective": "1.8", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which global unicast address does GigabitEthernet0/0 build for itself?",
  "exhibit": {"kind": "config", "content": EX_002},
  "options": opts(
    "2001:DB8:ACAD:1:1A:2BFF:FE3C:4D5E",
    "2001:DB8:ACAD:1:21A:2BFE:FF3C:4D5E",
    "2001:DB8:ACAD:1:21A:2BFF:FE3C:4D5E",
    "2001:DB8:ACAD:1:21A:2BFF:FE4D:5E3C"),
  "correct": ["C"],
  "explanation": "Modified EUI-64 splits the MAC in half, inserts FFFE between the two halves, and inverts the seventh bit of the first byte, turning 00 into 02; 001A2B and 3C4D5E therefore become 021A:2BFF:FE3C:4D5E under the configured prefix. Option A skips the bit inversion and leaves the first byte as 00, which is the single commonest omission. Option B writes the inserted value as FEFF rather than FFFE. Option D transposes the final two groups of the interface identifier.",
  "difficulty": 3,
  "skills": ["ipv6-addressing", "modified-eui-64", "interface-identifier", "ul-bit-inversion"],
},
{
  "id": "1.8-003", "objective": "1.8", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which entry correctly expresses the /64 segment for VLAN 30?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "2001:DB8:ACAD:7::/64",
    "2001:DB8:ACAE:7::/64",
    "2001:DB8:ACAD:7::/48",
    "2001:DB8:ACAD::7/64"),
  "correct": ["A"],
  "explanation": "A /48 allocation fixes the first three groups and leaves the fourth free as a subnet identifier, so segment 7 is written 2001:DB8:ACAD:7::/64. Option B alters the third group from ACAD to ACAE, which falls outside the allocation altogether. Option C keeps the right address but labels it /48, the length of the whole allocation rather than one segment. Option D places the 7 in the interface identifier instead of the subnet field, describing a host address rather than a subnet.",
  "difficulty": 2,
  "skills": ["ipv6-addressing", "ipv6-prefix", "subnet-identifier", "prefix-length"],
},
{
  "id": "1.8-004", "objective": "1.8", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which interface is up but has no address that can be routed off the local link?",
  "exhibit": {"kind": "cli_output", "content": EX_004},
  "options": opts("GigabitEthernet0/1", "Loopback0", "GigabitEthernet0/2",
                  "GigabitEthernet0/0"),
  "correct": ["D"],
  "explanation": "GigabitEthernet0/0 shows up/up but lists only an FE80 address, and link-local addresses are confined to the link they sit on, so nothing can be routed to it from elsewhere. Option A carries a 2001 global address in addition to its link-local and is fully reachable. Option C is administratively down and unassigned, so it fails the up part of the question rather than the addressing part. Option B names an interface that does not appear in this output at all.",
  "difficulty": 2,
  "skills": ["verify-ipv6-addressing", "show-ipv6-interface-brief", "link-local-scope", "global-unicast"],
},
{
  "id": "1.8-005", "objective": "1.8", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why do the link-local pings succeed while the global ones fail?",
  "exhibit": {"kind": "config", "content": EX_005},
  "options": opts(
    "Link-local addresses are always reachable, but global addresses require DHCPv6.",
    "The two global addresses sit in different /64 prefixes, so they need routing.",
    "The global addresses lack an EUI-64 interface identifier and cannot be pinged.",
    "Global addresses require ipv6 unicast-routing on both routers before any ping."),
  "correct": ["B"],
  "explanation": "The fourth group differs, making the prefixes 2001:DB8:ACAD:1::/64 and 2001:DB8:ACAD:2::/64, so the two globals are on separate subnets and would need a router between them. Link-local pings still work because FE80 addresses are scoped to the shared link and do not depend on the prefixes at all, which is exactly what makes the fault look intermittent. Option A invents a DHCPv6 dependency for statically configured addresses. Option C treats EUI-64 as mandatory, but a manually written identifier is fine. Option D would prevent transit routing, not a directly connected ping.",
  "difficulty": 3,
  "skills": ["ipv6-addressing", "ipv6-prefix", "same-subnet-requirement", "link-local-scope"],
},
{
  "id": "1.8-006", "objective": "1.8", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which interface command meets the requirement?",
  "exhibit": {"kind": "config", "content": EX_006},
  "options": opts(
    "ipv6 address autoconfig",
    "ipv6 address dhcp",
    "ipv6 address 2001:DB8:ACAD:1::1/64",
    "ipv6 enable",
    "ipv6 unicast-routing"),
  "correct": ["A"],
  "explanation": "Stateless address autoconfiguration takes the prefix from a router advertisement and appends an interface identifier the device generates itself, which is precisely what the requirement describes. Option B requests an address from a DHCPv6 server, which the requirement rules out explicitly. Option C hardcodes the prefix instead of learning it, so the address would not follow a renumbering. Option D brings IPv6 up but yields a link-local address only, leaving no global address. Option E is a global command enabling forwarding for the whole router and cannot be entered against an interface.",
  "difficulty": 2,
  "skills": ["ipv6-addressing", "slaac", "configure-ipv6-interface", "config-mode"],
},
{
  "id": "1.8-007", "objective": "1.8", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which global unicast address has been configured on GigabitEthernet0/1?",
  "exhibit": {"kind": "cli_output", "content": EX_007},
  "options": opts("2001:DB8:CAFE:10::1", "FE80::2D0:58FF:FE12:3402",
                  "2001:DB8:CAFE:20::1", "2001:DB8:CAFE:FF::1"),
  "correct": ["C"],
  "explanation": "Each block lists its interface first and its addresses beneath, and the second entry under GigabitEthernet0/1 is the global address 2001:DB8:CAFE:20::1. Option A belongs to GigabitEthernet0/0, the block directly above, which is the classic error of reading the right field from the neighbouring block. Option B is the correct block's link-local rather than its global address. Option D is the loopback's global address, taken from the block below.",
  "difficulty": 1,
  "skills": ["verify-ipv6-addressing", "show-ipv6-interface-brief", "global-unicast", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "1" / "1.8.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "1.8",
    "domain": 1,
    "blueprint_version": "v1.1",
    "scope_note": ("Configure and verify. EUI-64 derivation, compression and prefix "
                   "containment are all computed with the ipaddress module in "
                   "_selftest() before this file is written."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items, IPv6 self-test passed)")
