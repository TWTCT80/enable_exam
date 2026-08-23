#!/usr/bin/env python3
"""Generate bank/4/4.7.json - 'Explain the forwarding per-hop behavior for QoS'.

Two items, on the two distinctions that carry the objective: policing discards
or remarks what exceeds the rate while shaping buffers it and delays it, and
classification and marking belong at the trust boundary so every later hop can
act on the mark instead of re-inspecting the traffic.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

EX_001 = """A branch uploads nightly backups across a circuit it shares with
interactive traffic.

    Requirement
    ---------------------------------------------------------------
    The backup stream must be held to 4 Mbps on average
    Bursts above that must be smoothed out rather than discarded
    Retransmitting lost backup data wastes the circuit twice over
    A little extra delay on the backup traffic is acceptable"""

EX_002 = """                 +--------+          +--------+          +--------+
   IP phone ------| SW-ACC |----------| SW-DIST|----------| R-EDGE |
                  +--------+          +--------+          +--------+

The phone marks its own voice traffic. Voice must receive priority at
every hop across the campus and out to the WAN, and no hop should have
to inspect the traffic deeply to work out what it is carrying."""

ITEMS = [
{
  "id": "4.7-001", "objective": "4.7", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which QoS mechanism should be applied to the backup stream?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "Shaping, which buffers the excess and releases it at the agreed rate.",
    "Policing, which enforces the rate by discarding whatever exceeds it.",
    "Classification, which identifies the backup stream so it can be counted.",
    "Congestion avoidance, which drops early to keep queues from filling."),
  "correct": ["A"],
  "explanation": "Shaping holds traffic above the rate in a queue and releases it later, so a burst is delayed rather than lost, which suits a backup that tolerates delay but wastes the circuit if it has to retransmit. Option B meets the rate requirement but does so by discarding, which is what the third and fourth lines rule out. Option C identifies traffic without limiting it, so nothing enforces the rate. Option D deliberately drops to signal senders to slow down, again losing data.",
  "difficulty": 3,
  "skills": ["qos", "shaping", "policing", "per-hop-behaviour"],
},
{
  "id": "4.7-002", "objective": "4.7", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Where should classification and marking take place?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "At R-EDGE, so one device decides the policy for the whole campus.",
    "At every hop, each re-examining the traffic and marking it again.",
    "Nowhere; priority should be applied by queueing without any marking.",
    "As close to the source as possible, with later hops trusting the mark."),
  "correct": ["D"],
  "explanation": "Marking once at the edge, at the trust boundary where the phone attaches, lets every subsequent hop read a field in the header and queue accordingly rather than inspecting payload, which is the whole point of a per-hop behaviour. Option A leaves the campus hops with nothing to act on until the traffic reaches the WAN. Option B repeats expensive work at each device and risks the hops disagreeing. Option C removes the signal that queueing depends on.",
  "difficulty": 2,
  "skills": ["qos", "classification", "marking", "trust-boundary"],
},
]
dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "4" / "4.7.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({"objective": "4.7", "domain": 4,
    "blueprint_version": "v1.1",
    "scope_note": "Policing discards, shaping delays; marking belongs at the trust boundary.",
    "items": ITEMS}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
