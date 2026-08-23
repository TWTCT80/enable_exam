#!/usr/bin/env python3
"""Generate bank/5/5.2.json - 'Describe security program elements'.

User awareness, training and physical access control, each reached from an
incident rather than defined. The distinction that carries the objective is
awareness (everyone, recognising a situation) against training (a role,
performing a task correctly).
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

EX_001 = """Incident summary

    Fourteen staff across five departments received a message that
    appeared to come from the payroll system, warning that their bank
    details needed reconfirming before the month end.

    Nine followed the link and entered their network credentials into a
    page that closely resembled the real portal.

    The page was hosted outside the organisation. No software flaw was
    involved at any point."""

EX_002 = """Incident summary

    A visitor waited by the rear entrance and followed an employee
    through the door as it closed behind them. They then walked to the
    second-floor communications room, whose door was propped open with a
    fire extinguisher, and connected a small device to a spare switch
    port before leaving.

    Every switch in the room has a strong enable secret and permits SSH
    management only."""

EX_003 = """Three gaps identified in an internal review

    Gap
    -------------------------------------------------------------
    A  Staff cannot reliably tell a genuine internal message from a
       convincing imitation
    B  The two engineers who will run the new firewall have never
       configured that product and are unsure of its rule syntax
    C  Server room doors are left on the latch during deliveries"""

ITEMS = [
{
  "id": "5.2-001", "objective": "5.2", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which security programme element most directly addresses what happened here?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "A user awareness programme on recognising messages of this kind.",
    "Role-specific technical training for the network and server engineers.",
    "Tighter physical access control at the entrances to the building.",
    "A policy raising the minimum length of every user's password."),
  "correct": ["A"],
  "explanation": "Nothing technical failed: the staff were persuaded, so the gap is whether people across the organisation can recognise a convincing imitation, which is what an awareness programme addresses. Option B trains a small technical group on tasks, which would not have reached the nine people who entered credentials. Option C guards the premises, and the page was hosted elsewhere entirely. Option D lengthens passwords that were handed over willingly, so their strength never mattered.",
  "difficulty": 2,
  "skills": ["security-program", "user-awareness", "phishing", "social-engineering"],
},
{
  "id": "5.2-002", "objective": "5.2", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which element of the security programme failed in this incident?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "Password management, since the enable secret should be rotated more often.",
    "Awareness training, because staff should lock their screens when away.",
    "Physical access control, at both the rear door and the communications room.",
    "Device hardening, as management access should have been restricted further."),
  "correct": ["C"],
  "explanation": "The intruder never needed a credential: they were let through one door by following someone and found another propped open, so the failure is physical and occurs twice over. Option A hardens a secret that was never tested. Option B names a real habit, but no unattended workstation features in the account. Option D is contradicted by the switches already being restricted to SSH with a strong secret, which did nothing to stop a cable being plugged in.",
  "difficulty": 2,
  "skills": ["security-program", "physical-access-control", "tailgating", "defence-in-depth"],
},
{
  "id": "5.2-003", "objective": "5.2", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which gap is the one that role-specific training addresses?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts("Gap A", "Gap B", "Gap C", "None of the three"),
  "correct": ["B"],
  "explanation": "Training equips a particular role to perform a task correctly, and gap B is exactly that: two named engineers who need working knowledge of a product they will operate. Option A is a matter of general recognition across all staff, which awareness covers. Option C is a physical control at a door rather than anything taught. Option D is contradicted by gap B being a textbook training need.",
  "difficulty": 1,
  "skills": ["security-program", "training", "user-awareness", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "5" / "5.2.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "5.2", "domain": 5, "blueprint_version": "v1.1",
    "scope_note": ("Awareness reaches everyone and concerns recognising a situation; "
                   "training equips a role to perform a task."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
