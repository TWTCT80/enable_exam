#!/usr/bin/env python3
"""Generate bank/1/1.1.json - 'Explain the role and function of network components'.

An explain-level objective covering eight component types. Rather than asking
what each component is, every item puts a component in a situation: a PoE budget
that either stretches to another access point or does not, a segment that cannot
route between its own VLANs, a requirement only an inline sensor satisfies, and
an inventory to read.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import power_inline, poe_row, opts  # noqa: E402

AVAILABLE, USED = 370.0, 76.4
CLASS4_MAX = 30.0
assert int((AVAILABLE - USED) // CLASS4_MAX) == 9, "PoE budget arithmetic"

# --- exhibits -------------------------------------------------------------

EX_001 = power_inline("SW1", AVAILABLE, USED, [
    poe_row("Gi1/0/1", "auto", "on", "30.0", "AIR-AP2802I-E-K9", "4", "30.0"),
    poe_row("Gi1/0/2", "auto", "on", "15.4", "IP Phone 8841", "3", "30.0"),
    poe_row("Gi1/0/3", "auto", "on", "15.4", "IP Phone 8841", "3", "30.0"),
    poe_row("Gi1/0/4", "auto", "on", "15.6", "IP Phone 8851", "3", "30.0"),
    poe_row("Gi1/0/5", "auto", "off", "0.0", "n/a", "n/a", "30.0"),
]) + """

More access points of the same model are to be added. Each draws the
full 30.0 W of its class."""

EX_002 = """              +--------------------+
              |     SW-ACCESS      |   Layer 2 switch
              +--+--------------+--+
                 |              |
             VLAN 10         VLAN 20
       192.168.10.0/24    192.168.20.0/24
             PC-A              PC-B

Both hosts are addressed correctly for their own VLAN and both switch
ports show connected. Neither host can reach the other. Nothing else is
attached to SW-ACCESS."""

EX_003 = """      internet
          |
    +-----+-----+
    |  ISP-RTR  |
    +-----+-----+
          |
    +-----+-----+        +------------------+
    |  EDGE-FW  |--------|  DMZ web server  |
    +-----+-----+        +------------------+
          |
    internal LAN

Requirement: traffic reaching the DMZ web server must be examined against
known exploit signatures, and any matching packet must be dropped before it
reaches the server rather than reported afterwards."""

EX_004 = """Site equipment inventory

    Device       Role recorded by the installer
    ---------    ------------------------------------------------
    RTR-01       Forwards between the site and the WAN circuit
    SW-01        Forwards frames within the site, no routing
    WLC-01       Holds the wireless configuration and pushes it to
                 every access point that joins it
    AP-001       Radio unit serving clients; holds no configuration
                 of its own once it has joined
    SRV-01       Hosts the file and print services"""


ITEMS = [
{
  "id": "1.1-001", "objective": "1.1", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. How many additional access points of this class can SW1 power from its remaining budget?",
  "exhibit": {"kind": "cli_output", "content": EX_001},
  "options": opts("12", "19", "9", "8"),
  "correct": ["C"],
  "explanation": "The summary line reports 293.6 W remaining, and each additional access point draws the full 30.0 W of its class, so nine fit with 23.6 W left over and a tenth would exceed the budget. Option A divides the total 370 W by 30 and ignores the 76.4 W already committed to the devices listed. Option B divides the remaining budget by 15.4 W, the draw of a phone rather than an access point. Option D subtracts one unnecessarily, as though a reserve had to be held back, which the output does not indicate.",
  "difficulty": 2,
  "skills": ["poe", "power-budget", "access-points", "network-components"],
},
{
  "id": "1.1-002", "objective": "1.1", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which component must be added before PC-A and PC-B can communicate?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "A device that routes between the VLANs, such as a router or Layer 3 switch.",
    "A second Layer 2 switch, so that each VLAN has a dedicated switch of its own.",
    "A wireless LAN controller to coordinate the two segments centrally.",
    "A next-generation firewall to permit the traffic between the two VLANs."),
  "correct": ["A"],
  "explanation": "A Layer 2 switch forwards only within a VLAN, and the two hosts sit in different VLANs and different subnets, so something operating at Layer 3 has to move traffic between them. Option B adds switching capacity, which was never the shortage, and would leave both VLANs just as isolated. Option C names a device that manages access points and plays no part in routing between wired segments. Option D would filter traffic that no device is currently routing at all, so permitting it changes nothing.",
  "difficulty": 2,
  "skills": ["network-components", "layer-2-vs-layer-3-switch", "inter-vlan-routing", "router-role"],
},
{
  "id": "1.1-003", "objective": "1.1", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which addition satisfies the stated requirement?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "A Layer 3 switch placed in front of the server, filtering traffic with access lists.",
    "A router access list applied inbound on the internet-facing interface of ISP-RTR.",
    "An endpoint antivirus agent installed on the DMZ web server itself.",
    "An IPS inspecting the traffic inline, so it can drop matching packets."),
  "correct": ["D"],
  "explanation": "The requirement has two halves: match known exploit signatures, and drop the traffic before it arrives. Only an intrusion prevention system placed inline does both, since a sensor deployed out of band could detect but not stop. Option A filters on addresses and ports, which carries no signature knowledge. Option B has the same limitation and sits at the wrong point besides. Option C protects the host after the packet has already arrived, which the requirement explicitly rules out.",
  "difficulty": 3,
  "skills": ["network-components", "ips", "next-generation-firewall", "inline-inspection"],
},
{
  "id": "1.1-004", "objective": "1.1", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which device holds the wireless configuration on behalf of the access points at this site?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts("AP-001", "WLC-01", "SRV-01", "RTR-01"),
  "correct": ["B"],
  "explanation": "The inventory records WLC-01 as holding the wireless configuration and pushing it to every access point that joins, which is the controller's defining role in a centralised wireless deployment. Option A is the access point itself, and the inventory states plainly that it keeps no configuration of its own once joined. Option C hosts file and print services and has no wireless role. Option D forwards between the site and the WAN circuit, which is routing rather than wireless management.",
  "difficulty": 1,
  "skills": ["network-components", "wireless-controller", "access-points", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "1" / "1.1.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "1.1",
    "domain": 1,
    "blueprint_version": "v1.1",
    "scope_note": ("Components are placed in situations rather than defined. The PoE "
                   "budget arithmetic is asserted at generation time."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items, PoE budget checked)")
