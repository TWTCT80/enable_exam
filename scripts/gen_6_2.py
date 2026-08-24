#!/usr/bin/env python3
"""Generate bank/6/6.2.json - 'Compare traditional networks with controller-based
networking'.

The comparison that matters is where decisions are made and how a change is
expressed. 003 covers the trade-off the marketing leaves out: centralising the
policy creates a dependency that a distributed control plane does not have.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

EX_001 = """A new guest VLAN and its access policy must be added at 60 sites.

    Traditional deployment    each device holds its own configuration
                              and is reached over SSH
    Controller-based          devices are joined to a controller that
                              holds the intended policy centrally"""

EX_002 = """In a traditional network, each router runs OSPF, builds its own
link-state database, and computes its own best paths. In a
controller-based fabric, a central component works out the paths and
programs the devices to forward accordingly.

    Question
    ---------------------------------------------------------------
    Which part of a device's operation has moved in the second case?"""

EX_003 = """A campus runs a controller-based fabric. The controller becomes
unreachable from the fabric switches after a failure in the management
network.

    Observed while the controller is unreachable
    ---------------------------------------------------------------
    Traffic between hosts already communicating continues to flow
    Existing policy stays in force on the switches
    A request to add a new segment cannot be carried out"""

EX_004 = """                Traditional             Controller-based
    ----------    --------------------    ---------------------------
    Policy is     configured on each      declared once and pushed
    expressed     device separately       to the devices
    A change      touches every device    is made in one place
    Consistency   depends on the person   is a property of the system
    Interface     device CLI              API and controller"""

ITEMS = [
{
  "id": "6.2-001", "objective": "6.2", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. How does the work differ between the two deployments?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "Both require 60 separate sessions; only the transport used differs.",
    "The controller-based case still needs a visit per site to join each device.",
    "The traditional case needs 60 changes; the controller-based one needs one.",
    "The traditional case is faster, since no controller has to distribute it."),
  "correct": ["C"],
  "explanation": "In a traditional deployment the intent lives on each device, so it has to be expressed 60 times with 60 chances to differ; with a controller the intent is declared once and the controller renders it onto every joined device. Option A denies the difference the models exist to create. Option B confuses joining a device, which happens once at onboarding, with making a policy change. Option D reverses which is faster and treats distribution as though it were manual.",
  "difficulty": 2,
  "skills": ["controller-based-networking", "traditional-networks", "centralised-policy", "scale"],
},
{
  "id": "6.2-002", "objective": "6.2", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which part of the device's operation has moved to the controller?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "The control plane, which decides how traffic should be forwarded.",
    "The data plane, which moves each frame from one port to another.",
    "The management plane, which handles logins and configuration access.",
    "All three, since a joined device retains no local function."),
  "correct": ["A"],
  "explanation": "Working out paths and deciding what the forwarding tables should contain is the control plane, and that is what the controller has taken over; each device still moves packets itself. Option B names the part that necessarily stays on the device, since forwarding happens in its hardware at line rate. Option C names logins and access, which the exhibit does not discuss. Option D overstates it: the separation is the whole point, and a device with no data plane would forward nothing.",
  "difficulty": 2,
  "skills": ["controller-based-networking", "control-plane", "data-plane", "plane-separation"],
},
{
  "id": "6.2-003", "objective": "6.2", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does this behaviour show about the model?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "The fabric has failed, since a controller-based network cannot run without one.",
    "The controller was never required, as the switches clearly operate alone.",
    "Forwarding has moved into the controller, which is why nothing new can start.",
    "Forwarding continues from what is programmed, but changes cannot be made."),
  "correct": ["D"],
  "explanation": "The switches keep forwarding because their tables and policy are already programmed into hardware, but nothing new can be expressed while the component holding the intent is out of reach, which is the dependency centralisation creates and the reason controllers are deployed redundantly. Option A overstates the outage, since traffic plainly continues. Option B understates the dependency by ignoring the failed request. Option C places forwarding in the controller, which the continuing traffic disproves.",
  "difficulty": 3,
  "skills": ["controller-based-networking", "controller-dependency", "control-plane", "data-plane"],
},
{
  "id": "6.2-004", "objective": "6.2", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. According to this table, what makes consistency different between the two models?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts(
    "Traditional devices enforce it in hardware; controllers only recommend it.",
    "It rests on the engineer traditionally, and on the system otherwise.",
    "Both models leave it to the engineer; only the interface used differs.",
    "Controllers abandon consistency in exchange for making changes faster."),
  "correct": ["B"],
  "explanation": "The Consistency row states it plainly: configured device by device it depends on whoever does the work, whereas a single declared policy rendered onto every device makes agreement a property of how the system operates rather than of anyone's diligence. Option A inverts the table. Option C denies the row's distinction. Option D presents the two as a trade-off, when the table lists consistency and speed as gains together.",
  "difficulty": 1,
  "skills": ["controller-based-networking", "traditional-networks", "consistency", "read-correct-row"],
},
]
dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "6" / "6.2.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({"objective": "6.2", "domain": 6,
    "blueprint_version": "v1.1",
    "scope_note": "Includes the dependency centralisation creates, not only its benefits.",
    "items": ITEMS}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
