#!/usr/bin/env python3
"""Generate bank/2/2.1.json - 'Configure and verify VLANs (normal range)
spanning multiple switches'.

Configure-and-verify, so a harder mix. All three sub-topics: access ports for
data and voice (004, 009, 010), the default VLAN (002), and inter-VLAN
connectivity (005, 006, 007).
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import vlan_brief, vlan_row, ip_int_brief, ipint, opts  # noqa: E402

SEP = "-" * 58

# --- exhibits -------------------------------------------------------------

EX_A = vlan_brief("SW1", [
    vlan_row(1, "default", "active", "Gi0/5, Gi0/6, Gi0/7, Gi0/8"),
    vlan_row(10, "SALES", "active", "Gi0/1, Gi0/2"),
    vlan_row(20, "VOICE", "active", "Gi0/1, Gi0/2"),
    vlan_row(30, "SERVERS", "active", "Gi0/3"),
])

EX_003 = """! SW1 - GigabitEthernet0/4 as it stands today
!
interface GigabitEthernet0/4
 description spare port, to be handed to the server team
 no shutdown
!

VLAN 30 already exists on SW1. Gi0/4 must carry untagged traffic for a
single server in VLAN 30 and must never negotiate a trunk."""

EX_004 = """! SW1 - relevant configuration
!
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 20
!

An IP phone is cabled to Gi0/1, and a PC is cabled into the switch port
on the back of that phone."""

EX_005 = """! R1 - router on a stick
!
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
!
interface GigabitEthernet0/0.20
 encapsulation dot1Q 30
 ip address 192.168.20.1 255.255.255.0
!
""" + SEP + """
SW1 carries VLANs 10 and 20 across the trunk to R1. Hosts in VLAN 10
reach 192.168.10.1 without trouble. Hosts in VLAN 20 cannot reach
192.168.20.1 at all."""

EX_006 = """                     +----------------+
                     |  SW-CORE (L3)  |
                     +---+--------+---+
                         |        |
                     VLAN 10   VLAN 20
                 192.168.10.0/24  192.168.20.0/24

SW-CORE is a Layer 3 switch. Both VLANs exist in its VLAN database and
both have active access ports. No router is attached, and hosts in the
two VLANs must be able to reach each other."""

EX_007 = "\n".join([
    ip_int_brief("SW2", [
        ipint("Vlan1", "unassigned", "YES", "unset", "administratively down", "down"),
        ipint("Vlan10", "192.168.10.1", "YES", "manual", "up", "up"),
        ipint("Vlan30", "192.168.30.1", "YES", "manual", "down", "down"),
    ]),
    "",
    SEP,
    vlan_brief("SW2", [
        vlan_row(1, "default", "active", "Gi0/6, Gi0/7, Gi0/8"),
        vlan_row(10, "SALES", "active", "Gi0/1, Gi0/2"),
        vlan_row(30, "SERVERS", "active"),
    ]),
    "",
    "ip routing is enabled, and neither SVI carries a shutdown command.",
])

EX_008 = "\n".join([
    vlan_brief("SW1", [
        vlan_row(1, "default", "active", "Gi0/5, Gi0/6"),
        vlan_row(40, "PROJECT", "active", "Gi0/1"),
    ], reserved=False),
    "",
    SEP,
    vlan_brief("SW2", [
        vlan_row(1, "default", "active", "Gi0/5, Gi0/6"),
        vlan_row(10, "SALES", "active", "Gi0/2"),
    ], reserved=False),
    "",
    "Gi0/1 on SW1 and Gi0/1 on SW2 are both configured with",
    "switchport access vlan 40. The trunk joining the two switches is up",
    "and allows every VLAN. A host on each of those two ports cannot",
    "reach the other.",
])

EX_009 = """SW1# show interfaces GigabitEthernet0/2 switchport
Name: Gi0/2
Switchport: Enabled
Administrative Mode: static access
Operational Mode: static access
Administrative Trunking Encapsulation: dot1q
Operational Trunking Encapsulation: native
Negotiation of Trunking: Off
Access Mode VLAN: 10 (SALES)
Trunking Native Mode VLAN: 1 (default)
Voice VLAN: 20 (VOICE)"""

EX_010 = """! SW3 - GigabitEthernet0/2 as it stands today
!
interface GigabitEthernet0/2
 switchport mode access
!

