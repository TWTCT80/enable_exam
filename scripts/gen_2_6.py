#!/usr/bin/env python3
"""Generate bank/2/2.6.json - 'Describe Cisco Wireless Architectures and AP modes'.

Architectures (autonomous, centralised split-MAC, cloud-managed) and the AP
modes that matter at this level (local, FlexConnect, monitor). Each item works
from a requirement or an inventory rather than defining a term.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

# --- exhibits -------------------------------------------------------------

EX_001 = """Requirements for a new wireless deployment

    Fourteen sites, 180 access points in total
    One wireless policy applied everywhere, changed centrally
    Clients must roam between APs at a site without reauthenticating
    The team will not log in to individual access points
    Hardware is to be owned and hosted by the organisation"""

EX_002 = """A lightweight access point has joined its controller. The two now
divide the work of serving a client between them.

    Function
    -------------------------------------------------------
    Transmitting beacons and probe responses
    Acknowledging frames from clients at the radio
    Encrypting and decrypting frames on the air interface
    Deciding whether a client may associate
    Applying the security policy configured for the WLAN
    Managing the client's roam from one AP to the next"""

EX_003 = """A branch office holds twelve access points and reaches the wireless
controller across a WAN circuit at the head office.

When that circuit fails, staff at the branch must keep using the local
wireless network, and their traffic must stay on the branch LAN rather
than being carried anywhere else."""

EX_004 = """Access point mode reference

    Mode           What the radio does
    -----------    ---------------------------------------------------
    Local          Serves clients, and scans off-channel briefly
    FlexConnect    Serves clients, can switch traffic locally
    Monitor        Serves no clients; listens full time
    Sniffer        Captures frames and forwards them to an analyser
    Bridge         Provides a wireless link between two wired segments

An access point is to be dedicated to detecting rogue devices and
measuring interference across the band. It must never carry client
traffic."""

EX_005 = """Two access points recovered from a storeroom

    Property                     Unit A                Unit B
    -------------------------    ------------------    ---------------
    Holds its own full config    yes                   no
    Configured over              its own web page      a controller
    Behaviour with no            keeps serving         will not serve
    controller reachable         clients               clients
    Typical deployment size      one or two units      dozens upward"""


ITEMS = [
{
  "id": "2.6-001", "objective": "2.6", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which wireless architecture fits these requirements?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "Autonomous access points, each configured through its own interface.",
    "A centralised controller with lightweight access points joined to it.",
    "A cloud-managed deployment, with the controller hosted by the vendor.",
    "A mesh of bridge-mode access points relaying between the fourteen sites."),
  "correct": ["B"],
  "explanation": "One policy applied centrally, roaming handled between APs, no logging in to individual units and hardware owned on site all point to a controller-based split-MAC design. Option A would mean touching 180 devices for every change and offers no controller to coordinate a roam. Option C matches every requirement except the last, since a cloud deployment puts the control plane in the vendor's hands rather than the organisation's, which is the detail that separates the two. Option D describes a way of linking sites rather than an architecture for serving clients.",
  "difficulty": 2,
  "skills": ["wireless-architectures", "centralised-wlc", "split-mac", "design-to-requirements"],
},
{
  "id": "2.6-002", "objective": "2.6", "domain": 2, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Which two functions stay on the access point rather than moving to the controller? (Choose two.)",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "Deciding whether a client may associate",
    "Acknowledging frames from clients at the radio",
    "Applying the security policy configured for the WLAN",
    "Transmitting beacons and probe responses",
    "Managing the client's roam from one AP to the next"),
  "correct": ["B", "D"],
  "explanation": "The split divides work by how time-critical it is: anything that must answer within microseconds stays on the radio, so the AP keeps beaconing, probe responses, acknowledgements and encryption, while slower decisions move upstream. Options A and C are policy decisions the controller makes once and applies everywhere. Option E is coordination between two APs, which only something seeing both of them can do. That is why an AP in local mode stops serving clients when it loses its controller.",
  "difficulty": 3,
  "skills": ["split-mac", "wireless-architectures", "lightweight-ap", "wlc-role"],
},
{
  "id": "2.6-003", "objective": "2.6", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which access point mode meets the branch requirement?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "Monitor mode, so the access points keep scanning while the circuit is down.",
    "Local mode, which is the default and needs no change for this.",
    "FlexConnect mode, which puts client traffic onto the branch LAN.",
    "Bridge mode, so the APs relay to one another until the WAN returns."),
  "correct": ["C"],
  "explanation": "FlexConnect exists for exactly this: the AP keeps serving clients and puts their traffic straight onto the local LAN, so a WAN failure between branch and controller does not take the wireless network down with it. Option A stops client service entirely, which is the opposite of the requirement. Option B tunnels all client traffic to the controller, so the branch loses wireless the moment the circuit fails. Option D links wired segments together and does not address controller reachability.",
  "difficulty": 2,
  "skills": ["ap-modes", "flexconnect", "branch-survivability", "wireless-architectures"],
},
{
  "id": "2.6-004", "objective": "2.6", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which mode should be applied to that access point?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts("Monitor", "Bridge", "Sniffer", "FlexConnect"),
  "correct": ["A"],
  "explanation": "Monitor is the mode that takes an AP out of client service and leaves its radio listening across the band full time, which is what rogue detection and interference measurement need. Option C also carries no clients, but it captures frames for an external analyser rather than reporting rogues and interference to the controller. Option B provides a wireless link between wired segments. Option D keeps serving clients, which the requirement forbids outright.",
  "difficulty": 1,
  "skills": ["ap-modes", "monitor-mode", "rogue-detection", "read-correct-row"],
},
{
  "id": "2.6-005", "objective": "2.6", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which statement correctly identifies the two units?",
  "exhibit": {"kind": "topology", "content": EX_005},
  "options": opts(
    "Unit A is autonomous and Unit B is lightweight, needing a controller.",
    "Unit B is autonomous, which is why it depends on a controller being reachable.",
    "Both are lightweight; the difference is only which controller software they run.",
    "Unit A is a mesh access point and Unit B is configured for FlexConnect."),
  "correct": ["A"],
  "explanation": "Unit A carries its own full configuration, is administered through its own web page and keeps working with no controller, which describes an autonomous access point. Unit B holds no configuration and will not serve clients without a controller, which is the defining trait of a lightweight one. Option B reverses the two, and depending on a controller is precisely what autonomous means it does not do. Option C denies a difference the table records in four rows. Option D applies deployment modes that the table never mentions.",
  "difficulty": 2,
  "skills": ["wireless-architectures", "autonomous-ap", "lightweight-ap", "compare-deployment-models"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "2" / "2.6.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "2.6",
    "domain": 2,
    "blueprint_version": "v1.1",
    "scope_note": "Architectures and AP modes worked from requirements, not defined.",
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
