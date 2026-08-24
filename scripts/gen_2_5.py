#!/usr/bin/env python3
"""Generate bank/2/2.5.json - 'Interpret basic operations of Rapid PVST+'.

All four sub-topics:
  root port / root bridge      001, 002, 003, 005
  port states and roles        001, 004, 006
  PortFast                     007
  root, loop, BPDU guard/filter 008, 009, 010

The four protection features are deliberately spread across 007 to 010 and each
appears as a distractor in the others' options, because the mistake candidates
actually make is confusing which one fires in which circumstance rather than
forgetting that they exist.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import spanning_tree, stp_port, opts  # noqa: E402

# priority arithmetic the items depend on: default 32768 plus the VLAN as
# system ID extension; root primary lowers the configured value to 24576
assert 32768 + 10 == 32778
assert 24576 + 10 == 24586
assert 28672 + 10 == 28682

# --- exhibits -------------------------------------------------------------

EX_A = spanning_tree("SW1", 10, 32778, "0011.2233.4455", 32778, "00aa.bbcc.ddee",
    [stp_port("Gi0/1", "Root", "FWD", 4, "128.1"),
     stp_port("Gi0/2", "Altn", "BLK", 4, "128.2"),
     stp_port("Gi0/3", "Desg", "FWD", 19, "128.3")],
    root_cost=4, root_port="1 (GigabitEthernet0/1)")

EX_003 = """                    +-------------+
                    |  ROOT-SW    |
                    +--+-------+--+
                       |       |
              cost 4   |       |   cost 4
                       |       |
                 +-----+--+ +--+-----+
                 |  SW-A  | |  SW-B  |
                 +-----+--+ +--+-----+
                       |       |
                 Gi0/1 |       | Gi0/2
                    +--+-------+--+
                    |    SW-C     |
                    +-------------+

Both of SW-C's paths reach the root at a total cost of 8. SW-A's bridge
ID is 32778.0022.2222.2222 and SW-B's is 32778.0033.3333.3333. The two
links from SW-C use port priority 128 with port numbers 1 and 2."""

EX_005 = spanning_tree("SW3", 10, 32778, "0011.2233.4455", 32778, "00cc.4444.5555",
    [stp_port("Gi0/1", "Root", "FWD", 4, "128.1"),
     stp_port("Gi0/2", "Desg", "FWD", 4, "128.2")],
    root_cost=4, root_port="1 (GigabitEthernet0/1)") + """

An engineer now enters:

SW3(config)# spanning-tree vlan 10 root primary"""

EX_007 = """SW5(config)# interface GigabitEthernet0/5
SW5(config-if)# switchport mode access
SW5(config-if)# switchport access vlan 10
SW5(config-if)# spanning-tree portfast
%Warning: portfast should only be enabled on ports connected to a single
host. Connecting hubs, concentrators, switches, bridges, etc... to this
interface when portfast is enabled, can cause temporary bridging loops.
Use with CAUTION

SW5(config-if)#

Gi0/5 has in fact been patched into an access port on another switch,
not to an end device."""

EX_008 = """SW6#
*Aug 22 10:02:44.118: %SPANTREE-2-BLOCK_BPDUGUARD: Received BPDU on port
GigabitEthernet0/5 with BPDU Guard enabled. Disabling port.
*Aug 22 10:02:44.121: %PM-4-ERR_DISABLE: bpduguard error detected on
Gi0/5, putting Gi0/5 in err-disable state
SW6#

Gi0/5 is an access port configured with spanning-tree portfast and
spanning-tree bpduguard enable."""

EX_009 = """SW7#
*Aug 22 10:41:07.552: %SPANTREE-2-ROOTGUARD_BLOCK: Root guard blocking
port GigabitEthernet0/2 on VLAN0010.
SW7#

GigabitEthernet0/2 faces a switch administered by another team. Until a
moment ago it was a normal designated port carrying traffic."""

EX_010 = """                    +-------------+
                    |   ROOT-SW   |
                    +--+-------+--+
                       |       |
                       |       |
                 +-----+--+ +--+-----+
                 |  SW-D  |-|  SW-E  |
                 +--------+ +--------+
                    Gi0/3 blocking on SW-E

SW-E's Gi0/3 has been blocking correctly for months. A fault develops in
one direction of that fibre pair, so SW-E stops receiving BPDUs on Gi0/3
while its own transmissions still reach SW-D. Without protection Gi0/3
would age out its stored BPDU, decide no better path exists, and begin
forwarding, closing a loop."""


