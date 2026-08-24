#!/usr/bin/env python3
"""Generate bank/6/6.4.json - 'Explain AI (generative and predictive) and
machine learning in network operations'.

This objective is genuinely part of the published v1.1 blueprint, confirmed
against Cisco's PDF in blueprint/objectives.json. It is NOT the separate
AI/network-operations domain that arrives with v2.0, which this bank excludes.

The split the objective names: predictive systems learn what normal looks like
and flag departures from it; generative systems produce text or configuration.
003 covers the limitation that matters operationally - generated output is
plausible by construction and has to be verified before it is applied.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

EX_001 = """A monitoring platform has been collecting interface counters,
control-plane telemetry and flow records from the campus for nine months.

    Reported this morning
    ---------------------------------------------------------------
    "Utilisation on the DIST-1 to CORE-1 uplink is 4.2 standard
     deviations above the pattern observed for a Monday at 09:00 over
     the preceding thirty-six weeks. No configuration change is
     recorded. Investigate."

No threshold for this interface was ever configured by an engineer."""

EX_002 = """An engineer types the following into an assistant built into the
management platform:

    "Give me the configuration for a new branch router: two LAN
     subnets on 10.44.0.0/22, OSPF area 0 to the WAN link, and a
     floating static as backup."

The assistant returns a complete, syntactically valid configuration in
about two seconds."""

EX_003 = """The assistant's draft for the branch router included:

    interface GigabitEthernet0/3
     description backup circuit
     ip address 203.0.113.6 255.255.255.252
    !
    ip route 0.0.0.0 0.0.0.0 203.0.113.5 130

The branch router model in question has two Gigabit Ethernet interfaces,
numbered 0/0 and 0/1. There is no GigabitEthernet0/3 on the platform,
and the backup circuit terminates on a serial interface."""

ITEMS = [
{
  "id": "6.4-001", "objective": "6.4", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which capability produced this alert?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "A generative model, which composed the wording of the alert from telemetry.",
    "A static threshold, crossed once utilisation passed a configured percentage.",
    "A predictive model, which learned the pattern and flagged a departure.",
    "A scheduled report, comparing this morning's figures against yesterday's."),
  "correct": ["C"],
  "explanation": "The alert is expressed as a deviation from a baseline built over thirty-six weeks of history rather than a fixed percentage, which is what a model trained on past behaviour produces; nobody set a threshold, and that is precisely the point of learning one. Option A confuses how the message was phrased with what detected the condition. Option B is ruled out by no threshold having been configured. Option D compares two days, which could not yield a figure in standard deviations.",
  "difficulty": 2,
  "skills": ["ai-in-network-operations", "predictive-ai", "machine-learning", "anomaly-detection"],
},
{
  "id": "6.4-002", "objective": "6.4", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which kind of capability is the assistant demonstrating here?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "Predictive, since it anticipates the settings the branch will need.",
    "Generative, since it produces new configuration text from a description.",
    "Anomaly detection, comparing the request against known branch designs.",
    "Automation scheduling, queueing the configuration for a later window."),
  "correct": ["B"],
  "explanation": "Producing configuration text that did not previously exist, from a description given in ordinary language, is a generative capability; nothing here forecasts a future state or scores an observation against a baseline. Option A borrows the word predictive for ordinary anticipation, where in this context it means forecasting from learned patterns. Option C describes comparing something observed against normal behaviour, and no observation has been made. Option D describes when a change runs rather than where the text came from.",
  "difficulty": 2,
  "skills": ["ai-in-network-operations", "generative-ai", "configuration-generation", "machine-learning"],
},
{
  "id": "6.4-003", "objective": "6.4", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does this part of the draft illustrate about generated configuration?",
  "exhibit": {"kind": "config", "content": EX_003},
  "options": opts(
    "The model was given the wrong prompt, which is the sole cause of the error.",
    "Generated configuration is unusable in practice and should not be attempted.",
    "The syntax error would have been caught by the device on paste.",
    "Output can be plausible and still wrong, so it needs checking before use."),
  "correct": ["D"],
  "explanation": "Every line is valid IOS and reads exactly like a real backup circuit, yet it names an interface the platform does not have and puts the circuit on the wrong media, so the fault is invisible to anything that only checks syntax. That is the reason generated configuration is reviewed against the actual inventory before it is applied. Option A blames the prompt, which never claimed a third interface. Option B overcorrects into dismissing a useful drafting aid. Option C expects a syntax check to catch a semantically wrong but well-formed command.",
  "difficulty": 3,
  "skills": ["ai-in-network-operations", "generative-ai", "verification", "operational-risk"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "6" / "6.4.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "6.4", "domain": 6, "blueprint_version": "v1.1",
    "scope_note": ("A genuine v1.1 objective, confirmed against Cisco's published PDF. "
                   "Distinct from v2.0's separate AI/network-operations domain, which "
                   "this bank excludes."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
