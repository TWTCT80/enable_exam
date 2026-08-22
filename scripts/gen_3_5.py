#!/usr/bin/env python3
"""Generate bank/3/3.5.json - 'Describe the purpose, functions, and concepts of
first hop redundancy protocols'.

A *describe* objective, so the work is keeping every item apply-level: each one
reads a show standby capture, a config pair, or computes a virtual MAC. None of
them ask what an FHRP "is".

Scope: HSRP is the worked protocol, with VRRP appearing only as a contrasting
virtual-MAC range. No GLBP weighting/load-balancing internals - beyond v1.1's
describe-level objective.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import standby_brief, standby_row, hsrp_v1_vmac, opts  # noqa: E402

SEP = "-" * 58

# --- exhibits -------------------------------------------------------------

EX_001 = standby_brief("R1", [
    standby_row("Gi0/0", 1, 110, True, "Active", "local", "10.1.1.3", "10.1.1.1"),
])

EX_002 = """! R2 - relevant configuration
!
interface GigabitEthernet0/0
 ip address 10.1.1.2 255.255.255.0
 standby version 1
 standby 10 ip 10.1.1.1
 standby 10 priority 110
 standby 10 preempt
!"""

EX_003 = """                      10.1.1.0/24
        +-----------------+------------------+
                |                   |
            +---+---+           +---+---+
            |  R1   |           |  R2   |
            +-------+           +-------+
          10.1.1.2            10.1.1.3
          priority 110        priority 100
          no preempt          no preempt

Virtual IP 10.1.1.1, HSRP group 1 on both routers.

R1 was active. Its uplink failed, R2 took over, and R1 has now
recovered and re-formed its HSRP relationship with R2."""

EX_004 = """                      10.1.1.0/24
        +-----------------+------------------+
                |                   |         \\
            +---+---+           +---+---+      \\   +-------+
            |  R1   |           |  R2   |       +--|  PC1  |
            +-------+           +-------+          +-------+
          10.1.1.2            10.1.1.3          gateway 10.1.1.1
          HSRP active         HSRP standby

PC1 is statically configured with default gateway 10.1.1.1.
R1 then loses power completely."""

EX_005 = """                      10.1.1.0/24
        +-----------------+------------------+
                |                   |
            +---+---+           +---+---+
            |  R1   |           |  R2   |
            +-------+           +-------+
          10.1.1.2            10.1.1.3
          standby 1 priority 90    standby 1 priority 120
          standby 1 preempt        standby 1 preempt

Both routers use virtual IP 10.1.1.1 in HSRP group 1 and are
brought up at the same time."""

EX_006 = "\n".join([
    "R6# show standby GigabitEthernet0/0 1",
    "GigabitEthernet0/0 - Group 1",
    "  State is Active",
    "    2 state changes, last state change 01:42:11",
    "  Virtual IP address is 10.1.1.1",
    "  Active virtual MAC address is 0000.0c07.ac01",
    "    Local virtual MAC address is 0000.0c07.ac01 (v1 default)",
    "  Hello time 3 sec, hold time 10 sec",
    "  Preemption enabled",
    "  Active router is local",
    "  Standby router is 10.1.1.3, priority 100 (expires in 8.352 sec)",
    "  Priority 110 (configured 110)",
    "    Track object 1 state Up decrement 20",
    "",
    "Both routers are configured with standby 1 preempt.",
])

EX_007 = standby_brief("R7", [
    standby_row("Gi0/0", 5, 100, True, "Standby", "10.1.5.4", "local", "10.1.5.1"),
    standby_row("Gi0/1", 6, 120, True, "Active", "local", "10.1.6.4", "10.1.6.1"),
])

EX_008 = "\n".join([
    standby_brief("R8", [
        standby_row("Gi0/0", 1, 110, True, "Active", "local", "10.1.1.3", "10.1.1.1"),
    ]),
    "",
    "R8# show standby GigabitEthernet0/0 1 | include virtual MAC",
    "  Active virtual MAC address is 0000.0c07.ac01",
    "",
    SEP,
    "R8 burned-in address on Gi0/0 is 00d0.5842.1c01",
    "R9 burned-in address on Gi0/0 is 00d0.5842.7f22",
])

EX_009 = """! R1 - relevant configuration
!
interface GigabitEthernet0/0
 ip address 10.1.1.2 255.255.255.0
 standby 1 ip 10.1.1.1
 standby 1 priority 110
!
""" + SEP + """
! R2 - relevant configuration
!
interface GigabitEthernet0/0
 ip address 10.1.1.3 255.255.255.0
 standby 2 ip 10.1.1.1
 standby 2 priority 100