VLANs 10 and 20 both exist on SW3. A PC must reach the network untagged
through VLAN 10, while the IP phone it sits behind must tag its own
traffic for VLAN 20."""


ITEMS = [
{
  "id": "2.1-001", "objective": "2.1", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which VLAN has GigabitEthernet0/3 been assigned to?",
  "exhibit": {"kind": "cli_output", "content": EX_A},
  "options": opts("1", "30", "10", "20"),
  "correct": ["B"],
  "explanation": "The Ports column lists which interfaces belong to each VLAN, and Gi0/3 appears on the row for VLAN 30, named SERVERS. Option A is the default VLAN, whose row carries Gi0/5 through Gi0/8 instead. Option C is the SALES VLAN, listing Gi0/1 and Gi0/2. Option D is the VOICE VLAN, which lists the same two ports because they also carry voice traffic, and neither row mentions Gi0/3 at all.",
  "difficulty": 1,
  "skills": ["vlan-configuration", "show-vlan-brief", "access-ports", "read-correct-row"],
},
{
  "id": "2.1-002", "objective": "2.1", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which ports have never been moved out of the default VLAN?",
  "exhibit": {"kind": "cli_output", "content": EX_A},
  "options": opts("Gi0/1 and Gi0/2", "Gi0/3 only", "None; every port has been assigned",
                  "Gi0/5, Gi0/6, Gi0/7 and Gi0/8"),
  "correct": ["D"],
  "explanation": "VLAN 1 is the default, and any port not explicitly assigned elsewhere stays in it, so the four ports listed on that row are the untouched ones. Option A names ports that appear on the SALES and VOICE rows, so both have been configured. Option B names the single port belonging to SERVERS. Option C contradicts the output, which lists four ports still sitting on the VLAN 1 row.",
  "difficulty": 2,
  "skills": ["vlan-configuration", "default-vlan", "show-vlan-brief", "access-ports"],
},
{
  "id": "2.1-003", "objective": "2.1", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which pair of interface commands meets the requirement for Gi0/4?",
  "exhibit": {"kind": "config", "content": EX_003},
  "options": opts(
    "switchport mode access, then switchport access vlan 30",
    "switchport access vlan 30, then switchport mode trunk",
    "switchport mode access, then switchport voice vlan 30",
    "switchport mode dynamic auto, then switchport access vlan 30"),
  "correct": ["A"],
  "explanation": "Setting the mode to access fixes the port so it never negotiates a trunk, and the access vlan command places its untagged traffic in VLAN 30, which is exactly what a single server needs. Option B assigns the VLAN and then makes the port a trunk, which would tag traffic the server cannot read. Option C configures a voice VLAN, meant for the tagged traffic of an IP phone rather than a server. Option D leaves the port willing to negotiate, which the requirement forbids.",
  "difficulty": 2,
  "skills": ["vlan-configuration", "access-ports", "switchport-mode", "configure-access-vlan"],
},
{
  "id": "2.1-004", "objective": "2.1", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. How does SW1 handle the traffic arriving from the two devices on Gi0/1?",
  "exhibit": {"kind": "config", "content": EX_004},
  "options": opts(
    "Both devices send tagged frames, the PC in VLAN 10 and the phone in VLAN 20.",
    "Both devices send untagged frames, and the switch places all of it in VLAN 10.",
    "The PC sends untagged frames into VLAN 10; the phone tags its own for VLAN 20.",
    "The port turns into a trunk and carries VLANs 10 and 20 tagged in both directions."),
  "correct": ["C"],
  "explanation": "A port with both an access VLAN and a voice VLAN carries two kinds of traffic at once: whatever arrives untagged lands in the access VLAN, while the phone is told through CDP to tag its own traffic for the voice VLAN. Option A would require the PC to tag, which an ordinary host does not do. Option B ignores the voice VLAN entirely. Option D describes a trunk, and the configuration reads switchport mode access, which the voice VLAN does not change.",
  "difficulty": 3,
  "skills": ["vlan-configuration", "voice-vlan", "access-ports", "tagged-vs-untagged"],
},
{
  "id": "2.1-005", "objective": "2.1", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why can VLAN 20 hosts not reach their gateway while VLAN 10 hosts can?",
  "exhibit": {"kind": "config", "content": EX_005},
  "options": opts(
    "A subinterface number must match the VLAN ID before encapsulation takes effect.",
    "The trunk to R1 needs switchport nonegotiate before subinterfaces will pass traffic.",
    "Each subinterface needs its own no shutdown command before it will forward.",
    "The second subinterface tags for VLAN 30, which the trunk does not carry."),
  "correct": ["D"],
  "explanation": "The VLAN a subinterface serves is set by the encapsulation dot1Q value, not by the subinterface number, and the second one reads 30 while the trunk carries only VLANs 10 and 20, so nothing tagged for VLAN 20 ever reaches a matching subinterface. Option A inverts that relationship: the number is a label and is conventionally matched for readability alone. Option B names a command affecting trunk negotiation rather than tagging. Option C is wrong because subinterfaces follow the state of the physical interface, which is already up.",
  "difficulty": 3,
  "skills": ["inter-vlan-connectivity", "router-on-a-stick", "dot1q-encapsulation", "troubleshoot-vlan"],
},
{
  "id": "2.1-006", "objective": "2.1", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which approach gives the two VLANs reachability to each other on SW-CORE?",
  "exhibit": {"kind": "topology", "content": EX_006},
  "options": opts(
    "Create interface vlan 10 and interface vlan 20, then apply switchport mode access to each.",
    "Enable ip routing, then give interface vlan 10 and interface vlan 20 an address.",
    "Create a subinterface per VLAN with encapsulation dot1Q and an address on each.",
    "Convert one physical port per VLAN into a routed port and address each of them."),
  "correct": ["B"],
  "explanation": "A Layer 3 switch routes between VLANs using switched virtual interfaces, one per VLAN, but only once ip routing is enabled globally; without it the SVIs act as management interfaces and forward nothing. Option A applies a switchport command to a virtual interface, which has no physical port to switch. Option C describes router-on-a-stick, which belongs on a router across a trunk rather than on the switch itself. Option D consumes two physical ports and still leaves the VLANs unrouted.",
  "difficulty": 2,
  "skills": ["inter-vlan-connectivity", "svi", "layer-3-switch", "ip-routing"],
},
{
  "id": "2.1-007", "objective": "2.1", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why does the Vlan30 interface stay down while Vlan10 is up?",
  "exhibit": {"kind": "cli_output", "content": EX_007},
  "options": opts(
    "No access port in VLAN 30 is up, so nothing brings the SVI into service.",
    "The Vlan30 interface is missing a no shutdown command in the configuration.",
    "VLAN 30 has not been created in the switch's VLAN database.",
    "ip routing has not been enabled, so only one SVI may be active at a time."),
  "correct": ["A"],
  "explanation": "An SVI follows its VLAN, coming up only while at least one access port in that VLAN is up or a trunk carries it; the VLAN 30 row lists no ports at all, while VLAN 10 lists two, which is the whole difference between the two interfaces. Option B is ruled out by the note that neither SVI carries a shutdown. Option C is contradicted by VLAN 30 appearing in the VLAN table as active. Option D invents a one-SVI limit, and the exhibit states ip routing is already on.",
  "difficulty": 3,
  "skills": ["inter-vlan-connectivity", "svi", "svi-state", "troubleshoot-vlan"],
},
{
  "id": "2.1-008", "objective": "2.1", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why can the two hosts not reach each other across the trunk?",
  "exhibit": {"kind": "cli_output", "content": EX_008},
  "options": opts(
    "Spanning tree has placed VLAN 40 into a blocking state on the trunk link.",
    "The two switches disagree about the native VLAN configured on the trunk.",
    "VLAN 40 does not exist on SW2, so its port cannot become active in it.",
    "The two hosts sit in different subnets and require a router between them."),
  "correct": ["C"],
  "explanation": "A VLAN has to exist in a switch's own database before a port can join it, and SW2's table lists only VLANs 1 and 10; assigning its Gi0/1 to VLAN 40 therefore leaves that port inactive no matter what the trunk allows. Option A blames spanning tree, but a blocked VLAN would still appear in SW2's table. Option B describes a native VLAN mismatch, which affects untagged traffic rather than a VLAN missing entirely. Option D assumes different subnets, when both hosts are meant to share VLAN 40.",
  "difficulty": 2,
  "skills": ["vlan-configuration", "vlans-across-switches", "vlan-database", "troubleshoot-vlan"],
},
{
  "id": "2.1-009", "objective": "2.1", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. An IP phone on this port tags the traffic it originates. Which VLAN does that tagged traffic belong to?",
  "exhibit": {"kind": "cli_output", "content": EX_009},
  "options": opts("1 (default)", "20 (VOICE)", "10 (SALES)", "No VLAN; tagged frames are dropped"),
  "correct": ["B"],
  "explanation": "The Voice VLAN line records 20, and that is the VLAN the switch instructs the attached phone to tag its own traffic for. Option C is the Access Mode VLAN, which carries whatever arrives untagged, meaning the PC behind the phone rather than the phone itself. Option A is the Trunking Native Mode VLAN, which is irrelevant on a port operating in static access mode. Option D is contradicted by the voice VLAN being configured precisely so tagged frames are accepted.",
  "difficulty": 2,
  "skills": ["voice-vlan", "verify-vlan-configuration", "show-interfaces-switchport", "tagged-vs-untagged"],
},
{
  "id": "2.1-010", "objective": "2.1", "domain": 2, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Which two commands complete the configuration of Gi0/2? (Choose two.)",
  "exhibit": {"kind": "config", "content": EX_010},
  "options": opts(
    "switchport access vlan 10",
    "switchport trunk allowed vlan 10,20",
    "switchport mode trunk",
    "switchport voice vlan 20",
    "switchport trunk native vlan 10"),
  "correct": ["A", "D"],
  "explanation": "The access VLAN takes the untagged traffic from the PC and the voice VLAN tells the phone which tag to apply, so those two commands together serve both devices on one access port. Option B allows VLANs on a trunk, and this port is not one. Option C would convert the port to a trunk, which the attached PC could not use. Option E sets the untagged VLAN of a trunk, which again applies only to a port operating in trunk mode.",
  "difficulty": 2,
  "skills": ["vlan-configuration", "voice-vlan", "access-ports", "configure-access-vlan"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "2" / "2.1.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "2.1",
    "domain": 2,
    "blueprint_version": "v1.1",
    "scope_note": ("Configure and verify. Normal-range VLANs only. Trunk mechanics "
                   "belong to 2.2; this objective covers access ports, the default "
                   "VLAN, and inter-VLAN connectivity."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
