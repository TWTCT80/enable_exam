#!/usr/bin/env python3
"""Generate bank/3/3.3.json - 'Configure and verify IPv4 and IPv6 static routing'.

A configure-and-verify objective, so it carries more items and a harder mix
than the interpret/determine objectives: config exhibits, deliberate one-line
omissions, and mask/administrative-distance boundary errors.

Covers all four sub-topics: default route, network route, host route,
floating static - across both IPv4 and IPv6.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import (top, kid, parent, route_table, ipv6_route_table, v6, opts)  # noqa: E402

NOGOLR = "Gateway of last resort is not set"

# --- exhibits -------------------------------------------------------------

EX_001 = """    +------------+                          +------------+
    |     R1     |      10.1.1.0/30         |     R2     |
    |            |--------------------------|            |
    |      Gi0/0 | .1                    .2 | Gi0/0      |
    +------------+                          +-----+------+
                                                  | Gi0/1
                                                  |
                                    +-------------+--------------+
                                    |  branch hosts occupy       |
                                    |  172.16.8.0 - 172.16.11.255|
                                    +----------------------------+"""

EX_002 = """! R2 - relevant configuration
!
interface GigabitEthernet0/0
 ipv6 address 2001:DB8:ACAD:12::1/64
 no shutdown
!
ipv6 route 2001:DB8:ACAD:3::/64 2001:DB8:ACAD:12::2
!"""

EX_003 = """    +------------+                          +--------------+
    |     R3     |    203.0.113.0/30        |   ISP-EDGE   |
    |            |--------------------------|              |
    |      Gi0/1 | .2                    .1 |              |
    +-----+------+                          +-------+------+
          | Gi0/0                                   |
          |                                         |
   192.168.1.0/24                            the public internet
     (branch LAN)

R3 has no dynamic routing protocol configured."""

EX_004 = route_table("R4", NOGOLR, [
    parent("10.0.0.0/8 is variably subnetted, 4 subnets, 2 masks"),
    kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
    kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
    kid("C", "10.2.2.0/30 is directly connected, GigabitEthernet0/1"),
    kid("L", "10.2.2.1/32 is directly connected, GigabitEthernet0/1"),
    top("O", "192.168.5.0/24 [110/74] via 10.1.1.2, 01:22:40, GigabitEthernet0/0"),
])

EX_005 = """    +------------+                          +------------+
    |     R5     |      10.1.1.0/30         |     R2     |
    |            |--------------------------|            |
    |      Gi0/0 | .1                    .2 | Gi0/0      |
    +------------+                          +-----+------+
                                                  |
                                          10.9.9.0/24 LAN
                                                  |
                                       +----------+----------+
                                       | mgmt station        |
                                       | 10.9.9.9            |
                                       +---------------------+

Only 10.9.9.9 may be reached through R2. Every other host in
10.9.9.0/24 must remain unreachable from R5."""

EX_006 = """! R6 - relevant configuration
!
ipv6 unicast-routing
!
interface GigabitEthernet0/0
 ipv6 address 2001:DB8:ACAD:12::1/64
 no shutdown
!

R6(config)# ipv6 route 2001:DB8:ACAD:3::/64 FE80::2
% Interface has to be specified for a link-local nexthop
R6(config)#"""

EX_007 = "\n".join([
    "R7# show running-config | include ^ip route",
    "ip route 10.30.0.0 255.255.0.0 10.1.1.2",
    "ip route 10.30.7.7 255.255.255.255 10.1.2.2",
    "ip route 192.168.9.0 255.255.255.0 10.99.99.2",
    "ip route 0.0.0.0 0.0.0.0 203.0.113.1",
    "R7#",
    route_table("R7", "Gateway of last resort is 203.0.113.1 to network 0.0.0.0", [
        top("S*", "0.0.0.0/0 [1/0] via 203.0.113.1"),
        parent("10.0.0.0/8 is variably subnetted, 6 subnets, 4 masks"),
        kid("S", "10.30.0.0/16 [1/0] via 10.1.1.2"),
        kid("S", "10.30.7.7/32 [1/0] via 10.1.2.2"),
    ]).replace("R7# show ip route", "R7# show ip route static"),
])

