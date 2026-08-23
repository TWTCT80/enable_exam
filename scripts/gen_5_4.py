#!/usr/bin/env python3
"""Generate bank/5/5.4.json - 'Describe security password policy elements'.

Management, complexity, and the alternatives the objective names: multifactor
authentication, certificates and biometrics.

002 is the item that matters: two credentials are not two factors unless they
come from different categories, and a fingerprint plus a face scan is one
factor twice over.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

EX_001 = """Extract from a draft password policy

    Minimum length              twelve characters
    Composition                 upper case, lower case, digit, symbol
    Maximum age                 ninety days, enforced
    Account lockout             after ten failed attempts
    Reuse                       not addressed
    Second factor               not required"""

EX_002 = """Four schemes proposed for administrative logins

    Scheme   First credential        Second credential
    ------   --------------------   ---------------------------
    W        A password             An answer to a chosen question
    X        A password             A code from a hardware token
    Y        A password             A second, longer password
    Z        A fingerprint          A facial scan"""

EX_003 = """A field deployment of two hundred devices needs to authenticate to
the management platform.

    Requirement
    ---------------------------------------------------------------
    No shared value that is identical across the estate
    A stolen device must not yield anything reusable elsewhere
    Credentials must be revocable for one device on its own
    No human types anything during the device's enrolment"""

ITEMS = [
{
  "id": "5.4-001", "objective": "5.4", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which weakness does this policy leave open?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "Composition rules become unnecessary once a maximum age is enforced.",
    "Ninety days is far too long an interval between forced changes.",
    "Enforced rotation without any composition rule leaves passwords guessable.",
    "Nothing prevents a user returning to a password they have used before."),
  "correct": ["D"],
  "explanation": "The policy sets length, composition, age and lockout but says nothing about reuse, so a user can cycle through a handful of passwords and return to the first, which makes the ninety-day rotation largely decorative. Option A treats the two as alternatives when they address different attacks. Option B challenges an interval the policy does enforce and which is not the gap. Option C describes a policy with no composition rule, which this one plainly has.",
  "difficulty": 3,
  "skills": ["password-policy", "password-management", "password-reuse", "complexity"],
},
{
  "id": "5.4-002", "objective": "5.4", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which scheme is genuinely multifactor?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts("Scheme W", "Scheme X", "Scheme Y", "Scheme Z"),
  "correct": ["B"],
  "explanation": "Multifactor means credentials from different categories, and only scheme X combines something known with something held, so stealing the password alone leaves an attacker short of the token. Option A pairs a password with a security answer, which is a second thing known and often easier to research than the password. Option C is two passwords, one category twice. Option D pairs two biometrics, which are both something you are, and neither can be reissued if copied.",
  "difficulty": 2,
  "skills": ["password-policy", "multifactor-authentication", "authentication-factors", "biometrics"],
},
{
  "id": "5.4-003", "objective": "5.4", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which approach satisfies every line of the requirement?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "A certificate issued to each device by an internal authority.",
    "One pre-shared key, distributed to all two hundred devices.",
    "A long password per device, rotated on a quarterly schedule.",
    "A biometric enrolment recorded against each device's serial number."),
  "correct": ["A"],
  "explanation": "A per-device certificate is unique, carries no secret that works anywhere else, can be revoked individually, and is issued during enrolment without anyone typing a credential, which covers all four lines. Option B fails the first two outright, since one stolen device yields the key for the estate. Option C is unique per device but still a typed secret and a rotation burden across two hundred units. Option D applies a human characteristic to hardware, which has nobody to measure.",
  "difficulty": 2,
  "skills": ["password-policy", "certificates", "password-alternatives", "device-authentication"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "5" / "5.4.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "5.4", "domain": 5, "blueprint_version": "v1.1",
    "scope_note": "Two credentials are two factors only when they come from different categories.",
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
