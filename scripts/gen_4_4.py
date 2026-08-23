#!/usr/bin/env python3
"""Generate bank/4/4.4.json - 'Explain the function of SNMP in network operations'.

Polling against traps, and why version 3 exists. No OID syntax and no port
numbers: neither is what the objective asks for at this level.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

EX_001 = """Two ways of learning that an interface has failed

    Method A   The management station asks each device every five
               minutes whether its interfaces are up, and compares
               the answer with the previous one

    Method B   The device sends a message to the management station
               the moment the interface changes state, without being
               asked"""

EX_002 = """! R2 - relevant configuration
!
snmp-server community publicRO RO
snmp-server community privateRW RW
snmp-server host 10.9.9.50 version 2c publicRO
!

An audit has flagged this configuration. The management traffic crosses
a shared campus network on its way to 10.9.9.50."""

EX_003 = """Monitoring requirements for a new deployment

    Requirement
    ---------------------------------------------------------------
    Management traffic must be unreadable to anyone capturing it
    The identity of the management station must be verifiable
    Individual accounts, not one shared string for the whole estate"""

ITEMS = [
{
  "id": "4.4-001", "objective": "4.4", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which description correctly names the two methods?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "A is a trap and B is polling, since the device answers each request.",
    "Both are polling, differing only in how often the station asks.",
    "Both are traps, because each ends with the station learning of the fault.",
    "A is polling and B is a trap, sent by the device on its own initiative."),
  "correct": ["D"],
  "explanation": "Polling has the manager ask on a schedule and wait for an answer, which is method A, while a trap is sent by the agent the moment something happens, which is method B; the practical difference is that a trap arrives at once whereas polling can leave a fault unnoticed for most of an interval. Option A reverses the two. Option B ignores that method B involves no request. Option C calls both traps by looking at the outcome rather than what initiates the message.",
  "difficulty": 2,
  "skills": ["snmp", "polling", "traps", "network-monitoring"],
},
{
  "id": "4.4-002", "objective": "4.4", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What is the audit most likely to have objected to?",
  "exhibit": {"kind": "config", "content": EX_002},
  "options": opts(
    "Version 2c sends its community strings in clear, including the writable one.",
    "Two communities are configured where SNMP permits only one per device.",
    "The host statement names a single station, so no redundancy exists.",
    "Read-only access is inadequate for monitoring and should be writable."),
  "correct": ["A"],
  "explanation": "Under version 2c the community string is the whole of the authentication and travels unencrypted, so anyone capturing the traffic reads it, and a read-write string in that position lets them change the device rather than merely observe it. Version 3 with authentication and privacy is the answer. Option B invents a limit on communities. Option C raises availability rather than the security concern an audit would flag. Option D argues for wider access, which is the opposite of hardening.",
  "difficulty": 2,
  "skills": ["snmp", "snmpv2c", "community-strings", "device-hardening"],
},
{
  "id": "4.4-003", "objective": "4.4", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which SNMP version satisfies all three requirements?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts("Version 1", "Version 3", "Version 2c", "No version offers all three"),
  "correct": ["B"],
  "explanation": "Version 3 adds authentication and privacy on a per-user basis, so the traffic is encrypted, the sender can be verified, and each operator holds their own credential rather than sharing a string. Options A and C both authenticate with a community string sent in clear, which fails the first two requirements and offers no notion of an individual account. Option D is contradicted by version 3 being designed for exactly this set of concerns.",
  "difficulty": 1,
  "skills": ["snmp", "snmpv3", "authentication", "encryption"],
},
]
dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "4" / "4.4.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({"objective": "4.4", "domain": 4,
    "blueprint_version": "v1.1",
    "scope_note": "No OID syntax and no port numbers; neither is what this objective asks.",
    "items": ITEMS}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
