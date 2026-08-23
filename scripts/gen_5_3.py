#!/usr/bin/env python3
"""Generate bank/5/5.3.json - 'Configure and verify device access control using
local passwords'.

Configure-and-verify. The theme running through it is that a password appearing
in the configuration is not the same as a password protecting anything: type 7
is reversible, `login` without a password refuses connections outright, and
`login local` with no user database locks everyone out.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

# --- exhibits -------------------------------------------------------------

EX_001 = """! R1 - relevant configuration
!
enable password Harbour42
enable secret Wr3nch-Harbour-42
!
line vty 0 4
 login local
 transport input ssh
!"""

EX_002 = """! R2 - relevant configuration
!
service password-encryption
!
username backup password 7 08701E1D5D4C53
username netadmin secret 9 $9$Xk2mQvR8LpT4c0$hV1nZ7yW3sK
!

The configuration was reviewed after a contractor was given a copy of it
for a documentation exercise."""

EX_003 = """! R3 - relevant configuration
!
hostname R3
ip domain-name example.internal
crypto key generate rsa modulus 2048
!
enable secret Wr3nch-Harbour-42
!
line vty 0 4
 login local
 transport input ssh
!

No engineer can log in over SSH. The connection is accepted and then the
credentials are rejected, whatever is typed."""

EX_004 = """R4(config)# line vty 0 4
R4(config-line)# login
R4(config-line)# transport input telnet
R4(config-line)# end
R4#

An engineer then tries to connect from a workstation:

    % Password required, but none set

    [Connection to 10.4.4.1 closed by foreign host]"""

EX_005 = """R5# show running-config | include ^username
username helpdesk privilege 1 secret 9 $9$Lm4pQ2xR7vN9a0$cW8tY
username netadmin privilege 15 secret 9 $9$Kd7nB3wS5hJ2f0$pR6uX
username monitor privilege 1 secret 9 $9$Zq9cV4tG8mL1e0$nD3sA
username backup privilege 1 secret 9 $9$Rt5xH6yK2bF7d0$jM4wQ"""


ITEMS = [
{
  "id": "5.3-001", "objective": "5.3", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which value does R1 accept at the privileged EXEC prompt?",
  "exhibit": {"kind": "config", "content": EX_001},
  "options": opts(
    "Wr3nch-Harbour-42, because enable secret takes precedence.",
    "Harbour42, because enable password is the older command and is read first.",
    "Either value, since both commands populate the same credential store.",
    "Neither, because configuring both together disables privileged access."),
  "correct": ["A"],
  "explanation": "When both are present the secret always wins, and the older enable password is ignored entirely; the secret is also stored as a hash rather than recoverable text, which is why it replaced the earlier command. Option B assumes configuration order decides, when precedence is fixed regardless of where each line sits. Option C treats them as one store, but they are separate and only one is consulted. Option D invents a lockout that would make the pair impossible to configure safely.",
  "difficulty": 2,
  "skills": ["local-passwords", "enable-secret", "enable-password", "device-access-control"],
},
{
  "id": "5.3-002", "objective": "5.3", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What should the reviewer conclude about the two credentials now that the configuration has left the building?",
  "exhibit": {"kind": "config", "content": EX_002},
  "options": opts(
    "Both are safe, because service password-encryption has obscured each of them.",
    "Both must be changed, since neither command stores anything more than plain text.",
    "The netadmin secret must be changed; the backup password is beyond recovery.",
    "The backup password must be changed, as type 7 is reversible to plain text."),
  "correct": ["D"],
  "explanation": "Type 7 is an obfuscation rather than a hash and is trivially reversed with freely available tools, so the backup account's password is effectively public the moment the configuration leaves the organisation. The netadmin credential is stored as type 9, a genuine hash, and is not recoverable in the same way. Option A treats service password-encryption as real protection, which is the misconception the item targets. Option B ignores the difference between the two types. Option C reverses which of the two is at risk.",
  "difficulty": 3,
  "skills": ["local-passwords", "password-encryption", "type-7-reversible", "device-hardening"],
},
{
  "id": "5.3-003", "objective": "5.3", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why are the credentials rejected on every attempt?",
  "exhibit": {"kind": "config", "content": EX_003},
  "options": opts(
    "The RSA key must be regenerated after the domain name is set.",
    "login local checks a local user database, and no username is configured.",
    "transport input ssh has to be paired with transport output ssh to work.",
    "The enable secret has to be removed before local logins will be accepted."),
  "correct": ["B"],
  "explanation": "login local tells the line to authenticate against locally configured usernames, and this configuration defines none, so every attempt fails no matter what is typed; adding a username with a secret resolves it. Option A reverses the ordering, since the domain name must exist before the key is generated and this configuration does that correctly. Option C invents a pairing requirement, as transport output governs outbound sessions from the device. Option D confuses the enable secret, which guards privileged mode after login rather than login itself.",
  "difficulty": 2,
  "skills": ["local-passwords", "login-local", "username-database", "troubleshoot-access"],
},
{
  "id": "5.3-004", "objective": "5.3", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does this message indicate about the vty configuration?",
  "exhibit": {"kind": "cli_output", "content": EX_004},
  "options": opts(
    "The device is refusing Telnet because only SSH is permitted on those lines.",
    "The vty lines have run out of free sessions and are turning connections away.",
    "login was configured without a line password, so the device refuses access.",
    "The connection was closed because no enable secret has been configured yet."),
  "correct": ["C"],
  "explanation": "The plain login command tells the line to check a password configured on that line, and when none exists IOS refuses the session outright rather than letting anyone in unauthenticated, which is the safe behaviour and exactly what the message reports. Option A is contradicted by transport input telnet permitting the protocol used. Option B describes exhausted vty sessions, which produce a different refusal. Option D points at the enable secret, which is consulted only after a successful login.",
  "difficulty": 2,
  "skills": ["local-passwords", "login-command", "vty-lines", "troubleshoot-access"],
},
{
  "id": "5.3-005", "objective": "5.3", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which account can enter privileged EXEC mode without supplying a further credential?",
  "exhibit": {"kind": "cli_output", "content": EX_005},
  "options": opts("netadmin", "helpdesk", "backup", "monitor"),
  "correct": ["A"],
  "explanation": "Privilege level 15 places an account straight into privileged EXEC on login, and netadmin is the only one configured with it. Options B, C and D are all set to privilege 1, which lands them in user EXEC and requires the enable secret before they can go further. All four store their credential as type 9, so the difference between them is the privilege level rather than how the password is held.",
  "difficulty": 1,
  "skills": ["local-passwords", "privilege-levels", "verify-access-control", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "5" / "5.3.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "5.3",
    "domain": 5,
    "blueprint_version": "v1.1",
    "scope_note": ("A password in the configuration is not the same as a password "
                   "protecting something: type 7 reversibility, login with no "
                   "password, and login local with no user database."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
