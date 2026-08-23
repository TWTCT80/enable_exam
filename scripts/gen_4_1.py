#!/usr/bin/env python3
"""Generate bank/4/4.1.json - 'Configure and verify inside source NAT using
static and pools'.

Configure-and-verify, and the largest objective in domain 4.

Three faults carry it, and none of them produce an error message: the interface
roles are never declared (002), the pool runs out because no overload keyword
was given (003), and the access list covers a different range from the one that
needs translating (005). In each case the configuration reads as though it
should work.
"""
import ipaddress
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import nat_translations, nat_row, opts  # noqa: E402


def _selftest():
    pool = list(ipaddress.summarize_address_range(
        ipaddress.ip_address("203.0.113.9"), ipaddress.ip_address("203.0.113.14")))
    assert sum(n.num_addresses for n in pool) == 6, pool
    # item 005: the access list covers 10.1.1.0/24 but the failing hosts are in
    # 10.1.2.0/24, which it does not reach
    acl = ipaddress.ip_network("10.1.1.0/24")
    assert ipaddress.ip_address("10.1.1.50") in acl
    assert ipaddress.ip_address("10.1.2.40") not in acl


_selftest()

# --- exhibits -------------------------------------------------------------

EX_001 = nat_translations("R1", [
    nat_row("tcp", "203.0.113.5:1024", "10.1.1.50:49152",
            "198.51.100.20:80", "198.51.100.20:80"),
    nat_row("tcp", "203.0.113.9:1030", "10.1.1.77:51204",
            "198.51.100.44:443", "198.51.100.44:443"),
    nat_row("---", "203.0.113.5", "10.1.1.50", "---", "---"),
])

EX_002 = """! R2 - relevant configuration
!
ip nat inside source list 1 pool NAT-POOL overload
ip nat pool NAT-POOL 203.0.113.9 203.0.113.14 netmask 255.255.255.248
access-list 1 permit 10.1.1.0 0.0.0.255
!
interface GigabitEthernet0/1
 description inside LAN
 ip address 10.1.1.1 255.255.255.0
!
interface GigabitEthernet0/0
 description toward the ISP
 ip address 203.0.113.2 255.255.255.252
!

Hosts on 10.1.1.0/24 reach the ISP router but nothing beyond it. R2's
translation table is empty."""

EX_003 = """! R3 - relevant configuration
!
ip nat pool NAT-POOL 203.0.113.9 203.0.113.14 netmask 255.255.255.248
ip nat inside source list 1 pool NAT-POOL
access-list 1 permit 10.3.3.0 0.0.0.255
!
interface GigabitEthernet0/1
 ip address 10.3.3.1 255.255.255.0
 ip nat inside
!
interface GigabitEthernet0/0
 ip address 203.0.113.2 255.255.255.252
 ip nat outside
!

The subnet holds around forty active workstations. Each morning the
first few users reach the internet without trouble; the rest are
unable to, until someone else's session ends."""

EX_004 = """A web server sits on the inside network at 10.9.9.20 and must be
reachable from the internet at the fixed public address 203.0.113.20.

The mapping must hold whether or not the server has traffic in flight,
so that inbound connections can find it at any time."""

EX_005 = """! R5 - relevant configuration
!
ip nat inside source list 7 pool NAT-POOL overload
ip nat pool NAT-POOL 203.0.113.9 203.0.113.14 netmask 255.255.255.248
access-list 7 permit 10.1.1.0 0.0.0.255
!
interface GigabitEthernet0/1
 ip address 10.1.1.1 255.255.255.0
 ip nat inside
!
interface GigabitEthernet0/2
 ip address 10.1.2.1 255.255.255.0
 ip nat inside
!
interface GigabitEthernet0/0
 ip address 203.0.113.2 255.255.255.252
 ip nat outside
!

Hosts on 10.1.1.0/24 reach the internet. Hosts on 10.1.2.0/24 do not,
though they route to R5 correctly and R5 has a default route."""

EX_006 = """R6# show ip nat statistics
Total active translations: 4 (1 static, 3 dynamic; 3 extended)
Peak translations: 61, occurred 00:22:14 ago
Outside interfaces:
  GigabitEthernet0/0
Inside interfaces:
  GigabitEthernet0/1
Hits: 91744  Misses: 0
Expired translations: 57
Dynamic mappings:
-- Inside Source
[Id: 1] access-list 7 pool NAT-POOL refcount 3
 pool NAT-POOL: netmask 255.255.255.248
    start 203.0.113.9 end 203.0.113.14
    type generic, total addresses 6, allocated 6 (100%), misses 214"""


