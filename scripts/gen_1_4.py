#!/usr/bin/env python3
"""Generate bank/1/1.4.json - 'Identify interface and cable issues'.

The objective names collisions, errors, duplex and speed mismatch, and the
useful distinction between them is what the counters look like:

  duplex mismatch -> link comes UP, late collisions on the half-duplex end,
                     CRC/input errors on the full-duplex end
  speed  mismatch -> link never comes up at all
  bad cable / EMI -> CRC and input errors with no collisions on either end

Items 001, 002 and 005 are built around exactly those three signatures.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import interfaces_status, intf_status, opts  # noqa: E402


def counters(prompt, intf, line1, duplex_speed, *, runts=0, giants=0,
             in_err=0, crc=0, collisions=0, late=0, resets=0, mac="00d0.5842.1c01",
             pkts_in=418271, pkts_out=512394):
    """A `show interfaces <name>` capture, trimmed to the lines that matter."""
    return "\n".join([
        f"{prompt}# show interfaces {intf}",
        f"{intf} is {line1}",
        f"  Hardware is Gigabit Ethernet, address is {mac} (bia {mac})",
        "  MTU 1500 bytes, BW 100000 Kbit/sec, DLY 100 usec,",
        "     reliability 255/255, txload 1/255, rxload 1/255",
        "  Encapsulation ARPA, loopback not set",
        "  Keepalive set (10 sec)",
        f"  {duplex_speed}, media type is 10/100/1000BaseTX",
        "  ARP type: ARPA, ARP Timeout 04:00:00",
        f"     {pkts_in} packets input, 52194883 bytes, 0 no buffer",
        f"     {runts} runts, {giants} giants, 0 throttles",
        f"     {in_err} input errors, {crc} CRC, 0 frame, 0 overrun, 0 ignored",
        f"     {pkts_out} packets output, 71029338 bytes, 0 underruns",
        f"     0 output errors, {collisions} collisions, {resets} interface resets",
        f"     0 babbles, {late} late collision, 0 deferred",
    ])


SEP = "-" * 58

# --- exhibits -------------------------------------------------------------

EX_001 = "\n".join([
    counters("SW1", "GigabitEthernet0/1", "up, line protocol is up (connected)",
             "Full-duplex, 100Mb/s", in_err=1043, crc=1043, mac="00d0.5842.1c01"),
    SEP,
    counters("SW2", "GigabitEthernet0/1", "up, line protocol is up (connected)",
             "Half-duplex, 100Mb/s", collisions=8873, late=2214,
             mac="00d0.5842.7f22", pkts_in=318442, pkts_out=444120),
])

EX_002 = "\n".join([
    counters("SW3", "GigabitEthernet0/5", "up, line protocol is up (connected)",
             "Full-duplex, 1000Mb/s", runts=214, in_err=3391, crc=3391,
             mac="00d0.5842.9a04"),
    SEP,
    counters("SW4", "GigabitEthernet0/5", "up, line protocol is up (connected)",
             "Full-duplex, 1000Mb/s", runts=198, in_err=2904, crc=2904,
             mac="00d0.5842.b117", pkts_in=290155, pkts_out=377401),
])

EX_003 = interfaces_status("SW5", [
    intf_status("Gi0/1", "uplink to core", "connected", "1", "a-full", "a-1000"),
    intf_status("Gi0/2", "reception PC", "connected", "10", "a-full", "a-100"),
    intf_status("Gi0/3", "meeting room", "notconnect", "10", "auto", "auto"),
    intf_status("Gi0/4", "printer", "connected", "20", "a-half", "a-10"),
])

EX_004 = "\n".join([
    counters("SW6", "GigabitEthernet0/7", "down, line protocol is down (notconnect)",
             "Auto-duplex, Auto-speed", mac="00d0.5842.c201",
             pkts_in=0, pkts_out=0),
    "",
    "The port is not shut down in the running configuration, and the same",
    "patch lead works when moved to a neighbouring port.",
])

EX_005 = """! Two switches joined by a single copper run
!
SW7  interface GigabitEthernet0/1
      speed 100
      duplex full
!
SW8  interface GigabitEthernet0/1
      speed 1000
      duplex full
!

