#!/usr/bin/env python3
"""Generate bank/3/3.4.json - 'Configure and verify single area OSPFv2'.

Configure-and-verify, so a harder mix and config-heavy exhibits.

Covers all four sub-topics: neighbour adjacencies (003, 004, 012, 013),
point-to-point (008), broadcast DR/BDR selection (005, 006, 007) and
router ID (001, 002). Single area only - no ABR, no multi-area, no OSPFv3,
all of which sit outside the v1.1 objective.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import (ospf_neighbors, ospf_nbr, ospf_intf_brief, ospf_intf,  # noqa: E402
                    ospf_intf_detail, route_table, top, kid, parent, opts)

SEP = "-" * 58

# --- exhibits -------------------------------------------------------------

EX_001 = """! R1 - relevant configuration
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
!
interface Loopback1
 ip address 9.9.9.9 255.255.255.255
!
interface GigabitEthernet0/0
 ip address 10.1.1.1 255.255.255.252
 no shutdown
!
router ospf 1
 network 10.1.1.0 0.0.0.3 area 0
!"""

EX_002 = """R2# show ip ospf | include Routing Process
 Routing Process "ospf 1" with ID 10.1.2.1
R2#
R2# configure terminal
Enter configuration commands, one per line.  End with CNTL/Z.
R2(config)# router ospf 1
R2(config-router)# router-id 2.2.2.2
% OSPF: Reload or use "clear ip ospf process" command, for this to take effect
R2(config-router)# end
R2#
R2# show ip ospf | include Routing Process
 Routing Process "ospf 1" with ID 10.1.2.1"""

EX_003 = "\n".join([
    ospf_intf_detail("R1", "GigabitEthernet0/0", "10.1.1.1/30", 0, 1, "1.1.1.1",
                     "BROADCAST", 1, "DR", 1, dr_id="1.1.1.1", dr_addr="10.1.1.1",
                     hello=10, dead=40, wait=40),
    SEP,
    ospf_intf_detail("R2", "GigabitEthernet0/0", "10.1.1.2/30", 0, 1, "2.2.2.2",
                     "BROADCAST", 1, "DR", 1, dr_id="2.2.2.2", dr_addr="10.1.1.2",
                     hello=5, dead=20, wait=20),
])

EX_004 = """! R1 - relevant configuration
!
interface GigabitEthernet0/0
 ip address 10.1.1.1 255.255.255.252
 no shutdown
!
router ospf 1
 router-id 1.1.1.1
 network 10.1.1.0 0.0.0.3 area 0
!
""" + SEP + """
! R2 - relevant configuration
!
interface GigabitEthernet0/0
 ip address 10.1.1.5 255.255.255.252
 no shutdown
!
router ospf 2
 router-id 2.2.2.2
 network 10.1.1.4 0.0.0.3 area 0
!"""

EX_005 = """                    10.1.1.0/24  (broadcast segment)
      +---------+---------------+---------------+---------------+
                |               |               |               |
            +---+---+       +---+---+       +---+---+       +---+---+
            |  R1   |       |  R2   |       |  R3   |       |  R4   |
            +-------+       +-------+       +-------+       +-------+
        router-id 1.1.1.1   4.4.4.4         3.3.3.3         2.2.2.2
        ip ospf priority 1  priority 1      priority 5      priority 0

All four routers are powered on at the same moment and no adjacency
has formed yet."""

EX_006 = """                    10.1.1.0/24  (broadcast segment)
      +---------+---------------+---------------+---------------+
                |               |               |               |
            +---+---+       +---+---+       +---+---+       +---+---+
            |  R1   |       |  R2   |       |  R3   |       |  R5   |
            +-------+       +-------+       +-------+       +-------+
        router-id 1.1.1.1   4.4.4.4         3.3.3.3         5.5.5.5
        priority 1          priority 1      priority 5      priority 10

R3 was elected DR and R2 BDR some hours ago. R5 has just now been
cabled to the segment and brought up."""

EX_007 = ospf_intf_brief("R7", [
    ospf_intf("Gi0/0", 1, 0, "10.1.1.1/24", 1, "DR", "3/3"),
    ospf_intf("Gi0/1", 1, 0, "10.1.2.1/30", 1, "P2P", "1/1"),
])

EX_008 = ospf_neighbors("R8", [
    ospf_nbr("2.2.2.2", 1, "FULL/BDR", "00:00:36", "10.1.1.2", "GigabitEthernet0/0"),
    ospf_nbr("3.3.3.3", 1, "FULL/DR", "00:00:33", "10.1.1.3", "GigabitEthernet0/0"),
    ospf_nbr("4.4.4.4", 0, "FULL/  -", "00:00:38", "10.2.2.2", "Serial0/0/0"),
])

EX_009 = """! R9 - relevant configuration
!
interface GigabitEthernet0/0
 ip address 10.1.1.1 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 ip address 10.1.1.65 255.255.255.192
 no shutdown
