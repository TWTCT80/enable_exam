#!/usr/bin/env python3
"""Generate bank/1/1.2.json - 'Describe characteristics of network topology
architectures'.

Covers two-tier, three-tier, spine-leaf, WAN and SOHO. Each item either reads a
drawn topology or matches a stated requirement to an architecture, so the
candidate reasons about shape and scale rather than recalling a label.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

# --- exhibits -------------------------------------------------------------

EX_001 = """                +-----------+     +-----------+
                | DIST-SW-1 |=====| DIST-SW-2 |
                +--+-----+--+     +--+-----+--+
                   |     \\___________/     |
                   |      ___________      |
                   |     /           \\     |
              +----+----+         +----+----+
              | ACC-SW-1|         | ACC-SW-2|
              +----+----+         +----+----+
                   |                   |
               user ports          user ports

DIST-SW-1 and DIST-SW-2 also terminate the site's WAN circuits and
perform all routing between VLANs. There is no further switching layer
above them."""

EX_002 = """        +---------+                 +---------+
        | SPINE-1 |                 | SPINE-2 |
        +--+---+--+                 +--+---+--+
           |   |  \\_______________     |   |
           |   \\_________________ \\____|   |
           |                     \\ \\       |
        +--+-----+          +-----+-+-+   +-------+
        | LEAF-1 |          | LEAF-2  |   | LEAF-3|
        +--------+          +---------+   +-------+
           |                     |            |
        servers               servers      servers

Every leaf connects to every spine. No leaf connects to another leaf,
and no spine connects to another spine."""

EX_003 = """A new eight-person office is being fitted out above a shop.

    Requirement
    ---------------------------------------------------------
    One internet circuit, no second site
    Wired ports for eight desks and a printer
    Wireless coverage for the same eight people
    No on-site IT staff; minimum equipment to administer
    Budget covers one device, not a rack"""

EX_004 = """                       +------------+
   branch office -------|  BR-RTR-1  |
      LAN switch        +-----+------+
                              |
                     leased circuit from
                     the service provider
                              |
                        +-----+------+
                        |  HQ-RTR-1  |------- head office LAN
                        +------------+

The circuit between the two routers is billed monthly by the provider
and crosses roughly 40 km of the provider's own infrastructure."""


ITEMS = [
{
  "id": "1.2-001", "objective": "1.2", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Compared with a classic three-tier campus design, which layer is absent here?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "The access layer, since the user ports attach straight to distribution.",
    "The distribution layer, since routing happens on the same pair as the WAN.",
    "A dedicated core layer, whose work the distribution pair absorbs instead.",
    "None of them; access, distribution and core are all present in the drawing."),
  "correct": ["C"],
  "explanation": "Two access switches feed a distribution pair that also routes between VLANs and terminates the WAN, with nothing above it, which is the collapsed-core or two-tier arrangement: the core's aggregation work has been folded into the distribution layer. Option A is contradicted by ACC-SW-1 and ACC-SW-2 carrying the user ports. Option B mistakes the distribution pair for something else, when it is the layer doing the routing. Option D counts three layers where the drawing shows two.",
  "difficulty": 2,
  "skills": ["topology-architectures", "two-tier", "collapsed-core", "three-tier"],
},
{
  "id": "1.2-002", "objective": "1.2", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What is consistent about the path between servers attached to any two different leaves?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "Path length varies with the leaf pair, since some leaves sit closer together.",
    "Every such path crosses one spine, so all leaf-to-leaf paths match in length.",
    "Traffic passes directly from leaf to leaf whenever both sit in the same row.",
    "Paths grow longer as leaves are added, because each new leaf extends the chain."),
  "correct": ["B"],
  "explanation": "With every leaf attached to every spine and no leaf-to-leaf links, traffic between two leaves always goes up to a spine and back down, so the hop count is identical for every pair and latency becomes predictable no matter which servers are talking. Option A imagines physical proximity affecting the path, which the uniform wiring removes. Option C describes a direct leaf-to-leaf link the design deliberately omits. Option D expects a chain, but adding a leaf attaches it to the existing spines without lengthening any path.",
  "difficulty": 3,
  "skills": ["topology-architectures", "spine-leaf", "east-west-traffic", "predictable-latency"],
},
{
  "id": "1.2-003", "objective": "1.2", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which design fits these requirements?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "A SOHO design on one integrated router, switch and wireless device.",
    "A three-tier campus design with separate core, distribution and access layers.",
    "A spine-leaf fabric with two spines, sized down for the eight users.",
    "A dedicated WAN aggregation layer sitting between the users and the internet."),
  "correct": ["A"],
  "explanation": "Eight users, one circuit, no second site and a single device of budget describe a small office or home office, where one appliance combining routing, switching and wireless covers everything and leaves almost nothing to administer. Option B builds three layers for eight desks, which the budget and the absence of on-site staff both rule out. Option C applies a data centre fabric to a workload that has no east-west traffic to speak of. Option D adds an aggregation layer for a single circuit that needs none.",
  "difficulty": 2,
  "skills": ["topology-architectures", "soho", "design-to-requirements", "right-sizing"],
},
{
  "id": "1.2-004", "objective": "1.2", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which part of this drawing is the WAN?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts(
    "The branch office LAN switch and the ports it serves.",
    "BR-RTR-1 and HQ-RTR-1 taken together as a routed pair.",
    "The head office LAN reached through HQ-RTR-1.",
    "The leased circuit between the two routers."),
  "correct": ["D"],
  "explanation": "A WAN is the span between sites that an organisation rents rather than owns, and here that is the leased circuit crossing 40 km of the provider's infrastructure and billed monthly. Option A is a local network inside one building, which is a LAN by definition. Option C is the same on the other side. Option B names the two routers, which are the devices attaching to the WAN rather than the WAN itself; the boundary sits on the circuit between them.",
  "difficulty": 1,
  "skills": ["topology-architectures", "wan", "lan-vs-wan", "service-provider-circuit"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "1" / "1.2.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "1.2",
    "domain": 1,
    "blueprint_version": "v1.1",
    "scope_note": ("Architectures are read off drawn topologies or matched to stated "
                   "requirements, never named from a definition."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
