#!/usr/bin/env python3
"""Generate bank/2/2.2.json - 'Configure and verify interswitch connectivity'.

Configure-and-verify. All three sub-topics: trunk ports (002, 005, 008),
802.1Q tagging (007, 009) and the native VLAN (001, 003, 009).

The two items worth the most are 003 and 006, because both are faults that
leave every interface up and the trunk apparently working.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import interfaces_trunk, trunk_port, opts  # noqa: E402

SEP = "-" * 58

# --- exhibits -------------------------------------------------------------

EX_A = interfaces_trunk("SW1",
    [trunk_port("Gi0/1", "on", "802.1q", "trunking", "99"),
     trunk_port("Gi0/2", "desirable", "n-802.1q", "trunking", "1")],
    [("Gi0/1", "1-4094"), ("Gi0/2", "1-4094")],
    [("Gi0/1", "1,10,20,30"), ("Gi0/2", "1,10,20,30")],
    [("Gi0/1", "1,10,20,30"), ("Gi0/2", "1,10,30")])

EX_002 = """! SW1 - relevant configuration
!
interface GigabitEthernet0/1
 switchport mode dynamic auto
!
""" + SEP + """
! SW2 - relevant configuration
!
interface GigabitEthernet0/1
 switchport mode dynamic auto
!

Both interfaces are up and the cable between them is known good, yet
show interfaces trunk lists nothing on either switch."""

EX_003 = """SW1#
*Aug 22 09:14:11.204: %CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch
discovered on GigabitEthernet0/1 (99), with SW2 GigabitEthernet0/1 (1).
SW1#

The trunk between the two switches reports trunking on both sides and
tagged VLANs pass across it normally."""

EX_004 = interfaces_trunk("SW3",
    [trunk_port("Gi0/1", "on", "802.1q", "trunking", "1")],
    [("Gi0/1", "1,10,30")],
    [("Gi0/1", "1,10,30")],
    [("Gi0/1", "1,10,30")]) + """

VLAN 20 exists on SW3 and on the switch at the far end, and access ports
in VLAN 20 are up on both. Hosts in VLAN 20 cannot reach each other
across this link."""

EX_005 = """! SW4 - GigabitEthernet0/24 as it stands today
!
interface GigabitEthernet0/24
 description uplink to the distribution switch
 no shutdown
!

The uplink must be a trunk that never relies on negotiation, must tag
with 802.1Q, and must use VLAN 99 for untagged traffic."""

EX_006 = """SW5(config)# interface GigabitEthernet0/1
SW5(config-if)# switchport trunk allowed vlan 10,20,30
SW5(config-if)# switchport trunk allowed vlan 40
SW5(config-if)# end
SW5#
SW5# show interfaces trunk | begin Vlans allowed on trunk
Port        Vlans allowed on trunk
Gi0/1       40

VLANs 10, 20 and 30 stopped crossing this trunk the moment the second
command was entered."""

EX_008 = """SW6# show interfaces GigabitEthernet0/3 switchport
Name: Gi0/3
Switchport: Enabled
Administrative Mode: dynamic auto
Operational Mode: static access
Administrative Trunking Encapsulation: dot1q
Operational Trunking Encapsulation: native
Negotiation of Trunking: On
Access Mode VLAN: 1 (default)
Trunking Native Mode VLAN: 1 (default)"""

EX_009 = """! SW7 - relevant configuration
!
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30
!
""" + SEP + """
! SW8 - relevant configuration
!
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk native vlan 1
 switchport trunk allowed vlan 10,20
!

