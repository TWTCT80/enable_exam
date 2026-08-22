#!/usr/bin/env python3
"""Generate bank/1/1.12.json - 'Explain virtualization fundamentals'.

The objective names server virtualization, containers and VRFs. VRFs carry the
two harder items because they are the only part with real device output behind
them: show vrf, and two routing tables holding the same prefix at once, which
demonstrates the separation rather than asserting it.

Containers and server virtualization have no CLI on a Cisco device, so 002
compares two deployment models described in the exhibit and makes the candidate
work out which is which from their stated properties - not from the words
"container" or "hypervisor", which deliberately do not appear.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import LEGEND, kid, parent, show_vrf, vrf_row, opts  # noqa: E402


def vrf_route_table(prompt, vrf, lines):
    """A `show ip route vrf <name>` capture, with its Routing Table header."""
    return "\n".join([
        f"{prompt}# show ip route vrf {vrf}",
        "",
        f"Routing Table: {vrf}",
        LEGEND,
        "",
        "Gateway of last resort is not set",
        "",
    ] + lines)


SEP = "-" * 58

# --- exhibits -------------------------------------------------------------

EX_001 = "\n".join([
    vrf_route_table("R1", "CUSTOMER-A", [
        parent("192.168.10.0/24 is variably subnetted, 2 subnets, 2 masks"),
        kid("C", "192.168.10.0/24 is directly connected, GigabitEthernet0/1"),
        kid("L", "192.168.10.1/32 is directly connected, GigabitEthernet0/1"),
    ]),
    SEP,
    vrf_route_table("R1", "CUSTOMER-B", [
        parent("192.168.10.0/24 is variably subnetted, 2 subnets, 2 masks"),
        kid("C", "192.168.10.0/24 is directly connected, GigabitEthernet0/2"),
        kid("L", "192.168.10.1/32 is directly connected, GigabitEthernet0/2"),
    ]),
])

EX_002 = """Two ways of packaging the same set of applications onto one physical
server were trialled and measured.

    Property                     Model X            Model Y
    -------------------------    ---------------    ---------------
    Operating system per         one each           none; all share
    workload                                        the host's kernel
    Typical image size           several GB         tens of MB
    Time from start to serving   tens of seconds    under a second
    Isolation boundary           virtual hardware   kernel features"""

EX_003 = show_vrf("R3", [
    vrf_row("MGMT", "<not set>", "ipv4", "Gi0/0"),
    vrf_row("CUSTOMER-A", "65000:100", "ipv4", "Gi0/1,Gi0/3"),
    vrf_row("CUSTOMER-B", "65000:200", "ipv4", "Gi0/2"),
])


ITEMS = [
{
  "id": "1.12-001", "objective": "1.12", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Both tables on this one router hold 192.168.10.0/24 pointing at different interfaces. What makes that possible?",
  "exhibit": {"kind": "cli_output", "content": EX_001},
  "options": opts(
    "Each VRF has its own routing table, so the same prefix can exist once in each.",
    "The router load-balances the prefix across both interfaces as equal-cost paths.",
    "The second entry overrides the first, and only CUSTOMER-B can reach the subnet.",
    "The prefixes differ in mask, so longest prefix match separates the two entries."),
  "correct": ["A"],
  "explanation": "A VRF gives the router a separate routing and forwarding instance, so R1 maintains one table per customer and each may carry the same address space without conflict, which is what lets a provider serve two customers who both chose 192.168.10.0/24. Option B describes equal-cost paths, which apply within one table rather than across two. Option C assumes one entry wins, but both tables are shown populated and both are live. Option D looks for a mask difference, and the two prefixes are identical.",
  "difficulty": 3,
  "skills": ["virtualization", "vrf", "overlapping-address-space", "separate-routing-tables"],
},
{
  "id": "1.12-002", "objective": "1.12", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which model packages its workloads as containers, and what follows from the measurements?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "Model X, and its workloads start faster because no separate kernel has to boot.",
    "Model X, because sharing virtual hardware is what defines a container runtime.",
    "Model Y, and its workloads start faster because no guest OS has to boot.",
    "Model Y, and each of its workloads carries a full operating system of its own."),
  "correct": ["C"],
  "explanation": "Model Y runs no operating system per workload and shares the host kernel, which is exactly what a container does, and that is why its images are tens of megabytes and it serves in under a second: there is no guest system to start. Option A attaches the fast start to Model X, whose own row records tens of seconds. Option B calls virtual hardware a container property, when the exhibit lists it as Model X's isolation boundary. Option D contradicts Model Y's own row, which records no operating system per workload.",
  "difficulty": 2,
  "skills": ["virtualization", "containers", "server-virtualization", "compare-deployment-models"],
},
{
  "id": "1.12-003", "objective": "1.12", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which interfaces has R3 placed in the CUSTOMER-A instance?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts("Gi0/0 and Gi0/1", "Gi0/1 and Gi0/3", "Gi0/2 only", "Gi0/1 and Gi0/2"),
  "correct": ["B"],
  "explanation": "The Interfaces column lists what each instance owns, and the CUSTOMER-A row names Gi0/1 and Gi0/3, so traffic arriving on either is looked up in that instance's own table. Option A pairs a CUSTOMER-A interface with Gi0/0, which belongs to the separate MGMT instance. Option C is the single interface held by CUSTOMER-B. Option D pairs one CUSTOMER-A interface with one from CUSTOMER-B, which would defeat the separation the instances exist to provide.",
  "difficulty": 1,
  "skills": ["virtualization", "vrf", "show-vrf", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "1" / "1.12.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "1.12",
    "domain": 1,
    "blueprint_version": "v1.1",
    "scope_note": ("VRFs carry the harder items because they have real device output "
                   "behind them. The container item withholds the words 'container' "
                   "and 'hypervisor' from the exhibit so the candidate classifies on "
                   "properties rather than labels."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
