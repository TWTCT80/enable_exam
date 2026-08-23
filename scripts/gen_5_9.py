#!/usr/bin/env python3
"""Generate bank/5/5.9.json - 'Describe wireless security protocols'.

WPA, WPA2 and WPA3. Deliberately distinct from 2.9-004, which asks only which
scan entry is strongest; these ask WHY the generations differ - the offline
dictionary attack WPA3 closes, and the per-user credentials Enterprise adds.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

EX_001 = """A shared office passphrase has been in use for two years and is
known to about sixty people.

    Observed
    ---------------------------------------------------------------
    Someone captured the association exchange of a joining client
    They then worked offline against that capture for several days
    They recovered the passphrase and joined the network
    No interaction with the network was needed during those days

The site runs WPA2-Personal. A move to WPA3-Personal is proposed."""

EX_002 = """Two candidate designs for staff wireless at a site of 400 people

    Property                     Design 1              Design 2
    -------------------------    ------------------    ---------------
    Credential each user holds   one shared phrase     their own login
    Removing one leaver          change it for all     disable one
                                 400 people            account
    Backing store                none                  RADIUS server
    Per-user session keys        derived from the      derived per
                                 shared phrase         authentication"""

EX_003 = """Wireless security generations as recorded in the site standard

    Generation   Data protection      Personal-mode key exchange
    ----------   ------------------   ------------------------------
    WPA          TKIP                 Pre-shared key, 4-way handshake
    WPA2         AES-CCMP             Pre-shared key, 4-way handshake
    WPA3         AES with SAE         Simultaneous Authentication of
                                      Equals"""

ITEMS = [
{
  "id": "5.9-001", "objective": "5.9", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What would moving to WPA3-Personal change about this attack?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "Nothing, since WPA3-Personal still derives its keys from a shared phrase.",
    "The capture would be prevented, because WPA3 encrypts the association itself.",
    "The offline stage would no longer work, as SAE gives nothing to attack offline.",
    "The attack would take longer, because WPA3 requires a passphrase of 20 characters."),
  "correct": ["C"],
  "explanation": "The weakness is that WPA2's handshake yields material an attacker can grind against a wordlist at leisure, with no further contact. WPA3 replaces it with SAE, where each guess has to be tried against the network live, so days of offline work become impossible and slow online attempts are detectable. Option A misses that the exchange changed even though a phrase is still used. Option B protects the wrong stage. Option D invents a length rule and would only postpone the same attack.",
  "difficulty": 3,
  "skills": ["wireless-security", "wpa3", "sae", "offline-dictionary-attack"],
},
{
  "id": "5.9-002", "objective": "5.9", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which design is the Enterprise mode, and what does it give the site?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "Design 1, because one phrase for the whole site is simpler to administer.",
    "Design 2, since each user holds a credential that can be revoked alone.",
    "Design 1, as a shared phrase still produces a separate key for each session.",
    "Neither; both are Personal mode with different ways of storing the phrase."),
  "correct": ["B"],
  "explanation": "Enterprise mode authenticates each user individually against a backing store such as RADIUS, which is why a leaver is handled by disabling one account rather than reissuing a phrase to 400 people. Option A describes Personal mode and treats its administrative simplicity as the distinguishing feature. Option C is true of both modes and so separates nothing. Option D denies the RADIUS row, which is exactly what marks Design 2 as Enterprise.",
  "difficulty": 2,
  "skills": ["wireless-security", "wpa2-enterprise", "wpa2-personal", "credential-revocation"],
},
{
  "id": "5.9-003", "objective": "5.9", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which generation is the earliest one that protects data with AES?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts("WPA", "WPA3", "WPA2", "None of them use AES"),
  "correct": ["C"],
  "explanation": "The Data protection column shows WPA2 introducing AES-CCMP, which WPA3 then carries forward alongside its new key exchange. Option A is WPA, which uses TKIP, a stopgap built to run on hardware designed for the broken WEP. Option B is later than the earliest and changes the key exchange rather than the cipher family. Option D contradicts two rows of the table.",
  "difficulty": 1,
  "skills": ["wireless-security", "wpa2", "aes-ccmp", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "5" / "5.9.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "5.9", "domain": 5, "blueprint_version": "v1.1",
    "scope_note": ("Distinct from 2.9-004: these ask why the generations differ, not "
                   "which scan entry is strongest."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
