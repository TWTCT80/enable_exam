#!/usr/bin/env python3
"""Generate bank/2/2.3.json - 'Configure and verify Layer 2 discovery protocols'.

Uses `show cdp neighbors detail`, `show cdp`, `show lldp` and
`show lldp neighbors`. The summary form of `show cdp neighbors` is deliberately
avoided: its Capability column is not left-justified like the rest of the row
and I could not confirm the exact spacing, so rather than invent a layout the
items use the detail view, which is line-oriented and unambiguous.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import lldp_neighbors, lldp_row, opts  # noqa: E402

SEP = "-" * 58

# --- exhibits -------------------------------------------------------------

EX_001 = """SW1# show cdp neighbors detail
-------------------------
Device ID: R1.example.internal
Entry address(es):
  IP address: 10.1.1.1
Platform: Cisco ISR4331,  Capabilities: Router Switch IGMP
Interface: GigabitEthernet0/1,  Port ID (outgoing port): GigabitEthernet0/0/0
Holdtime : 158 sec

Version :
Cisco IOS Software, ISR Software (X86_64_LINUX_IOSD-UNIVERSALK9-M),
Version 16.9.4, RELEASE SOFTWARE (fc2)

advertisement version: 2
Duplex: full"""

EX_002 = """SW2# show cdp neighbors detail
SW2#
SW2# show cdp
% CDP is not enabled

SW2 is cabled to two Cisco switches that both report SW2 as a CDP
neighbour on their own side."""

EX_003 = "\n".join([
    "SW3# show cdp neighbors detail",
    "-------------------------",
    "Device ID: SW4",
    "Entry address(es):",
    "  IP address: 10.1.1.4",
    "Platform: cisco WS-C2960-24TT-L,  Capabilities: Switch IGMP",
    "Interface: GigabitEthernet0/2,  Port ID (outgoing port): GigabitEthernet0/1",
    "Holdtime : 142 sec",
    "",
    SEP,
    "",
    "GigabitEthernet0/5 connects to a third-party switch from another",
    "vendor. It is up and passing traffic, but no neighbour is ever",
    "reported on that interface. CDP is running globally on SW3 and is",
    "enabled on Gi0/5.",
])

EX_004 = lldp_neighbors("SW4", [
    lldp_row("R2", "Gi0/1", "120", "R", "Gi0/0/0"),
    lldp_row("SW5", "Gi0/2", "120", "B", "Gi0/24"),
    lldp_row("AP-014", "Gi0/9", "120", "B,W", "GigabitEthernet0"),
])

EX_005 = """SW6# show cdp neighbors detail
-------------------------
Device ID: DIST-SW-1
Entry address(es):
  IP address: 10.9.9.2
Platform: cisco WS-C3850-24T,  Capabilities: Switch IGMP
Interface: GigabitEthernet0/24,  Port ID (outgoing port): GigabitEthernet1/0/13
Holdtime : 171 sec

Version :
Cisco IOS Software, IOS-XE Software, Catalyst L3 Switch Software

