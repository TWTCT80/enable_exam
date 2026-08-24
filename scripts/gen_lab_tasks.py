#!/usr/bin/env python3
"""Generate app/lab-tasks.md - one Packet Tracer task per configure-and-verify
objective.

Simulations and simlets cannot be reproduced honestly in a web app, so the
runner does not pretend to. These tasks are the substitute: build it, state what
must be true, verify it with a real command, then break it deliberately and
watch the output change.

The list of objectives is read from blueprint/objectives.json rather than typed
here, so it covers exactly the 15 objectives Cisco marks configure-and-verify
and uses their published wording.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLUEPRINT = ROOT / "blueprint" / "objectives.json"
DEST = ROOT / "app" / "lab-tasks.md"

# objective id -> (build, goal, verify, break_it, caveat or None)
TASKS = {
"1.6": (
 "One router, two switches, four PCs. Two PCs on each switch.",
 "Divide 192.168.20.0/24 into four equal subnets. Put each switch's PCs in a "
 "different one, give the router a subinterface or a second interface per "
 "subnet, and address every host correctly for its own block.",
 "`show ip interface brief` on the router, then ping the gateway from each PC.",
 "Change one PC's mask from /26 to /24 and ping a host in a neighbouring "
 "subnet. It will now believe that host is local, ARP for it, and get nothing.",
 None),

"1.8": (
 "Two routers cabled directly to one another.",
 "Put 2001:DB8:ACAD:12::/64 on the link. Configure one side manually and let "
 "the other build its address with the eui-64 keyword. Enable IPv6 routing on "
 "both.",
 "`show ipv6 interface brief`. Confirm the EUI-64 side matches the MAC with "
 "FFFE inserted and the seventh bit inverted, then ping both the link-local "
 "and the global address.",
 "Remove `ipv6 unicast-routing` from one router. Pings to its own interface "
 "still succeed while anything transiting it stops, which is what makes this "
 "fault look like a routing problem.",
 None),

"2.1": (
 "Two switches joined by one link, two PCs on each.",
 "Create VLAN 10 and VLAN 20 on both switches. Put one PC per VLAN on each "
 "switch. Hosts in the same VLAN must reach each other across the link; hosts "
 "in different VLANs must not.",
 "`show vlan brief` on both switches, then ping within and across VLANs.",
 "Delete VLAN 20 from the second switch only. Its access port goes inactive "
 "and those hosts stop passing traffic even though the trunk is fine.",
 None),

"2.2": (
 "The two switches from task 2.1.",
 "Make the link a static 802.1Q trunk. Set the native VLAN to 99 on both ends "
 "and allow only VLANs 10, 20 and 99 across it.",
 "`show interfaces trunk`. Check the Mode, Native vlan and the allowed list, "
 "and confirm all four sections agree.",
 "Set the native VLAN to 1 on one side only. The trunk stays up and tagged "
 "VLANs keep working, and the console logs "
 "`%CDP-4-NATIVE_VLAN_MISMATCH`. Note that nothing appears broken.",
 None),

"2.3": (
 "Three devices in a line: router, switch, switch.",
 "Using only discovery protocol output, work out the full topology from the "
 "middle device: who is on each port, what platform they are, and which of "
 "their interfaces faces you.",
 "`show cdp neighbors detail`. Read the Interface field as local and the Port "
 "ID field as remote; they sit on one line and are easy to swap.",
 "Enter `no cdp run` on one neighbour. It disappears from your table while "
 "still forwarding traffic normally. Then enable LLDP on both and compare.",
 "Packet Tracer supports CDP fully; LLDP support depends on the version and "
 "device model."),

"2.4": (
 "Two switches joined by two parallel links.",
 "Bundle both links into one Layer 2 EtherChannel using LACP, with one side "
 "active and the other passive, and carry a trunk over the bundle.",
 "`show etherchannel summary`. Look for `(SU)` on the port-channel and `(P)` "
 "against each member.",
 "Change the allowed VLAN list on one member port only. That port is suspended "
 "with `(s)` while the bundle stays up on the other, which is the fault that "
 "halves your bandwidth quietly.",
 None),

"3.3": (
 "Three routers in a line, a LAN behind each end, plus a second path between "
 "the outer two.",
 "Give every LAN full reachability using static routes only. Then add a "
 "floating static over the second path as a backup for one prefix.",
 "`show ip route`. The floating static must NOT appear while the primary is up.",
 "Shut the primary link. Watch the floating static install, then bring the link "
 "back and watch it withdraw again. If it never appeared, its distance was too "
 "low; if it never installs, check the next hop is resolvable.",
 None),

"3.4": (
 "Three routers in a triangle, one LAN behind each.",
 "Run single-area OSPFv2 across all three. Set a deterministic router ID on "
 "each with the `router-id` command. Make one link point-to-point with "
 "`ip ospf network point-to-point`.",
 "`show ip ospf neighbor`. The point-to-point link shows `FULL/  -` with no "
 "elected role; the others show `FULL/DR` or `FULL/BDR`.",
 "Set `ip ospf hello-interval 5` on one end of a link. The adjacency drops and "
 "will not re-form, with no message explaining why. Compare "
 "`show ip ospf interface` on both ends to find it.",
 None),

"4.1": (
 "An inside LAN, a router, and a server standing in for the internet.",
 "Configure PAT so the whole inside subnet shares one public address. Then add "
 "a static NAT so one inside server is reachable at a fixed public address.",
 "`show ip nat translations` while traffic flows, and `show ip nat statistics` "
 "for the pool figures.",
 "Remove `ip nat inside` from the LAN interface. Traffic still routes to the "
 "next hop and the translation table simply stays empty, with no error at any "
 "point.",
 None),

"4.2": (
 "Two routers with a working link between them.",
 "Make one an authoritative time source with `ntp master`. Point the other at "
 "it with `ntp server`. Wait for synchronisation, which takes a few minutes.",
 "`show ntp status` on the client. It must read synchronized with a stratum "
 "one higher than the master's.",
 "Block NTP from the client with an access list. Watch the client fall to "
 "`Clock is unsynchronized, stratum 16` and note that it keeps forwarding "
 "traffic and logging the whole time, with timestamps now meaningless.",
 "Packet Tracer's NTP implementation is simplified; synchronisation may "
 "behave differently from real IOS."),

"4.6": (
 "A router, a switch with two VLANs, and a DHCP server in the second VLAN.",
 "Configure the router to relay requests from the client VLAN to the server "
 "with `ip helper-address`. Separately, set the router's WAN-facing interface "
 "to obtain its own address with `ip address dhcp`.",
 "`show ip interface brief` on the router; the WAN interface's Method column "
 "reads DHCP. Then check the server's binding list for the client leases.",
 "Remove the helper address. Clients broadcast, nothing answers, and they fall "
 "back to a 169.254 address, while a host placed in the server's own VLAN gets "
 "a lease immediately.",
 None),

"5.3": (
 "One switch with a management address.",
 "Set an `enable secret`, create a local username with a secret, restrict the "
 "vty lines to SSH with `login local`, and put a password on the console.",
 "Try Telnet from a PC and confirm it is refused. Then connect over SSH and "
 "confirm you reach user EXEC and need the enable secret to go further.",
 "Add `service password-encryption` and look at the running configuration. The "
 "type 7 values look protected but are reversible; the type 9 secrets are not. "
 "That difference is the whole point.",
 None),

"5.6": (
 "A router with two LANs and a server on one of them.",
 "Write an extended access list that stops one host reaching one service on "
 "that server while leaving all its other traffic, and everyone else's access "
 "to the server, untouched. Apply it inbound close to the source.",
 "`show access-lists` and read the match counters after generating traffic.",
 "Add a permit for the blocked host BELOW the deny. Its counter stays at zero "
 "because the deny matches first. Move it above and watch the counters swap "
 "over.",
 None),

"5.7": (
 "A switch with two PCs and an uplink.",
 "Configure port security on both access ports: maximum one address, sticky "
 "learning, violation mode restrict. Then enable DHCP snooping on the VLAN and "
 "trust the uplink only.",
 "`show port-security interface` for the sticky address and violation count, "
 "and `show ip dhcp snooping` for the trust table.",
 "Swap the two PCs between ports. Each port now sees an address that is not "
 "its sticky one and the violation counter climbs while the port stays up, "
 "which is exactly what restrict mode is for. Then set one port to shutdown "
 "mode and repeat to compare.",
 "Packet Tracer's DHCP snooping support varies by version and may be absent. "
 "If it is, do the port security half here and the snooping half on real gear, "
 "CML or GNS3."),

"5.10": (
 "A wireless LAN controller, one lightweight access point, and a wireless "
 "client.",
 "Join the access point to the controller. Create a WLAN in the controller GUI "
 "using WPA2 with PSK and AES, mapped to its own interface and VLAN. Enable "
 "the WLAN.",
 "The client associates and obtains an address. In the GUI, confirm Layer 2 "
 "Security reads WPA+WPA2, WPA2 Encryption reads AES and Authentication Key "
 "Mgmt reads PSK.",
 "Change the key management to 802.1X with no RADIUS server configured. The "
 "SSID is still advertised and every association fails, which looks like a "
 "radio problem and is not.",
 "Packet Tracer 8.x includes a 3504 controller; earlier versions do not. On a "
 "version without one, use the access point's own GUI for the WPA2 PSK half."),
}


def main() -> int:
    bp = json.loads(BLUEPRINT.read_text())
    cv = [o for o in bp["objectives"] if o.get("config_verify")]

    missing = [o["id"] for o in cv if o["id"] not in TASKS]
    extra = [k for k in TASKS if k not in {o["id"] for o in cv}]
    if missing or extra:
        print(f"FATAL: task list out of step with the blueprint. "
              f"missing={missing} extra={extra}", file=sys.stderr)
        return 1

    out = [
        "# Packet Tracer lab tasks",
        "",
        f"For every **configure and verify** objective in the "
        f"{bp['exam']} {bp['blueprint_version']} blueprint - 15 of the 53.",
        "",
        "The exam includes simulations and simlets. Those cannot be reproduced",
        "honestly in a web app, so the runner does not try; this is the substitute.",
        "Each task names what to build, what must be true when you are done, the",
        "command that proves it, and a fault to introduce deliberately.",
        "",
        "**Break it on purpose.** The written items in this bank lean heavily on",
        "faults where every interface is up and the configuration reads as though",
        "it should work. You will recognise those far faster having watched the",
        "output change under your own hands than by reading about them.",
        "",
        "---",
        "",
    ]

    for o in cv:
        build, goal, verify, break_it, caveat = TASKS[o["id"]]
        out += [
            f"## {o['id']}  {o['text']}",
            "",
            f"**Build.** {build}",
            "",
            f"**Goal.** {goal}",
            "",
            f"**Verify.** {verify}",
            "",
            f"**Break it.** {break_it}",
            "",
        ]
        if caveat:
            out += [f"> **Tool note.** {caveat}", ""]
        out += ["---", ""]

    out += [
        "## If a task will not run in Packet Tracer",
        "",
        "Packet Tracer implements a subset of IOS, and the subset moves between",
        "versions. Where a note above says support is uncertain, the honest answer",
        "is to check on your own version rather than assume: configure it and see",
        "whether the verification command returns what it should.",
        "",
        "Where it genuinely will not, Cisco Modeling Labs, GNS3 or real hardware",
        "run the same commands. The tasks are written against IOS behaviour, not",
        "against any one simulator.",
        "",
    ]

    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text("\n".join(out))
    print(f"wrote {DEST} - {len(cv)} tasks, one per configure-and-verify objective")
    return 0


if __name__ == "__main__":
    sys.exit(main())