ITEMS = [
{
  "id": "2.5-001", "objective": "2.5", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which interface is SW1's root port for VLAN 10?",
  "exhibit": {"kind": "cli_output", "content": EX_A},
  "options": opts("Gi0/3", "Gi0/1", "Gi0/2", "None; SW1 is the root bridge"),
  "correct": ["B"],
  "explanation": "The Role column names Gi0/1 as Root, and the Root ID section confirms it by naming port 1 as the path toward the root at a cost of 4. Option A is a designated port, which forwards for its own segment rather than toward the root. Option C is an alternate port, holding a second path to the root in reserve while blocking. Option D is ruled out because the Root ID and Bridge ID carry different addresses, so the root is elsewhere.",
  "difficulty": 1,
  "skills": ["rapid-pvst", "root-port", "port-roles", "show-spanning-tree"],
},
{
  "id": "2.5-002", "objective": "2.5", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does this output establish about SW1's place in the VLAN 10 tree?",
  "exhibit": {"kind": "cli_output", "content": EX_A},
  "options": opts(
    "SW1 is the root, since its Bridge ID priority matches the Root ID priority.",
    "SW1 is the root, because one of its ports is designated and forwarding.",
    "SW1 is the secondary root and assumes the role if the current root fails.",
    "SW1 is not the root, because the Root ID names a different address."),
  "correct": ["D"],
  "explanation": "A bridge is the root only when the Root ID and Bridge ID describe the same bridge, and here the priorities match at 32778 while the addresses differ, so the root is another switch. Option A rests on the priorities alone, which is the trap: a tie in priority is normal and the address then decides. Option B misreads a designated port, which almost every switch has. Option C invents a secondary role that this output never records.",
  "difficulty": 2,
  "skills": ["rapid-pvst", "root-bridge", "bridge-id", "show-spanning-tree"],
},
{
  "id": "2.5-003", "objective": "2.5", "domain": 2, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Which two statements describe how SW-C settles on a root port? (Choose two.)",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "Both ports become root ports, and SW-C shares the load across them.",
    "Cost to the root is compared first, and here the two paths tie at 8.",
    "The tie falls to the neighbour advertising the lower bridge ID, so Gi0/1 wins.",
    "The tie falls to the neighbour advertising the higher bridge ID, so Gi0/2 wins.",
    "SW-C holds a fresh root election whenever two paths tie on cost."),
  "correct": ["B", "C"],
  "explanation": "Spanning tree compares cost to the root first, and with both paths at 8 that decides nothing, so the next comparison applies: the bridge ID of the neighbour sending the BPDU, where SW-A's 0022.2222.2222 beats SW-B's 0033.3333.3333 and Gi0/2 becomes an alternate port. Option A describes equal-cost load sharing, which routing protocols do and spanning tree deliberately does not. Option D applies the comparison backwards, since lower always wins. Option E invents a re-election that the tie-breakers exist to avoid.",
  "difficulty": 3,
  "skills": ["rapid-pvst", "root-port", "root-port-tiebreak", "bridge-id"],
},
{
  "id": "2.5-004", "objective": "2.5", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why does the bridge priority read 32778 when the configured value is 32768?",
  "exhibit": {"kind": "cli_output", "content": EX_A},
  "options": opts(
    "The switch adds one to the priority for each VLAN it currently carries.",
    "The extra ten counts the ports this switch holds in the forwarding state.",
    "The VLAN ID is carried in the priority field as the system ID extension.",
    "32778 is the value the root advertised, and SW1 has adopted it."),
  "correct": ["C"],
  "explanation": "Rapid PVST+ runs one instance per VLAN, so the bridge ID reserves part of the priority field for the VLAN number, and the output spells it out as priority 32768 sys-id-ext 10. That is why every VLAN on this switch shows a slightly different priority. Option A ties the value to how many VLANs exist, which would change as VLANs are added. Option B connects it to port states, which the priority does not track. Option D has the switch adopting the root's priority, when a bridge always advertises its own.",
  "difficulty": 2,
  "skills": ["rapid-pvst", "bridge-id", "sys-id-ext", "per-vlan-spanning-tree"],
},
{
  "id": "2.5-005", "objective": "2.5", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What is the effect of the command the engineer has entered?",
  "exhibit": {"kind": "cli_output", "content": EX_005},
  "options": opts(
    "SW3 and the current root alternate the role between them from now on.",
    "SW3's configured priority drops to 24576, so its bridge ID now wins.",
    "SW3's priority is set to zero, the only value that guarantees the role.",
    "Nothing changes for VLAN 10 until the present root bridge is reloaded."),
  "correct": ["B"],
  "explanation": "The root primary macro lowers the configured priority for that VLAN to 24576, well below the current root's 32768, and since priority is compared before the address SW3 wins the election immediately. Its bridge ID then displays as 24586 once the VLAN's system ID extension is added. Option A invents a shared role that spanning tree has no concept of. Option C describes what root primary would do only if a competing bridge were already at 24576. Option D expects a reload, but the election reruns as soon as the new BPDU is sent.",
  "difficulty": 3,
  "skills": ["rapid-pvst", "root-bridge", "root-primary", "bridge-priority"],
},
{
  "id": "2.5-006", "objective": "2.5", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What is GigabitEthernet0/2 doing for VLAN 10?",
  "exhibit": {"kind": "cli_output", "content": EX_A},
  "options": opts(
    "Forwarding as the designated port for the segment attached to it.",
    "Learning addresses while it counts down to a forwarding state.",
    "Sitting administratively disabled after a shutdown command.",
    "Blocking, while holding an alternate path toward the root bridge."),
  "correct": ["D"],
  "explanation": "The row reads Altn for role and BLK for state, so the port has a valid path to the root but is kept out of forwarding to avoid a loop, ready to take over if the root port fails. Option A describes the Desg role that Gi0/3 carries. Option B describes the LRN state, which appears while a port transitions rather than while it holds steady. Option C would show the port as disabled, and a shut port is not assigned an alternate role at all.",
  "difficulty": 1,
  "skills": ["rapid-pvst", "port-roles", "port-states", "alternate-port"],
},
{
  "id": "2.5-007", "objective": "2.5", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What risk does this configuration create, given what Gi0/5 is actually plugged into?",
  "exhibit": {"kind": "cli_output", "content": EX_007},
  "options": opts(
    "The port forwards at once, so a loop can form before any BPDU is acted on.",
    "The port is err-disabled the moment the neighbouring switch sends a BPDU.",
    "The port refuses to negotiate a trunk for as long as PortFast is applied.",
    "None, because PortFast is ignored on any port that reaches another switch."),
  "correct": ["A"],
  "explanation": "PortFast moves an access port straight into forwarding without waiting through the listening and learning stages, which is safe for a single host but not for a link to another switch: traffic flows before spanning tree has had a chance to block anything, which is exactly what the warning describes. Option B describes BPDU guard, which is not configured here. Option C invents an interaction with trunk negotiation. Option D claims the switch detects what is attached, when only BPDU guard turns that detection into protection.",
  "difficulty": 2,
  "skills": ["portfast", "rapid-pvst", "bridging-loop", "port-states"],
},
{
  "id": "2.5-008", "objective": "2.5", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What happened on Gi0/5?",
  "exhibit": {"kind": "cli_output", "content": EX_008},
  "options": opts(
    "A loop was detected across the port, and it was shut to break the loop.",
    "The neighbour advertised a superior root, so the port was held blocking.",
    "Something sending BPDUs was plugged into a PortFast access port.",
    "BPDUs stopped arriving on the port, so it was disabled as unsafe."),
  "correct": ["C"],
  "explanation": "BPDU guard exists to enforce the assumption PortFast makes, namely that only an end device sits on the port; the moment a BPDU arrives, that assumption is broken and the port is err-disabled rather than left to form a loop. Option A describes the outcome BPDU guard prevents rather than what it detects. Option B describes root guard, which blocks rather than err-disables. Option D describes loop guard, which reacts to BPDUs stopping rather than starting.",
  "difficulty": 3,
  "skills": ["bpdu-guard", "portfast", "err-disable", "rapid-pvst"],
},
{
  "id": "2.5-009", "objective": "2.5", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What did SW7 receive on Gi0/2 to trigger this message?",
  "exhibit": {"kind": "cli_output", "content": EX_009},
  "options": opts(
    "Nothing; the port stopped receiving BPDUs from its neighbour altogether.",
    "A BPDU advertising a bridge better than the current root bridge.",
    "A BPDU on a port that had been configured with PortFast.",
    "Two devices claiming the designated role for the same segment."),
  "correct": ["B"],
  "explanation": "Root guard protects the topology's shape: it allows a neighbour to participate normally until that neighbour claims a better root, at which point the port is moved to root-inconsistent and blocks, which is why a port facing another team's switch is the classic place to apply it. Option A describes loop guard's trigger. Option C describes BPDU guard, which err-disables rather than blocking. Option D describes a condition spanning tree resolves by election rather than by guarding.",
  "difficulty": 2,
  "skills": ["root-guard", "rapid-pvst", "root-bridge", "spanning-tree-protection"],
},
{
  "id": "2.5-010", "objective": "2.5", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which feature keeps Gi0/3 from forwarding in this situation?",
  "exhibit": {"kind": "topology", "content": EX_010},
  "options": opts(
    "BPDU guard, which err-disables a port as soon as a BPDU reaches it.",
    "PortFast, which leaves the port out of the spanning tree calculation.",
    "Root guard, which stops the neighbour from claiming the root role.",
    "Loop guard, which holds the port blocking once BPDUs stop arriving."),
  "correct": ["D"],
  "explanation": "Loop guard covers exactly this case: a non-designated port that has been receiving BPDUs and then stops is moved to loop-inconsistent rather than being allowed to age out its stored BPDU and start forwarding, which is what would close the loop on a unidirectional fault. Option A reacts to a BPDU arriving, and the problem here is one no longer arriving. Option B describes a feature for host ports that would make the situation worse. Option C guards against a neighbour claiming the root, which is not what is happening.",
  "difficulty": 2,
  "skills": ["loop-guard", "rapid-pvst", "unidirectional-link", "spanning-tree-protection"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "2" / "2.5.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "2.5",
    "domain": 2,
    "blueprint_version": "v1.1",
    "scope_note": ("Interpret-level. The four protection features each get an item and "
                   "each appear as distractors in the others, because confusing which "
                   "one fires when is the actual failure mode."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items, priority arithmetic asserted)")