EX_008 = """    +------------+                              +--------------+
    |     R8     |   2001:DB8:FEED:1::/64       |   ISP-EDGE   |
    |            |------------------------------|              |
    |      Gi0/1 | ::2                      ::1 |              |
    +-----+------+                              +------+-------+
          | Gi0/0                                      |
          |                                            |
  2001:DB8:ACAD:1::/64                          the public internet
      (branch LAN)

ipv6 unicast-routing is already enabled on R8."""

EX_009 = """! R9 - relevant configuration
!
interface GigabitEthernet0/0
 description LAN segment shared with R-A, R-B and R-C
 ip address 10.1.1.1 255.255.255.0
 no shutdown
!
ip route 192.168.8.0 255.255.255.0 GigabitEthernet0/0
!

GigabitEthernet0/0 attaches to a switch carrying several other routers."""

EX_010 = """! R10 - relevant configuration
!
interface GigabitEthernet0/0
 ipv6 address 2001:DB8:ACAD:12::1/64
 no shutdown
!

R10 must reach 2001:DB8:ACAD:5::/64 through the neighbour whose global
address on the shared link is 2001:DB8:ACAD:12::2. Nothing else is
configured for IPv6 on R10."""

EX_011 = "\n".join([
    "R11# show running-config | include ^ipv6 route",
    "ipv6 route 2001:DB8:ACAD:3::/64 2001:DB8:ACAD:12::2",
    "ipv6 route 2001:DB8:ACAD:3::/64 2001:DB8:ACAD:24::2 5",
    "R11#",
    ipv6_route_table("R11", [
        v6("S", "2001:DB8:ACAD:3::/64", "1/0", "2001:DB8:ACAD:12::2"),
    ], total=6),
])

EX_012 = ipv6_route_table("R12", [
    v6("S", "2001:DB8:ACAD:7::/64", "1/0", "2001:DB8:ACAD:12::2"),
    v6("S", "2001:DB8:ACAD:9::/64", "1/0", "2001:DB8:ACAD:34::2"),
    v6("S", "::/0", "1/0", "2001:DB8:FEED:1::1"),
], total=8)


