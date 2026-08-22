#!/usr/bin/env python3
"""Generate bank/2/2.4.json - 'Configure and verify (Layer 2/Layer 3)
EtherChannel (LACP)'.

Both layers the objective names: Layer 2 bundles throughout, and a Layer 3
bundle in 006. LACP negotiation is the focus, with the passive/passive deadlock
in 003 mirroring the dynamic-auto deadlock in 2.2-002 - the same shape of fault
in a different protocol, which is worth having twice.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import etherchannel_summary, po_row, opts  # noqa: E402

SEP = "-" * 58

# --- exhibits -------------------------------------------------------------

EX_A = etherchannel_summary("SW1", [
    po_row(1, "Po1(SU)", "LACP", ["Gi0/1(P)", "Gi0/2(P)"]),
    po_row(2, "Po2(SD)", "LACP", ["Gi0/3(D)", "Gi0/4(D)"]),
], groups=2, aggregators=2)

EX_003 = """! SW1 - relevant configuration
!
interface range GigabitEthernet0/1 - 2
 channel-group 1 mode passive
!
""" + SEP + """
! SW2 - relevant configuration
!
interface range GigabitEthernet0/1 - 2
 channel-group 1 mode passive
!

All four interfaces are up. Neither switch shows a bundled port-channel."""

EX_004 = """SW3 has been configured with channel-group 5 mode active on its two
uplink interfaces, and the bundle must come up using LACP.

    Candidate configuration for the far end, SW4
    --------------------------------------------
    The two matching interfaces on SW4 need a channel-group command."""

EX_005 = etherchannel_summary("SW5", [
    po_row(1, "Po1(SU)", "LACP", ["Gi0/1(P)", "Gi0/2(s)"]),
]) + """

Gi0/1 carries switchport trunk allowed vlan 1,10,20 while Gi0/2 carries
switchport trunk allowed vlan 1,10,20,30. Both interfaces are up and
both run LACP."""

EX_006 = """! SW6 - a Layer 3 switch aggregating two links to R1
!
interface Port-channel1
 ip address 10.9.9.1 255.255.255.252
!
interface range GigabitEthernet0/1 - 2
 channel-group 1 mode active
!

The port-channel refuses the ip address command, reporting that the
interface is a switchport."""

EX_007 = """! SW7 - the two links to be bundled
!
interface GigabitEthernet0/1
 switchport mode trunk
!
interface GigabitEthernet0/2
 switchport mode trunk
!