!
router ospf 1
 router-id 9.9.9.9
!

OSPF must be enabled on GigabitEthernet0/0 in area 0, and on no other
interface."""

EX_010 = """! R10 - relevant configuration
!
interface GigabitEthernet0/0
 ip address 10.1.1.1 255.255.255.252
 no shutdown
!
router ospf 1
 router-id 10.10.10.10
 passive-interface GigabitEthernet0/0
 network 10.1.1.0 0.0.0.3 area 0
!

A neighbouring router is correctly configured for area 0 on the far end
of the 10.1.1.0/30 link."""

EX_011 = ospf_neighbors("R11", [
    ospf_nbr("5.5.5.5", 1, "FULL/DROTHER", "00:00:31", "10.1.1.5", "GigabitEthernet0/0"),
    ospf_nbr("6.6.6.6", 2, "FULL/DR", "00:00:34", "10.1.1.6", "GigabitEthernet0/0"),
    ospf_nbr("7.7.7.7", 1, "FULL/BDR", "00:00:39", "10.1.1.7", "GigabitEthernet0/0"),
])

EX_012 = """! R1 - relevant configuration
!
interface GigabitEthernet0/0
 ip address 10.1.1.1 255.255.255.252
 ip ospf hello-interval 10
 no shutdown
!
router ospf 1
 router-id 1.1.1.1
 network 10.1.1.0 0.0.0.3 area 0
!
""" + SEP + """
! R2 - relevant configuration
!
interface GigabitEthernet0/0
 ip address 10.1.1.2 255.255.255.252
 ip ospf hello-interval 5
 no shutdown
!
router ospf 1
 router-id 2.2.2.2
 network 10.1.1.0 0.0.0.3 area 1
