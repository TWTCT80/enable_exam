#!/usr/bin/env python3
"""Generate bank/6/6.1.json - 'Explain how automation impacts network management'.

Both directions of the impact. 002 is deliberately the harder one: automation
removes the delay that used to limit a mistake to one device, so the same
property that makes it valuable is what makes a bad template expensive.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

EX_001 = """An audit of 180 access switches, all built from the same design
document over four years by six engineers.

    Finding
    ---------------------------------------------------------------
    41 switches carry an NTP server the standard no longer lists
    17 have a logging host that was decommissioned in 2024
    9 permit Telnet on their vty lines
    Every one of them was configured by hand, by someone following
    the same document"""

EX_002 = """A team introduces automation and pushes a corrected NTP and logging
baseline to all 180 access switches in one run.

    Outcome
    ---------------------------------------------------------------
    The run completes in eleven minutes
    All 180 switches now match the standard exactly
    The template also carried a typo in the management ACL, which is
    now present on all 180 switches
    The previous manual process would have reached perhaps four
    switches in that time"""

EX_003 = """The intended configuration for every access switch is held in a
version-controlled repository. Any change is proposed, reviewed and
merged there, and the automation applies whatever the repository holds.

    Question put to the team
    ---------------------------------------------------------------
    "Someone made an emergency change directly on SW-ACC-14 at 02:00
     last night. What happens to it?" """

EX_004 = """Two ways of applying the same change to 180 switches

    Aspect                  By hand                Automated
    --------------------    -------------------    -----------------
    Time to complete        several days           minutes
    Variation between       likely, and grows      none; one source
    devices                 with each engineer     produces all
    Record of what changed  whatever was noted     the run itself
    Effect of an error      one device at a time   every device at once"""

ITEMS = [
{
  "id": "6.1-001", "objective": "6.1", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which problem do these findings describe?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "A hardware fault common to a batch of switches from one supplier.",
    "Configuration drift, where devices diverge from the standard over time.",
    "A routing problem, since the affected switches cannot reach the servers.",
    "A licensing lapse that has reverted features to their defaults."),
  "correct": ["B"],
  "explanation": "One design document, six engineers and four years produced 180 switches that no longer agree with the standard or with each other, which is configuration drift; it accumulates precisely because each change is applied by a person, once, from memory or from a document that has since moved on. Option A blames hardware for settings that were typed in. Option C describes reachability, and the finding is about which values are configured. Option D invents a licensing mechanism that does not rewrite an NTP server address.",
  "difficulty": 2,
  "skills": ["automation-impact", "configuration-drift", "consistency", "network-management"],
},
{
  "id": "6.1-002", "objective": "6.1", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does this outcome illustrate about automation?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "That automation is unsuitable for changes affecting management access.",
    "That the eleven-minute run was too fast and should have been throttled.",
    "That the typo would have been avoided had the run been done by hand.",
    "That it applies a mistake as widely and as quickly as a correction."),
  "correct": ["D"],
  "explanation": "The same property that fixed 180 switches in eleven minutes carried the ACL typo to all 180 in the same run, because automation removes the delay that used to confine an error to whichever device someone was working on. That is an argument for reviewing and testing the template, not for going back to typing. Option A rules out a use it handles well. Option B treats speed as the fault rather than the absence of a check. Option C assumes a manual process would have caught it, when the same person wrote both.",
  "difficulty": 3,
  "skills": ["automation-impact", "blast-radius", "change-testing", "network-management"],
},
{
  "id": "6.1-003", "objective": "6.1", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What becomes of the overnight change?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "The next run overwrites it, since the repository is the source of truth.",
    "It is merged into the repository automatically at the next run.",
    "It persists, because automation only adds configuration and never removes it.",
    "The automation halts on that switch and reports a conflict for review."),
  "correct": ["A"],
  "explanation": "When the repository holds the intended state and the automation applies whatever it holds, anything changed on the device outside that flow is undone the next time the job runs; keeping the fix means putting it through the repository. Option B has the device teaching the repository, which reverses the direction of authority. Option C describes an additive tool, and applying a declared state removes what is not declared. Option D describes a behaviour some tools can be configured for but not the default this arrangement implies.",
  "difficulty": 2,
  "skills": ["automation-impact", "source-of-truth", "version-control", "configuration-drift"],
},
{
  "id": "6.1-004", "objective": "6.1", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which row records a cost of automating rather than a benefit?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts(
    "Time to complete", "Variation between devices",
    "Effect of an error", "Record of what changed"),
  "correct": ["C"],
  "explanation": "Three rows favour automation plainly, but the last one does not: an error reaching every device at once is worse than an error reaching one, and it is the row that justifies review, testing and staged rollout. Option A shows days becoming minutes. Option B shows variation disappearing. Option D shows an ad hoc note replaced by the run itself as the record, which is a gain in traceability.",
  "difficulty": 1,
  "skills": ["automation-impact", "blast-radius", "network-management", "read-correct-row"],
},
]
dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "6" / "6.1.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({"objective": "6.1", "domain": 6,
    "blueprint_version": "v1.1",
    "scope_note": "Both directions of the impact, including what automation makes worse.",
    "items": ITEMS}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