The two links must be aggregated into one logical trunk using LACP,
with SW7 actively initiating the negotiation."""

EX_008 = etherchannel_summary("SW8", [
    po_row(1, "Po1(SU)", "LACP", ["Gi0/1(P)", "Gi0/2(P)"]),
    po_row(2, "Po2(SU)", "PAgP", ["Gi0/5(P)", "Gi0/6(P)"]),
    po_row(3, "Po3(SU)", "-", ["Gi0/9(P)", "Gi0/10(P)"]),
], groups=3, aggregators=3)


ITEMS = [
{
  "id": "2.4-001", "objective": "2.4", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What do the flags on Port-channel 2 tell you about its state?",
  "exhibit": {"kind": "cli_output", "content": EX_A},
  "options": opts(
    "It is a Layer 3 bundle that has not yet been given an address.",
    "It is a Layer 2 bundle that is down, and both member ports are down with it.",
    "It is suspended because its members carry mismatched configuration.",
    "It is in hot-standby, waiting for Port-channel 1 to fail before taking over."),
  "correct": ["B"],
  "explanation": "The flag key reads S for Layer 2 and D for down, so Po2(SD) is a Layer 2 bundle that is down, and each member shows (D) for the same reason. Option A misreads S, since R rather than S marks a Layer 3 bundle. Option C describes the s flag for suspended, which would appear against a member port rather than as D on all of them. Option D describes the H flag, which is absent here.",
  "difficulty": 1,
  "skills": ["etherchannel", "show-etherchannel-summary", "port-channel-flags", "read-correct-row"],
},
{
  "id": "2.4-002", "objective": "2.4", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which member ports are actively carrying traffic for their bundle?",
  "exhibit": {"kind": "cli_output", "content": EX_A},
  "options": opts("Gi0/3 and Gi0/4", "All four member ports listed",
                  "None of them, since neither bundle is in use", "Gi0/1 and Gi0/2"),
  "correct": ["D"],
  "explanation": "The P flag means a port is bundled into its port-channel and carrying traffic, and only Gi0/1 and Gi0/2 show it. Option A names the two ports flagged D for down, which pass nothing. Option B counts all four and ignores that the flags differ between the rows. Option C is contradicted by Po1 showing U for in use, which is exactly what distinguishes it from Po2.",
  "difficulty": 2,
  "skills": ["etherchannel", "port-channel-flags", "show-etherchannel-summary", "verify-etherchannel"],
},
{
  "id": "2.4-003", "objective": "2.4", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why has the bundle not come up on either switch?",
  "exhibit": {"kind": "config", "content": EX_003},
  "options": opts(
    "Both ends are passive, so neither one begins the LACP negotiation.",
    "Passive mode belongs to PAgP, so no LACP negotiation was ever attempted.",
    "The interfaces must be shut down before a channel-group can take effect.",
    "A channel-group number must differ between the two switches to avoid a loop."),
  "correct": ["A"],
  "explanation": "LACP passive waits for the far end to speak first, so two passive ends sit silent and no bundle forms; changing either side to active resolves it. Option B assigns passive to the wrong protocol, since PAgP uses desirable and auto while LACP uses active and passive. Option C invents a shutdown requirement the command does not have. Option D reverses the rule, as the group number is locally significant and need not match, though the modes must be compatible.",
  "difficulty": 3,
  "skills": ["etherchannel", "lacp", "lacp-modes", "troubleshoot-etherchannel"],
},
{
  "id": "2.4-004", "objective": "2.4", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which command on SW4's interfaces brings the bundle up?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts(
    "channel-group 5 mode desirable",
    "channel-group 5 mode auto",
    "channel-group 5 mode passive",
    "channel-group 5 mode on"),
  "correct": ["C"],
  "explanation": "SW3 is active, which initiates LACP, so the far end may be either active or passive; passive answers the negotiation and the bundle forms. Options A and B name the PAgP modes desirable and auto, and PAgP cannot negotiate with LACP at all. Option D forces the bundle on with no protocol, which will not pair with an end that expects an LACP exchange and commonly leaves ports suspended instead.",
  "difficulty": 2,
  "skills": ["etherchannel", "lacp", "lacp-modes", "configure-etherchannel"],
},
{
  "id": "2.4-005", "objective": "2.4", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why is Gi0/2 flagged s rather than bundling with Gi0/1?",
  "exhibit": {"kind": "cli_output", "content": EX_005},
  "options": opts(
    "The port is in hot-standby and will bundle only if Gi0/1 fails.",
    "LACP allows a maximum of one active member per port-channel group.",
    "The port negotiated a different speed setting, so it cannot join the bundle.",
    "Its allowed VLAN list differs from Gi0/1's, so the bundle suspends it."),
  "correct": ["D"],
  "explanation": "Every member of an EtherChannel must carry identical switchport settings, and Gi0/2 allows VLAN 30 where Gi0/1 does not, so the switch suspends it rather than bundling a mismatched link. Option A describes the H flag for hot-standby, not s. Option B invents a one-member limit that would make the feature pointless. Option C blames speed, which the exhibit does not show differing, and the stated VLAN difference is sufficient on its own.",
  "difficulty": 3,
  "skills": ["etherchannel", "member-port-consistency", "suspended-port", "troubleshoot-etherchannel"],
},
{
  "id": "2.4-006", "objective": "2.4", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which change lets the port-channel take the address?",
  "exhibit": {"kind": "config", "content": EX_006},
  "options": opts(
    "Apply switchport mode trunk to the port-channel before addressing it.",
    "Apply no switchport to Port-channel1 and to both member interfaces.",
    "Move the address onto the member interfaces and leave the bundle unaddressed.",
    "Change the member interfaces to channel-group 1 mode passive."),
  "correct": ["B"],
  "explanation": "A Layer 3 EtherChannel needs the logical interface and its members taken out of switching with no switchport before an address will be accepted, and doing it on the port-channel alone leaves the members mismatched. Option A moves further into Layer 2, which is the opposite of what the error asks for. Option C addresses the members individually, which defeats the aggregation. Option D changes the LACP mode, which affects negotiation and has no bearing on whether the interface routes.",
  "difficulty": 2,
  "skills": ["etherchannel", "layer-3-etherchannel", "no-switchport", "configure-etherchannel"],
},
{
  "id": "2.4-007", "objective": "2.4", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which command applied to both interfaces meets the requirement?",
  "exhibit": {"kind": "config", "content": EX_007},
  "options": opts(
    "channel-group 1 mode active",
    "channel-group 1 mode desirable",
    "channel-protocol lacp",
    "channel-group 1 mode on"),
  "correct": ["A"],
  "explanation": "Active is the LACP mode that initiates the negotiation, which is precisely what the requirement asks SW7 to do, and applying it to both interfaces places them in the same group. Option B is the PAgP equivalent and would not speak LACP. Option C selects a protocol but creates no group, so no bundle forms from it alone. Option D forces the channel up without any negotiation, so nothing verifies that the far end agrees before traffic is committed to the bundle.",
  "difficulty": 2,
  "skills": ["etherchannel", "lacp", "lacp-modes", "configure-etherchannel"],
},
{
  "id": "2.4-008", "objective": "2.4", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which port-channel was brought up without any negotiation protocol?",
  "exhibit": {"kind": "cli_output", "content": EX_008},
  "options": opts("Po1", "Po2", "Po3", "None; all three negotiated"),
  "correct": ["C"],
  "explanation": "The Protocol column names what negotiated each bundle, and Po3 shows a dash, meaning its members were forced on with channel-group mode on and no protocol ran. Option A shows LACP, the open standard. Option B shows PAgP, Cisco's own. Option D is contradicted by that dash, and a bundle formed without negotiation is the one that will silently forward into a mismatched far end.",
  "difficulty": 1,
  "skills": ["etherchannel", "show-etherchannel-summary", "lacp", "static-etherchannel"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "2" / "2.4.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "2.4",
    "domain": 2,
    "blueprint_version": "v1.1",
    "scope_note": ("Both layers the objective names. PAgP appears only as a contrast "
                   "to LACP, which is the protocol the objective specifies."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
