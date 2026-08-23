#!/usr/bin/env python3
"""Generate bank/5/5.1.json - 'Define key security concepts'.

A define-level objective, which the spec forbids turning into a definition quiz.
Every item therefore gives an incident and makes the candidate place its parts:
the threat is the actor, the vulnerability is the weakness, the exploit is what
leverages it, and mitigation is what closes it rather than what hides it.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

# --- exhibits -------------------------------------------------------------

EX_001 = """Incident summary - finance office workstation

    The machine was running a document reader two versions behind, with
    a published flaw in the way it parses embedded fonts.

    A crafted document arrived by email. When the user opened it, code
    inside the file used that font-parsing flaw to run commands.

    The group behind the campaign has targeted finance departments
    across the sector for the past two years."""

EX_002 = """A public-facing server runs a version of its application with a
published remote code execution flaw. The vendor released a fixed
version three weeks ago.

Four responses have been proposed while the incident is open."""

EX_003 = """After the third compromise of the same application server, the team
added a signature to the intrusion prevention system that matches the
exact request pattern used in the attacks. Blocking took effect
immediately and no further compromises have occurred this week.

The application itself has not been updated. The vendor's patch is
still waiting for a change window."""

EX_004 = """Incident record

    Element                Detail
    -------------------    --------------------------------------------
    Actor                  A group known to target logistics firms
    Weakness               Default administrative credentials left in
                           place on an internet-facing appliance
    Method used            An automated script that tried the vendor's
                           documented default credentials
    Outcome                Administrative access to the appliance
    Response taken         Credentials changed, management moved to an
                           internal-only address"""


ITEMS = [
{
  "id": "5.1-001", "objective": "5.1", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which part of this account describes the vulnerability?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "The group that has been targeting finance departments for two years.",
    "The unpatched font-parsing flaw in the document reader.",
    "The crafted document that carried the code to the user.",
    "The commands that ran on the workstation once the file was opened."),
  "correct": ["B"],
  "explanation": "A vulnerability is the weakness itself, and here that is the flaw in how the outdated reader parses fonts; it existed before anyone tried to use it and would still exist if nobody had. Option A is the threat, meaning the actor with the intent and capability to act. Option C is the exploit, the crafted artefact that leverages the weakness. Option D is the impact, which is what resulted rather than what allowed it.",
  "difficulty": 2,
  "skills": ["security-concepts", "vulnerability", "threat", "exploit"],
},
{
  "id": "5.1-002", "objective": "5.1", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which response removes the vulnerability rather than reducing its exposure?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "Rate-limit inbound connections to the server at the perimeter firewall.",
    "Move the server to a different public address and update the records.",
    "Increase how often the server's logs are reviewed by the operations team.",
    "Apply the vendor's fixed version to the application."),
  "correct": ["D"],
  "explanation": "Patching eliminates the flaw, so there is nothing left to exploit however the traffic arrives; every other option leaves the weakness in place and only makes reaching it harder or noticing it faster. Option A slows an attack without preventing it. Option B relies on the address not being rediscovered, which scanning defeats within hours. Option C improves detection after the fact rather than removing the cause.",
  "difficulty": 2,
  "skills": ["security-concepts", "mitigation-techniques", "patching", "vulnerability"],
},
{
  "id": "5.1-003", "objective": "5.1", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What is the limitation of the protection the team has put in place?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "The flaw remains, so a variant the signature does not match still works.",
    "An intrusion prevention system cannot inspect traffic bound for a server.",
    "Signatures stop matching after thirty days and have to be rewritten.",
    "The block also turns away the legitimate users of the application."),
  "correct": ["A"],
  "explanation": "A signature matches one observed pattern, so it buys time but leaves the underlying weakness intact; anyone who alters the request enough to miss the signature reaches the same flaw. It is a compensating control, useful until the patch lands rather than instead of it. Option B is wrong because an inline sensor inspects exactly this traffic. Option C invents an expiry that signatures do not have. Option D describes a false positive, which the exhibit gives no sign of.",
  "difficulty": 3,
  "skills": ["security-concepts", "mitigation-techniques", "compensating-control", "vulnerability"],
},
{
  "id": "5.1-004", "objective": "5.1", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which row of this record describes the exploit?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts("Actor", "Weakness", "Method used", "Response taken"),
  "correct": ["C"],
  "explanation": "An exploit is the means by which a weakness is turned into access, which the record files under Method used: the script that submitted the documented default credentials. Option A is the threat, the group with intent. Option B is the vulnerability, namely the credentials left unchanged. Option D is the mitigation applied afterwards, which closed the weakness rather than using it.",
  "difficulty": 1,
  "skills": ["security-concepts", "exploit", "threat", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "5" / "5.1.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "5.1",
    "domain": 5,
    "blueprint_version": "v1.1",
    "scope_note": ("Concepts are placed within an incident rather than defined, since "
                   "the spec bans definition quizzes."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
