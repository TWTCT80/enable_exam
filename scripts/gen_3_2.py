#!/usr/bin/env python3
"""Generate bank/3/3.2.json - 'Determine how a router makes a forwarding decision by default'.

SCOPE RULE: 3.2 owns packet simulation - longest prefix match, route-source
selection by administrative distance, and metric comparison within a protocol.
Items that only *read* a field out of the table belong to 3.1.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import top, kid, parent, cont, route_table, route_entry, opts  # noqa: E402

NOGOLR = "Gateway of last resort is not set"

# --- exhibits -------------------------------------------------------------

EX_001 = route_table("R1", NOGOLR, [
    parent("10.0.0.0/8 is variably subnetted, 6 subnets, 4 masks"),
    kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
    kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
    kid("C", "10.1.2.0/30 is directly connected, GigabitEthernet0/1"),
    kid("L", "10.1.2.1/32 is directly connected, GigabitEthernet0/1"),
    kid("O", "10.20.0.0/16 [110/65] via 10.1.1.2, 00:10:04, GigabitEthernet0/0"),
    kid("O", "10.20.30.0/24 [110/74] via 10.1.2.2, 00:10:04, GigabitEthernet0/1"),
])

EX_002 = route_table("R2", NOGOLR, [
    parent("10.0.0.0/8 is variably subnetted, 6 subnets, 3 masks"),
    kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
    kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
    kid("C", "10.1.2.0/30 is directly connected, GigabitEthernet0/1"),
    kid("L", "10.1.2.1/32 is directly connected, GigabitEthernet0/1"),
    kid("O", "10.40.32.0/20 [110/65] via 10.1.1.2, 00:22:41, GigabitEthernet0/0"),
    kid("O", "10.40.48.0/20 [110/65] via 10.1.2.2, 00:22:41, GigabitEthernet0/1"),
])

EX_003 = route_table("R3", "Gateway of last resort is 203.0.113.1 to network 0.0.0.0", [
    top("S*", "0.0.0.0/0 [1/0] via 203.0.113.1"),
    parent("10.0.0.0/8 is variably subnetted, 6 subnets, 3 masks"),
    kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
    kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
    kid("C", "10.1.2.0/30 is directly connected, GigabitEthernet0/1"),
    kid("L", "10.1.2.1/32 is directly connected, GigabitEthernet0/1"),
    kid("O", "10.20.0.0/16 [110/65] via 10.1.1.2, 00:31:12, GigabitEthernet0/0"),
    kid("O", "10.30.0.0/16 [110/74] via 10.1.2.2, 00:31:12, GigabitEthernet0/1"),
    parent("203.0.113.0/24 is variably subnetted, 2 subnets, 2 masks"),
    kid("C", "203.0.113.0/30 is directly connected, GigabitEthernet0/2"),
    kid("L", "203.0.113.2/32 is directly connected, GigabitEthernet0/2"),
])

EX_004 = route_table("R4", NOGOLR, [
    parent("10.0.0.0/8 is variably subnetted, 4 subnets, 2 masks"),
    kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
    kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
    kid("C", "10.1.2.0/30 is directly connected, GigabitEthernet0/1"),
    kid("L", "10.1.2.1/32 is directly connected, GigabitEthernet0/1"),
    top("O", "192.168.20.0/24 [110/65] via 10.1.1.2, 00:08:19, GigabitEthernet0/0"),
    top("O", "192.168.40.0/24 [110/74] via 10.1.2.2, 00:08:19, GigabitEthernet0/1"),
])

EX_005 = route_table("R5", NOGOLR, [
    parent("10.0.0.0/8 is variably subnetted, 6 subnets, 4 masks"),
    kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
    kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
    kid("C", "10.1.2.0/30 is directly connected, GigabitEthernet0/1"),
    kid("L", "10.1.2.1/32 is directly connected, GigabitEthernet0/1"),
    kid("D", "10.50.0.0/16 [90/2172416] via 10.1.1.2, 00:19:37, GigabitEthernet0/0"),
    kid("O", "10.50.7.0/24 [110/65] via 10.1.2.2, 00:19:37, GigabitEthernet0/1"),
])

EX_006 = route_entry("R6", "192.168.100.0", "192.168.100.0/24", "ospf 1", 110, 65,
                     "type intra area", "10.1.1.2", "GigabitEthernet0/0",
                     "00:07:41", "3.3.3.3")

EX_007 = "\n".join([
    "R7# show running-config | include ^ip route",
    "ip route 192.168.60.0 255.255.255.0 10.9.9.2 130",
    "R7#",
    route_table("R7", NOGOLR, [
        parent("10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks"),
        kid("C", "10.9.9.0/30 is directly connected, GigabitEthernet0/0"),
        kid("L", "10.9.9.1/32 is directly connected, GigabitEthernet0/0"),
        top("O", "192.168.60.0/24 [110/74] via 10.9.9.2, 00:41:55, GigabitEthernet0/0"),
    ]),
])

EX_008 = """                          +--------+
                   +------|   R2   |------+
        cost 10    |      +--------+      |    cost 10
                   |                      |
              +--------+              +--------+   cost 1   +-------------------+
              |   R1   |              |   R4   |------------| 192.168.70.0/24   |
              +--------+              +--------+            +-------------------+
                   |                      |
        cost 5     |      +--------+      |    cost 5
                   +------|   R3   |------+
                          +--------+

