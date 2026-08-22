#!/usr/bin/env python3
"""Generate bank/2/2.7.json - 'Describe physical infrastructure connections of
WLAN components (AP, WLC, access/trunk ports, and LAG)'.

Item 001 carries this objective: a lightweight AP in local mode needs an ACCESS
port, not a trunk, because every client VLAN rides inside the CAPWAP tunnel and
the AP itself lives in one VLAN. Candidates reason "several SSIDs, therefore
several VLANs, therefore a trunk" and get it wrong. 002 shows the case where
that reasoning IS right, so the two items define the boundary between them.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import interfaces_status, intf_status, opts  # noqa: E402

# --- exhibits -------------------------------------------------------------

EX_001 = """                              CAPWAP tunnel
        +--------+   ................................   +---------+
        |  AP-21 |===[ SW-ACC ]=====[ SW-DIST ]=========|   WLC   |
        +--------+                                      +---------+
       lightweight,                                      10.50.0.5
       local mode

AP-21 advertises three SSIDs, mapped on the controller to VLANs 10, 20
and 30. The access point itself is addressed from the management VLAN,
VLAN 50. All client traffic is carried inside CAPWAP to the WLC."""

EX_002 = """        +-----------+
        |   AP-07   |-----------[ SW-ACC ]
        +-----------+
        autonomous

AP-07 holds its own configuration and no controller is deployed. It
advertises three SSIDs and bridges each one directly onto the wired
network as VLAN 10, VLAN 20 and VLAN 30 respectively."""

EX_003 = """A wireless controller is being cabled into the distribution layer.

    Requirement
    ---------------------------------------------------------------
    Four controller ports go to the same distribution switch pair
    The four are to act as one logical link, surviving any one failure
    Every WLAN interface on the controller must reach the switches
    The controller's LAG implementation does not negotiate with LACP"""

EX_004 = interfaces_status("SW-ACC", [
    intf_status("Gi1/0/8", "AP-21 lightweight", "connected", "50", "a-full", "a-1000"),
    intf_status("Gi1/0/9", "AP-07 autonomous", "connected", "trunk", "a-full", "a-1000"),
    intf_status("Gi1/0/10", "printer", "connected", "20", "a-full", "a-100"),
    intf_status("Gi1/0/24", "uplink to SW-DIST", "connected", "trunk", "a-full", "a-1000"),
])


ITEMS = [
{
  "id": "2.7-001", "objective": "2.7", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. How should the switch port serving AP-21 be configured?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "As a trunk allowing VLANs 10, 20 and 30, one for each advertised SSID.",
    "As a trunk allowing VLANs 10, 20, 30 and 50, with 50 as the native VLAN.",
    "As an access port in VLAN 50, where the AP itself is addressed.",
    "As a routed port with an address in each of the three client VLANs."),
  "correct": ["C"],
  "explanation": "A lightweight AP in local mode wraps every client frame in CAPWAP and sends it to the controller, so the switch never sees VLAN 10, 20 or 30 on that link; the only traffic on the wire belongs to the AP itself, which lives in VLAN 50. An access port is therefore correct and a trunk would carry nothing extra. Options A and B follow the reasoning that several SSIDs must mean several VLANs on the cable, which holds for an autonomous AP but not behind a controller. Option D would need the AP to route, which it does not.",
  "difficulty": 3,
  "skills": ["wlan-physical-connections", "access-port", "capwap", "lightweight-ap"],
},
{
  "id": "2.7-002", "objective": "2.7", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which switchport configuration does the link to this autonomous access point require?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "As an access port in VLAN 10, with the other two SSIDs tunnelled inside it.",
    "As a trunk carrying VLANs 10, 20 and 30 down to the access point.",
    "As an access port in a management VLAN, since the AP holds its own config.",
    "As a routed port, because an autonomous access point performs its own routing."),
  "correct": ["B"],
  "explanation": "An autonomous access point has no controller to tunnel to, so it tags each SSID's traffic onto the wire itself and the switch must carry all three VLANs, which requires a trunk. Option A would collapse three separate networks into one and there is no tunnel here to carry the others. Option C describes the correct answer for a lightweight AP in local mode, which is the contrast worth holding onto. Option D has the AP routing between the VLANs, which it bridges rather than routes.",
  "difficulty": 2,
  "skills": ["wlan-physical-connections", "trunk-port", "autonomous-ap", "vlan-tagging"],
},
{
  "id": "2.7-003", "objective": "2.7", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. How should the four controller ports and the switch side be configured?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "Four separate access ports, one per WLAN interface on the controller.",
    "One EtherChannel with LACP active on the switch side to negotiate the bundle.",
    "Four separate trunks, letting the controller balance across them itself.",
    "One EtherChannel set to mode on, carrying a trunk for the WLAN interfaces."),
  "correct": ["D"],
  "explanation": "The requirements ask for one logical link that survives a failure, so the four ports bundle into an EtherChannel, and they must carry several WLAN interfaces, so that bundle is a trunk. Because the controller's LAG does not negotiate, the switch side has to be forced on rather than left to LACP. Option B is the right shape but relies on a negotiation the exhibit says will not happen, leaving the ports unbundled. Option A gives one VLAN per port and no resilience. Option C leaves four independent links with no bundle at all.",
  "difficulty": 3,
  "skills": ["wlan-physical-connections", "lag", "etherchannel", "wlc-connectivity"],
},
{
  "id": "2.7-004", "objective": "2.7", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which port is serving the lightweight access point?",
  "exhibit": {"kind": "cli_output", "content": EX_004},
  "options": opts("Gi1/0/24", "Gi1/0/9", "Gi1/0/8", "Gi1/0/10"),
  "correct": ["C"],
  "explanation": "Gi1/0/8 sits in VLAN 50 as an access port and its description names the lightweight unit, which is the expected shape: one VLAN for the AP itself and CAPWAP carrying everything else. Option B is the autonomous AP, whose Vlan column reads trunk because it tags client VLANs on the wire. Option A is the uplink between switches, also a trunk. Option D is an ordinary access port in VLAN 20 serving a printer.",
  "difficulty": 1,
  "skills": ["wlan-physical-connections", "show-interfaces-status", "access-port", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "2" / "2.7.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "2.7",
    "domain": 2,
    "blueprint_version": "v1.1",
    "scope_note": ("001 and 002 are a deliberate pair: the same three-SSID situation "
                   "needs an access port behind a controller and a trunk without one."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