Both interfaces report trunking."""


ITEMS = [
{
  "id": "2.2-001", "objective": "2.2", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which VLAN carries untagged frames across GigabitEthernet0/1?",
  "exhibit": {"kind": "cli_output", "content": EX_A},
  "options": opts("1", "10", "99", "30"),
  "correct": ["C"],
  "explanation": "The Native vlan column records which VLAN a trunk leaves untagged, and the Gi0/1 row reads 99. Option A is the native VLAN of Gi0/2, the row beneath, which is the ordinary default and the value most candidates expect to see. Option B and option D name VLANs that appear only in the allowed and forwarding lists further down, meaning they cross the trunk tagged rather than untagged.",
  "difficulty": 1,
  "skills": ["trunk-ports", "native-vlan", "show-interfaces-trunk", "read-correct-row"],
},
{
  "id": "2.2-002", "objective": "2.2", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why has no trunk formed between the two switches?",
  "exhibit": {"kind": "config", "content": EX_002},
  "options": opts(
    "Both ports are set to dynamic auto, so neither one asks to become a trunk.",
    "Dynamic auto requires 802.1Q to be stated explicitly before it will negotiate.",
    "The two ports are in different VLANs, which blocks trunk negotiation.",
    "A trunk cannot form until an access VLAN is removed from both interfaces."),
  "correct": ["A"],
  "explanation": "Dynamic auto waits to be asked: it accepts a trunk if the far end proposes one but never proposes one itself, so two ports both set to auto sit in access mode indefinitely. Setting either side to trunk or dynamic desirable resolves it. Option B invents an encapsulation prerequisite that negotiation handles on its own. Option C misapplies VLAN membership, which does not govern whether negotiation happens. Option D describes removing configuration neither interface carries.",
  "difficulty": 2,
  "skills": ["trunk-ports", "dtp", "dynamic-auto", "troubleshoot-trunk"],
},
{
  "id": "2.2-003", "objective": "2.2", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What is the practical consequence of the condition this message reports?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts(
    "The trunk drops and no VLAN can cross it until the two ends agree.",
    "Tagged frames for VLAN 99 are discarded by SW2 as belonging to an unknown VLAN.",
    "Both switches move every VLAN into spanning tree blocking as a safety measure.",
    "Untagged frames from VLAN 99 on SW1 arrive in VLAN 1 on SW2."),
  "correct": ["D"],
  "explanation": "Each end leaves its own native VLAN untagged and assumes anything untagged belongs to that VLAN, so with 99 on one side and 1 on the other the two VLANs are quietly bridged into one broadcast domain. Option A expects the trunk to fail, but the exhibit states it reports trunking and tagged VLANs still pass, which is what makes this fault hard to spot. Option B describes tagged traffic, which is unaffected. Option C invents a spanning tree response that no switch takes to a native VLAN mismatch.",
  "difficulty": 3,
  "skills": ["native-vlan", "native-vlan-mismatch", "802-1q", "troubleshoot-trunk"],
},
{
  "id": "2.2-004", "objective": "2.2", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why does VLAN 20 traffic fail to cross this trunk?",
  "exhibit": {"kind": "cli_output", "content": EX_004},
  "options": opts(
    "VLAN 20 is being pruned because no access port in it is currently up.",
    "VLAN 20 is absent from the list of VLANs allowed on the trunk.",
    "The trunk's native VLAN of 1 prevents any even-numbered VLAN from crossing.",
    "Spanning tree has blocked VLAN 20 on this link to prevent a loop."),
  "correct": ["B"],
  "explanation": "The Vlans allowed on trunk section reads 1,10,30, so frames tagged for VLAN 20 are dropped at the trunk regardless of the VLAN existing and having active ports at both ends. Option A blames pruning, but a pruned VLAN would still be listed as allowed and would appear in the allowed-and-active section. Option C invents a rule about even-numbered VLANs. Option D blames spanning tree, which would show the VLAN as allowed but missing only from the forwarding section.",
  "difficulty": 2,
  "skills": ["trunk-ports", "allowed-vlan-list", "show-interfaces-trunk", "troubleshoot-trunk"],
},
{
  "id": "2.2-005", "objective": "2.2", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which set of commands configures Gi0/24 to meet the stated requirement?",
  "exhibit": {"kind": "config", "content": EX_005},
  "options": opts(
    "switchport trunk encapsulation dot1q, switchport mode dynamic desirable, switchport trunk native vlan 99",
    "switchport mode trunk, switchport trunk native vlan 99, switchport nonegotiate",
    "switchport trunk encapsulation dot1q, switchport mode trunk, switchport trunk native vlan 99",
    "switchport mode access, switchport access vlan 99, switchport trunk encapsulation dot1q"),
  "correct": ["C"],
  "explanation": "The three requirements map onto three commands: dot1q sets the tagging, mode trunk fixes the port so it does not depend on negotiation, and the native vlan command moves untagged traffic to 99. Option A leaves the port at dynamic desirable, which still negotiates. Option B omits the encapsulation and adds nonegotiate, which suppresses DTP frames but leaves the tagging method unset on a switch that supports more than one. Option D configures an access port, which carries a single VLAN untagged and tags nothing.",
  "difficulty": 2,
  "skills": ["trunk-ports", "802-1q", "native-vlan", "configure-trunk"],
},
{
  "id": "2.2-006", "objective": "2.2", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why did VLANs 10, 20 and 30 stop crossing the trunk?",
  "exhibit": {"kind": "cli_output", "content": EX_006},
  "options": opts(
    "The second command replaced the list instead of extending it.",
    "A trunk accepts at most one allowed-VLAN command per interface.",
    "VLAN 40 does not exist, so the switch cleared the list as invalid.",
    "The list was reset because the interface was not shut down first."),
  "correct": ["A"],
  "explanation": "switchport trunk allowed vlan sets the list outright, so entering it a second time discards whatever went before; extending a list requires the add keyword, as in switchport trunk allowed vlan add 40. Option B invents a one-command limit, when the command may be issued repeatedly and simply overwrites each time. Option C blames a missing VLAN, but an allowed list may name VLANs that do not yet exist. Option D adds a shutdown requirement the command does not have.",
  "difficulty": 3,
  "skills": ["trunk-ports", "allowed-vlan-list", "configure-trunk", "command-side-effects"],
},
{
  "id": "2.2-007", "objective": "2.2", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which VLAN is allowed and active on GigabitEthernet0/2 but is not currently forwarding on it?",
  "exhibit": {"kind": "cli_output", "content": EX_A},
  "options": opts("1", "10", "30", "20"),
  "correct": ["D"],
  "explanation": "Comparing the last two sections for Gi0/2 shows 1,10,20,30 allowed and active but only 1,10,30 forwarding, so VLAN 20 is the one held out of the forwarding state on that port. Options A, B and C all appear in both lists for Gi0/2, so each is passing traffic normally, and the value of this output is precisely that the two lists can differ.",
  "difficulty": 1,
  "skills": ["trunk-ports", "show-interfaces-trunk", "spanning-tree-forwarding", "read-correct-row"],
},
{
  "id": "2.2-008", "objective": "2.2", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does the difference between the two mode lines tell you about the far end of this link?",
  "exhibit": {"kind": "cli_output", "content": EX_008},
  "options": opts(
    "The far end has been configured as a trunk, which SW6 declined to match.",
    "The far end never proposed a trunk, so SW6's port settled into access mode.",
    "The far end is disconnected, which is why no trunk could be negotiated.",
    "The far end uses a different encapsulation, so negotiation could not complete."),
  "correct": ["B"],
  "explanation": "Administrative Mode records what was configured and Operational Mode what the port actually became; dynamic auto will accept a trunk but never ask for one, so ending in static access means nothing on the far end proposed one either. Option A is backwards, since a trunk proposal from the far end is exactly what dynamic auto accepts. Option C is ruled out by Switchport being Enabled with a negotiated operational mode at all. Option D invents an encapsulation clash, which would not silently produce access mode.",
  "difficulty": 2,
  "skills": ["trunk-ports", "dtp", "administrative-vs-operational-mode", "verify-trunk"],
},
{
  "id": "2.2-009", "objective": "2.2", "domain": 2, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Which two problems do these configurations create between SW7 and SW8? (Choose two.)",
  "exhibit": {"kind": "config", "content": EX_009},
  "options": opts(
    "No trunk will form, because both ends are configured statically.",
    "VLAN 30 is allowed on SW7 but not on SW8, so its frames are dropped at SW8.",
    "The encapsulation differs between the two ends, so tagged frames are unreadable.",
    "Untagged traffic crosses between VLAN 99 and VLAN 1, merging two domains.",
    "VLANs 10 and 20 will be pruned because the native VLANs disagree."),
  "correct": ["B", "D"],
  "explanation": "Two independent faults sit in these configurations: the allowed lists differ, so VLAN 30 leaves SW7 tagged and is discarded by SW8, and the native VLANs differ, so untagged frames cross between VLAN 99 and VLAN 1 and silently join the two. Option A is wrong because two ends both set to trunk form one readily. Option C invents an encapsulation difference that neither configuration states. Option E attaches pruning to the native VLAN, which governs untagged traffic rather than which VLANs are carried.",
  "difficulty": 2,
  "skills": ["trunk-ports", "native-vlan-mismatch", "allowed-vlan-list", "troubleshoot-trunk"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "2" / "2.2.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "2.2",
    "domain": 2,
    "blueprint_version": "v1.1",
    "scope_note": ("Trunk ports, 802.1Q and the native VLAN. The high-value items are "
                   "the faults that leave every interface up and the trunk apparently "
                   "healthy: a native VLAN mismatch and an overwritten allowed list."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
