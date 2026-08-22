#!/usr/bin/env python3
"""Generate bank/1/1.10.json - 'Verify IP parameters for Client OS'.

The objective names Windows, macOS and Linux, so all three appear here in their
own native output rather than a Cisco-flavoured paraphrase: ipconfig /all,
ifconfig with its hexadecimal netmask, and ip addr / ip route.
"""
import ipaddress
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402


def _selftest():
    # macOS prints the mask in hex; item 002 turns on converting it
    assert ipaddress.IPv4Address(0xFFFFE000).compressed == "255.255.224.0"
    net = ipaddress.ip_network("10.44.130.55/19", strict=False)
    assert str(net) == "10.44.128.0/19"
    assert str(net.broadcast_address) == "10.44.159.255"
    # APIPA
    assert ipaddress.ip_address("169.254.44.17") in ipaddress.ip_network("169.254.0.0/16")
    # item 004's Linux prefix
    assert str(ipaddress.ip_network("172.20.14.55/26", strict=False)) == "172.20.14.0/26"


_selftest()

# --- exhibits -------------------------------------------------------------

EX_001 = r"""C:\> ipconfig /all

Windows IP Configuration

   Host Name . . . . . . . . . . . . : WKS-104
   Primary Dns Suffix  . . . . . . . : example.internal
   IP Routing Enabled. . . . . . . . : No

Ethernet adapter Ethernet:

   Description . . . . . . . . . . . : Intel(R) Ethernet Connection I219-LM
   Physical Address. . . . . . . . . : 00-1A-2B-3C-4D-5E
   DHCP Enabled. . . . . . . . . . . : Yes
   Autoconfiguration Enabled . . . . : Yes
   Autoconfiguration IPv4 Address. . : 169.254.44.17(Preferred)
   Subnet Mask . . . . . . . . . . . : 255.255.0.0
   Default Gateway . . . . . . . . . :
   DNS Servers . . . . . . . . . . . :

Other workstations on the same switch are working normally."""

EX_002 = """MacBook:~ user$ ifconfig en0
en0: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500
        options=400<CHANNEL_IO>
        ether 3c:22:fb:1a:2b:3c
        inet6 fe80::1c2f:8a3b:4d5e:6f70%en0 prefixlen 64 secured scopeid 0xb
        inet 10.44.130.55 netmask 0xffffe000 broadcast 10.44.159.255
        nd6 options=201<PERFORMNUD,DAD>
        media: autoselect
        status: active"""

EX_003 = """user@host:~$ ip addr show ens192
2: ens192: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:0c:29:ab:cd:ef brd ff:ff:ff:ff:ff:ff
    inet 172.20.14.55/26 brd 172.20.14.63 scope global ens192
       valid_lft forever preferred_lft forever

user@host:~$ ip route
172.20.14.0/26 dev ens192 proto kernel scope link src 172.20.14.55 metric 100

The host reaches 172.20.14.60 by address without trouble, but every
address outside 172.20.14.0/26 times out."""

EX_004 = """user@host:~$ ip addr show ens160
3: ens160: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:50:56:9a:33:c1 brd ff:ff:ff:ff:ff:ff
    inet 192.168.118.37/28 brd 192.168.118.47 scope global ens160
       valid_lft forever preferred_lft forever
    inet6 fe80::250:56ff:fe9a:33c1/64 scope link
       valid_lft forever preferred_lft forever"""


ITEMS = [
{
  "id": "1.10-001", "objective": "1.10", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does this workstation's addressing indicate has happened?",
  "exhibit": {"kind": "cli_output", "content": EX_001},
  "options": opts(
    "The workstation has been assigned a valid address from a DHCP scope.",
    "No DHCP server answered, so Windows assigned a link-local address itself.",
    "An administrator configured the address statically and omitted the gateway.",
    "The network adapter has been disabled and holds a placeholder address."),
  "correct": ["B"],
  "explanation": "The 169.254.0.0/16 range with a 255.255.0.0 mask and no gateway or DNS entries is what Windows assigns itself when DHCP goes unanswered, and the output labels it Autoconfiguration IPv4 Address rather than IPv4 Address. Option A is contradicted by that label and by the empty gateway field. Option C is ruled out because DHCP Enabled reads Yes, so the address was not entered by hand. Option D would leave the adapter reporting media disconnected rather than an address at all.",
  "difficulty": 2,
  "skills": ["verify-ip-parameters", "windows-ipconfig", "apipa", "dhcp-failure"],
},
{
  "id": "1.10-002", "objective": "1.10", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which subnet is this Mac attached to?",
  "exhibit": {"kind": "cli_output", "content": EX_002},
  "options": opts("10.44.130.0/24", "10.44.0.0/16", "10.44.128.0/19", "10.44.130.0/19"),
  "correct": ["C"],
  "explanation": "macOS prints the mask in hexadecimal, and 0xffffe000 expands to 255.255.224.0, a /19 whose blocks step by 32 in the third octet; 130 falls in the block beginning at 128, which the broadcast address of 10.44.159.255 confirms. Option A assumes a /24 and takes the host's own third octet as the network. Option B applies the classful /16 for the 10.0.0.0 range and ignores the mask entirely. Option D pairs the correct prefix length with an address that is not on a /19 boundary.",
  "difficulty": 3,
  "skills": ["verify-ip-parameters", "macos-ifconfig", "hexadecimal-netmask", "subnet-boundary"],
},
{
  "id": "1.10-003", "objective": "1.10", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why can this Linux host reach its own subnet but nothing outside it?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts(
    "The routing table holds no default route, so off-subnet traffic has nowhere to go.",
    "The interface is administratively down and cannot forward beyond the link.",
    "The /26 prefix is too small to permit traffic to leave the local segment.",
    "No DNS server has been configured, so remote destinations cannot be resolved by name."),
  "correct": ["A"],
  "explanation": "The routing table lists only the connected 172.20.14.0/26 entry, with no default via line, so the kernel has nowhere to send anything that does not match that prefix. Option B is contradicted by the interface state, which reads UP,LOWER_UP with an address bound. Option C invents a prefix length that blocks routing; a /26 routes off-subnet as readily as any other. Option D is ruled out because the failures happen when addressing destinations numerically, which never involves DNS.",
  "difficulty": 2,
  "skills": ["verify-ip-parameters", "linux-ip-route", "default-gateway", "troubleshoot-connectivity"],
},
{
  "id": "1.10-004", "objective": "1.10", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. How many addresses on this host's subnet can be assigned to devices?",
  "exhibit": {"kind": "cli_output", "content": EX_004},
  "options": opts("16", "30", "62", "14"),
  "correct": ["D"],
  "explanation": "The inet line reads /28, which leaves four host bits and therefore sixteen addresses in the block, of which the network address and the broadcast at 192.168.118.47 are unusable, leaving fourteen for devices. Option A counts every address in the block and forgets to deduct the two reserved ones. Option B is the figure for a /27 and comes from misreading the prefix by one bit. Option C is the figure for a /26, two bits out.",
  "difficulty": 1,
  "skills": ["verify-ip-parameters", "linux-ip-addr", "usable-host-range", "prefix-length"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "1" / "1.10.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "1.10",
    "domain": 1,
    "blueprint_version": "v1.1",
    "scope_note": ("All three client operating systems named in the objective appear "
                   "in their own native output. Mask conversions are checked with the "
                   "ipaddress module in _selftest()."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items, mask self-test passed)")
