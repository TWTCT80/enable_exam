#!/usr/bin/env python3
"""Generate bank/4/4.3.json - 'Explain the role of DHCP and DNS'.

Separated by what fails when each is missing. APIPA is deliberately absent: it
already carries 1.10-001, and repeating it here would be the same item twice.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

EX_001 = r"""C:\> ping 10.9.9.20

Pinging 10.9.9.20 with 32 bytes of data:
Reply from 10.9.9.20: bytes=32 time=2ms TTL=126
Reply from 10.9.9.20: bytes=32 time=1ms TTL=126

C:\> ping files.example.internal
Ping request could not find host files.example.internal. Please check
the name and try again.

The workstation holds a valid address, mask and default gateway, and
10.9.9.20 is the host registered as files.example.internal."""

EX_002 = """A new subnet is being brought into service. The team wants every
workstation on it to receive, without anyone visiting a desk:

    an address from the correct range
    the subnet mask for that range
    the address of the gateway to leave the subnet
    the addresses of the two name servers"""

EX_003 = r"""C:\> ipconfig /all

Ethernet adapter Ethernet:

   DHCP Enabled. . . . . . . . . . . : Yes
   IPv4 Address. . . . . . . . . . . : 10.20.30.44(Preferred)
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Lease Obtained. . . . . . . . . . : Sunday, 23 August 2026 08:14:02
   Default Gateway . . . . . . . . . : 10.20.30.1
   DHCP Server . . . . . . . . . . . : 10.20.30.10
   DNS Servers . . . . . . . . . . . : 10.20.30.10
                                       10.20.30.11"""

ITEMS = [
{
  "id": "4.3-001", "objective": "4.3", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which service is at fault here?",
  "exhibit": {"kind": "cli_output", "content": EX_001},
  "options": opts(
    "DHCP, since the workstation must have been issued incorrect parameters.",
    "Routing, because the reply to the name-based attempt never came back.",
    "DNS, as the address is reachable but the name cannot be resolved to it.",
    "Neither; the server is refusing requests that arrive by name only."),
  "correct": ["C"],
  "explanation": "The numeric ping succeeds, which proves addressing, routing and the server itself are all working, and the failure message says the name could not be found rather than that the host did not answer, so resolution is the only step that broke. Option A is contradicted by the working ping, which needs a correct address, mask and gateway. Option B is ruled out by the same reply. Option D invents a server behaviour, and the request never reached the server at all.",
  "difficulty": 2,
  "skills": ["dns", "dhcp", "name-resolution", "troubleshoot-connectivity"],
},
{
  "id": "4.3-002", "objective": "4.3", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which service delivers all four of those items to a workstation?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "DNS, which returns the addressing a client needs along with names.",
    "DHCP, which supplies the address together with the other parameters.",
    "ARP, which discovers each of these values from the local segment.",
    "DHCP for the address, with the remaining three set by hand on each host."),
  "correct": ["B"],
  "explanation": "A DHCP offer carries the address and the options alongside it, so mask, gateway and name servers arrive in the same exchange, which is what makes bringing a subnet into service a matter of configuring one scope. Option A gives DNS a role it does not have, since it maps names to addresses. Option C describes ARP, which resolves an address to a MAC within one segment. Option D splits the work unnecessarily and would need the desk visits the requirement rules out.",
  "difficulty": 2,
  "skills": ["dhcp", "dhcp-options", "default-gateway", "dns"],
},
{
  "id": "4.3-003", "objective": "4.3", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which address would this host contact to turn a hostname into an address?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts("10.20.30.10", "10.20.30.1", "10.20.30.44", "255.255.255.0"),
  "correct": ["A"],
  "explanation": "The DNS Servers line names 10.20.30.10 first, and that is where a name lookup goes; the same host also happens to run DHCP, which is common but incidental. Option B is the default gateway, used to leave the subnet rather than to resolve names. Option C is the workstation's own address. Option D is the subnet mask, which is not an address the host contacts at all.",
  "difficulty": 1,
  "skills": ["dns", "verify-ip-parameters", "dhcp", "read-correct-row"],
},
]
dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "4" / "4.3.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({"objective": "4.3", "domain": 4,
    "blueprint_version": "v1.1",
    "scope_note": "APIPA is left to 1.10-001 rather than repeated here.",
    "items": ITEMS}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
