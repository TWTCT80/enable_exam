#!/usr/bin/env python3
"""Generate bank/6/6.3.json - 'Describe controller-based, software defined
architecture'.

Both sub-topics the objective lists: separation of control and data plane (002),
northbound and southbound APIs (001, 005), and overlay, underlay and fabric
(003, 004).

The direction of the two API types is the part candidates reverse, so 001 gives
the layout and asks which way each call travels rather than asking for a
definition.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

STACK = """        +--------------------------------------+
        |   provisioning portal, ticketing,    |
        |   monitoring and analytics tools     |
        +--------------------------------------+
                          |  API  A
        +--------------------------------------+
        |             CONTROLLER               |
        +--------------------------------------+
                          |  API  B
        +--------------------------------------+
        |   switches, routers, access points   |
        +--------------------------------------+"""

EX_001 = STACK + """

A ticketing system asks the controller to create a segment. The
controller then instructs forty switches to implement it."""

EX_002 = """A fabric switch receives a frame and forwards it in hardware within
microseconds, using tables it did not compute for itself. A central
component worked out what those tables should contain and programmed
them, and it recomputes them whenever the topology changes."""

EX_003 = """A campus fabric carries traffic between two hosts.

    Layer          What it consists of
    -----------    --------------------------------------------
    Layer one      The physical switches, their links, and the
                   routing that lets each device reach every
                   other device's loopback
    Layer two      Tunnels built between those loopbacks, in
                   which the hosts' own traffic is carried"""

EX_004 = """                     +---------+   +---------+
                     | SPINE-1 |   | SPINE-2 |
                     +----+----+   +----+----+
                          | \\_______/ |
                          |  ________/|
                     +----+-/---+  +--+------+
                     |  LEAF-1  |  |  LEAF-2 |
                     +----------+  +---------+

Every leaf connects to every spine. A controller holds the policy for
the whole arrangement and programs each device. Host traffic between
leaves is carried in tunnels between the leaf loopbacks, over the
routed links shown."""

EX_005 = STACK + """

An engineer writes a script that runs on the monitoring server and asks
the controller for a list of every device it manages."""

ITEMS = [
{
  "id": "6.3-001", "objective": "6.3", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which API does each of the two actions use?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "Both use API A, since the controller mediates every request that arrives.",
    "The ticketing request uses A, northbound; the switches are reached over B.",
    "The ticketing request uses B, and the controller reaches the switches over A.",
    "Both use API B, because every action ends at a device in the end."),
  "correct": ["B"],
  "explanation": "Northbound faces the applications above the controller, so a ticketing system calls in over API A, and southbound faces the infrastructure below it, so the controller programs the switches over API B. The names describe direction relative to the controller rather than importance. Option C reverses the two, which is the usual slip. Option A ignores that the controller must also speak downward. Option D looks at where the effect lands rather than which interface each call crosses.",
  "difficulty": 2,
  "skills": ["sdn-architecture", "northbound-api", "southbound-api", "controller-based-networking"],
},
{
  "id": "6.3-002", "objective": "6.3", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which description matches what this switch is doing?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "It runs both planes locally, with the central component only monitoring it.",
    "It runs the control plane locally while the data plane is centralised.",
    "It runs neither plane; the central component forwards the traffic itself.",
    "It runs the data plane locally while the control plane sits centrally."),
  "correct": ["D"],
  "explanation": "Forwarding a frame in hardware in microseconds is the data plane and stays on the switch, while deciding what the tables should hold is the control plane and has moved to the central component; that division is what separation of the planes means. Option A denies the separation the exhibit describes. Option B reverses the two, which would put per-frame forwarding across the network. Option C leaves the switch doing nothing, contradicted by it forwarding the frame.",
  "difficulty": 2,
  "skills": ["sdn-architecture", "control-plane", "data-plane", "plane-separation"],
},
{
  "id": "6.3-003", "objective": "6.3", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which layer is the underlay, and what does it carry?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "Layer one is the underlay, carrying the tunnels that hold host traffic.",
    "Layer two is the underlay, since host traffic is what the fabric exists for.",
    "Layer one is the overlay, because it is the physical network beneath.",
    "Neither; underlay and overlay describe the same links seen from two angles."),
  "correct": ["A"],
  "explanation": "The underlay is the real network of switches, links and routing whose only job is to let every device reach every other, and the overlay is the set of tunnels built across it in which host traffic actually travels. Option B swaps them by reasoning from purpose rather than position. Option C names the right layer but calls it the overlay, inverting the terms. Option D collapses a distinction that exists precisely so host addressing can change without the physical network being touched.",
  "difficulty": 3,
  "skills": ["sdn-architecture", "underlay", "overlay", "fabric"],
},
{
  "id": "6.3-004", "objective": "6.3", "domain": 6, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Which two components does this arrangement contain? (Choose two.)",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts(
    "An underlay: the routed spine-and-leaf links carrying loopback reachability",
    "A three-tier campus hierarchy of core, distribution and access layers",
    "A WAN circuit supplied and billed by a service provider",
    "An overlay: tunnels between the leaf loopbacks carrying host traffic",
    "A collapsed core, since the two spines aggregate the leaf switches"),
  "correct": ["A", "D"],
  "explanation": "The drawing holds both halves of a fabric: the routed links between spines and leaves form the underlay whose job is to let every device reach every other, and the tunnels built between leaf loopbacks form the overlay in which host traffic actually travels. Option B names a campus hierarchy this is not. Option C introduces a provider circuit the drawing never shows. Option E borrows a campus term for spines that aggregate nothing in that sense.",
  "difficulty": 2,
  "skills": ["sdn-architecture", "fabric", "overlay", "underlay"],
},
{
  "id": "6.3-005", "objective": "6.3", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which API does the engineer's script use?",
  "exhibit": {"kind": "topology", "content": EX_005},
  "options": opts(
    "API A, the northbound interface the controller offers to applications.",
    "API B, the southbound interface toward the managed devices.",
    "Neither, since a read-only request bypasses both interfaces.",
    "Both in turn, as the request is relayed down to each device."),
  "correct": ["A"],
  "explanation": "The script runs above the controller and asks it for information, so it calls in over the northbound API, which is what the controller publishes for applications and tools. Option B is the interface the controller uses to reach the switches, which the script never touches. Option C invents an exemption for reads, when a query is an ordinary API call. Option D assumes the controller must poll every device, but it answers from what it already holds.",
  "difficulty": 1,
  "skills": ["sdn-architecture", "northbound-api", "southbound-api", "controller-based-networking"],
},
]
dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "6" / "6.3.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({"objective": "6.3", "domain": 6,
    "blueprint_version": "v1.1",
    "scope_note": "API direction is asked from a drawn stack, not from a definition.",
    "items": ITEMS}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
