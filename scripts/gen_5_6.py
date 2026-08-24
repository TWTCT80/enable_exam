#!/usr/bin/env python3
"""Generate bank/5/5.6.json - 'Configure and verify access control lists'.

Configure-and-verify, and the largest objective in domain 5.

The three faults that matter are all ones where the ACL is syntactically fine
and does the wrong thing: an entry shadowed by a broader deny above it (002), a
destination left as `any` so far more is blocked than intended (005), and a list
applied in the direction the traffic never crosses (009). Match counters appear
throughout, because a counter of zero is the evidence that separates them.
"""
import ipaddress
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import access_lists, acl_line, opts  # noqa: E402


def _selftest():
    # wildcard for a /26 is the inverse of 255.255.255.192
    net = ipaddress.ip_network("192.168.40.64/26")
    assert str(net.hostmask) == "0.0.0.63"
    assert str(ipaddress.ip_network("192.168.40.64/27").hostmask) == "0.0.0.31"
    assert str(ipaddress.ip_network("192.168.40.0/24").hostmask) == "0.0.0.255"
    # 192.168.30.55 falls inside the /24 that item 002 denies first
    assert ipaddress.ip_address("192.168.30.55") in ipaddress.ip_network("192.168.30.0/24")


_selftest()

# --- exhibits -------------------------------------------------------------

EX_001 = """R1 must permit traffic from every host in 192.168.40.64/26 and is
being given a standard access list to do it.

    192.168.40.64/26 runs from 192.168.40.64 to 192.168.40.127."""

EX_002 = access_lists("R2", [
    ("Standard IP access list 20", [
        acl_line(10, "deny", "192.168.30.0, wildcard bits 0.0.0.255", 3184),
        acl_line(20, "permit", "192.168.30.55", 0),
        acl_line(30, "permit", "any", 92417),
    ]),
]) + """

Line 20 was added so that the server at 192.168.30.55 would be exempt
from the block. It still cannot get through."""

EX_003 = access_lists("R3", [
    ("Standard IP access list 30", [
        acl_line(10, "permit", "10.10.1.0, wildcard bits 0.0.0.255", 4417),
        acl_line(20, "permit", "10.10.2.0, wildcard bits 0.0.0.255", 2298),
    ]),
]) + """

Access list 30 is applied inbound on GigabitEthernet0/1. Hosts in
10.10.1.0/24 and 10.10.2.0/24 pass without trouble. Hosts in
10.10.3.0/24 arrive on the same interface and are dropped, though no
line mentions them."""

EX_004 = """                                        +----------+
   10.1.5.0/24 ---[ R-BRANCH ]--- WAN ---[ R-HQ ]---| FILE-SRV |
     PC-A among them                                | 10.9.9.20|
                                                    +----------+

PC-A at 10.1.5.44 must be stopped from reaching FILE-SRV at 10.9.9.20.
PC-A must keep full access to every other destination, and every other
host must keep full access to FILE-SRV."""

EX_005 = access_lists("R5", [
    ("Extended IP access list 110", [
        acl_line(10, "deny", "tcp 10.20.0.0 0.0.255.255 any eq 22", 1204),
        acl_line(20, "permit", "ip any any", 58),
    ]),
]) + """

The intent was to stop staff subnets reaching the management server at
10.90.1.10 over SSH. Staff now report that they cannot open an SSH
session to any device at all."""

EX_006 = access_lists("R6", [
    ("Extended IP access list FILTER-IN", [
        acl_line(10, "permit", "tcp any host 10.9.9.20 eq www", 18422),
        acl_line(20, "permit", "tcp any host 10.9.9.20 eq 443", 40119),
        acl_line(30, "deny", "tcp any host 10.9.9.20", 0),
        acl_line(40, "permit", "ip any any", 7733),
    ]),
])

EX_007 = """! R7 - relevant configuration
!
ip access-list extended GUEST-FILTER
 deny ip 192.168.99.0 0.0.0.255 10.0.0.0 0.255.255.255
 permit ip any any
!
interface GigabitEthernet0/2
 description guest VLAN gateway
 ip address 192.168.99.1 255.255.255.0
!

GUEST-FILTER must be evaluated on traffic as it arrives from the guest
VLAN, before R7 routes it anywhere."""

EX_008 = access_lists("R8", [
    ("Standard IP access list 44", [
        acl_line(10, "permit", "172.16.8.0, wildcard bits 0.0.3.255", 9021),
        acl_line(20, "permit", "172.16.20.7", 145),
        acl_line(30, "deny", "any", 612),
    ]),
])