advertisement version: 2
Duplex: full"""


ITEMS = [
{
  "id": "2.3-001", "objective": "2.3", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which interface on the neighbouring device is this link plugged into?",
  "exhibit": {"kind": "cli_output", "content": EX_001},
  "options": opts("GigabitEthernet0/1", "GigabitEthernet1/0/1", "GigabitEthernet0/0/0",
                  "GigabitEthernet1/0/13"),
  "correct": ["C"],
  "explanation": "The Interface field names the local port and the Port ID field names the far end, so the cable leaves SW1's Gi0/1 and lands on R1's GigabitEthernet0/0/0. Option A is the local interface, which is the commonest misreading of this output because both values sit on the same line. Options B and D are interface names that appear nowhere in the capture, and the three-part numbering of the real answer reflects the router's module layout.",
  "difficulty": 2,
  "skills": ["cdp", "show-cdp-neighbors-detail", "verify-discovery-protocol", "read-correct-row"],
},
{
  "id": "2.3-002", "objective": "2.3", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why does SW2 report no neighbours when its own neighbours can see it?",
  "exhibit": {"kind": "cli_output", "content": EX_002},
  "options": opts(
    "CDP has been switched off globally on SW2 with no cdp run.",
    "SW2's neighbours are advertising CDPv2, which SW2 cannot interpret.",
    "The links to SW2 are trunks, and CDP is exchanged only on access ports.",
    "SW2 needs an IP address on a management interface before CDP will operate."),
  "correct": ["A"],
  "explanation": "The message CDP is not enabled means the global process is off, so SW2 neither sends nor accepts advertisements; its neighbours still list it because they hold entries learned before it stopped, or because the direction is simply one-way. Option B invents a version incompatibility that CDPv2 does not create. Option C is wrong because CDP runs on trunks and access ports alike. Option D adds an addressing requirement CDP does not have, since it works at Layer 2.",
  "difficulty": 2,
  "skills": ["cdp", "cdp-run", "verify-discovery-protocol", "troubleshoot-discovery"],
},
{
  "id": "2.3-003", "objective": "2.3", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What should be enabled so that SW3 can discover the device on Gi0/5?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts(
    "cdp enable on Gi0/5, which must have been switched off for that interface.",
    "cdp timer 30, so advertisements are sent often enough to be seen.",
    "A second CDP process, because one instance serves only Cisco-built neighbours.",
    "LLDP, which is vendor-neutral, using lldp run and lldp transmit and receive."),
  "correct": ["D"],
  "explanation": "CDP is Cisco proprietary, so a switch from another vendor neither sends nor understands it, and the fix is the open standard LLDP: enable it globally with lldp run and allow it on the interface. Option A repeats what the exhibit already rules out, since CDP is stated to be enabled on Gi0/5. Option B changes how often advertisements go out, which cannot help a neighbour that does not speak the protocol. Option C invents a second process; CDP has only one and its limitation is the protocol, not capacity.",
  "difficulty": 3,
  "skills": ["lldp", "cdp", "vendor-neutral-discovery", "configure-discovery-protocol"],
},
{
  "id": "2.3-004", "objective": "2.3", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which neighbour has advertised itself as both a bridge and a wireless access point?",
  "exhibit": {"kind": "cli_output", "content": EX_004},
  "options": opts("SW5", "AP-014", "R2", "None of them advertise two capabilities"),
  "correct": ["B"],
  "explanation": "The capability codes at the top of the output map B to Bridge and W to WLAN Access Point, and only the AP-014 row carries both letters. Option A shows B alone, which is an ordinary switch. Option C shows R for Router. Option D is contradicted by the AP-014 row, and its longer Port ID reflects the access point naming its single uplink in full rather than abbreviating it.",
  "difficulty": 2,
  "skills": ["lldp", "show-lldp-neighbors", "capability-codes", "read-correct-row"],
},
{
  "id": "2.3-005", "objective": "2.3", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which management address has the neighbour advertised to SW6?",
  "exhibit": {"kind": "cli_output", "content": EX_005},
  "options": opts("10.1.1.4", "10.9.9.1", "10.9.9.2", "None; CDP carries no addressing"),
  "correct": ["C"],
  "explanation": "The Entry address section carries whatever address the neighbour advertises for management, and here it reads 10.9.9.2. Option A is an address from a different capture and appears nowhere in this one. Option B assumes the neighbour holds the first address in the subnet, which the output never states. Option D denies that CDP carries addressing at all, yet the Entry address field exists precisely to convey it, which is why CDP is useful for mapping an undocumented network.",
  "difficulty": 1,
  "skills": ["cdp", "show-cdp-neighbors-detail", "management-address", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "2" / "2.3.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "2.3",
    "domain": 2,
    "blueprint_version": "v1.1",
    "scope_note": ("The summary form of show cdp neighbors is avoided: its Capability "
                   "column spacing could not be confirmed, so the detail view is used "
                   "rather than an invented layout."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