!"""


ITEMS = [
{
  "id": "3.5-001", "objective": "3.5", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which address should hosts on the 10.1.1.0/24 segment carry as their default gateway?",
  "exhibit": {"kind": "cli_output", "content": EX_001},
  "options": opts("10.1.1.2", "10.1.1.3", "10.1.1.1", "10.1.1.110"),
  "correct": ["C"],
  "explanation": "Hosts point at the virtual address the group presents, listed in the Virtual IP column as 10.1.1.1, which survives a failover because the standby router adopts it. Option A is R1's own interface address, and pointing hosts there would strand them the moment R1 failed, which is the entire problem an FHRP exists to solve. Option B is the standby router's real address and has the same weakness. Option D reads the Pri column value of 110 as though it were part of an address.",
  "difficulty": 1,
  "skills": ["fhrp-purpose", "virtual-ip", "verify-hsrp", "default-gateway-redundancy"],
},
{
  "id": "3.5-002", "objective": "3.5", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which virtual MAC address does R2 use for this HSRP group?",
  "exhibit": {"kind": "config", "content": EX_002},
  "options": opts(
    hsrp_v1_vmac(16), hsrp_v1_vmac(10), "0000.5e00.010a", hsrp_v1_vmac(1)),
  "correct": ["B"],
  "explanation": "An HSRP version 1 virtual MAC is 0000.0C07.AC followed by the group number in hexadecimal, and group 10 in hex is 0a, giving 0000.0c07.ac0a. Option A writes the group as the literal digits 10, producing 0000.0c07.ac10, which is a genuine virtual MAC but belongs to group 16. Option C uses the 0000.5E00.01 range, which identifies VRRP rather than HSRP. Option D is the group 1 address, ignoring the configured group number entirely.",
  "difficulty": 2,
  "skills": ["hsrp-virtual-mac", "hexadecimal-conversion", "fhrp-concepts", "hsrp-groups"],
},
{
  "id": "3.5-003", "objective": "3.5", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which role does each router hold once R1 has recovered?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "R2 stays active and R1 becomes standby, despite R1's higher priority.",
    "R1 resumes the active role at once, because its priority is the higher of the two.",
    "Both routers hold the active role until the next hello exchange separates them.",
    "R1 stays out of the group until preemption is configured on R2."),
  "correct": ["A"],
  "explanation": "Priority decides an election, but without the preempt keyword a returning router cannot displace a sitting active router, so R2 keeps the role and R1 settles for standby. Option B applies the priority comparison to a group that has already elected, which is what preemption exists to enable and neither router has it. Option C describes a split-active state that the hello exchange prevents. Option D inverts the requirement: preemption would be needed on R1, the router trying to take over, not on R2.",
  "difficulty": 3,
  "skills": ["hsrp-preemption", "hsrp-priority", "fhrp-concepts", "failover-behaviour"],
},
{
  "id": "3.5-004", "objective": "3.5", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does PC1 experience after R1 loses power?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts(
    "PC1 must be reconfigured with R2's interface address as its gateway.",
    "PC1 has to renew its DHCP lease to be issued a new default gateway.",
    "PC1 loses reachability until its ARP cache expires and it re-resolves.",
    "PC1 keeps the same gateway, as R2 takes over the virtual IP and MAC."),
  "correct": ["D"],
  "explanation": "The standby router assumes both the virtual IP address and the virtual MAC address, so the entry already cached by PC1 stays valid and forwarding resumes without any change on the host. That property is the whole purpose of a first hop redundancy protocol. Option A would require touching every host, which is precisely what the protocol avoids. Option B assumes a DHCP dependency PC1 does not have, since its gateway is static. Option C is the most tempting error: it would be true if only the IP moved, but the virtual MAC moves with it.",
  "difficulty": 2,
  "skills": ["fhrp-purpose", "virtual-mac", "failover-behaviour", "arp-cache"],
},
{
  "id": "3.5-005", "objective": "3.5", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Once both routers have finished negotiating, which one forwards traffic sent to 10.1.1.1?",
  "exhibit": {"kind": "topology", "content": EX_005},
  "options": opts(
    "R1, because it holds the lower interface address on the segment.",
    "Both routers share the load, since each is configured to preempt.",
    "R2, because its configured priority is the higher of the two.",
    "Whichever router completed boot first and claimed the virtual address."),
  "correct": ["C"],
  "explanation": "HSRP elects the router with the numerically higher priority, so R2's 120 beats R1's 90 and R2 becomes active while R1 stands by. Option A applies a lowest-address tie-break, which HSRP consults only when priorities are equal, and even then it prefers the higher address. Option B assumes load sharing between the two, but a single HSRP group has exactly one forwarder. Option D describes what would happen without preemption, yet both routers carry the preempt keyword, so the higher priority asserts itself regardless of boot order.",
  "difficulty": 2,
  "skills": ["hsrp-priority", "hsrp-election", "hsrp-preemption", "active-router-selection"],
},
{
  "id": "3.5-006", "objective": "3.5", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Tracked object 1 transitions to Down. What follows?",
  "exhibit": {"kind": "cli_output", "content": EX_006},
  "options": opts(
    "R6's priority falls to 90, and the router at 10.1.1.3 preempts to become active.",
    "R6's priority falls to 90, but R6 stays active because it already owns the role.",
    "R6 leaves the group entirely and stops responding to the virtual IP address.",
    "R6's priority is unaffected, since tracking influences only the routing table."),
  "correct": ["A"],
  "explanation": "The tracking statement decrements R6's priority by 20 when the object goes down, taking 110 to 90, which is below the standby router's 100; because both routers are configured to preempt, the router at 10.1.1.3 then takes the active role. Option B ignores preemption, which is exactly what makes the decrement useful. Option C overstates the effect, as a lowered priority demotes the router rather than removing it. Option D denies the decrement the exhibit prints on the Track object line.",
  "difficulty": 3,
  "skills": ["hsrp-tracking", "hsrp-priority", "hsrp-preemption", "failover-behaviour"],
},
{
  "id": "3.5-007", "objective": "3.5", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. In group 5, which device currently holds the active role?",
  "exhibit": {"kind": "cli_output", "content": EX_007},
  "options": opts("R7 itself", "10.1.5.1", "10.1.6.4", "10.1.5.4"),
  "correct": ["D"],
  "explanation": "On the group 5 row the Active column names 10.1.5.4 while the Standby column reads local, so the peer is forwarding and R7 is standing by. Option A reverses the two columns, a slip made easy by R7 being active in the other group listed. Option B quotes the Virtual IP for group 5, which identifies the group rather than the device holding the role. Option C takes the address from the group 6 row, reading the correct column from the wrong line.",
  "difficulty": 1,
  "skills": ["verify-hsrp", "show-standby-brief", "active-standby-roles", "read-correct-row"],
},
{
  "id": "3.5-008", "objective": "3.5", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. A host on the segment resolves its default gateway. Which MAC address does it cache?",
  "exhibit": {"kind": "cli_output", "content": EX_008},
  "options": opts(
    "00d0.5842.1c01", "0000.0c07.ac01", "00d0.5842.7f22", "ffff.ffff.ffff"),
  "correct": ["B"],
  "explanation": "An ARP request for the virtual IP is answered with the group's virtual MAC, 0000.0c07.ac01, which is why the cached entry stays correct after a failover moves the role to the other router. Option A is R8's burned-in address; a host that cached it would lose reachability the moment R8 failed, defeating the redundancy. Option C is R9's burned-in address and has the same flaw. Option D is the broadcast address, which never appears as the resolved result of an ARP request.",
  "difficulty": 2,
  "skills": ["virtual-mac", "arp-resolution", "fhrp-purpose", "failover-behaviour"],
},
{
  "id": "3.5-009", "objective": "3.5", "domain": 3, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Both routers share the 10.1.1.0/24 segment and both are up. Which two outcomes result from the configurations shown? (Choose two.)",
  "exhibit": {"kind": "config", "content": EX_009},
  "options": opts(
    "The routers negotiate a single group and elect R1 as the active router.",
    "Each router becomes the active router for its own group.",
    "Both routers answer ARP for 10.1.1.1 with different virtual MACs.",
    "Neither router responds to traffic addressed to 10.1.1.1.",
    "R1 suppresses R2's group because it holds the higher configured priority."),
  "correct": ["B", "C"],
  "explanation": "HSRP routers only negotiate with peers in the same group number, so R1 in group 1 and R2 in group 2 never see each other; each declares itself active for its own group, and each answers for 10.1.1.1 with the virtual MAC derived from its own group number. Option A assumes the shared virtual IP is enough to pair them, when the group number is what binds peers. Option D contradicts both routers being active. Option E applies a priority comparison across groups that never communicate.",
  "difficulty": 2,
  "skills": ["hsrp-groups", "group-number-mismatch", "virtual-mac", "troubleshoot-fhrp"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "3" / "3.5.json"
dest.write_text(json.dumps({
    "objective": "3.5",
    "domain": 3,
    "blueprint_version": "v1.1",
    "scope_note": ("Describe-level objective kept apply-level: every item reads a "
                   "capture, a config pair, or computes a virtual MAC. HSRP is the "
                   "worked protocol; VRRP appears only as a contrasting MAC range."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