EX_009 = access_lists("R9", [
    ("Extended IP access list 120", [
        acl_line(10, "deny", "tcp 172.20.4.0 0.0.0.255 host 10.9.9.30 eq 3389", 0),
        acl_line(20, "permit", "ip any any", 0),
    ]),
]) + """

! R9 - relevant configuration
!
interface GigabitEthernet0/0
 description toward the 172.20.4.0/24 client subnet
 ip access-group 120 out
!

Clients in 172.20.4.0/24 still reach 10.9.9.30, which sits beyond
GigabitEthernet0/1."""


ITEMS = [
{
  "id": "5.6-001", "objective": "5.6", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which entry permits exactly that range and nothing beyond it?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "access-list 10 permit 192.168.40.64 255.255.255.192",
    "access-list 10 permit 192.168.40.64 0.0.0.31",
    "access-list 10 permit 192.168.40.64 0.0.0.63",
    "access-list 10 permit 192.168.40.64 0.0.0.255"),
  "correct": ["C"],
  "explanation": "An access list takes a wildcard mask, which is the inverse of the subnet mask, so a /26 written as 255.255.255.192 becomes 0.0.0.63 and covers the sixty-four addresses from .64 to .127. Option A supplies the subnet mask itself, which IOS reads as a wildcard and which would match an unintended scatter of addresses. Option B is the wildcard for a /27 and reaches only halfway to .127. Option D is the wildcard for a /24 and permits the whole of 192.168.40.0.",
  "difficulty": 2,
  "skills": ["access-control-lists", "wildcard-mask", "standard-acl", "configure-acl"],
},
{
  "id": "5.6-002", "objective": "5.6", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why is the server at 192.168.30.55 still blocked?",
  "exhibit": {"kind": "cli_output", "content": EX_002},
  "options": opts(
    "Line 10 denies the whole subnet first, so line 20 is never reached.",
    "The host entry on line 20 needs a wildcard of 0.0.0.0 before it takes effect.",
    "A standard access list cannot match a single host, only a whole network.",
    "The permit any on line 30 overrides everything configured above it."),
  "correct": ["A"],
  "explanation": "An access list is read from the top and stops at the first match, so 192.168.30.55 matches the deny on line 10 and is dropped before line 20 is considered; its counter of zero proves the line has never been reached. The exemption has to be placed above the deny to work. Option B invents a syntax requirement, since a bare address in a standard list already implies a host match. Option C is contradicted by line 20 being accepted at all. Option D reverses the order of evaluation.",
  "difficulty": 3,
  "skills": ["access-control-lists", "acl-order", "first-match-wins", "troubleshoot-acl"],
},
{
  "id": "5.6-003", "objective": "5.6", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why is traffic from 10.10.3.0/24 dropped when no line refers to it?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts(
    "The list has to be applied in both directions before return traffic passes.",
    "R3 needs a route to 10.10.3.0/24 before the access list will evaluate it.",
    "A deny statement for 10.10.3.0/24 is missing and has to be added explicitly.",
    "Every access list ends in an implicit deny, so unmatched traffic drops."),
  "correct": ["D"],
  "explanation": "Every access list carries an invisible deny any as its final entry, so a packet that matches no permit is discarded even though nothing visible mentions it; permitting 10.10.3.0/24 requires adding a line for it. Option A confuses direction of application with return traffic. Option B ties filtering to routing, but the list is evaluated on arrival regardless of whether a route exists. Option C has it backwards, since the drop is the default and it is the permit that would need adding.",
  "difficulty": 2,
  "skills": ["access-control-lists", "implicit-deny", "verify-acl", "troubleshoot-acl"],
},
{
  "id": "5.6-004", "objective": "5.6", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which approach meets both requirements?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts(
    "A standard list near the source on R-BRANCH, matching PC-A's address.",
    "An extended list near the source on R-BRANCH, matching PC-A and the server.",
    "A standard list near the destination on R-HQ, matching PC-A's address.",
    "An extended list near the destination on R-HQ, so the decision is made last."),
  "correct": ["B"],
  "explanation": "Only an extended list can match a source and a destination together, which is what letting PC-A reach everything except one server requires, and an extended list belongs close to the source so the unwanted traffic never crosses the WAN. Options A and C both use a standard list, which matches the source alone and would cut PC-A off from everything reachable through that interface. Option D matches correctly but carries the traffic across the WAN before discarding it, wasting the circuit it was meant to protect.",
  "difficulty": 2,
  "skills": ["access-control-lists", "extended-acl", "acl-placement", "standard-vs-extended"],
},
{
  "id": "5.6-005", "objective": "5.6", "domain": 5, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Which two observations explain why staff lost SSH to every device? (Choose two.)",
  "exhibit": {"kind": "cli_output", "content": EX_005},
  "options": opts(
    "The source wildcard is too narrow to reach the staff subnets.",
    "The destination reads any, so SSH to every host is denied rather than one.",
    "Line 20 is never evaluated, because the deny above consumes every packet.",
    "Naming host 10.90.1.10 as the destination would restore the intent.",
    "An extended list cannot match a port, so the eq keyword is ignored."),
  "correct": ["B", "D"],
  "explanation": "The rule was meant to protect one management server, but its destination field says any, so every SSH session from those subnets is dropped wherever it was headed; replacing any with the server's own address narrows it to what was intended. Option A points at the source wildcard, which is wide but deliberately so. Option C is contradicted by line 20 showing fifty-eight matches. Option E denies port matching, which is what distinguishes an extended list from a standard one.",
  "difficulty": 3,
  "skills": ["access-control-lists", "extended-acl", "over-broad-match", "troubleshoot-acl"],
},
{
  "id": "5.6-006", "objective": "5.6", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which line of FILTER-IN has never matched a packet?",
  "exhibit": {"kind": "cli_output", "content": EX_006},
  "options": opts("Line 30", "Line 10", "Line 40", "Line 20"),
  "correct": ["A"],
  "explanation": "Each entry carries a running match counter, and line 30 is the only one reading zero, meaning no traffic to that host has ever fallen through to it. Options B and D are the two permits carrying tens of thousands of matches between them. Option C is the final permit, which has matched 7,733 packets bound elsewhere. A counter of zero is worth noticing either way: it can mean the rule is unnecessary, or that something above it is matching first.",
  "difficulty": 1,
  "skills": ["access-control-lists", "verify-acl", "match-counters", "read-correct-row"],
},
{
  "id": "5.6-007", "objective": "5.6", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which command applies GUEST-FILTER as the requirement describes?",
  "exhibit": {"kind": "config", "content": EX_007},
  "options": opts(
    "R7(config)# ip access-group GUEST-FILTER in",
    "R7(config-if)# ip access-group extended GUEST-FILTER in",
    "R7(config-if)# ip access-list GUEST-FILTER in",
    "R7(config-if)# ip access-group GUEST-FILTER in"),
  "correct": ["D"],
  "explanation": "A list is bound to an interface with ip access-group, entered under that interface, and in applies it to traffic arriving from the guest VLAN before routing. Option A has the right command but is entered in global configuration mode, where it does not exist. Option B inserts the extended keyword, which belongs to ip access-list when the list is created rather than to the command that binds it. Option C uses ip access-list, which opens the list for editing instead of binding it to the interface.",
  "difficulty": 2,
  "skills": ["access-control-lists", "ip-access-group", "config-mode", "apply-acl"],
},
{
  "id": "5.6-008", "objective": "5.6", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which line of access list 44 permits a host at 172.16.10.30?",
  "exhibit": {"kind": "cli_output", "content": EX_008},
  "options": opts("Line 20", "Line 10", "Line 30", "No line permits it"),
  "correct": ["B"],
  "explanation": "The wildcard 0.0.3.255 on line 10 leaves the last two bits of the third octet free, so it covers 172.16.8.0 through 172.16.11.255, and 172.16.10.30 falls inside that range. Option A permits a single host at 172.16.20.7 and nothing else. Option C is the explicit deny that closes the list. Option D would be correct only if the wildcard were read as covering 172.16.8.0 alone rather than a block of four.",
  "difficulty": 1,
  "skills": ["access-control-lists", "wildcard-mask", "verify-acl", "block-size"],
},
{
  "id": "5.6-009", "objective": "5.6", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why does list 120 have no effect on the traffic it was written for?",
  "exhibit": {"kind": "cli_output", "content": EX_009},
  "options": opts(
    "The list should match on the destination port rather than the source subnet.",
    "Extended lists must be numbered above 199 before they can be applied outbound.",
    "It is applied outbound on the interface the clients arrive on.",
    "The permit on line 20 cancels the deny above it whenever both are unmatched."),
  "correct": ["C"],
  "explanation": "Traffic from 172.20.4.0/24 enters R9 on Gi0/0 and leaves by Gi0/1, so an outbound list on Gi0/0 only sees traffic travelling the other way; both counters reading zero confirms nothing has ever been evaluated. Applying it inbound on Gi0/0, or outbound on Gi0/1, would work. Option A misplaces the fault in the matching, which is written correctly. Option B invents a numbering rule. Option D reverses how evaluation works, since a deny that matches stops the list.",
  "difficulty": 2,
  "skills": ["access-control-lists", "acl-direction", "apply-acl", "troubleshoot-acl"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "5" / "5.6.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "5.6",
    "domain": 5,
    "blueprint_version": "v1.1",
    "scope_note": ("Wildcard arithmetic is asserted with the ipaddress module at "
                   "generation time. Match counters carry the evidence in the "
                   "troubleshooting items."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items, wildcard self-test passed)")