ITEMS = [
{
  "id": "4.1-001", "objective": "4.1", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which public address has been given to the host at 10.1.1.77?",
  "exhibit": {"kind": "cli_output", "content": EX_001},
  "options": opts("203.0.113.5", "203.0.113.9", "198.51.100.44", "10.1.1.50"),
  "correct": ["B"],
  "explanation": "The Inside local column carries the private address and the Inside global column the public one it is presented as, so the row for 10.1.1.77 shows 203.0.113.9. Option A belongs to 10.1.1.50, the row above, which is the classic wrong-row read. Option C is an Outside global address, meaning the server being contacted rather than anything on the inside. Option D is an inside local address and never appears on the internet at all.",
  "difficulty": 1,
  "skills": ["nat", "show-ip-nat-translations", "inside-global", "read-correct-row"],
},
{
  "id": "4.1-002", "objective": "4.1", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why does R2 translate nothing at all?",
  "exhibit": {"kind": "config", "content": EX_002},
  "options": opts(
    "The pool is too small for the number of hosts on the inside subnet.",
    "The access list should permit the outside subnet rather than the inside one.",
    "The overload keyword prevents a pool being used for inside source NAT.",
    "Neither interface is marked ip nat inside or ip nat outside."),
  "correct": ["D"],
  "explanation": "NAT only acts on traffic crossing between an interface declared inside and one declared outside, and neither declaration is present, so the pool and access list are never consulted and the table stays empty. Option A would show translations succeeding until the pool ran out rather than none at all, and overload makes six addresses ample. Option B reverses which side the list describes. Option C is wrong because overload with a pool is the ordinary way to share a small range.",
  "difficulty": 2,
  "skills": ["nat", "ip-nat-inside-outside", "configure-nat", "troubleshoot-nat"],
},
{
  "id": "4.1-003", "objective": "4.1", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What explains the pattern the users are reporting?",
  "exhibit": {"kind": "config", "content": EX_003},
  "options": opts(
    "Without overload, the pool gives one address per host and holds only six.",
    "The access list permits a /24, which is wider than the pool can support.",
    "The pool's netmask is wrong, so only the first few addresses are usable.",
    "The inside and outside interfaces have been declared the wrong way round."),
  "correct": ["A"],
  "explanation": "A pool without the overload keyword hands each inside host its own public address for the life of its translation, and this pool holds six, so the seventh user onward is refused until an earlier translation expires. Adding overload lets all forty share the pool by port. Option B blames the access list, which correctly names the subnet to translate. Option C misreads the netmask, which describes the pool addresses rather than limiting how many are handed out. Option D is contradicted by the interface declarations, which are correct.",
  "difficulty": 3,
  "skills": ["nat", "nat-pool", "overload", "troubleshoot-nat"],
},
{
  "id": "4.1-004", "objective": "4.1", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which command creates the mapping the requirement describes?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts(
    "ip nat inside source list 1 pool WEB overload",
    "ip nat outside source static 203.0.113.20 10.9.9.20",
    "ip nat inside source static 10.9.9.20 203.0.113.20",
    "ip nat pool WEB 203.0.113.20 203.0.113.20 netmask 255.255.255.255"),
  "correct": ["C"],
  "explanation": "A static inside source entry ties one inside local address to one inside global address permanently, which is what lets an inbound connection find the server without the server having spoken first. Option A builds a dynamic mapping, so no entry exists until the server originates traffic. Option B translates in the outside source direction, which rewrites addresses on the far side rather than presenting an inside host publicly. Option D defines a pool without any command referring to it.",
  "difficulty": 2,
  "skills": ["nat", "static-nat", "configure-nat", "inbound-reachability"],
},
{
  "id": "4.1-005", "objective": "4.1", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why do only the hosts on one of the two inside subnets reach the internet?",
  "exhibit": {"kind": "config", "content": EX_005},
  "options": opts(
    "GigabitEthernet0/2 is missing the ip nat inside declaration.",
    "Access list 7 permits 10.1.1.0/24 only, so 10.1.2.0/24 is untranslated.",
    "A router supports one inside interface per NAT configuration.",
    "The pool has to be widened considerably before a second subnet can be translated."),
  "correct": ["B"],
  "explanation": "The access list decides which traffic NAT acts on, and list 7 names 10.1.1.0/24 alone, so packets from 10.1.2.0/24 pass through untranslated and their private source address is dropped upstream. Adding a line for the second subnet resolves it. Option A is contradicted by Gi0/2 carrying the declaration already. Option C invents a one-interface limit. Option D points at the pool, which overload makes ample for both subnets.",
  "difficulty": 2,
  "skills": ["nat", "nat-acl", "configure-nat", "troubleshoot-nat"],
},
{
  "id": "4.1-006", "objective": "4.1", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What do the pool figures at the foot of this output indicate?",
  "exhibit": {"kind": "cli_output", "content": EX_006},
  "options": opts(
    "The pool is healthy, since the hit counter is high and misses read zero.",
    "Six translations have expired, which is why the pool shows fully allocated.",
    "The static entry has consumed the pool, leaving nothing for dynamic use.",
    "The pool is fully allocated, and 214 attempts have found no address free."),
  "correct": ["D"],
  "explanation": "The pool line reads allocated 6 of 6 at 100 per cent with 214 misses, meaning every address is in use and that many translation attempts have been turned away, so the pool needs widening or an overload keyword. Option A quotes the Hits and Misses counters higher up, which describe packets matching existing translations rather than the pool's capacity. Option B misreads the expired count, which is a lifetime total. Option C blames the static entry, which is counted separately from the dynamic pool.",
  "difficulty": 3,
  "skills": ["nat", "show-ip-nat-statistics", "pool-exhaustion", "verify-nat"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "4" / "4.1.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "4.1",
    "domain": 4,
    "blueprint_version": "v1.1",
    "scope_note": ("Three silent faults: undeclared interface roles, a pool without "
                   "overload, and an access list covering the wrong subnet. None "
                   "produce an error message."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items, pool arithmetic asserted)")
