#!/usr/bin/env python3
"""Generate bank/1/1.6.json - 'Configure and verify IPv4 addressing and subnetting'.

Configure-and-verify, and the objective where arithmetic carries the item, so
the mix is harder than average and every stem needs real calculation rather
than a remembered table.

All boundary maths in this file is checked by _selftest() at generation time -
a wrong network or broadcast address would teach the candidate the error.
"""
import ipaddress
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import ip_int_brief, ipint, opts  # noqa: E402


def _selftest():
    """Assert every boundary this file asserts to the candidate."""
    n = ipaddress.ip_network("192.168.20.100/27", strict=False)
    assert str(n.network_address) == "192.168.20.96"
    assert str(n.broadcast_address) == "192.168.20.127"

    a = ipaddress.ip_network("192.168.10.70/26", strict=False)
    b = ipaddress.ip_network("192.168.10.130/26", strict=False)
    assert a != b and str(a.network_address) == "192.168.10.64"
    assert str(b.network_address) == "192.168.10.128"
    assert ipaddress.ip_address("192.168.10.65") in a

    block = ipaddress.ip_network("172.16.8.0/22")
    plan = ["172.16.8.0/23", "172.16.10.0/24", "172.16.11.0/25", "172.16.11.128/26"]
    nets = [ipaddress.ip_network(p) for p in plan]
    assert all(x.subnet_of(block) for x in nets)
    for i, x in enumerate(nets):
        for y in nets[i + 1:]:
            assert not x.overlaps(y), (x, y)
    assert [x.num_addresses - 2 for x in nets] == [510, 254, 126, 62]

    c = ipaddress.ip_network("10.10.10.65/26", strict=False)
    assert str(c.broadcast_address) == "10.10.10.127"
    assert ipaddress.ip_address("10.10.10.126") in set(c.hosts())

    assert ipaddress.ip_network("192.168.5.0/26").num_addresses - 2 == 62   # fits 60
    assert ipaddress.ip_network("192.168.5.0/27").num_addresses - 2 == 30   # does not

    d = ipaddress.ip_network("172.18.45.200/21", strict=False)
    assert str(d) == "172.18.40.0/21"

    assert ipaddress.ip_network("10.1.5.0/24").subnet_of(ipaddress.ip_network("10.1.0.0/16"))

    host = ipaddress.ip_network("192.168.30.200/26", strict=False)
    assert str(host.network_address) == "192.168.30.192"
    assert ipaddress.ip_address("192.168.30.129") not in host


_selftest()

# --- exhibits -------------------------------------------------------------

EX_001 = """! R1 - relevant configuration
!
interface GigabitEthernet0/1
 description accounting LAN
 ip address 192.168.20.100 255.255.255.224
 no shutdown
!"""

EX_002 = """! Two hosts on one switched segment, no router present
!
PC1   IPv4 address . . . : 192.168.10.70
      Subnet mask  . . . : 255.255.255.192

PC2   IPv4 address . . . : 192.168.10.130
      Subnet mask  . . . : 255.255.255.192

PC1 can reach 192.168.10.65 but gets no reply from PC2."""

EX_003 = """Address block available for the branch:  172.16.8.0/22

    Segment            Hosts required
    ---------------    --------------
    User LAN                      500
    Voice LAN                     200
    Server LAN                    100
    Management LAN                 50

The four segments must be carved from the block with no overlap."""

EX_004 = """! R4 - relevant configuration
!
interface GigabitEthernet0/0
 ip address 10.10.10.65 255.255.255.192
 no shutdown
!"""

EX_005 = """                        192.168.5.0/24
        +---------+---------+---------+---------+
            |           |         |         |
        +---+---+   +---+---+ +---+---+ +---+---+
        | Sales |   |Support| |Finance| |  Ops  |
        +-------+   +-------+ +-------+ +-------+
         60 hosts    60 hosts  60 hosts  60 hosts

Every segment must hold 60 hosts, and the design must leave room for
as many equally sized subnets as the block allows."""

EX_006 = ip_int_brief("R6", [
    ipint("GigabitEthernet0/0", "10.1.1.1"),
    ipint("GigabitEthernet0/1", "172.18.45.200"),
    ipint("GigabitEthernet0/2", "unassigned", "YES", "unset",
          "administratively down", "down"),
]) + "\n\nGigabitEthernet0/1 is configured with the mask 255.255.248.0."

EX_007 = ip_int_brief("R7", [
    ipint("GigabitEthernet0/0", "10.30.1.1"),
    ipint("GigabitEthernet0/1", "10.30.2.1"),
    ipint("GigabitEthernet0/2", "unassigned", "YES", "unset",
          "administratively down", "down"),
    ipint("Loopback0", "7.7.7.7"),
])

EX_008 = """R8(config)# interface GigabitEthernet0/0
R8(config-if)# ip address 10.1.0.1 255.255.0.0
R8(config-if)# exit
R8(config)# interface GigabitEthernet0/1
R8(config-if)# ip address 10.1.5.1 255.255.255.0
% 10.1.5.0 overlaps with GigabitEthernet0/0
R8(config-if)#"""

