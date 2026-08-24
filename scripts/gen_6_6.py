#!/usr/bin/env python3
"""Generate bank/6/6.6.json - 'Recognize the capabilities of configuration
management mechanisms such as Ansible and Terraform'.

The two tools v1.1 names, and only those. Puppet and Chef were removed from the
blueprint at v1.1 and do not appear here, not even as distractors, because a
distractor naming a retired tool teaches the wrong map of the subject.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

EX_001 = """A team is choosing how to push configuration to 180 switches.

    Requirement
    ---------------------------------------------------------------
    Nothing may be installed on the switches themselves
    The control host initiates the work; devices are never asked to poll
    Connections use SSH or the device API, already open for management
    Running the same job twice must not change a device the second time"""

EX_002 = """---
- name: Access layer baseline
  hosts: access_switches
  gather_facts: false
  tasks:
    - name: Ensure Loopback0 exists and is up
      cisco.ios.ios_interfaces:
        config:
          - name: Loopback0
            enabled: true
        state: merged"""

EX_003 = """$ terraform plan

Terraform used the selected providers to generate the following
execution plan. Resource actions are indicated with the following
symbols:
  + create

Terraform will perform the following actions:

  # iosxe_interface.loopback10 will be created
  + resource "iosxe_interface" "loopback10" {
      + name        = "Loopback10"
      + description = "automation test"
      + enabled     = true
    }

Plan: 1 to add, 0 to change, 0 to destroy."""

EX_004 = """$ terraform apply

  # iosxe_interface.loopback20 will be updated in-place
  ~ resource "iosxe_interface" "loopback20" {
        name        = "Loopback20"
      ~ description = "old text" -> "branch uplink test"
        enabled     = true
    }

Plan: 0 to add, 1 to change, 0 to destroy."""

ITEMS = [
{
  "id": "6.6-001", "objective": "6.6", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which mechanism matches this way of working?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "A tool needing a small agent on each switch, reporting to a central master.",
    "Ansible, which is agentless and pushes over SSH or the device API.",
    "A tool where each device pulls its own configuration on a timer.",
    "Any of them, since every current tool works in essentially this way."),
  "correct": ["B"],
  "explanation": "Nothing installed on the devices, work started from a control host and carried over connections already open for management describes an agentless push model, which is how Ansible operates; its modules are also written to be idempotent, so a repeated run changes nothing. Option A requires the agent the first line forbids. Option C describes a pull model, where devices initiate rather than the control host. Option D denies a distinction the requirement is written around.",
  "difficulty": 2,
  "skills": ["configuration-management", "ansible", "agentless", "push-model"],
},
{
  "id": "6.6-002", "objective": "6.6", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does running this playbook do?",
  "exhibit": {"kind": "config", "content": EX_002},
  "options": opts(
    "It collects facts from every switch and writes them into a report.",
    "It removes Loopback0 from any switch on which it is found.",
    "It runs against one named switch rather than against a group.",
    "It ensures Loopback0 exists and is enabled on the access switches."),
  "correct": ["D"],
  "explanation": "The hosts line targets the access_switches group, the task names the desired outcome, and state merged tells the module to bring the device to that state without touching anything else, so a switch already correct is left alone. Option A is contradicted by gather_facts being false and by there being no reporting task. Option B would need a state that removes rather than merges. Option C misreads a group name as a single hostname.",
  "difficulty": 2,
  "skills": ["configuration-management", "ansible", "playbook", "idempotency"],
},
{
  "id": "6.6-003", "objective": "6.6", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What has this command actually done?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts(
    "Previewed the difference between the declared state and what exists.",
    "Applied the change to the device and reported exactly what it altered afterwards.",
    "Checked the file for syntax errors without contacting anything.",
    "Reversed the previous run, removing what that run had created."),
  "correct": ["A"],
  "explanation": "A plan is a dry run: the tool reads the declared desired state, compares it against what it has recorded and against the device, and prints the actions that would close the gap, which is why the summary counts what would be added rather than what was. Option B describes apply, the separate step that follows. Option C describes a purely local check, but a plan consults the provider to see what exists. Option D describes a destroy.",
  "difficulty": 3,
  "skills": ["configuration-management", "terraform", "declarative", "plan-and-apply"],
},
{
  "id": "6.6-004", "objective": "6.6", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What will happen to Loopback20 when this runs?",
  "exhibit": {"kind": "cli_output", "content": EX_004},
  "options": opts(
    "It will be created, since the resource is listed in the plan.",
    "It will be destroyed and rebuilt with the new description.",
    "Its description will be changed and nothing else about it.",
    "Nothing, because the summary counts no resources to add."),
  "correct": ["C"],
  "explanation": "The tilde marks a change in place and sits against the description line alone, while name and enabled are shown unchanged, so a single attribute is updated and the interface is never removed. The summary agrees: nothing to add, one to change, nothing to destroy. Option A misreads an update as a creation. Option B describes a replacement, which would count one to add and one to destroy. Option D reads only the add column.",
  "difficulty": 1,
  "skills": ["configuration-management", "terraform", "plan-and-apply", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "6" / "6.6.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "6.6", "domain": 6, "blueprint_version": "v1.1",
    "scope_note": ("Ansible and Terraform only. Puppet and Chef were removed from the "
                   "blueprint at v1.1 and do not appear, not even as distractors."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
