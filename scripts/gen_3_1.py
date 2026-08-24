#!/usr/bin/env python3
"""Generate bank/3/3.1.json - 'Interpret the components of routing table'.

SCOPE RULE for this objective: 3.1 is *reading* the table (code, prefix, mask,
next hop, AD, metric, gateway of last resort). If answering requires simulating
a packet's path, it belongs to 3.2 (forwarding decision). Keep the line.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import top, kid, parent, cont, route_table, opts  # noqa: E402


# ---- exhibits ------------------------------------------------------------

EX_001 = route_table("R1", "Gateway of last resort is not set",
    [
        parent("10.0.0.0/8 is variably subnetted, 4 subnets, 2 masks"),
        kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
        kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
        kid("C", "10.1.2.0/30 is directly connected, GigabitEthernet0/1"),
        kid("L", "10.1.2.1/32 is directly connected, GigabitEthernet0/1"),
        top("D", "192.168.10.0/24 [90/2172416] via 10.1.1.2, 00:04:11, GigabitEthernet0/0"),
        top("O", "192.168.20.0/24 [110/65] via 10.1.2.2, 00:09:53, GigabitEthernet0/1"),
    ])

EX_002 = route_table("R2", "Gateway of last resort is not set",
    [
        parent("10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks"),
        kid("C", "10.7.7.0/30 is directly connected, GigabitEthernet0/0"),
        kid("L", "10.7.7.2/32 is directly connected, GigabitEthernet0/0"),
        top("R", "192.168.20.0/24 [120/3] via 10.7.7.1, 00:00:12, GigabitEthernet0/0"),
        top("O", "192.168.40.0/24 [110/74] via 10.7.7.1, 02:41:55, GigabitEthernet0/0"),
    ])

_S_DEFAULT = top("S*", "0.0.0.0/0 [1/0] via 203.0.113.1")
EX_003 = route_table("BR1", "Gateway of last resort is 203.0.113.1 to network 0.0.0.0",
    [
        _S_DEFAULT,
        parent("192.168.1.0/24 is variably subnetted, 2 subnets, 2 masks"),
        kid("C", "192.168.1.0/24 is directly connected, GigabitEthernet0/1"),
        kid("L", "192.168.1.1/32 is directly connected, GigabitEthernet0/1"),
        parent("203.0.113.0/24 is variably subnetted, 2 subnets, 2 masks"),
        kid("C", "203.0.113.0/30 is directly connected, GigabitEthernet0/0"),
        kid("L", "203.0.113.2/32 is directly connected, GigabitEthernet0/0"),
    ])

EX_004 = route_table("R4", "Gateway of last resort is not set",
    [
        parent("10.0.0.0/8 is variably subnetted, 6 subnets, 3 masks"),
        kid("C", "10.0.0.0/30 is directly connected, GigabitEthernet0/0"),
        kid("L", "10.0.0.1/32 is directly connected, GigabitEthernet0/0"),
        kid("O", "10.10.0.0/24 [110/65] via 10.0.0.2, 00:18:02, GigabitEthernet0/0"),
        kid("O", "10.10.1.0/24 [110/65] via 10.0.0.2, 00:18:02, GigabitEthernet0/0"),
        kid("O", "10.20.0.0/30 [110/128] via 10.0.0.2, 00:17:58, GigabitEthernet0/0"),
        kid("O", "10.30.9.9/32 [110/129] via 10.0.0.2, 00:17:58, GigabitEthernet0/0"),
    ])

EX_005 = route_table("SW3", "Gateway of last resort is not set",
    [
        parent("10.0.0.0/8 is variably subnetted, 4 subnets, 2 masks"),
        kid("C", "10.20.30.0/24 is directly connected, GigabitEthernet0/1"),
        kid("L", "10.20.30.1/32 is directly connected, GigabitEthernet0/1"),
        kid("C", "10.40.50.0/24 is directly connected, GigabitEthernet0/2"),
        kid("L", "10.40.50.1/32 is directly connected, GigabitEthernet0/2"),
    ])

EX_006 = route_table("R6", "Gateway of last resort is not set",
    [
        parent("10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks"),
        kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
        kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
        top("O", "209.165.201.0/24 [110/2] via 10.1.1.2, 00:15:41, GigabitEthernet0/0"),
        top("O IA", "192.168.5.0/24 [110/66] via 10.1.1.2, 00:15:41, GigabitEthernet0/0"),
        top("O E2", "198.51.100.0/24 [110/20] via 10.1.1.2, 00:12:19, GigabitEthernet0/0"),
    ])

EX_007 = route_table("R7", "Gateway of last resort is not set",
    [
        parent("10.0.0.0/8 is variably subnetted, 3 subnets, 2 masks"),
        kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
        kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
        kid("O", "10.1.1.4/30 [110/128] via 10.1.1.2, 00:22:07, GigabitEthernet0/0"),
        top("S", "192.168.50.0/24 [1/0] via 10.1.1.6"),
    ])

_ECMP = top("O", "192.168.8.0/24 [110/74] via 10.4.4.2, 00:31:16, GigabitEthernet0/1")
EX_008 = route_table("R8", "Gateway of last resort is not set",
    [
        parent("10.0.0.0/8 is variably subnetted, 4 subnets, 2 masks"),
        kid("C", "10.4.4.0/30 is directly connected, GigabitEthernet0/1"),
        kid("L", "10.4.4.1/32 is directly connected, GigabitEthernet0/1"),
        kid("C", "10.5.5.0/30 is directly connected, GigabitEthernet0/2"),
        kid("L", "10.5.5.1/32 is directly connected, GigabitEthernet0/2"),
        _ECMP,
        cont(_ECMP, "[110/74] via 10.5.5.2, 00:31:16, GigabitEthernet0/2"),
    ])

EX_009 = route_table("R9", "Gateway of last resort is not set",
    [
        parent("10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks"),
        kid("C", "10.9.9.0/30 is directly connected, GigabitEthernet0/0"),
        kid("L", "10.9.9.1/32 is directly connected, GigabitEthernet0/0"),
        top("D", "192.168.70.0/24 [90/3072] via 10.9.9.2, 01:12:33, GigabitEthernet0/0"),
        top("D EX", "192.168.80.0/24 [170/2681856] via 10.9.9.2, 00:41:02, GigabitEthernet0/0"),
    ])

EX_010 = route_table("R10", "Gateway of last resort is not set",
    [
        parent("10.0.0.0/8 is variably subnetted, 4 subnets, 2 masks"),
        kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
        kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
        kid("C", "10.1.1.4/30 is directly connected, GigabitEthernet0/1"),
        kid("L", "10.1.1.5/32 is directly connected, GigabitEthernet0/1"),
        top("O", "192.168.20.0/24 [110/65] via 10.1.1.2, 00:33:20, GigabitEthernet0/0"),
        top("O", "192.168.30.0/24 [110/74] via 10.1.1.6, 00:33:18, GigabitEthernet0/1"),
        top("O", "192.168.40.0/24 [110/74] via 10.1.1.6, 00:33:18, GigabitEthernet0/1"),
    ])


ITEMS = [
{
  "id": "3.1-001", "objective": "3.1", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. According to the output, what administrative distance is associated with R1's route to 192.168.20.0/24?",
  "exhibit": {"kind": "cli_output", "content": EX_001},
  "options": opts("65", "2172416", "110", "90"),
  "correct": ["C"],
  "explanation": "In show ip route the bracketed pair is always [administrative distance/metric], so the OSPF entry [110/65] carries an administrative distance of 110. Option A takes 65, which is the OSPF cost, and reverses the two bracket fields. Option B quotes 2172416, the composite metric belonging to the EIGRP row for 192.168.10.0/24, so it reads the correct field from the wrong row. Option D quotes 90, the administrative distance shown on that same EIGRP row, another wrong-row read.",
  "difficulty": 1,
  "skills": ["routing-table-components", "administrative-distance", "read-ad-metric-bracket"],
},
{
  "id": "3.1-002", "objective": "3.1", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. A technician reports that R2 chose the OSPF entry for 192.168.40.0/24 because \"110 is the cost of that route.\" Which statement identifies the error in the technician's reading of the output?",
  "exhibit": {"kind": "cli_output", "content": EX_002},
  "options": opts(
    "110 is the administrative distance of the entry; the OSPF cost shown for it is 74.",
    "110 is the OSPF cost of the entry; the administrative distance shown for it is 74.",
    "110 is the hop count that OSPF inherited from the RIP entry above it in the table.",
    "110 is a composite metric, because OSPF entries are not assigned an administrative distance.",
  ),
  "correct": ["A"],
  "explanation": "The bracket prints [administrative distance/metric]. For 192.168.40.0/24 that is [110/74], so 110 is the administrative distance and 74 is the OSPF cost. Option B simply reverses the two fields, the single commonest misreading of this output. Option C imports the hop-count metric idea from the RIP entry [120/3] above and applies it to OSPF, confusing one protocol's metric type with another's. Option D asserts that OSPF has no administrative distance, when every installed entry is selected using one.",
  "difficulty": 2,
  "skills": ["routing-table-components", "administrative-distance", "metric", "protocol-metric-types"],
},
{
  "id": "3.1-003", "objective": "3.1", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does the asterisk on the S* 0.0.0.0/0 entry indicate about that route?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts(
    "It is administratively shut down and is being retained only as a backup entry.",
    "It was learned dynamically from a neighbour rather than configured on BR1.",
    "It has been redistributed into a dynamic routing protocol by this router already.",
    "It is the candidate default that sets the gateway of last resort.",
  ),
  "correct": ["D"],
  "explanation": "The legend defines * as candidate default, and the header line confirms the result: gateway of last resort is 203.0.113.1 to network 0.0.0.0. Option A confuses the asterisk with a floating or inactive static, but an unusable route is not installed in the table at all. Option B misreads the S code, which denotes a statically configured route, not a dynamically learned one. Option C invents redistribution, which the output never indicates and which the asterisk does not signify.",
  "difficulty": 2,
  "skills": ["routing-table-components", "gateway-of-last-resort", "route-codes", "default-route"],
},
{
  "id": "3.1-004", "objective": "3.1", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does the line \"10.0.0.0/8 is variably subnetted, 6 subnets, 3 masks\" state about the entries listed beneath it?",
  "exhibit": {"kind": "cli_output", "content": EX_004},
  "options": opts(
    "R4 holds six equal-sized subnets of 10.0.0.0/8, three of which are redundant duplicates.",
    "The six child entries are subnets of 10.0.0.0/8 and use three different masks.",
    "R4 is summarising the six child subnets of 10.0.0.0/8 into three advertised routes.",
    "Three of the six child subnets were learned from a classful protocol that discarded the mask.",
  ),
  "correct": ["B"],
  "explanation": "The banner is a header for the child entries: six subnets of 10.0.0.0/8 are present and they use three distinct masks, which the output bears out with /30, /24 and /32 prefixes. Option A misreads \"3 masks\" as duplicate routes and contradicts \"variably\", which means the subnets are deliberately unequal in size. Option C confuses this header with route summarisation, an advertisement behaviour the routing table does not describe. Option D invents classful behaviour; a classful protocol could not produce three different masks here at all.",
  "difficulty": 2,
  "skills": ["routing-table-components", "network-mask", "vlsm", "parent-child-routes"],
},
{
  "id": "3.1-005", "objective": "3.1", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Two entries in the output reference GigabitEthernet0/1. Which statement describes the entry coded L?",
  "exhibit": {"kind": "cli_output", "content": EX_005},
  "options": opts(
    "It is the /32 host route for the IPv4 address configured on that interface itself.",
    "It is a host route to a directly attached endpoint that SW3 discovered through ARP.",
    "It is a loopback route that IOS generated automatically for the interface.",
    "It is a link-local route used until the interface acquires a routable address.",
  ),
  "correct": ["A"],
  "explanation": "L marks a local route: the /32 that IOS installs for the router's own configured interface address, here 10.20.30.1/32 alongside the connected 10.20.30.0/24 network. Option B confuses the local route with an ARP-derived host entry for a neighbouring device, but the table shows the router's own address. Option C reads L as loopback, an extremely common misreading of the code letter. Option D borrows IPv6 link-local addressing and applies it to an IPv4 table where no such entry exists.",
  "difficulty": 2,
  "skills": ["routing-table-components", "route-codes", "local-vs-connected", "host-route"],
},
{
  "id": "3.1-006", "objective": "3.1", "domain": 3, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Which two prefixes did OSPF learn from inside its own routing domain? (Choose two.)",
  "exhibit": {"kind": "cli_output", "content": EX_006},
  "options": opts(
    "209.165.201.0/24",
    "192.168.5.0/24",
    "198.51.100.0/24",
    "10.1.1.0/30",
    "10.1.1.1/32"),
  "correct": ["A", "B"],
  "explanation": "Plain O marks an intra-area route and O IA marks one that crossed from another area, and both originated inside the OSPF domain, so 209.165.201.0/24 and 192.168.5.0/24 qualify. Option C carries O E2, meaning it was redistributed into OSPF from outside the domain, which is the distinction this item turns on. Option D is coded C, a directly connected subnet OSPF never learned. Option E is the L entry IOS creates for the router's own interface address.",
  "difficulty": 2,
  "skills": ["routing-table-components", "route-codes", "ospf-external-routes", "intra-vs-inter-area"],
},
{
  "id": "3.1-007", "objective": "3.1", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. The static route to 192.168.50.0/24 specifies a next-hop address but no exit interface. Which entry in the table must R7 resolve in order to determine an outgoing interface for that static route?",
  "exhibit": {"kind": "cli_output", "content": EX_007},
  "options": opts(
    "10.1.1.0/30, because a static next hop must sit on a directly connected subnet.",
    "10.1.1.4/30, because that entry's range covers the next hop 10.1.1.6.",
    "10.1.1.1/32, because the local route identifies the router's own outgoing interface.",
    "No entry, because the static route is already directly attached via GigabitEthernet0/0.",
  ),
  "correct": ["B"],
  "explanation": "A next-hop-only static route is recursive: R7 looks up the next hop 10.1.1.6, which falls inside 10.1.1.4/30 (hosts .5 and .6), and inherits that entry's outgoing interface. Option A asserts the next hop must be directly connected, a widespread misconception that recursion exists precisely to relax. Option C picks the L /32 for the router's own address, which describes R7 itself and can never resolve a remote next hop. Option D denies recursion entirely and misreads the static as a connected route.",
  "difficulty": 3,
  "skills": ["routing-table-components", "next-hop", "recursive-lookup", "static-route-resolution"],
},
{
  "id": "3.1-008", "objective": "3.1", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. R8 lists two paths for 192.168.8.0/24 with identical bracketed values. What does the presence of both paths in the table indicate?",
  "exhibit": {"kind": "cli_output", "content": EX_008},
  "options": opts(
    "R8 installed the first path only and holds the second in reserve until the primary fails.",
    "The repeated entry shows an OSPF adjacency flapping between the two neighbours.",
    "R8 will forward using the path whose next-hop address is numerically lower.",
    "R8 installed both paths and will share traffic for that prefix across them.",
  ),
  "correct": ["D"],
  "explanation": "Both paths show [110/74], so their cost is equal and OSPF installs both as equal-cost paths that share the load. Option A describes a floating route held out of the table, but a backup path with a worse distance would not be printed here at all. Option B reads duplication as instability, yet both paths show a matching 00:31:16 uptime, which indicates stability rather than flapping. Option C invents a numerically-lowest-next-hop tie-break, borrowing a bridge-ID style comparison that OSPF does not apply to installed routes.",
  "difficulty": 3,
  "skills": ["routing-table-components", "metric", "equal-cost-multipath", "read-ecmp-continuation"],
},
{
  "id": "3.1-009", "objective": "3.1", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Both prefixes were learned from the same neighbour, 10.9.9.2. Which conclusion does the administrative distance shown for 192.168.80.0/24 support?",
  "exhibit": {"kind": "cli_output", "content": EX_009},
  "options": opts(
    "The prefix entered EIGRP by redistribution from a source outside the EIGRP autonomous system.",
    "The prefix came from an EIGRP neighbour in a different autonomous system without redistribution.",
    "The prefix is an automatically generated EIGRP summary route advertised by that neighbour.",
    "The prefix was assigned a higher administrative distance because its metric is higher.",
  ),
  "correct": ["A"],
  "explanation": "The entry is coded D EX with an administrative distance of 170, which the legend and bracket both show, and that combination marks an EIGRP external route created by redistribution. Option B invents a cross-autonomous-system adjacency, but EIGRP neighbours must share an AS number to form one. Option C describes a summary route, which appears as a normal D entry rather than D EX. Option D claims distance follows metric, confusing the two bracket fields, which are set independently.",
  "difficulty": 2,
  "skills": ["routing-table-components", "administrative-distance", "route-codes", "eigrp-external-routes"],
},
{
  "id": "3.1-010", "objective": "3.1", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. According to the output, which next-hop address does R10 list for the 192.168.30.0/24 prefix?",
  "exhibit": {"kind": "cli_output", "content": EX_010},
  "options": opts("10.1.1.2", "192.168.30.1", "10.1.1.6", "10.1.1.1"),
  "correct": ["C"],
  "explanation": "The 192.168.30.0/24 row reads via 10.1.1.6, GigabitEthernet0/1, so 10.1.1.6 is the listed next hop. Option A is 10.1.1.2, the next hop printed on the 192.168.20.0/24 row directly above, the classic error of reading the correct field from the adjacent row. Option B assumes the next hop is the first address inside the destination prefix, which the table never states. Option D is 10.1.1.1, R10's own local interface address shown by the L entry, not a next hop.",
  "difficulty": 1,
  "skills": ["routing-table-components", "next-hop", "read-correct-row"],
},
{
  "id": "3.1-011", "objective": "3.1", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Setting aside the connected and local entries, which of R11's routed entries carries the longest prefix?",
  "exhibit": {"kind": "cli_output", "content": route_table("R11", "Gateway of last resort is not set", [
      parent("10.0.0.0/8 is variably subnetted, 6 subnets, 6 masks"),
      kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
      kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
      kid("S", "10.40.0.0/13 [1/0] via 10.1.1.2"),
      kid("O", "10.20.0.0/16 [110/65] via 10.1.1.2, 00:14:03, GigabitEthernet0/0"),
      kid("O", "10.20.30.0/24 [110/74] via 10.1.1.2, 00:14:03, GigabitEthernet0/0"),
      kid("D", "10.60.5.0/26 [90/3072] via 10.1.1.2, 00:09:41, GigabitEthernet0/0"),
  ])},
  "options": opts("10.20.0.0/16", "10.40.0.0/13", "10.20.30.0/24", "10.60.5.0/26"),
  "correct": ["D"],
  "explanation": "Prefix length counts the leading bits fixed by the mask, so the larger the number after the slash the more specific the entry; /26 is the longest among the routed entries. Option A at /16 leaves sixteen host bits free and is far broader. Option B at /13 is the broadest entry in the whole table, and picking it treats a smaller number as more specific, inverting the comparison. Option C at /24 is the closest rival and is the answer only if the /26 line is overlooked.",
  "difficulty": 1,
  "skills": ["routing-table-components", "network-mask", "prefix-length", "read-correct-row"],
},
{
  "id": "3.1-012", "objective": "3.1", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. The three learned entries show second bracket values of 3, 2172416 and 65. What accounts for the difference in magnitude between them?",
  "exhibit": {"kind": "cli_output", "content": route_table("R12", "Gateway of last resort is not set", [
      parent("10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks"),
      kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
      kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
      top("R", "192.168.20.0/24 [120/3] via 10.1.1.2, 00:00:14, GigabitEthernet0/0"),
      top("D", "192.168.40.0/24 [90/2172416] via 10.1.1.2, 00:31:02, GigabitEthernet0/0"),
      top("O", "192.168.60.0/24 [110/65] via 10.1.1.2, 00:44:19, GigabitEthernet0/0"),
  ])},
  "options": opts(
    "The three destinations sit at different hop counts, which the values count.",
    "Each protocol computes its metric differently, so the values share no scale.",
    "A larger value means the destination lies further from R12 in router hops.",
    "The values are administrative distances scaled by each protocol's weighting."),
  "correct": ["B"],
  "explanation": "The second bracket field is the metric of whichever protocol installed the entry, and the three protocols measure entirely different things: RIP counts hops, EIGRP composes bandwidth and delay, OSPF sums interface cost. Comparing 3 against 2172416 is therefore meaningless. Options A and C both read every value as a hop count, which holds only for the RIP entry. Option D confuses the two bracket fields, since the administrative distances are the first values, 120, 90 and 110.",
  "difficulty": 2,
  "skills": ["routing-table-components", "metric", "protocol-metric-types", "metric-not-comparable"],
},
{
  "id": "3.1-013", "objective": "3.1", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does the code on R13's 0.0.0.0/0 entry reveal about how that gateway of last resort was obtained?",
  "exhibit": {"kind": "cli_output", "content": route_table("R13", "Gateway of last resort is 10.1.1.2 to network 0.0.0.0", [
      top("O*E2", "0.0.0.0/0 [110/1] via 10.1.1.2, 00:22:15, GigabitEthernet0/0"),
      parent("10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks"),
      kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
      kid("L", "10.1.1.1/32 is directly connected, GigabitEthernet0/0"),
  ])},
  "options": opts(
    "It was configured statically on R13 and flagged as a candidate default.",
    "It was learned from a neighbour inside R13's own area as an intra-area route.",
    "It was learned from another OSPF area and then marked as a candidate default.",
    "It was injected into OSPF from outside the domain and flagged as a candidate default."),
  "correct": ["D"],
  "explanation": "The code combines three facts: O means OSPF learned it, E2 means it is an external type 2 route injected from outside the OSPF domain, and the asterisk marks it as the candidate default. Option A would require the code S, since a locally configured default appears as a static route. Option B ignores the E2, which is precisely what rules out an intra-area origin. Option C describes an inter-area route, which would carry the code IA rather than E2.",
  "difficulty": 3,
  "skills": ["routing-table-components", "route-codes", "gateway-of-last-resort", "ospf-external-routes"],
},
]

out = pathlib.Path(__file__).resolve().parent
dest = pathlib.Path("/home/kali/kod/ccnatester/bank/3/3.1.json")
doc = {
    "objective": "3.1",
    "domain": 3,
    "blueprint_version": "v1.1",
    "scope_note": ("3.1 is INTERPRETING the table (code, prefix, mask, next hop, AD, "
                   "metric, gateway of last resort). Items that require simulating a "
                   "packet's path belong to 3.2, not here."),
    "items": ITEMS,
}
dest.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
