#!/usr/bin/env python3
"""Generate bank/4/4.5.json - 'Describe the use of syslog features'.

Facilities and severity levels. The severity table is supplied in the exhibit
where an item turns on it, so the candidate reads a real message against a
reference rather than reciting eight words in order.

002 is the item that matters operationally: logging trap sets a threshold, and
the counter-intuitive part is that a LOWER number is MORE severe, so a trap
level of 4 sends levels 0 through 4 and silently discards everything above.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

LEVELS = """    Level  Keyword          Meaning
    -----  --------------   ------------------------------
      0    emergencies      system unusable
      1    alerts           immediate action needed
      2    critical         critical condition
      3    errors           error condition
      4    warnings         warning condition
      5    notifications    normal but significant
      6    informational    informational message
      7    debugging        debugging output"""

EX_001 = """A message arrives at the syslog server from a switch.

    %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/7,
    changed state to down

""" + LEVELS

EX_002 = """! R2 - relevant configuration
!
logging host 10.9.9.40
logging trap 4
!

Four messages are generated on R2 in the next minute:

    %LINK-3-UPDOWN: Interface GigabitEthernet0/1, changed state to down
    %SYS-5-CONFIG_I: Configured from console by netadmin on vty0
    %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Gi0/1 from FULL to DOWN
    %SYS-2-MALLOCFAIL: Memory allocation of 4096 bytes failed

""" + LEVELS

EX_003 = """Two messages arrive within the same second from the same router.

    %SYS-2-MALLOCFAIL: Memory allocation of 4096 bytes failed
    %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 10.9.9.40 started

""" + LEVELS

EX_004 = """A message recorded on the syslog server

    %SEC-6-IPACCESSLOGP: list 110 denied tcp 10.20.4.55(51204) ->
    10.90.1.10(22), 1 packet

""" + LEVELS

ITEMS = [
{
  "id": "4.5-001", "objective": "4.5", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which part of this message names the facility that raised it?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts("UPDOWN", "5", "LINEPROTO", "GigabitEthernet0/7"),
  "correct": ["C"],
  "explanation": "A syslog message is built as facility, then severity, then mnemonic, so LINEPROTO is the facility, 5 is the severity and UPDOWN is the mnemonic naming the specific event. Option A is that mnemonic. Option B is the severity, which places the message at notifications. Option D is a value from the message text, describing what the event concerns rather than which subsystem reported it.",
  "difficulty": 2,
  "skills": ["syslog", "facilities", "severity-levels", "message-format"],
},
{
  "id": "4.5-002", "objective": "4.5", "domain": 4, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Which two of the four messages reach the syslog server? (Choose two.)",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "%LINK-3-UPDOWN: Interface GigabitEthernet0/1, changed state to down",
    "%SYS-5-CONFIG_I: Configured from console by netadmin on vty0",
    "%OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Gi0/1 from FULL to DOWN",
    "%SYS-2-MALLOCFAIL: Memory allocation of 4096 bytes failed",
    "None of them, since logging trap 4 excludes every level shown"),
  "correct": ["A", "D"],
  "explanation": "logging trap 4 forwards everything at level 4 or more severe, and severity counts downward, so levels 0 through 4 are sent while 5 through 7 are discarded; that captures the level 3 link message and the level 2 memory failure. Options B and C both sit at level 5, notifications, and are dropped, which is how a trap level set too low silently loses configuration and adjacency changes. Option E inverts the scale, treating a higher number as more severe.",
  "difficulty": 3,
  "skills": ["syslog", "logging-trap", "severity-levels", "log-filtering"],
},
{
  "id": "4.5-003", "objective": "4.5", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which message should be dealt with first, and why?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "The LOGGINGHOST message, since level 6 outranks level 2 on this scale.",
    "Neither is urgent; both sit in the routine half of the severity range.",
    "Both equally, as messages from one facility carry the same weight.",
    "The MALLOCFAIL message, because level 2 is nearer the severe end."),
  "correct": ["D"],
  "explanation": "Severity runs from 0 as the most serious to 7 as the least, so the level 2 memory allocation failure is a critical condition while the level 6 logging notice is informational housekeeping. Option A reads the scale backwards, which is the mistake this item exists to catch. Option B places level 2 in the routine half, when the table marks it critical. Option C treats the shared SYS facility as making them equivalent, but the facility says which subsystem spoke rather than how much it matters.",
  "difficulty": 2,
  "skills": ["syslog", "severity-levels", "triage", "message-format"],
},
{
  "id": "4.5-004", "objective": "4.5", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. At which severity level was this message recorded?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts("110", "2", "6", "1"),
  "correct": ["C"],
  "explanation": "The severity is the number between the facility and the mnemonic, so SEC-6-IPACCESSLOGP is level 6, informational, which is the usual level for an access list logging a match. Option A is the access list number taken from the message text. Option B and option D are severities that appear nowhere in this message; the value 1 is the packet count at the end of the line, which is a different number entirely.",
  "difficulty": 1,
  "skills": ["syslog", "severity-levels", "message-format", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "4" / "4.5.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "4.5", "domain": 4, "blueprint_version": "v1.1",
    "scope_note": ("The severity table is supplied in the exhibit, so items test "
                   "reading a real message against it rather than reciting it."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