!"""

EX_013 = "\n".join([
    ospf_neighbors("R13", [
        ospf_nbr("2.2.2.2", 1, "EXSTART/DR", "00:00:35", "10.1.1.2",
                 "GigabitEthernet0/0"),
    ]),
    "",
    "R13# show interfaces GigabitEthernet0/0 | include MTU",
    "  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,",
    "R13#",
    SEP,
    "R14# show interfaces GigabitEthernet0/0 | include MTU",
    "  MTU 9000 bytes, BW 1000000 Kbit/sec, DLY 10 usec,",
])


ITEMS = [
{
  "id": "3.4-001", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. No router ID has been set under the OSPF process. Which value does R1 adopt as its router ID when OSPF starts?",
  "exhibit": {"kind": "config", "content": EX_001},
  "options": opts("1.1.1.1", "10.1.1.1", "9.9.9.9", "0.0.0.0"),
  "correct": ["C"],
  "explanation": "With no router-id command, OSPF prefers the highest IPv4 address on any active loopback, and 9.9.9.9 outranks 1.1.1.1. Option A assumes Loopback0 wins because of its interface number, but the comparison is on address value, not interface order. Option B is the highest physical interface address, which is consulted only when no loopback exists. Option D would mean OSPF failed to pick an ID, in which case the process refuses to start rather than running with zeros.",
  "difficulty": 2,
  "skills": ["ospf-router-id", "router-id-selection-order", "loopback-precedence"],
},
{
  "id": "3.4-002", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. An engineer sets a router ID on R2, but the verification command still reports the old value. Which action makes the configured value take effect?",
  "exhibit": {"kind": "cli_output", "content": EX_002},
  "options": opts(
    "Clear the OSPF process with clear ip ospf process, or reload the router.",
    "Re-enter the router-id command from interface configuration mode instead.",
    "Remove and re-add the network statement so OSPF re-reads its configuration.",
    "Configure a loopback with address 2.2.2.2 so the ID is derived from it."),
  "correct": ["A"],
  "explanation": "A router ID is chosen when the OSPF process starts and is then held for the life of that process, which is why IOS prints the reload-or-clear notice visible in the exhibit. Option B invents an interface-level version of the command, which does not exist; router-id is a router-configuration command. Option C touches the network statement, which changes which interfaces run OSPF but never re-runs ID selection. Option D would matter only if no ID had been configured at all, and it still would not apply without restarting the process.",
  "difficulty": 3,
  "skills": ["ospf-router-id", "clear-ip-ospf-process", "verify-ospf", "config-takes-effect"],
},
{
  "id": "3.4-003", "objective": "3.4", "domain": 3, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Both interfaces are up on the same link, yet no adjacency forms. Which two differences in the output explain it? (Choose two.)",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts(
    "The hello intervals differ between the two interfaces.",
    "The two routers advertise different router IDs on the segment.",
    "The dead intervals differ between the two interfaces.",
    "Both interfaces report State DR, so neither will accept the other.",
    "The interface cost of 1 is too low for a broadcast network type."),
  "correct": ["A", "C"],
  "explanation": "OSPF requires both the hello and the dead interval to match before neighbours will form, and R1 uses 10 and 40 where R2 uses 5 and 20, so each discards the other's hellos. Option B inverts a requirement, since router IDs must differ rather than match. Option D mistakes a symptom for a cause: each claims DR precisely because neither has seen the other. Option E invents a minimum cost, and cost never governs whether an adjacency forms.",
  "difficulty": 2,
  "skills": ["ospf-adjacency", "hello-dead-interval-mismatch", "verify-ospf", "troubleshoot-adjacency"],
},
{
  "id": "3.4-004", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. The link between R1 and R2 is up and both routers run OSPF in area 0, yet no adjacency forms. What prevents it?",
  "exhibit": {"kind": "config", "content": EX_004},
  "options": opts(
    "The two routers have conflicting router IDs on the shared segment.",
    "The OSPF process IDs differ, and they must match for an adjacency to form.",
    "The hello intervals differ because only one router sets them explicitly.",
    "The two interfaces do not sit in the same IPv4 subnet."),
  "correct": ["D"],
  "explanation": "With a /30 mask, 10.1.1.1 belongs to 10.1.1.0/30 while 10.1.1.5 belongs to 10.1.1.4/30, so the addresses look adjacent but the interfaces are on different subnets and OSPF will not peer across them. Option B names the process IDs 1 and 2, which is the most tempting distractor here: the process ID is locally significant and need not match. Option A is wrong because 1.1.1.1 and 2.2.2.2 differ, which is what OSPF requires. Option C invents a timer difference neither configuration shows.",
  "difficulty": 3,
  "skills": ["ospf-adjacency", "same-subnet-requirement", "process-id-is-local", "troubleshoot-adjacency"],
},
{
  "id": "3.4-005", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which router is elected designated router on the shared segment?",
  "exhibit": {"kind": "topology", "content": EX_005},
  "options": opts("R1", "R2", "R3", "R4"),
  "correct": ["C"],
  "explanation": "DR election compares interface priority first and only falls back to the highest router ID on a tie. R3 carries priority 5, above every other router, so it becomes DR regardless of its router ID. Option B is the trap: R2 holds the highest router ID at 4.4.4.4 and would win only if all priorities were equal. Option A has neither the highest priority nor the highest ID. Option D is configured with priority 0, which bars it from becoming DR or BDR at all.",
  "difficulty": 2,
  "skills": ["dr-bdr-election", "ospf-priority", "priority-before-router-id", "broadcast-network"],
},
{
  "id": "3.4-006", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. R5 joins a segment where the DR and BDR were elected hours earlier. What happens to the designated router role?",
  "exhibit": {"kind": "topology", "content": EX_006},
  "options": opts(
    "R3 stays designated router, because OSPF elections are not preemptive.",
    "R5 becomes designated router at once, since its priority is the highest present.",
    "R5 becomes backup designated router and is promoted at the next hello interval.",
    "The election is rerun, making R5 designated router and R3 backup designated router."),
  "correct": ["A"],
  "explanation": "OSPF elections are non-preemptive: once a DR and BDR are established, a newly arrived router with a better priority does not displace them, and R5 becomes a DROTHER until the DR fails. Option B applies the priority comparison that governs only a fresh election. Option C invents a promotion path through the BDR role, but the sitting BDR keeps its place too. Option D assumes any topology change reruns the election, which would cause exactly the churn that non-preemption exists to prevent.",
  "difficulty": 3,
  "skills": ["dr-bdr-election", "non-preemptive-election", "ospf-priority", "broadcast-network"],
},
{
  "id": "3.4-007", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. R7 must be prevented from ever becoming the designated router or backup designated router on GigabitEthernet0/0, while continuing to run OSPF there. Which command accomplishes that?",
  "exhibit": {"kind": "cli_output", "content": EX_007},
  "options": opts(
    "R7(config-router)# priority 0",
    "R7(config-if)# ip ospf priority 0",
    "R7(config-if)# ip ospf priority 255",
    "R7(config-router)# passive-interface GigabitEthernet0/0"),
  "correct": ["B"],
  "explanation": "Priority is an interface setting, and the value 0 removes the router from the election while leaving OSPF running on the link. Option A has the right keyword and value but is entered in router configuration mode, where priority is not a valid command. Option C sets 255, the highest priority, which makes the router almost certain to become DR, the opposite of the requirement. Option D silences OSPF on the interface entirely, so no adjacency would form at all.",
  "difficulty": 2,
  "skills": ["ospf-priority", "dr-bdr-election", "config-mode", "interface-configuration"],
},
{
  "id": "3.4-008", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. The neighbour reached over Serial0/0/0 shows FULL with no role after the slash. What does that indicate about the link?",
  "exhibit": {"kind": "cli_output", "content": EX_008},
  "options": opts(
    "The neighbour has not finished exchanging its link-state database with R8.",
    "The OSPF priority on that neighbour's interface has been set to zero.",
    "The designated router for that segment has not been elected yet.",
    "The link uses a point-to-point network type, which elects no DR or BDR."),
  "correct": ["D"],
  "explanation": "OSPF elects a DR and BDR only on multi-access networks; on a point-to-point link there is no role to print, so the state shows FULL with a dash. Option A misreads FULL, which is the final state and confirms the databases are already synchronised. Option B is tempting because the Pri column reads 0, but that is what a point-to-point interface reports, not evidence of a configured priority. Option C would leave the neighbours in a transitional state rather than FULL.",
  "difficulty": 1,
  "skills": ["ospf-point-to-point", "verify-ospf", "neighbor-states", "dr-bdr-election"],
},
{
  "id": "3.4-009", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which network statement enables OSPF on GigabitEthernet0/0 in area 0 without also enabling it on GigabitEthernet0/1?",
  "exhibit": {"kind": "config", "content": EX_009},
  "options": opts(
    "network 10.1.1.0 255.255.255.252 area 0",
    "network 10.1.1.0 0.0.0.255 area 0",
    "network 10.1.1.0 0.0.0.3 area 0",
    "network 10.1.1.0 0.0.0.3 area 1"),
  "correct": ["C"],
  "explanation": "The network statement takes a wildcard mask, and a /30 corresponds to 0.0.0.3, which matches 10.1.1.0 through 10.1.1.3 and so covers GigabitEthernet0/0 alone. Option A supplies a subnet mask where the command expects a wildcard; IOS reads the value as a wildcard anyway, so the match bears no relation to the /30 link. Option B widens the match to 10.1.1.0 through 10.1.1.255, which also picks up 10.1.1.65 on GigabitEthernet0/1 and violates the requirement. Option D has the correct wildcard but places the interface in area 1, breaking the single-area design.",
  "difficulty": 2,
  "skills": ["ospf-network-statement", "wildcard-mask", "enable-ospf-on-interface", "single-area"],
},
{
  "id": "3.4-010", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What is the effect of R10's configuration on the 10.1.1.0/30 link?",
  "exhibit": {"kind": "config", "content": EX_010},
  "options": opts(
    "R10 advertises the 10.1.1.0/30 prefix into OSPF but forms no adjacency on that link.",
    "R10 stops advertising 10.1.1.0/30 and forms no adjacency on that link.",
    "R10 forms the adjacency normally but withholds the 10.1.1.0/30 prefix.",
    "R10 is unaffected, because passive-interface applies only to distance-vector protocols."),
  "correct": ["A"],
  "explanation": "A passive interface stops OSPF from sending or accepting hellos on that link, so no adjacency can form, while the network statement still causes the prefix to be advertised into the area. Option B misses that half: suppressing hellos does not withdraw the prefix. Option C reverses the behaviour entirely. Option D confuses OSPF with RIP or EIGRP, where the command exists as well; it is equally effective under OSPF, which is exactly why misapplying it silently breaks adjacencies.",
  "difficulty": 3,
  "skills": ["passive-interface", "ospf-adjacency", "route-advertisement", "troubleshoot-adjacency"],
},
{
  "id": "3.4-011", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which neighbour is acting as the designated router on GigabitEthernet0/0?",
  "exhibit": {"kind": "cli_output", "content": EX_011},
  "options": opts("5.5.5.5", "6.6.6.6", "7.7.7.7", "10.1.1.5"),
  "correct": ["B"],
  "explanation": "The State column carries the neighbour's role after the slash, and 6.6.6.6 is the row that reads FULL/DR. Option A is the DROTHER row, a neighbour that took no role in the election. Option C is the BDR, which stands by rather than serving as DR. Option D quotes an address from the Address column instead of the Neighbor ID column, which is a different field entirely and belongs to the 5.5.5.5 row.",
  "difficulty": 1,
  "skills": ["verify-ospf", "show-ip-ospf-neighbor", "dr-bdr-election", "read-correct-column"],
},
{
  "id": "3.4-012", "objective": "3.4", "domain": 3, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. R1 and R2 share an up/up link but never become neighbours. Which two configuration differences account for that? (Choose two.)",
  "exhibit": {"kind": "config", "content": EX_012},
  "options": opts(
    "The two routers have been given identical router IDs.",
    "The two interfaces have been addressed in different subnets.",
    "The interfaces have been placed in different OSPF areas.",
    "The configured hello intervals do not match.",
    "One of the two interfaces has been configured as passive."),
  "correct": ["C", "D"],
  "explanation": "Two routers must agree on the area and on their hello and dead timers before an adjacency will form; R1 uses area 0 with hello 10 while R2 uses area 1 with hello 5, so both checks fail. Option A is wrong because the IDs 1.1.1.1 and 2.2.2.2 are properly distinct. Option B is wrong because 10.1.1.1 and 10.1.1.2 both sit inside 10.1.1.0/30. Option E describes a command that appears in neither configuration.",
  "difficulty": 2,
  "skills": ["ospf-adjacency", "area-mismatch", "hello-dead-interval-mismatch", "troubleshoot-adjacency"],
},
{
  "id": "3.4-013", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. The adjacency between R13 and its neighbour never advances beyond the state shown. Which cause does the remaining output point to?",
  "exhibit": {"kind": "cli_output", "content": EX_013},
  "options": opts(
    "The interface MTU values on the two routers do not match.",
    "The dead interval expired before the databases could be exchanged.",
    "Both routers claim the designated router role for the segment.",
    "The neighbour's router ID duplicates one already known to R13."),
  "correct": ["A"],
  "explanation": "An adjacency that halts at EXSTART or EXCHANGE points at the database exchange itself, and the two interfaces report 1500 and 9000 bytes, so the routers cannot agree on a payload size and the exchange never completes. Option B is wrong because an expired dead interval drops the neighbour out of the table rather than freezing it in EXSTART. Option C describes a condition that resolves through election rather than stalling the exchange. Option D would prevent the neighbour from being listed at all rather than holding it mid-exchange.",
  "difficulty": 2,
  "skills": ["ospf-adjacency", "mtu-mismatch", "neighbor-states", "troubleshoot-adjacency"],
},
{
  "id": "3.4-014", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. The OSPF process on R14 carries no network statements, and the design calls for enabling OSPF directly on the interface instead. Which command does that?",
  "exhibit": {"kind": "config", "content": """! R14 - relevant configuration
