#!/usr/bin/env python3
"""Generate bank/5/5.8.json - 'Compare authentication, authorization, and
accounting concepts'.

Each item separates the three by what fails when one of them is missing, which
is more useful than reciting the three words.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

EX_001 = """An engineer signs in to a switch and the following happens.

    The username and secret are checked against the access control
    server, which confirms the account and permits the session.

    The engineer types a configuration command. The switch asks the
    server whether this account may run it. The server declines and the
    switch prints an error.

    A record is written showing which account attempted the command, on
    which device, and at what time."""

EX_002 = """A contractor's account can sign in to every switch without trouble.
Once connected, the account can run show commands, but any attempt to
enter configuration mode is refused.

The refusal is consistent across every device and happens immediately,
with no delay while the switch waits for anything."""

EX_003 = """The security team is asked which record answers each question.

    Question
    ------------------------------------------------------------
    A  Was this really the person the account belongs to?
    B  Was this account allowed to run that particular command?
    C  Which commands did this account run last Tuesday, and when?"""

ITEMS = [
{
  "id": "5.8-001", "objective": "5.8", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which of the three stages refused the command?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "Authentication, since the account was checked before anything else.",
    "Authorization, which decides what a confirmed account may do.",
    "Accounting, which recorded the attempt and blocked it as unapproved.",
    "All three together, because the server evaluates them as one decision."),
  "correct": ["B"],
  "explanation": "Authentication had already succeeded, which is why the session opened at all, and the refusal came when the switch asked whether that account was permitted this command, which is authorization. Option A confuses the two: proving identity says nothing about what follows. Option C describes accounting, which records what happened and never blocks anything. Option D merges three stages that a server deliberately evaluates in sequence.",
  "difficulty": 2,
  "skills": ["aaa", "authorization", "authentication", "accounting"],
},
{
  "id": "5.8-002", "objective": "5.8", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does this pattern of behaviour indicate?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "The account's credentials are wrong on some devices but not on others.",
    "The accounting records are full, so the switches refuse further commands.",
    "The account authenticates correctly but is not authorized for that level.",
    "The access control server is unreachable, so the switches have fallen back."),
  "correct": ["C"],
  "explanation": "Signing in successfully proves authentication works, and being blocked at a specific privilege proves the restriction lies in what the account is permitted to do, which is authorization applied consistently by the same policy. Option A is contradicted by the sign-in succeeding everywhere. Option B has accounting refusing commands, which it never does. Option D would produce a fallback or a timeout, and the exhibit rules that out by noting the refusal is immediate.",
  "difficulty": 2,
  "skills": ["aaa", "authorization", "authentication", "troubleshoot-aaa"],
},
{
  "id": "5.8-003", "objective": "5.8", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which question does accounting answer?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts("Question A", "Question C", "Question B", "All three of them"),
  "correct": ["B"],
  "explanation": "Accounting is the record of what was done and when, so question C is the one it answers, and it is the reason a per-command log is worth collecting at all. Option A is authentication, which establishes who the account holder is at sign-in. Option C is authorization, which decides in the moment whether an action is permitted. Option D collapses three separate records that exist precisely because they answer different questions.",
  "difficulty": 1,
  "skills": ["aaa", "accounting", "authentication", "authorization"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "5" / "5.8.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "5.8", "domain": 5, "blueprint_version": "v1.1",
    "scope_note": "The three are separated by what fails when each is missing.",
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