ITEMS = [
{
  "id": "3.3-001", "objective": "3.3", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. R1 must reach every host in the 172.16.8.0 through 172.16.11.255 range by way of R2, using one static route. Which command configures it?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "ip route 172.16.8.0 255.255.252.0 10.1.1.2",
    "ip route 172.16.8.0 255.255.254.0 10.1.1.2",
    "ip route 172.16.8.0 255.255.255.0 10.1.1.2",
    "ip route 172.16.8.0 0.0.3.255 10.1.1.2"),
  "correct": ["A"],
  "explanation": "The range spans four values in the third octet, 8 through 11, which is a /22, written 255.255.252.0. Option B is a /23 and covers only 172.16.8.0 through 172.16.9.255, leaving half the range unreachable, a boundary error of exactly one block. Option C is a /24 and covers only the first quarter. Option D supplies the wildcard mask 0.0.3.255, which belongs in an access list; the ip route command expects a subnet mask.",
  "difficulty": 2,
  "skills": ["static-route-configuration", "network-route", "subnet-mask", "block-size"],
},
{
  "id": "3.3-002", "objective": "3.3", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. GigabitEthernet0/0 is up and the neighbour replies to a ping of its own IPv6 address, yet R2 forwards no traffic toward 2001:DB8:ACAD:3::/64. Which omission accounts for this?",
  "exhibit": {"kind": "config", "content": EX_002},
  "options": opts(
    "The static route must also name GigabitEthernet0/0 as the exit interface.",
    "The global command ipv6 unicast-routing has not been entered.",
    "The interface is missing a manually configured link-local address.",
    "The static route prefix length must be /128 rather than /64."),
  "correct": ["B"],
  "explanation": "A Cisco router drops IPv6 transit traffic until ipv6 unicast-routing is enabled globally; the interface still holds an address and answers pings addressed to itself, which is exactly why the fault looks like a routing problem. Option A would be required only for a link-local next hop, and this next hop is global. Option C is wrong because IOS derives a link-local address automatically. Option D confuses a host route's length with the /64 the destination network genuinely uses.",
  "difficulty": 3,
  "skills": ["ipv6-static-route", "ipv6-unicast-routing", "missing-config-line", "troubleshoot-forwarding"],
},
{
  "id": "3.3-003", "objective": "3.3", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Every destination for which R3 holds no specific route must be sent to the ISP router at 203.0.113.1. Which command achieves that?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "ip default-gateway 203.0.113.1",
    "ip route 0.0.0.0 255.255.255.255 203.0.113.1",
    "ip route 0.0.0.0 0.0.0.0 203.0.113.1",
    "ip default-network 203.0.113.0"),
  "correct": ["C"],
  "explanation": "A default route is the prefix 0.0.0.0 with the mask 0.0.0.0, which matches every destination and loses every longest-match comparison, so it applies only when nothing more specific exists. Option A is a real command, but it applies to a device with IP routing disabled, such as a Layer 2 switch, and is ignored on a routing router. Option B pairs the all-zeros network with a host mask, matching only the address 0.0.0.0. Option D marks a classful network as a candidate default and does not create this route.",
  "difficulty": 2,
  "skills": ["static-route-configuration", "default-route", "gateway-of-last-resort"],
},
{
  "id": "3.3-004", "objective": "3.3", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. A backup path to 192.168.5.0/24 through 10.2.2.2 must carry traffic only while the OSPF-learned route is absent. Which command creates that backup?",
  "exhibit": {"kind": "cli_output", "content": EX_004},
  "options": opts(
    "ip route 192.168.5.0 255.255.255.0 10.2.2.2",
    "ip route 192.168.5.0 255.255.255.0 10.2.2.2 90",
    "ip route 192.168.5.0 255.255.255.0 10.2.2.2 255",
    "ip route 192.168.5.0 255.255.255.0 10.2.2.2 130"),
  "correct": ["D"],
  "explanation": "The exhibit shows the OSPF entry at distance 110, so the static must be given a distance above 110 to stay out of the table until OSPF withdraws the prefix; 130 does that. Option A accepts the default static distance of 1 and would displace OSPF immediately, defeating the intent. Option B sets 90, which also beats 110 and takes over at once. Option C sets 255, which marks a route permanently unusable, so it would never install even after OSPF disappeared.",
  "difficulty": 3,
  "skills": ["floating-static", "administrative-distance", "backup-path", "static-route-configuration"],
},
{
  "id": "3.3-005", "objective": "3.3", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which command gives R5 a route to the management station alone, without making the rest of its subnet reachable?",
  "exhibit": {"kind": "topology", "content": EX_005},
  "options": opts(
    "ip route 10.9.9.9 255.255.255.255 10.1.1.2",
    "ip route 10.9.9.9 255.255.255.0 10.1.1.2",
    "ip route 10.9.9.9 0.0.0.0 10.1.1.2",
    "ip route 10.9.9.0 255.255.255.255 10.1.1.2"),
  "correct": ["A"],
  "explanation": "A host route uses the all-ones mask 255.255.255.255, so it matches the single address 10.9.9.9 and nothing else. Option B applies a /24 mask, which IOS resolves to the whole 10.9.9.0/24 network and makes every host reachable, the opposite of the requirement. Option C supplies an all-zeros mask, producing a default-style entry rather than a host entry. Option D pairs the network address with a host mask, creating a route to 10.9.9.0 rather than to the station.",
  "difficulty": 2,
  "skills": ["static-route-configuration", "host-route", "subnet-mask"],
},
{
  "id": "3.3-006", "objective": "3.3", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. R6 rejects the static route with the message shown. Which explanation accounts for the rejection?",
  "exhibit": {"kind": "cli_output", "content": EX_006},
  "options": opts(
    "Link-local addresses may never serve as the next hop of an IPv6 static route.",
    "A link-local next hop is ambiguous, so the exit interface must be supplied.",
    "The command needs an administrative distance whenever the next hop is link-local.",
    "FE80::2 must first be bound with an ipv6 neighbor statement before it can be used."),
  "correct": ["B"],
  "explanation": "Every link repeats the same FE80::/10 space, so a link-local next hop identifies a router only in combination with the link it sits on; IOS therefore insists the exit interface be named, as in ipv6 route 2001:DB8:ACAD:3::/64 GigabitEthernet0/0 FE80::2. Option A overstates the rule, since link-local next hops are permitted and common. Option C invents a distance requirement that does not exist. Option D borrows static neighbour binding, which does not resolve the ambiguity the error describes.",
  "difficulty": 2,
  "skills": ["ipv6-static-route", "link-local-next-hop", "exit-interface", "ipv6-addressing"],
},
{
  "id": "3.3-007", "objective": "3.3", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Four static routes are configured on R7, but the verification output lists only three. Which explanation accounts for the missing entry?",
  "exhibit": {"kind": "cli_output", "content": EX_007},
  "options": opts(
    "The 192.168.9.0/24 route was refused because its subnet mask is invalid.",
    "The 192.168.9.0/24 route is present but suppressed, as this command hides /24 entries.",
    "R7 has no route to the next hop 10.99.99.2, so the static route cannot be installed.",
    "The 192.168.9.0/24 route was displaced by the default route already in the table."),
  "correct": ["C"],
  "explanation": "A static route configured with a next-hop address installs only once the router can resolve that address through an existing entry. No route covers 10.99.99.2 here, so the static stays in the configuration but never reaches the table. Option A is wrong because 255.255.255.0 is perfectly valid. Option B invents filtering behaviour; the command hides non-static routes, not particular mask lengths. Option D misapplies longest prefix match, since a /24 is more specific than the default and would never be displaced by it.",
  "difficulty": 2,
  "skills": ["verify-static-routes", "recursive-lookup", "next-hop-reachability", "show-ip-route-static"],
},
{
  "id": "3.3-008", "objective": "3.3", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which command configures R8 to send all IPv6 traffic with no more specific match to the ISP router?",
  "exhibit": {"kind": "topology", "content": EX_008},
  "options": opts(
    "ipv6 route 0.0.0.0/0 2001:DB8:FEED:1::1",
    "ipv6 route ::/128 2001:DB8:FEED:1::1",
    "ip route ::/0 2001:DB8:FEED:1::1",
    "ipv6 route ::/0 2001:DB8:FEED:1::1"),
  "correct": ["D"],
  "explanation": "The IPv6 default prefix is ::/0, and static IPv6 routes are configured with the ipv6 route command, so the combination in option D is correct. Option A writes the IPv4 default prefix into an IPv6 command, mixing the two address families. Option B uses ::/128, which is the unspecified address as a host route and matches nothing useful. Option C pairs the right prefix with the IPv4 command keyword, which IOS will not accept for an IPv6 destination.",
  "difficulty": 1,
  "skills": ["ipv6-static-route", "default-route", "static-route-configuration"],
},
{
  "id": "3.3-009", "objective": "3.3", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. R9's static route names an Ethernet exit interface instead of a next-hop address. Which consequence follows on this shared segment?",
  "exhibit": {"kind": "config", "content": EX_009},
  "options": opts(
    "R9 must ARP for each remote destination in turn and depends on proxy ARP to answer.",
    "The route is refused, because Ethernet interfaces cannot appear in an ip route command.",
    "R9 installs the route with an administrative distance of 0 rather than the usual 1.",
    "R9 shares the traffic evenly across every other router attached to the segment."),
  "correct": ["A"],
  "explanation": "Naming a broadcast interface tells R9 the destination is reachable out that port but not which neighbour to address, so it ARPs for the remote destination itself and forwards only if a neighbour answers on that host's behalf through proxy ARP. Option B is wrong because the command is accepted. Option C repeats the common belief that an exit-interface static becomes a connected route with distance 0; it still carries 1, though it is displayed as directly connected. Option D invents load sharing that no single static route performs.",
  "difficulty": 3,
  "skills": ["static-route-configuration", "exit-interface-vs-next-hop", "proxy-arp", "multi-access-link"],
},
{
  "id": "3.3-010", "objective": "3.3", "domain": 3, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Which two commands must be entered on R10 so that it forwards traffic to 2001:DB8:ACAD:5::/64 through its neighbour? (Choose two.)",
  "exhibit": {"kind": "config", "content": EX_010},
  "options": opts(
    "ip routing",
    "ipv6 unicast-routing",
    "ipv6 route 2001:DB8:ACAD:5::/64 2001:DB8:ACAD:12::2",
    "ipv6 route 2001:DB8:ACAD:5::/64 FE80::2",
    "ipv6 address autoconfig on GigabitEthernet0/0"),
  "correct": ["B", "C"],
  "explanation": "R10 needs IPv6 forwarding turned on globally and a static route toward the neighbour's global address, so B and C together satisfy the requirement. Option A enables IPv4 routing, which is on by default and has no effect on IPv6 traffic. Option D points at a link-local next hop without the exit interface, which IOS rejects as ambiguous. Option E would replace the manually configured address with an autoconfigured one, changing the interface rather than establishing the route.",
  "difficulty": 2,
  "skills": ["ipv6-static-route", "ipv6-unicast-routing", "static-route-configuration"],
},
{
  "id": "3.3-011", "objective": "3.3", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Two IPv6 static routes for the same prefix are configured on R11, yet the verification output lists only one. What does that indicate?",
  "exhibit": {"kind": "cli_output", "content": EX_011},
  "options": opts(
    "The second route was refused at configuration time as a duplicate prefix.",
    "The second route is active but this command displays only the first path.",
    "Both routes are in use and the displayed output has simply been truncated.",
    "The second route has a higher distance and waits as a backup."),
  "correct": ["D"],
  "explanation": "The second command ends in 5, which sets its administrative distance to 5 against the first route's default of 1, making it an IPv6 floating static that installs only if the primary is withdrawn. Option A is wrong because IOS accepts several statics for one prefix precisely so backups can exist. Option B invents a display limit; the command lists every installed static. Option C treats the single entry as truncation, but the table reports its entry count and the primary is genuinely the only installed path.",
  "difficulty": 2,
  "skills": ["ipv6-static-route", "floating-static", "administrative-distance", "verify-static-routes"],
},
{
  "id": "3.3-012", "objective": "3.3", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which next-hop address has R12 recorded for the 2001:DB8:ACAD:9::/64 prefix?",
  "exhibit": {"kind": "cli_output", "content": EX_012},
  "options": opts(
    "2001:DB8:ACAD:12::2",
    "2001:DB8:FEED:1::1",
    "2001:DB8:ACAD:34::2",
    "2001:DB8:ACAD:9::1"),
  "correct": ["C"],
  "explanation": "In show ipv6 route output the next hop appears on the indented via line beneath its prefix, and the one under 2001:DB8:ACAD:9::/64 reads 2001:DB8:ACAD:34::2. Option A takes the via line belonging to the 2001:DB8:ACAD:7::/64 entry above it, the classic error of reading the right field from the neighbouring block. Option B belongs to the ::/0 default entry below. Option D assumes the next hop is the first address inside the destination prefix, which the output never states.",
  "difficulty": 1,
  "skills": ["verify-static-routes", "ipv6-static-route", "next-hop", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "3" / "3.3.json"
dest.write_text(json.dumps({
    "objective": "3.3",
    "domain": 3,
    "blueprint_version": "v1.1",
    "scope_note": ("Configure and verify. Covers default / network / host / floating "
                   "static across IPv4 and IPv6. Harder mix than the interpret "
                   "objectives, per the spec's weighting of configure-and-verify."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