!
interface GigabitEthernet0/0
 ip address 10.1.1.1 255.255.255.252
 no shutdown
!
router ospf 1
 router-id 14.14.14.14
!"""},
  "options": opts(
    "R14(config-router)# network GigabitEthernet0/0 area 0",
    "R14(config-if)# ip ospf 1 area 0",
    "R14(config-if)# ospf 1 area 0",
    "R14(config-router)# interface GigabitEthernet0/0 area 0"),
  "correct": ["B"],
  "explanation": "The interface-level form is ip ospf followed by the process ID and the area, entered under the interface, and it enables OSPF on that interface without any network statement. Option A keeps the network keyword, which expects an address and wildcard rather than an interface name. Option C drops the leading ip, so IOS does not recognise the command. Option D tries to nest an interface command inside router configuration mode, mixing the two modes that the interface-level form exists to separate.",
  "difficulty": 2,
  "skills": ["enable-ospf-on-interface", "ip-ospf-area-command", "config-mode", "single-area"],
},
{
  "id": "3.4-015", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What OSPF cost does R15 assign to Serial0/0/0?",
  "exhibit": {"kind": "cli_output", "content": """R15# show interfaces Serial0/0/0 | include BW
  MTU 1500 bytes, BW 1544 Kbit/sec, DLY 20000 usec,
