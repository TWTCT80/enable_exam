#!/usr/bin/env python3
"""Generate bank/4/4.6.json - 'Configure and verify DHCP client and relay'.

Both halves the objective names: the router as a DHCP client on its own
interface, and the router as a relay for clients on a subnet the server cannot
hear. 001 turns on why a relay is needed at all - DISCOVER is a broadcast, and
a router does not forward broadcasts.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import ip_int_brief, ipint, opts  # noqa: E402

EX_001 = """                VLAN 30                      VLAN 99
    clients ---[ SW-L3 ]------------------------[ DHCP-SRV ]
              10.30.0.1                          10.99.0.10

The DHCP server holds a scope for 10.30.0.0/24. Clients on VLAN 30 send
their requests and receive nothing. A workstation moved onto VLAN 99
obtains an address from the same server immediately."""

EX_002 = """! SW-L3 - relevant configuration
!
interface Vlan30
 description client VLAN
 ip address 10.30.0.1 255.255.255.0
!
interface Vlan99
 description server VLAN
 ip address 10.99.0.1 255.255.255.0
!

The DHCP server at 10.99.0.10 must serve clients in VLAN 30."""

EX_003 = """! R3 - relevant configuration
!
interface GigabitEthernet0/0
 description circuit to the service provider
 no shutdown
!

The provider issues this circuit's address by DHCP and will not supply a
static allocation. R3 must take whatever address the provider offers,
including the default route that comes with it."""

EX_004 = ip_int_brief("R4", [
    ipint("GigabitEthernet0/0", "198.51.100.37", "YES", "DHCP", "up", "up"),
    ipint("GigabitEthernet0/1", "10.4.4.1", "YES", "manual", "up", "up"),
    ipint("GigabitEthernet0/2", "unassigned", "YES", "unset",
          "administratively down", "down"),
])

ITEMS = [
{
  "id": "4.6-001", "objective": "4.6", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why does the same server answer one VLAN and not the other?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "A DHCP request is a broadcast and does not leave VLAN 30.",
    "The scope for 10.30.0.0/24 must be defined on the VLAN 30 interface itself.",
    "DHCP works only where the server and the client share an IP subnet by design.",
    "The clients need a static address before they can request a dynamic one."),
  "correct": ["A"],
  "explanation": "A client with no address starts by broadcasting, and a broadcast stops at the boundary of its own VLAN, so a server one subnet away never hears it; the workstation moved onto VLAN 99 succeeds because it is then in the same broadcast domain. A relay configured with ip helper-address forwards the request as a unicast. Option B misplaces the scope, which lives on the server. Option C states a limitation that relays exist to remove. Option D reverses the process entirely.",
  "difficulty": 3,
  "skills": ["dhcp-relay", "broadcast-domain", "dhcp-discover", "troubleshoot-dhcp"],
},
{
  "id": "4.6-002", "objective": "4.6", "domain": 4, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Which two facts describe the helper address this design needs? (Choose two.)",
  "exhibit": {"kind": "config", "content": EX_002},
  "options": opts(
    "It belongs on interface Vlan99, where the server sits.",
    "It belongs on interface Vlan30, where the clients broadcast.",
    "Its value is 10.30.0.1, the gateway the clients already use.",
    "Its value is 10.99.0.10, the address of the DHCP server.",
    "It must be applied on both interfaces so each direction works."),
  "correct": ["B", "D"],
  "explanation": "The helper address goes on the interface that receives the clients' broadcasts, which is Vlan30, and names where those requests should be forwarded, which is the server at 10.99.0.10. Option A places it on the server side, where no client broadcast ever arrives. Option C points the relay back at the router's own address. Option E adds a statement on an interface with nothing to relay, which would forward the server's own broadcasts toward the clients.",
  "difficulty": 2,
  "skills": ["dhcp-relay", "ip-helper-address", "configure-dhcp-relay", "svi"],
},
{
  "id": "4.6-003", "objective": "4.6", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which command lets R3 accept whatever address the provider offers?",
  "exhibit": {"kind": "config", "content": EX_003},
  "options": opts(
    "ip helper-address from the provider's first-hop router",
    "ip address dhcp",
    "ip address negotiated 198.51.100.0 255.255.255.0",
    "ip dhcp pool WAN followed by a network statement"),
  "correct": ["B"],
  "explanation": "ip address dhcp puts the interface into client mode, so it requests an address from the provider and installs the default route that accompanies the lease, which is exactly what the circuit requires. Option A configures a relay, which forwards other devices' requests rather than making a request of its own. Option C invents a command; negotiation of this kind is not how IOS expresses it. Option D turns the router into a DHCP server handing out addresses, which is the opposite role.",
  "difficulty": 2,
  "skills": ["dhcp-client", "ip-address-dhcp", "configure-dhcp-client", "default-route"],
},
{
  "id": "4.6-004", "objective": "4.6", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which interface obtained its address from a DHCP server?",
  "exhibit": {"kind": "cli_output", "content": EX_004},
  "options": opts("GigabitEthernet0/1", "GigabitEthernet0/2", "Neither of the two up interfaces",
                  "GigabitEthernet0/0"),
  "correct": ["D"],
  "explanation": "The Method column records how each address arrived, and Gi0/0 reads DHCP while carrying a live address. Option A reads manual, meaning an operator typed the address into the configuration. Option B is unassigned and administratively down, so it has requested nothing. Option C is contradicted by the DHCP entry on Gi0/0, and the Method column exists precisely so this distinction is visible without reading the configuration.",
  "difficulty": 1,
  "skills": ["dhcp-client", "verify-dhcp-client", "show-ip-interface-brief", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "4" / "4.6.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "4.6", "domain": 4, "blueprint_version": "v1.1",
    "scope_note": "Both halves: the router as DHCP client, and the router as relay.",
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
