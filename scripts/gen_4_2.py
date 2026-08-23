#!/usr/bin/env python3
"""Generate bank/4/4.2.json - 'Configure and verify NTP operating in a client
and server mode'.

Uses `show ntp status`, which is line-oriented, rather than
`show ntp associations`, whose columns I could not confirm to the character.

003 links this objective to 4.5 on purpose: an unsynchronised clock makes every
syslog timestamp on the device worthless for correlating an incident, which is
the practical reason NTP matters at all.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

EX_001 = """R1# show ntp status
Clock is synchronized, stratum 3, reference is 10.1.1.1
nominal freq is 250.0000 Hz, actual freq is 249.9990 Hz, precision is 2**18
reference time is EB1A2C44.6C2A1E30 (09:14:12.422 UTC Sun Aug 23 2026)
clock offset is 0.4120 msec, root delay is 1.82 msec
root dispersion is 12.11 msec, peer dispersion is 0.92 msec"""

EX_002 = """R2 is to take its time from the public source at 203.0.113.30 and
must not offer itself as a time source to anything else."""

EX_003 = """R3# show ntp status
Clock is unsynchronized, stratum 16, no reference clock
nominal freq is 250.0000 Hz, actual freq is 250.0000 Hz, precision is 2**18
reference time is 00000000.00000000 (00:00:00.000 UTC Mon Jan 1 1900)
clock offset is 0.0000 msec, root delay is 0.00 msec

R3 is forwarding traffic normally and its syslog server is receiving
messages from it without interruption."""

EX_004 = """A site has no reachable external time source. One router with an
accurate hardware clock is to become the reference for the other
devices at that site, which will then take their time from it."""

ITEMS = [
{
  "id": "4.2-001", "objective": "4.2", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. How far is R1 from the authoritative source of this time?",
  "exhibit": {"kind": "cli_output", "content": EX_001},
  "options": opts(
    "It is the authoritative source, which is what stratum 3 records.",
    "One step, since it takes its time directly from 10.1.1.1.",
    "Three steps, which is what a stratum of 3 counts.",
    "Sixteen steps, the value NTP uses when counting from a reference clock."),
  "correct": ["C"],
  "explanation": "Stratum counts distance from the reference clock, so a device reporting stratum 3 sits three steps away, taking its time from a stratum 2 peer which took it from a stratum 1 source attached to the reference itself. Option A describes stratum 1. Option B counts only the hop to its own peer and ignores what lies beyond it, which is what the number exists to record. Option D quotes 16, the value that means unsynchronised rather than a distance.",
  "difficulty": 1,
  "skills": ["ntp", "stratum", "show-ntp-status", "verify-ntp"],
},
{
  "id": "4.2-002", "objective": "4.2", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which command configures R2 as the requirement describes?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "ntp server 203.0.113.30",
    "ntp master 3",
    "ntp peer 203.0.113.30",
    "ntp source 203.0.113.30"),
  "correct": ["A"],
  "explanation": "ntp server names an upstream source to synchronise from and leaves the device a client, which is precisely the requirement. Option B makes the router an authoritative source of its own, which the requirement forbids. Option C establishes a symmetric relationship in which either device may synchronise the other. Option D sets which address the router uses when sending NTP packets and selects no source at all.",
  "difficulty": 2,
  "skills": ["ntp", "ntp-client", "configure-ntp", "ntp-server-command"],
},
{
  "id": "4.2-003", "objective": "4.2", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does this state cost the team, given that traffic and logging both continue?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts(
    "Routing decisions become unreliable, since protocols timestamp their updates.",
    "The syslog timestamps R3 sends cannot be trusted or correlated.",
    "Nothing measurable, because stratum 16 still keeps time to within a second.",
    "SSH sessions will be refused, as key exchange depends on an accurate clock."),
  "correct": ["B"],
  "explanation": "Stratum 16 with no reference means the clock is running free, so every timestamp R3 stamps on a log message is its own guess; the messages arrive but cannot be lined up against events on any other device, which is exactly when an incident timeline is needed. Option A ties routing to timestamps, which the protocols in scope here do not depend on. Option C treats stratum 16 as a working state rather than the marker for unsynchronised. Option D invents a dependency SSH does not have.",
  "difficulty": 3,
  "skills": ["ntp", "unsynchronised-clock", "syslog-correlation", "verify-ntp"],
},
{
  "id": "4.2-004", "objective": "4.2", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which command makes that router the reference for the site?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts(
    "ntp server 127.127.1.1 on each of the other devices",
    "ntp peer, entered on every device including the reference",
    "ntp update-calendar on the router with the accurate clock",
    "ntp master, entered on the router with the accurate clock"),
  "correct": ["D"],
  "explanation": "ntp master tells a router to declare itself an authoritative time source using its own clock, which is what an isolated site needs when no external source is reachable; the other devices then point at it with ntp server. Option A has each device treat its own internal clock as the source, so nothing is shared. Option B builds symmetric relationships with no agreed reference. Option C copies NTP time into the hardware calendar, which assumes synchronisation rather than establishing it.",
  "difficulty": 2,
  "skills": ["ntp", "ntp-master", "ntp-server-mode", "configure-ntp"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "4" / "4.2.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "4.2", "domain": 4, "blueprint_version": "v1.1",
    "scope_note": ("show ntp status is used rather than show ntp associations, whose "
                   "column layout could not be confirmed."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