R15#
R15# show ip ospf | include Reference bandwidth
 Reference bandwidth unit is 100 mbps"""},
  "options": opts("1", "100", "65", "64"),
  "correct": ["D"],
  "explanation": "Cost is the reference bandwidth divided by interface bandwidth, so 100,000,000 divided by 1,544,000 gives 64.77, and OSPF discards the remainder to leave 64. Option C rounds the quotient up to 65 instead of truncating, which is the single commonest arithmetic slip on this calculation. Option A is the cost a link at or above the reference bandwidth receives, since the formula floors at 1. Option B quotes the reference bandwidth itself rather than the result of the division.",
  "difficulty": 3,
  "skills": ["ospf-cost", "reference-bandwidth", "routing-protocol-metric", "cost-calculation"],
},
{
  "id": "3.4-016", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. From which neighbour has R16 most recently received OSPF routing information?",
  "exhibit": {"kind": "cli_output", "content": """R16# show ip protocols
*** IP Routing is NSF aware ***

Routing Protocol is "ospf 1"
  Outgoing update filter list for all interfaces is not set
  Incoming update filter list for all interfaces is not set
  Router ID 16.16.16.16
  Number of areas in this router is 1. 1 normal 0 stub 0 nssa
  Maximum path: 4
  Routing for Networks:
    10.1.1.0 0.0.0.3 area 0
    10.1.2.0 0.0.0.3 area 0
  Routing Information Sources:
    Gateway         Distance      Last Update
    2.2.2.2              110      00:00:19
    3.3.3.3              110      00:14:52
  Distance: (default is 110)"""},
  "options": opts("2.2.2.2", "3.3.3.3", "16.16.16.16", "10.1.1.0"),
  "correct": ["A"],
  "explanation": "The Last Update column counts elapsed time since the update arrived, so the smaller figure is the more recent one, and 2.2.2.2 at nineteen seconds beats 3.3.3.3 at almost fifteen minutes. Option B reads the larger elapsed time as the more recent, inverting the column's meaning. Option C quotes R16's own router ID, which identifies the local router rather than a source. Option D takes a value from the Routing for Networks list, which records what R16 advertises, not who it hears from.",
  "difficulty": 2,
  "skills": ["verify-ospf", "show-ip-protocols", "routing-information-sources", "read-correct-column"],
},
{
  "id": "3.4-017", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. The neighbour has been sitting in the state shown for several minutes. What does that state indicate?",
  "exhibit": {"kind": "cli_output", "content": ospf_neighbors("R17", [
      ospf_nbr("2.2.2.2", 1, "INIT/DROTHER", "00:00:31", "10.1.1.2", "GigabitEthernet0/0"),
  ])},
  "options": opts(
    "The neighbour finished exchanging databases but has not installed the routes.",
    "R17 has seen the neighbour's hello, but the neighbour has not yet seen R17's.",
    "The two routers disagree over which of them is the designated router.",
    "The dead interval has expired and the neighbour is being removed from the table."),
  "correct": ["B"],
  "explanation": "INIT means hellos are arriving in one direction only: R17 has heard the neighbour, but has not yet seen its own router ID listed in the neighbour's hello, so the relationship cannot advance to two-way. It usually points at something filtering traffic in one direction. Option A describes FULL, the state that follows a completed exchange. Option C describes an election dispute, which does not hold a neighbour at INIT. Option D is contradicted by the Dead Time of 31 seconds still counting down.",
  "difficulty": 2,
  "skills": ["ospf-adjacency", "neighbor-states", "one-way-hello", "troubleshoot-adjacency"],
},
{
  "id": "3.4-018", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which OSPF cost does R18 apply to traffic leaving Serial0/0/0?",
  "exhibit": {"kind": "cli_output", "content": ospf_intf_brief("R18", [
      ospf_intf("Gi0/0", 1, 0, "10.1.1.1/30", 1, "DR", "1/1"),
      ospf_intf("Se0/0/0", 1, 0, "10.1.2.1/30", 64, "P2P", "1/1"),
      ospf_intf("Lo0", 1, 0, "18.18.18.18/32", 1, "LOOP", "0/0"),
  ])},
  "options": opts("1", "110", "64", "0"),
  "correct": ["C"],
  "explanation": "The Cost column on the Serial0/0/0 row reads 64, which is the value OSPF adds when a path leaves by that interface. Option A takes the cost from the GigabitEthernet0/0 row, reading the right column on the wrong line. Option B quotes 110, which is OSPF's administrative distance and never appears in this output at all. Option D assumes an unlisted interface costs nothing, but every OSPF-enabled interface carries a cost of at least 1.",
  "difficulty": 1,
  "skills": ["verify-ospf", "ospf-cost", "show-ip-ospf-interface-brief", "read-correct-row"],
},
{
  "id": "3.4-019", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Both ends of this Ethernet link have been set to the point-to-point network type. What will show ip ospf neighbor report once the adjacency settles?",
  "exhibit": {"kind": "config", "content": """! R19 - relevant configuration