All routers are in OSPF area 0. Costs shown are the outgoing interface
costs along each direction of travel from R1 toward 192.168.70.0/24."""

EX_009 = route_table("R9", "Gateway of last resort is 203.0.113.1 to network 0.0.0.0", [
    top("S*", "0.0.0.0/0 [1/0] via 203.0.113.1"),
    parent("192.168.1.0/24 is variably subnetted, 2 subnets, 2 masks"),
    kid("C", "192.168.1.0/24 is directly connected, GigabitEthernet0/1"),
    kid("L", "192.168.1.1/32 is directly connected, GigabitEthernet0/1"),
    top("S", "192.168.90.0/24 is directly connected, Null0"),
    parent("203.0.113.0/24 is variably subnetted, 2 subnets, 2 masks"),
    kid("C", "203.0.113.0/30 is directly connected, GigabitEthernet0/0"),
    kid("L", "203.0.113.2/32 is directly connected, GigabitEthernet0/0"),
])

EX_010 = route_table("R10", NOGOLR, [
    parent("10.0.0.0/8 is variably subnetted, 9 subnets, 5 masks"),
    kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
    kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
    kid("C", "10.1.2.0/30 is directly connected, GigabitEthernet0/1"),
    kid("L", "10.1.2.1/32 is directly connected, GigabitEthernet0/1"),
    kid("C", "10.1.3.0/30 is directly connected, GigabitEthernet0/2"),
    kid("L", "10.1.3.1/32 is directly connected, GigabitEthernet0/2"),
    kid("O", "10.80.0.0/16 [110/65] via 10.1.1.2, 00:05:52, GigabitEthernet0/0"),
    kid("O", "10.80.16.0/20 [110/74] via 10.1.2.2, 00:05:52, GigabitEthernet0/1"),
    kid("O", "10.80.20.0/24 [110/83] via 10.1.3.2, 00:05:52, GigabitEthernet0/2"),
])

_ECMP11 = top("O", "192.168.12.0/24 [110/74] via 10.4.4.2, 00:27:03, GigabitEthernet0/1")
EX_011 = route_table("R11", NOGOLR, [
    parent("10.0.0.0/8 is variably subnetted, 4 subnets, 2 masks"),
    kid("C", "10.4.4.0/30 is directly connected, GigabitEthernet0/1"),
    kid("L", "10.4.4.1/32 is directly connected, GigabitEthernet0/1"),
    kid("C", "10.5.5.0/30 is directly connected, GigabitEthernet0/2"),
    kid("L", "10.5.5.1/32 is directly connected, GigabitEthernet0/2"),
    _ECMP11,
    cont(_ECMP11, "[110/74] via 10.5.5.2, 00:27:03, GigabitEthernet0/2"),
])

EX_012 = route_table("R12", "Gateway of last resort is 203.0.113.1 to network 0.0.0.0", [
    top("S*", "0.0.0.0/0 [1/0] via 203.0.113.1"),
    parent("10.0.0.0/8 is variably subnetted, 6 subnets, 4 masks"),
    kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
    kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
    kid("C", "10.1.2.0/30 is directly connected, GigabitEthernet0/1"),
    kid("L", "10.1.2.1/32 is directly connected, GigabitEthernet0/1"),
    kid("O", "10.30.0.0/16 [110/65] via 10.1.1.2, 00:14:22, GigabitEthernet0/0"),
    kid("O", "10.30.8.0/22 [110/74] via 10.1.2.2, 00:14:22, GigabitEthernet0/1"),
    parent("203.0.113.0/24 is variably subnetted, 2 subnets, 2 masks"),
    kid("C", "203.0.113.0/30 is directly connected, GigabitEthernet0/2"),
    kid("L", "203.0.113.2/32 is directly connected, GigabitEthernet0/2"),
])

EX_013 = route_table("R13", NOGOLR, [
    parent("10.0.0.0/8 is variably subnetted, 6 subnets, 3 masks"),
    kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
    kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
    kid("C", "10.1.2.0/30 is directly connected, GigabitEthernet0/1"),
    kid("L", "10.1.2.1/32 is directly connected, GigabitEthernet0/1"),
    kid("O", "10.60.0.0/16 [110/65] via 10.1.1.2, 00:44:10, GigabitEthernet0/0"),
    kid("S", "10.60.5.7/32 [1/0] via 10.1.2.2"),
])

EX_014 = route_entry("R14", "10.70.20.5", "10.70.20.0/24", "ospf 1", 110, 83,
                     "type intra area", "10.1.1.2", "GigabitEthernet0/0",
                     "00:11:03", "4.4.4.4")

EX_015 = route_entry("R15", "172.20.40.0", "172.20.40.0/24", "eigrp 100", 90, 3072,
                     "type internal", "10.8.8.2", "GigabitEthernet0/1",
                     "00:03:12", "10.8.8.2",
                     tail=("Total delay is 20 microseconds, minimum bandwidth is 1000000 Kbit",
                           "Reliability 255/255, minimum MTU 1500 bytes",
                           "Loading 1/255, Hops 1"))


ITEMS = [
{
  "id": "3.2-001", "objective": "3.2", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. A workstation sends traffic to a file server at 10.20.30.55. Which interface does R1 use to reach that server?",
  "exhibit": {"kind": "cli_output", "content": EX_001},
  "options": opts("GigabitEthernet0/0", "GigabitEthernet0/1",
                  "The packet is dropped.", "Both interfaces, load-shared."),
  "correct": ["B"],
  "explanation": "A router forwards using the most specific matching entry. 10.20.30.55 is matched by both 10.20.0.0/16 and 10.20.30.0/24, and the /24 is longer, so R1 uses its next hop 10.1.2.2 out GigabitEthernet0/1. Option A follows the /16 entry and ignores longest prefix match entirely, the single commonest forwarding error. Option C assumes no match exists when two entries in fact match. Option D treats the two overlapping entries as equal-cost paths, but load sharing requires the same prefix, not merely overlapping ones.",
  "difficulty": 1,
  "skills": ["longest-prefix-match", "route-table-lookup", "forwarding-decision"],
},
{
  "id": "3.2-002", "objective": "3.2", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. An administrator logged in to R2 pings 10.40.48.10. Out which interface does the echo request leave?",
  "exhibit": {"kind": "cli_output", "content": EX_002},
  "options": opts("GigabitEthernet0/0",
                  "The packet is dropped; no gateway of last resort is set.",
                  "GigabitEthernet0/1",
                  "Both interfaces, because the two /20 entries overlap."),
  "correct": ["C"],
  "explanation": "A /20 covers sixteen values in the third octet. 10.40.32.0/20 therefore spans 10.40.32.0 to 10.40.47.255, and 10.40.48.0/20 spans 10.40.48.0 to 10.40.63.255. The destination 10.40.48.10 falls in the second block, so R2 forwards out GigabitEthernet0/1. Option A places .48 inside the first block, a boundary error of exactly one /20. Option B ignores that a matching entry exists. Option D assumes the two blocks overlap, but consecutive /20s are disjoint.",
  "difficulty": 2,
  "skills": ["longest-prefix-match", "subnet-boundary", "block-size", "forwarding-decision"],
},
{
  "id": "3.2-003", "objective": "3.2", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Traffic reaches R3 addressed to a public host at 198.18.7.9. How does R3 handle it?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts("GigabitEthernet0/0, following the 10.20.0.0/16 entry.",
                  "GigabitEthernet0/1, following the 10.30.0.0/16 entry.",
                  "The packet is discarded, because no entry in the table matches it.",
                  "GigabitEthernet0/2, following the default route."),
  "correct": ["D"],
  "explanation": "No specific entry covers 198.18.7.9, so the least specific match applies: the S* 0.0.0.0/0 default via 203.0.113.1, which the table resolves to GigabitEthernet0/2. Options A and B pick specific entries whose prefixes do not contain the destination at all, an error that comes from scanning for a familiar-looking row rather than testing containment. Option C forgets that 0.0.0.0/0 matches every destination, which is precisely why the header reports a gateway of last resort.",
  "difficulty": 2,
  "skills": ["longest-prefix-match", "default-route", "gateway-of-last-resort", "forwarding-decision"],
},
{
  "id": "3.2-004", "objective": "3.2", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. A frame carrying a datagram for 172.31.9.4 is de-encapsulated on R4. What becomes of that datagram?",
  "exhibit": {"kind": "cli_output", "content": EX_004},
  "options": opts("It discards the packet, because no entry in the table matches the destination.",
                  "It floods the packet out every interface except the one it arrived on.",
                  "It forwards the packet out GigabitEthernet0/0 as a best-effort attempt.",
                  "It forwards the packet toward the numerically closest network in the table."),
  "correct": ["A"],
  "explanation": "No entry covers 172.31.9.4 and the header confirms that no gateway of last resort is set, so R4 has nowhere to send the packet and drops it. Option B applies switch behaviour for unknown unicast frames to a routed lookup, which never floods. Option C invents a best-effort default that IOS does not implement. Option D assumes numeric proximity between addresses matters, but a lookup tests prefix containment, and 172.31.9.4 is not contained by any entry shown.",
  "difficulty": 2,
  "skills": ["route-table-lookup", "no-matching-route", "forwarding-decision"],
},
{
  "id": "3.2-005", "objective": "3.2", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. R5 must reach a database server at 10.50.7.99. Which entry does R5 select, and on what basis?",
  "exhibit": {"kind": "cli_output", "content": EX_005},
  "options": opts(
    "GigabitEthernet0/0, because the EIGRP entry's distance of 90 beats the OSPF entry's 110.",
    "GigabitEthernet0/0, because the EIGRP entry's metric is the larger of the two values.",
    "GigabitEthernet0/1, because /24 is a longer match than /16 for that destination.",
    "Neither; R5 drops the packet because two protocols advertise overlapping prefixes."),
  "correct": ["C"],
  "explanation": "Both entries are already installed for different prefixes, so administrative distance has nothing left to decide. The lookup picks the longest match: 10.50.7.99 falls inside 10.50.7.0/24, so R5 forwards out GigabitEthernet0/1. Option A applies administrative distance across two different prefixes, the central misconception this item targets; distance only breaks ties between sources offering the same prefix. Option B compares metrics from different protocols, which are never comparable. Option D invents a conflict where the two entries coexist normally.",
  "difficulty": 3,
  "skills": ["longest-prefix-match", "administrative-distance", "ad-vs-prefix-length", "forwarding-decision"],
},
{
  "id": "3.2-006", "objective": "3.2", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. R6 is also receiving a RIP advertisement for 192.168.100.0/24 with a hop count of 2. Which statement explains which route R6 installs in its routing table?",
  "exhibit": {"kind": "cli_output", "content": EX_006},
  "options": opts(
    "The OSPF route, because its administrative distance of 110 is lower than RIP's 120.",
    "The RIP route, because a hop count of 2 is numerically lower than an OSPF cost of 65.",
    "Both routes, because R6 load-shares whenever two protocols offer the same prefix.",
    "The RIP route, because its updates arrive more often than OSPF link-state refreshes."),
  "correct": ["A"],
  "explanation": "When two sources offer the same prefix, IOS compares administrative distance first and installs the more trustworthy source. The exhibit prints distance 110 for the OSPF entry, and RIP's 120 is higher, so the OSPF route stays. Option B compares a hop count with an OSPF cost, but metrics from different protocols have no common scale. Option C invents cross-protocol load sharing, which does not occur. Option D substitutes update frequency for distance, which plays no part in route selection.",
  "difficulty": 2,
  "skills": ["administrative-distance", "route-source-selection", "cross-protocol-comparison"],
},
{
  "id": "3.2-007", "objective": "3.2", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. A static route for 192.168.60.0/24 is configured, yet the routing table shows only the OSPF entry. Which statement describes R7's forwarding behaviour for that prefix?",
  "exhibit": {"kind": "cli_output", "content": EX_007},
  "options": opts(
    "OSPF forwards the traffic now; the static route installs only if the OSPF route is withdrawn.",
    "The static route forwards the traffic, because static routes always outrank dynamic ones.",
    "Traffic is shared between the OSPF next hop and the statically configured next hop.",
    "The static route is rejected as invalid, because 130 exceeds the maximum usable distance."),
  "correct": ["A"],
  "explanation": "The trailing 130 sets the static route's administrative distance above OSPF's 110, making it a floating static. The better-trusted OSPF entry is installed and the static waits in reserve, appearing only if OSPF withdraws the prefix. Option B assumes statics always win, which is true only at their default distance of 1. Option C would require equal distance and equal cost. Option D treats 130 as out of range, but the configurable distance runs to 255, and 130 was chosen deliberately.",
  "difficulty": 3,
  "skills": ["administrative-distance", "floating-static", "route-source-selection", "backup-path"],
},
{
  "id": "3.2-008", "objective": "3.2", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Both paths from R1 to 192.168.70.0/24 are inside OSPF area 0. Which path does R1 install, based on the costs shown?",
  "exhibit": {"kind": "topology", "content": EX_008},
  "options": opts("The path through R2, with a total cost of 21.",
                  "The path through R3, with a total cost of 11.",
                  "Both paths, because OSPF always load-shares across available paths.",
                  "The path through R2, because it has the lower administrative distance."),
  "correct": ["B"],
  "explanation": "OSPF sums the outgoing interface costs along each path. Through R2 the total is 10 plus 10 plus 1, which is 21; through R3 it is 5 plus 5 plus 1, which is 11. The lower total wins, so R1 installs the path through R3. Option A adds the costs correctly but then selects the higher total. Option C assumes load sharing without checking that the costs are unequal. Option D invokes administrative distance to separate two routes learned from the same protocol, where it is identical and decides nothing.",
  "difficulty": 2,
  "skills": ["routing-protocol-metric", "ospf-cost", "path-selection", "metric-accumulation"],
},
{
  "id": "3.2-009", "objective": "3.2", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Users report that nothing sent to 192.168.90.5 ever arrives, and no error is returned. What is R9 doing with that traffic?",
  "exhibit": {"kind": "cli_output", "content": EX_009},
  "options": opts(
    "It forwards the packet to 203.0.113.1 out GigabitEthernet0/0 using the default route.",
    "It forwards the packet out GigabitEthernet0/1 toward the 192.168.1.0/24 network.",
    "It queues the packet until a more specific route for 192.168.90.0/24 is learned.",
    "It discards the packet, because the longest match points to Null0."),
  "correct": ["D"],
  "explanation": "192.168.90.0/24 is a static route to the Null0 interface, and it is a longer match for 192.168.90.5 than the 0.0.0.0/0 default, so it wins the lookup. Traffic sent to Null0 is silently discarded. Option A applies the default route despite a more specific entry existing. Option B picks an unrelated connected network that does not contain the destination. Option C invents queueing behaviour; a router that resolves a lookup to Null0 drops the packet immediately rather than holding it.",
  "difficulty": 2,
  "skills": ["longest-prefix-match", "null0-discard-route", "forwarding-decision"],
},
{
  "id": "3.2-010", "objective": "3.2", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which interface carries the traffic that R10 sends toward the host 10.80.20.55?",
  "exhibit": {"kind": "cli_output", "content": EX_010},
  "options": opts("GigabitEthernet0/0", "GigabitEthernet0/2", "GigabitEthernet0/1",
                  "The packet is dropped."),
  "correct": ["B"],
  "explanation": "Three entries match 10.80.20.55: the /16, the /20 spanning 10.80.16.0 to 10.80.31.255, and the /24 spanning 10.80.20.0 to 10.80.20.255. The /24 is the longest and wins, so the packet leaves by GigabitEthernet0/2. Option A stops at the first matching row rather than continuing to look for a longer one. Option C selects the /20, the second-longest match, and is the answer for a destination such as 10.80.17.5. Option D ignores that three entries match.",
  "difficulty": 1,
  "skills": ["longest-prefix-match", "route-table-lookup", "forwarding-decision"],
},
{
  "id": "3.2-011", "objective": "3.2", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. A sustained transfer leaves R11 addressed to 192.168.12.30. Which interface or interfaces carry it?",
  "exhibit": {"kind": "cli_output", "content": EX_011},
  "options": opts(
    "Only GigabitEthernet0/1, because that path is listed first in the table.",
    "Only GigabitEthernet0/2, because it carries the higher interface number.",
    "Neither; the duplicated entry makes the prefix unusable until one path is removed.",
    "Both interfaces, because the two paths have equal cost."),
  "correct": ["D"],
  "explanation": "The prefix has two paths with identical [110/74] values, so OSPF installs both and R11 shares the traffic across them. Option A treats table order as a tie-break, but listing order carries no preference. Option B invents an interface-number tie-break that IOS does not apply to installed paths. Option C reads the second line as a duplicate fault, when the aligned continuation line is simply how IOS prints an additional equal-cost path for the same prefix.",
  "difficulty": 2,
  "skills": ["equal-cost-multipath", "routing-protocol-metric", "load-sharing", "forwarding-decision"],
},
{
  "id": "3.2-012", "objective": "3.2", "domain": 3, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. R12 receives one packet destined for 10.30.5.20 and another destined for 10.30.9.7. Which two statements describe how R12 forwards these packets? (Choose two.)",
  "exhibit": {"kind": "cli_output", "content": EX_012},
  "options": opts(
    "The packet to 10.30.5.20 is forwarded out GigabitEthernet0/0.",
    "The packet to 10.30.5.20 is forwarded out GigabitEthernet0/1.",
    "The packet to 10.30.9.7 is forwarded out GigabitEthernet0/1.",
    "The packet to 10.30.9.7 is forwarded out GigabitEthernet0/0.",
    "Both packets are sent to 203.0.113.1 by way of the default route."),
  "correct": ["A", "C"],
  "explanation": "A /22 covers four values in the third octet, so 10.30.8.0/22 spans 10.30.8.0 to 10.30.11.255. The destination 10.30.9.7 falls inside it and takes GigabitEthernet0/1, while 10.30.5.20 falls outside it and matches only the /16, taking GigabitEthernet0/0. Option B misreads the /22 as beginning below 10.30.8.0. Option D sends 10.30.9.7 to the less specific /16 and ignores longest prefix match. Option E applies the default route even though specific entries match both destinations.",
  "difficulty": 2,
  "skills": ["longest-prefix-match", "subnet-boundary", "block-size", "forwarding-decision"],
},
{
  "id": "3.2-013", "objective": "3.2", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. A lone management station is addressed 10.60.5.7. Which interface does R13 use when reaching it?",
  "exhibit": {"kind": "cli_output", "content": EX_013},
  "options": opts(
    "GigabitEthernet0/0, because the OSPF entry has the better administrative distance.",
    "GigabitEthernet0/1, because a /32 host route is the longest possible match.",
    "Either interface, because the two entries both match the destination address.",
    "Neither, because a /32 entry describes the router's own address and cannot be used."),
  "correct": ["B"],
  "explanation": "A /32 host route matches exactly one address, and it is the longest match available for 10.60.5.7, so it beats the covering 10.60.0.0/16 and the packet leaves by GigabitEthernet0/1. Option A compares administrative distance between two different prefixes, where prefix length decides instead. Option C ignores that overlapping matches are resolved by length rather than left as a choice. Option D confuses this static host route with the L entries IOS creates for a router's own interface addresses.",
  "difficulty": 2,
  "skills": ["longest-prefix-match", "host-route", "ad-vs-prefix-length", "forwarding-decision"],
},
{
  "id": "3.2-014", "objective": "3.2", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. R14's routing table also holds a 10.70.0.0/16 entry learned through OSPF. What does this output confirm about how R14 forwards a packet addressed to 10.70.20.5?",
  "exhibit": {"kind": "cli_output", "content": EX_014},
  "options": opts(
    "R14 will use the 10.70.0.0/16 entry, because it was learned earlier.",
    "R14 will drop the packet, because two entries overlap for that address.",
    "R14 will use the 10.70.20.0/24 entry, the longest match for that address.",
    "R14 will alternate between the /16 and /24 entries on successive packets."),
  "correct": ["C"],
  "explanation": "Querying show ip route with a host address makes IOS report the entry that address actually resolves to, and it names 10.70.20.0/24 rather than the covering /16, confirming the longest match. Option A treats age as a tie-break, but the table stores no such preference between different prefixes. Option B assumes overlap is an error, when overlapping entries are normal and resolved by length. Option D invents per-packet alternation, which happens only between installed equal-cost paths for one prefix.",
  "difficulty": 1,
  "skills": ["longest-prefix-match", "route-table-lookup", "verify-forwarding-decision"],
},
{
  "id": "3.2-015", "objective": "3.2", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. R15 receives advertisements for 172.20.40.0/24 from both EIGRP and OSPF, and the OSPF advertisement carries a cost of 3. Why did R15 install the entry shown rather than the OSPF one?",
  "exhibit": {"kind": "cli_output", "content": EX_015},
  "options": opts(
    "Because EIGRP updates arrive faster than OSPF LSAs, so EIGRP populated the table first.",
    "Because the EIGRP route is internal, and internal routes are always preferred over OSPF.",
    "Because metrics are compared only when two routes carry the same prefix length.",
    "Because administrative distance is compared first, and EIGRP's 90 beats OSPF's 110."),
  "correct": ["D"],
  "explanation": "The exhibit prints distance 90 for the EIGRP entry. When two protocols offer the same prefix, IOS compares administrative distance before it ever looks at a metric, so EIGRP wins and the OSPF cost of 3 is never weighed against 3072. Option A substitutes timing for distance. Option B invents a rule about internal routes that would apply within EIGRP, not between protocols. Option C states a condition that is already satisfied here, since both advertisements carry the same /24.",
  "difficulty": 3,
  "skills": ["administrative-distance", "route-source-selection", "cross-protocol-comparison", "metric-not-comparable"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "3" / "3.2.json"
dest.write_text(json.dumps({
    "objective": "3.2",
    "domain": 3,
    "blueprint_version": "v1.1",
    "scope_note": ("3.2 owns packet simulation: longest prefix match, route-source "
                   "selection by administrative distance, and metric comparison "
                   "within a protocol. Items that only read a field belong to 3.1."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