EX_009 = """C:\\> ipconfig

Windows IP Configuration

Ethernet adapter Ethernet:

   Connection-specific DNS Suffix  . : example.internal
   IPv4 Address. . . . . . . . . . . : 192.168.30.200
   Subnet Mask . . . . . . . . . . . : 255.255.255.192
   Default Gateway . . . . . . . . . : 192.168.30.129

The host reaches other stations on its own segment but nothing beyond it."""


ITEMS = [
{
  "id": "1.6-001", "objective": "1.6", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What is the broadcast address of the subnet that GigabitEthernet0/1 belongs to?",
  "exhibit": {"kind": "config", "content": EX_001},
  "options": opts("192.168.20.127", "192.168.20.128", "192.168.20.255", "192.168.20.126"),
  "correct": ["A"],
  "explanation": "A 255.255.255.224 mask is a /27, so subnets step in blocks of 32 and .100 falls in the block running from .96 to .127; the last address, .127, is the broadcast. Option B is the network address of the next subnet, an error of exactly one address past the boundary. Option C is the broadcast for the whole /24 and ignores that the interface is subnetted at all. Option D is the last usable host address, which sits one below the broadcast.",
  "difficulty": 2,
  "skills": ["ipv4-subnetting", "broadcast-address", "block-size", "subnet-boundary"],
},
{
  "id": "1.6-002", "objective": "1.6", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why does PC1 get no reply from PC2 even though both are cabled to the same switch?",
  "exhibit": {"kind": "config", "content": EX_002},
  "options": opts(
    "192.168.10.130 is the broadcast address of the subnet PC1 occupies.",
    "PC2's address lies outside the private range and requires translation.",
    "The /26 mask places the two hosts in different subnets.",
    "Both hosts resolve to the same network address, so their addresses conflict."),
  "correct": ["C"],
  "explanation": "255.255.255.192 is a /26, giving blocks of 64: PC1's .70 sits in the .64 to .127 subnet while PC2's .130 sits in .128 to .191, so the two need a router between them despite sharing a switch. That PC1 reaches .65 confirms its own subnet works. Option A is wrong because the broadcast of PC1's subnet is .127. Option B misapplies private addressing, since all of 192.168.0.0/16 is private. Option D describes an address conflict, which would need the two hosts to share one address.",
  "difficulty": 3,
  "skills": ["ipv4-subnetting", "subnet-boundary", "same-subnet-requirement", "troubleshoot-addressing"],
},
{
  "id": "1.6-003", "objective": "1.6", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which set of subnets satisfies every host requirement without overlapping?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "172.16.8.0/24, 172.16.9.0/24, 172.16.10.0/25, 172.16.11.0/26",
    "172.16.8.0/22, 172.16.9.0/24, 172.16.10.0/25, 172.16.11.0/26",
    "172.16.8.0/23, 172.16.10.0/25, 172.16.11.0/24, 172.16.11.128/26",
    "172.16.8.0/23, 172.16.10.0/24, 172.16.11.0/25, 172.16.11.128/26"),
  "correct": ["D"],
  "explanation": "Each segment needs the smallest subnet that still fits it: 500 hosts need a /23 giving 510, 200 need a /24 giving 254, 100 need a /25 giving 126, and 50 need a /26 giving 62. Placed in descending order from 172.16.8.0 those four tile the /22 exactly. Option A starts with a /24, which offers only 254 addresses and cannot hold 500 hosts. Option B opens with the entire /22, leaving nothing for the other three. Option C assigns a /24 at 172.16.11.0 that swallows the /26 placed at 172.16.11.128.",
  "difficulty": 3,
  "skills": ["ipv4-subnetting", "vlsm", "host-requirements", "subnet-allocation"],
},
{
  "id": "1.6-004", "objective": "1.6", "domain": 1, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Which two addresses in this subnet cannot be given to a host? (Choose two.)",
  "exhibit": {"kind": "config", "content": EX_004},
  "options": opts("10.10.10.65", "10.10.10.64", "10.10.10.126", "10.10.10.127",
                  "10.10.10.100"),
  "correct": ["B", "D"],
  "explanation": "A 255.255.255.192 mask is a /26, so the interface sits in the block from 10.10.10.64 to 10.10.10.127; the first of those is the network address and the last is the broadcast, and neither may be assigned. Option A is the router's own address, already in use as an ordinary host address. Option C is the highest usable host address, one below the broadcast. Option E sits comfortably inside the usable range.",
  "difficulty": 2,
  "skills": ["ipv4-subnetting", "usable-host-range", "broadcast-address", "subnet-boundary"],
},
{
  "id": "1.6-005", "objective": "1.6", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which subnet mask meets the host requirement while producing the largest number of subnets?",
  "exhibit": {"kind": "topology", "content": EX_005},
  "options": opts("255.255.255.192", "255.255.255.224", "255.255.255.128",
                  "255.255.255.240"),
  "correct": ["A"],
  "explanation": "Sixty hosts need at least 62 usable addresses, which a /26 provides, and a /26 divides the /24 into four subnets, exactly matching the four segments. Option B is a /27 with only 30 usable addresses and cannot hold 60 hosts. Option D is a /28 with 14 usable and falls further short still. Option C is a /25, which does hold 126 hosts but splits the block into only two subnets, leaving two segments with nowhere to go.",
  "difficulty": 2,
  "skills": ["ipv4-subnetting", "host-requirements", "subnet-mask-selection", "maximise-subnets"],
},
{
  "id": "1.6-006", "objective": "1.6", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which subnet does the address on GigabitEthernet0/1 belong to?",
  "exhibit": {"kind": "cli_output", "content": EX_006},
  "options": opts("172.18.45.0/21", "172.18.32.0/21", "172.18.40.0/21", "172.18.44.0/21"),
  "correct": ["C"],
  "explanation": "A 255.255.248.0 mask is a /21, which steps in blocks of 8 in the third octet, giving boundaries at 32, 40 and 48; the address 172.18.45.200 falls in the block starting at 40 and running to 47.255. Option A treats the host's own third octet as the network number, which only holds when the mask lands on a /24. Option B picks the previous block and is the answer for anything from 172.18.32.0 to 172.18.39.255. Option D uses a block of 4, which would be a /22 rather than a /21.",
  "difficulty": 2,
  "skills": ["ipv4-subnetting", "network-address", "block-size", "subnet-boundary"],
},
{
  "id": "1.6-007", "objective": "1.6", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which interface has been disabled by an administrator rather than failing on its own?",
  "exhibit": {"kind": "cli_output", "content": EX_007},
  "options": opts("GigabitEthernet0/0", "Loopback0", "GigabitEthernet0/1",
                  "GigabitEthernet0/2"),
  "correct": ["D"],
  "explanation": "The Status column reads administratively down only for GigabitEthernet0/2, and that wording means a shutdown command is in the configuration rather than a cable or carrier fault, which would show simply as down. Options A and C both read up in Status and Protocol and are carrying traffic normally. Option B is a loopback, which stays up because it is a virtual interface and has no physical layer to lose.",
  "difficulty": 1,
  "skills": ["verify-ipv4-addressing", "show-ip-interface-brief", "interface-status", "read-correct-row"],
},
{
  "id": "1.6-008", "objective": "1.6", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why did R8 reject the address configured on GigabitEthernet0/1?",
  "exhibit": {"kind": "cli_output", "content": EX_008},
  "options": opts(
    "The mask 255.255.255.0 is invalid for an address in the 10.0.0.0 range.",
    "10.1.5.0/24 falls inside the 10.1.0.0/16 already assigned to another interface.",
    "A router may hold only one address from a given classful network at a time.",
    "The second address was entered before the first interface was brought up."),
  "correct": ["B"],
  "explanation": "GigabitEthernet0/0 owns 10.1.0.0 through 10.1.255.255, and 10.1.5.0/24 sits wholly inside that span, so accepting it would leave R8 with two interfaces claiming the same addresses; IOS blocks the overlap and names the conflicting interface. Option A treats the mask as illegal, but a /24 is fine in that space and the error text mentions overlap rather than the mask. Option C invents a classful limit that vanished with CIDR. Option D points at ordering, which the error message never mentions.",
  "difficulty": 3,
  "skills": ["ipv4-addressing", "overlapping-subnets", "configure-interface-address", "troubleshoot-addressing"],
},
{
  "id": "1.6-009", "objective": "1.6", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why can this host reach its own segment but nothing beyond it?",
  "exhibit": {"kind": "cli_output", "content": EX_009},
  "options": opts(
    "The subnet mask is too long to permit traffic to leave the local segment.",
    "The default gateway address is the broadcast address of the host's subnet.",
    "The host address is reserved and cannot originate routed traffic.",
    "The default gateway lies in a different subnet from the host."),
  "correct": ["D"],
  "explanation": "A 255.255.255.192 mask gives blocks of 64, so the host at .200 sits in the subnet from .192 to .255 while the configured gateway at .129 sits in the block from .128 to .191; a host can only send to a gateway inside its own subnet, so off-net traffic has nowhere to go. Option A invents a mask length that blocks routing. Option B is wrong because the broadcast for this host's subnet is .255. Option C treats .200 as reserved, but it is an ordinary usable address here.",
  "difficulty": 2,
  "skills": ["ipv4-subnetting", "default-gateway", "same-subnet-requirement", "verify-ip-parameters"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "1" / "1.6.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "1.6",
    "domain": 1,
    "blueprint_version": "v1.1",
    "scope_note": ("Configure and verify. Every boundary asserted to the candidate is "
                   "checked by _selftest() with the ipaddress module before the file "
                   "is written."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items, boundary self-test passed)")