!
interface GigabitEthernet0/0
 ip address 10.1.1.1 255.255.255.252
 ip ospf network point-to-point
!
""" + SEP + """
! R20 - relevant configuration
!
interface GigabitEthernet0/0
 ip address 10.1.1.2 255.255.255.252
 ip ospf network point-to-point
!

Both routers place the interface in area 0 and use default timers."""},
  "options": opts(
    "A designated router and backup are still elected, but the hello timers halve.",
    "No adjacency forms, because Ethernet interfaces cannot use that network type.",
    "The adjacency reaches FULL, but no link-state advertisements cross the link.",
    "No designated router is elected, and the state shows FULL with no role."),
  "correct": ["D"],
  "explanation": "Changing the network type to point-to-point tells OSPF to treat the segment as having exactly two routers, so the election is skipped entirely and the neighbour prints as FULL with a dash where a role would otherwise appear. Option A keeps an election that the network type removes. Option B assumes the type is tied to the physical medium, but it is a software setting commonly applied to Ethernet links carrying only two routers. Option C would leave the routers with no shared topology, which FULL rules out.",
  "difficulty": 3,
  "skills": ["ospf-point-to-point", "ospf-network-type", "dr-bdr-election", "neighbor-states"],
},
{
  "id": "3.4-020", "objective": "3.4", "domain": 3, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. R20's loopback carries a /24 mask, yet its neighbour installs the prefix as a /32. What accounts for the difference?",
  "exhibit": {"kind": "cli_output", "content": """! R20 - relevant configuration
