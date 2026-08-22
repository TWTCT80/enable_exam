#!/usr/bin/env python3
"""Generate bank/1/1.3.json - 'Compare physical interface and cabling types'.

Both sub-topics: media selection (single-mode fibre, multimode fibre, copper)
and the shared-media / point-to-point distinction. Media limits are supplied in
the exhibit as a reference table rather than assumed from memory, so the item
tests choosing against constraints rather than reciting distances.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import interfaces_status, intf_status, opts  # noqa: E402

MEDIA_TABLE = """    Media                       Practical maximum run
    ------------------------    ---------------------
    Copper twisted pair         100 m
    Multimode fibre             550 m
    Single-mode fibre           10 km and beyond"""

# --- exhibits -------------------------------------------------------------

EX_001 = f"""A 1 Gbps link is needed between two buildings on one campus. The
cable route measured along the duct is 340 m.

{MEDIA_TABLE}"""

EX_002 = f"""A contractor ran copper twisted pair between the ground-floor comms
room and a cabinet on the third floor of an adjacent wing. The measured
run is 145 m. Both switch ports are configured identically and neither
comes up; swapping the transceivers and the patch leads changes nothing.

{MEDIA_TABLE}"""

EX_003 = """    Segment A                          Segment B

      +-------+                          +--------+
      |  HUB  |                          | SWITCH |
      +---+---+                          +---+----+
     /   / \\   \\                        /   / \\   \\
   PC1 PC2 PC3 PC4                    PC5 PC6 PC7 PC8

Each device is attached by its own cable, and every port on both
devices is running at 100 Mbps."""

EX_004 = interfaces_status("SW9", [
    intf_status("Gi0/21", "reception", "connected", "10", "a-full", "a-1000"),
    intf_status("Gi0/22", "meeting room", "connected", "10", "a-full", "a-1000"),
    intf_status("Gi0/23", "print room", "connected", "20", "a-full", "a-100"),
    intf_status("Gi0/25", "link to annexe", "connected", "1", "full", "1000",
                "1000BaseSX"),
])


ITEMS = [
{
  "id": "1.3-001", "objective": "1.3", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which medium is the least costly one that will carry this link over the measured distance?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "Copper twisted pair, since 1 Gbps is well within its rated speed for this link.",
    "Multimode fibre, which spans the distance without single-mode optics.",
    "Single-mode fibre, the only medium rated beyond 100 m.",
    "Copper twisted pair with a repeater placed at the midpoint of the run."),
  "correct": ["B"],
  "explanation": "The run is 340 m, which is beyond copper's 100 m limit but comfortably inside multimode's 550 m, and multimode optics cost less than single-mode, so it is the cheapest medium that actually reaches. Option A ignores distance entirely and considers only speed, which copper does support but cannot deliver over 340 m. Option C would work but pays for reach the campus does not need. Option D adds active equipment mid-duct, which introduces a powered device and a failure point where a passive fibre run needs neither.",
  "difficulty": 2,
  "skills": ["cabling-types", "media-selection", "distance-limits", "multimode-fibre"],
},
{
  "id": "1.3-002", "objective": "1.3", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What best explains why neither port will come up?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "The two switch ports have been left in mismatched VLANs.",
    "The copper run needs a crossover cable rather than a straight-through one.",
    "Autonegotiation is disabled, so the ports never agree on a speed.",
    "The run is 45 m beyond the copper limit, so no reliable link forms."),
  "correct": ["D"],
  "explanation": "Twisted pair is specified to 100 m, and this run is 145 m, so signal attenuation prevents a link establishing at all no matter what is fitted at the ends, which is exactly why swapping transceivers and leads changed nothing. Option A describes a VLAN mismatch, which leaves ports up while blocking traffic rather than keeping them down. Option B invokes cable pinout, which modern switches resolve automatically and which would not survive the swap testing already done. Option C describes a mismatch that the exhibit rules out by stating both ports are configured identically.",
  "difficulty": 3,
  "skills": ["cabling-types", "distance-limits", "copper-limitations", "troubleshoot-physical"],
},
{
  "id": "1.3-003", "objective": "1.3", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. How do the two segments compare in the number of collision domains they create?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "Segment A has four and segment B has one, because the switch merges its ports.",
    "Both have four, because each device is attached by its own dedicated cable.",
    "Segment A has one and segment B has four, because each switch port is its own.",
    "Both have one, because both devices join all their ports into a single domain."),
  "correct": ["C"],
  "explanation": "A hub repeats every received signal out of all other ports, so all four stations on segment A share one collision domain regardless of having separate cables. A switch forwards selectively and each port forms its own point-to-point link, giving segment B four separate domains. Option A reverses the two devices. Option B assumes a dedicated cable is enough, but the hub's shared repeating is what defines the domain. Option D describes two hubs and ignores the switch entirely.",
  "difficulty": 2,
  "skills": ["shared-media-vs-point-to-point", "collision-domain", "hub-vs-switch", "ethernet-connections"],
},
{
  "id": "1.3-004", "objective": "1.3", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which port is fitted with a fibre transceiver rather than a copper connection?",
  "exhibit": {"kind": "cli_output", "content": EX_004},
  "options": opts("Gi0/25", "Gi0/21", "Gi0/23", "Gi0/22"),
  "correct": ["A"],
  "explanation": "The Type column records the physical media, and Gi0/25 reads 1000BaseSX, an optical standard, while every other port reads 10/100/1000BaseTX, where TX denotes twisted pair. The port's description, link to annexe, fits a run between buildings. Options B and D are both copper access ports negotiating at gigabit, and option C is a copper port that settled at 100 Mbps, which reflects the device plugged into it rather than the media fitted.",
  "difficulty": 1,
  "skills": ["cabling-types", "show-interfaces-status", "media-type", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "1" / "1.3.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "1.3",
    "domain": 1,
    "blueprint_version": "v1.1",
    "scope_note": ("Media distance limits are given in the exhibit as a reference "
                   "table, so items test selecting against constraints rather than "
                   "reciting distances."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