Both ports were previously left at their defaults and the link worked."""


ITEMS = [
{
  "id": "1.4-001", "objective": "1.4", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Users across this link report slow transfers. What do the counters on the two ends point to?",
  "exhibit": {"kind": "cli_output", "content": EX_001},
  "options": opts(
    "A duplex mismatch between the two ends of the link.",
    "A speed mismatch that is forcing repeated renegotiation.",
    "A faulty cable introducing interference along its length.",
    "Congestion, because the link is saturated in both directions."),
  "correct": ["A"],
  "explanation": "SW2 is half-duplex while SW1 is full-duplex, and that pairing produces exactly this signature: the half-duplex end logs late collisions because the far end transmits whenever it likes, while the full-duplex end records CRC errors from frames SW2 truncated when it backed off. Option B is wrong because both ends agree at 100Mb/s and a speed mismatch would leave the link down rather than up. Option C would show errors on both ends without any collisions at all. Option D is ruled out because collisions and CRC errors are faults, not the queueing that congestion produces.",
  "difficulty": 3,
  "skills": ["duplex-mismatch", "late-collisions", "interface-counters", "troubleshoot-physical"],
},
{
  "id": "1.4-002", "objective": "1.4", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Both ends agree on speed and duplex, yet the link is dropping traffic. What do these counters indicate?",
  "exhibit": {"kind": "cli_output", "content": EX_002},
  "options": opts(
    "A duplex mismatch that autonegotiation has failed to resolve.",
    "One of the two switches is running an incompatible software version.",
    "The VLAN configuration differs between the two switch ports.",
    "A physical fault on the cable run, such as damage or interference."),
  "correct": ["D"],
  "explanation": "Both ends report Full-duplex at 1000Mb/s, so negotiation succeeded, yet each is receiving runts and CRC errors while logging no collisions whatsoever. Frames arriving damaged in both directions with no collisions point at the medium itself rather than at any configuration. Option A is contradicted by both ends reading full-duplex and by the complete absence of late collisions. Option B invents a software fault that would not corrupt frames on the wire. Option C would place the ports in different VLANs, which stops traffic passing rather than corrupting it.",
  "difficulty": 2,
  "skills": ["interface-counters", "crc-errors", "cable-fault", "troubleshoot-physical"],
},
{
  "id": "1.4-003", "objective": "1.4", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which port currently has nothing connected to it?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts("Gi0/4", "Gi0/3", "Gi0/2", "Gi0/1"),
  "correct": ["B"],
  "explanation": "The Status column reads notconnect only for Gi0/3, meaning the switch detects no link partner on that port, which is also why its Duplex and Speed still read auto rather than a negotiated value. Option A is connected and has negotiated half-duplex at 10Mb/s, which is unusual but is a working link. Options C and D both read connected with negotiated speeds, so each has a live partner at the far end.",
  "difficulty": 1,
  "skills": ["show-interfaces-status", "interface-status", "cable-fault", "read-correct-row"],
},
{
  "id": "1.4-004", "objective": "1.4", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does this port's state tell you, given that the same patch lead works elsewhere?",
  "exhibit": {"kind": "cli_output", "content": EX_004},
  "options": opts(
    "An administrator has shut the port down in the configuration.",
    "The port is negotiating and will come up once the timers expire.",
    "The port detects no link partner, so the fault is the far end or this port.",
    "The port is up but has been placed in a VLAN that carries no traffic at present."),
  "correct": ["C"],
  "explanation": "Down with line protocol down and a notconnect qualifier means no electrical link is detected, and since the lead is known good and no shutdown is present, the problem sits in this port or in whatever should be answering at the far end. Option A would read administratively down instead, which is the wording IOS reserves for a configured shutdown. Option B invents a negotiation delay; a port awaiting negotiation still reports a partner. Option D describes a VLAN issue, which leaves the port up and passing nothing rather than down.",
  "difficulty": 2,
  "skills": ["interface-status", "cable-fault", "troubleshoot-physical", "admin-down-vs-down"],
},
{
  "id": "1.4-005", "objective": "1.4", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Both ports were hardcoded as shown during a maintenance window. What is the result on this link?",
  "exhibit": {"kind": "config", "content": EX_005},
  "options": opts(
    "The link stays down, because the two ends cannot agree on a speed.",
    "The link comes up at 100Mb/s, since the lower of the two speeds wins.",
    "The link comes up but suffers a duplex mismatch and late collisions.",
    "The link comes up at 1000Mb/s once SW7 renegotiates to match SW8."),
  "correct": ["A"],
  "explanation": "Speed must match for an Ethernet link to establish at all, so hardcoding 100 on one end and 1000 on the other leaves both ports down; unlike duplex, speed is not something the two ends can disagree about while still passing frames. Option B invents a lowest-common-speed rule that applies to autonegotiation, which both ports have now been taken out of. Option C describes the duplex mismatch signature, but both ends here specify full duplex and never get far enough to exchange frames. Option D expects renegotiation from a port that has been hardcoded.",
  "difficulty": 3,
  "skills": ["speed-mismatch", "duplex-mismatch", "autonegotiation", "troubleshoot-physical"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "1" / "1.4.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "1.4",
    "domain": 1,
    "blueprint_version": "v1.1",
    "scope_note": ("Built around the three counter signatures that actually separate "
                   "the faults: duplex mismatch (link up, late collisions one end, "
                   "CRC the other), speed mismatch (link down), and cable damage "
                   "(CRC both ends, no collisions)."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