!
interface Loopback0
 ip address 10.9.9.9 255.255.255.0
!
router ospf 1
 router-id 20.20.20.20
 network 10.9.9.0 0.0.0.255 area 0
!
""" + SEP + "\n" + route_table("R21", "Gateway of last resort is not set", [
      parent("10.0.0.0/8 is variably subnetted, 3 subnets, 2 masks"),
      kid("C", "10.1.1.0/30 is directly connected, GigabitEthernet0/0"),
      kid("L", "10.1.1.2/32 is directly connected, GigabitEthernet0/0"),
      kid("O", "10.9.9.9/32 [110/2] via 10.1.1.1, 00:06:18, GigabitEthernet0/0"),
  ])},
  "options": opts(
    "The wildcard mask in the network statement forced the advertised length to /32.",
    "OSPF summarised the loopback prefix to its classful boundary before advertising.",
    "OSPF advertises a loopback as a host route unless the network type is changed.",
    "R21 applied its own mask, because the two routers sit in different areas."),
  "correct": ["C"],
  "explanation": "OSPF treats a loopback as a stub host and advertises it as a /32 no matter what mask the interface carries, which is why R21 installs 10.9.9.9/32; setting the interface to the point-to-point network type is what restores the configured length. Option A confuses the wildcard, which selects which interfaces participate, with the length that gets advertised. Option B describes summarisation to a classful boundary, which would produce a shorter prefix rather than a longer one. Option D invokes an area difference that the single-area configuration rules out.",
  "difficulty": 2,
  "skills": ["ospf-loopback-advertisement", "host-route", "ospf-network-type", "verify-ospf"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "3" / "3.4.json"
dest.write_text(json.dumps({
    "objective": "3.4",
    "domain": 3,
    "blueprint_version": "v1.1",
    "scope_note": ("Single area OSPFv2 only. No multi-area, no ABR/ASBR behaviour "
                   "and no OSPFv3 - all outside the v1.1 objective."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
