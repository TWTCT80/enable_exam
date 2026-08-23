#!/usr/bin/env python3
"""Generate bank/5/5.7.json - 'Configure and verify Layer 2 security features'.

All three features the objective names, and the dependency between two of them:
dynamic ARP inspection validates against the DHCP snooping binding table, so
enabling DAI without snooping drops every ARP on an untrusted port (006). That
chain is the part candidates miss.

The DAI and DHCP snooping tables whose column justification I could not confirm
are avoided; the items use the line-oriented status output, the trust table at
the foot of `show ip dhcp snooping`, configurations and real log messages.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import (port_security_interface, dhcp_snooping, snoop_trust,
                    opts)  # noqa: E402

# --- exhibits -------------------------------------------------------------

EX_001 = port_security_interface("SW1", "GigabitEthernet0/5", [
    ("Port Security", "Enabled"),
    ("Port Status", "Secure-shutdown"),
    ("Violation Mode", "Shutdown"),
    ("Aging Time", "0 mins"),
    ("Aging Type", "Absolute"),
    ("Maximum MAC Addresses", "1"),
    ("Total MAC Addresses", "1"),
    ("Configured MAC Addresses", "0"),
    ("Sticky MAC Addresses", "1"),
    ("Last Source Address:Vlan", "00d0.5842.7f22:10"),
    ("Security Violation Count", "1"),
])

EX_002 = """A hot-desking area is being secured with port security.

    Requirement
    ---------------------------------------------------------------
    Traffic from an unexpected MAC address must be discarded
    The port must stay up so the authorised device keeps working
    Each violation must raise a log message and increment a counter
    No engineer visit should be needed to restore service"""

EX_003 = "\n".join([
    "SW3#",
    "*Aug 23 08:41:02.117: %PORT_SECURITY-2-PSECURE_VIOLATION: Security",
    "violation occurred, caused by MAC address 00d0.5842.9a04 on port",
    "GigabitEthernet0/7.",
    "*Aug 23 08:41:02.120: %PM-4-ERR_DISABLE: psecure-violation error",
    "detected on Gi0/7, putting Gi0/7 in err-disable state",
    "SW3#",
    "",
    port_security_interface("SW3", "GigabitEthernet0/7", [
        ("Port Security", "Enabled"),
        ("Port Status", "Secure-shutdown"),
        ("Violation Mode", "Shutdown"),
        ("Aging Time", "0 mins"),
        ("Maximum MAC Addresses", "1"),
        ("Sticky MAC Addresses", "1"),
        ("Last Source Address:Vlan", "00d0.5842.9a04:10"),
        ("Security Violation Count", "1"),
    ]),
    "",
    "The workstation on Gi0/7 was replaced yesterday. The sticky address",
    "still recorded on the port belongs to the machine that was taken away.",
    "No errdisable recovery is configured on SW3.",
])

EX_004 = """                                    +---------------+
    clients --- [ SW-ACC ]--- Gi0/1 ---| DHCP server   |
     Gi0/3..Gi0/20                     | 10.10.10.10   |
                                       +---------------+

DHCP snooping is about to be enabled on SW-ACC for VLAN 10. Every client
port faces a desk; Gi0/1 is the only path toward the DHCP server."""

EX_005 = dhcp_snooping("SW5", "10", [
    snoop_trust("GigabitEthernet0/1", "no", "no", "unlimited"),
    snoop_trust("GigabitEthernet0/3", "no", "no", "10"),
    snoop_trust("GigabitEthernet0/4", "no", "no", "10"),
]) + """

GigabitEthernet0/1 is the uplink toward the DHCP server. Since snooping
was enabled, no client on VLAN 10 has obtained an address."""

EX_006 = """! SW6 - relevant configuration
!
ip arp inspection vlan 10
!
interface GigabitEthernet0/1
 description uplink to distribution
 ip arp inspection trust
!

There is no ip dhcp snooping command anywhere in the configuration.
Since DAI was enabled, every host on VLAN 10 has lost connectivity, and
ARP requests from the desk ports are being discarded."""

EX_007 = "\n".join([
    "SW7#",
    "*Aug 23 09:14:22.418: %SW_DAI-4-DHCP_SNOOPING_DENY: 1 Invalid ARPs",
    "(Req) on Gi0/5, vlan 10.([00d0.5842.7f22/10.10.10.99/0000.0000.0000/",
    "10.10.10.1/09:14:22 UTC Mon Aug 23 2026])",
    "SW7#",
    "",
    "DHCP snooping and dynamic ARP inspection are both operational on",
    "VLAN 10. The binding table records 00d0.5842.7f22 holding the lease",
    "for 10.10.10.55.",
])

EX_008 = dhcp_snooping("SW8", "10,20", [
    snoop_trust("GigabitEthernet0/1", "yes", "yes", "unlimited"),
    snoop_trust("GigabitEthernet0/2", "yes", "yes", "unlimited"),
    snoop_trust("GigabitEthernet0/9", "no", "no", "15"),
    snoop_trust("GigabitEthernet0/10", "no", "no", "15"),
])


ITEMS = [
{
  "id": "5.7-001", "objective": "5.7", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What state is this port in, and what put it there?",
  "exhibit": {"kind": "cli_output", "content": EX_001},
  "options": opts(
    "It is forwarding normally, and the violation counter records an old event.",
    "It is administratively shut down and needs a no shutdown command.",
    "It has been err-disabled by a violation, since the mode is shutdown.",
    "It is protecting itself by dropping frames while staying up."),
  "correct": ["C"],
  "explanation": "Secure-shutdown is the status a port takes after a violation while the mode is set to shutdown, and the violation count of one confirms a single event caused it. Option A misreads the status, since Secure-shutdown means the port is not passing traffic at all. Option B describes an operator-issued shutdown, which would show the port as administratively down instead. Option D describes what the protect or restrict modes do, and this port is set to shutdown.",
  "difficulty": 1,
  "skills": ["port-security", "violation-modes", "err-disable", "verify-port-security"],
},
{
  "id": "5.7-002", "objective": "5.7", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which violation mode satisfies every line of the requirement?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "restrict, which drops the traffic, logs it and counts violations.",
    "protect, which drops the offending traffic and leaves the port up.",
    "shutdown, which err-disables the port the moment a violation occurs.",
    "shutdown paired with an errdisable recovery timer for that cause."),
  "correct": ["A"],
  "explanation": "Restrict is the only mode that does all three things at once: it discards frames from unexpected addresses, keeps the port forwarding for the authorised device, and both logs and counts each violation. Option B drops the traffic and stays up but does so silently, so the security team gets no record. Options C and D both take the port down, which stops the authorised device working, and the recovery timer in option D only shortens the outage rather than avoiding it.",
  "difficulty": 2,
  "skills": ["port-security", "violation-modes", "restrict-mode", "configure-port-security"],
},
{
  "id": "5.7-003", "objective": "5.7", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What is needed to bring Gi0/7 back into service for the replacement machine?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts(
    "Clear the switch's ARP cache so that the new workstation is learned again.",
    "Raise the maximum MAC addresses to two so both machines are permitted.",
    "Wait for the aging timer to expire, after which the port recovers itself.",
    "Remove the stale sticky address, then shut and no shut the port."),
  "correct": ["D"],
  "explanation": "The sticky entry still holds the old machine's address and the port is err-disabled, so both have to be dealt with: clear the learned address, then bounce the port, since err-disable does not clear on its own here. Option A confuses the ARP cache, which maps addresses at Layer 3 and has no bearing on port security. Option B would leave the departed machine permanently authorised and merely postpone the problem. Option C is ruled out by the aging time reading zero, which means aging is disabled.",
  "difficulty": 3,
  "skills": ["port-security", "sticky-mac", "err-disable-recovery", "troubleshoot-port-security"],
},
{
  "id": "5.7-004", "objective": "5.7", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which ports should be configured as trusted for DHCP snooping?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts(
    "The client-facing ports, so that requests from desks are forwarded.",
    "GigabitEthernet0/1 alone, so replies from the server are accepted.",
    "Every port in VLAN 10, since snooping needs to see the whole exchange.",
    "None of them, because trust matters only where a relay agent is used."),
  "correct": ["B"],
  "explanation": "Snooping discards server-sourced messages such as offers and acknowledgements arriving on untrusted ports, which is precisely how it blocks a rogue server plugged into a desk; the legitimate server sits beyond Gi0/1, so that uplink alone is trusted. Option A trusts the desks, which is what the feature exists to prevent. Option C trusts everything and disables the protection entirely. Option D ties trust to relay agents, when it applies wherever snooping runs.",
  "difficulty": 2,
  "skills": ["dhcp-snooping", "trusted-ports", "rogue-dhcp-server", "configure-dhcp-snooping"],
},
{
  "id": "5.7-005", "objective": "5.7", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why has no client obtained an address since snooping was enabled?",
  "exhibit": {"kind": "cli_output", "content": EX_005},
  "options": opts(
    "The client ports need trusting so their requests reach the server.",
    "Snooping has to be removed from the VLAN before leases will be issued.",
    "The uplink is untrusted, so the server's replies are being discarded.",
    "The binding table has reached its limit and refuses to record new leases."),
  "correct": ["C"],
  "explanation": "Every interface in the trust table reads no, including Gi0/1, and an untrusted port drops DHCP offers and acknowledgements, so the requests leave but nothing comes back. Marking Gi0/1 trusted resolves it. Option A trusts the desks, which would defeat the feature and does not address replies being dropped. Option B abandons the protection rather than configuring it. Option D blames the binding table, which stays empty precisely because no lease has ever completed.",
  "difficulty": 3,
  "skills": ["dhcp-snooping", "trusted-ports", "troubleshoot-dhcp-snooping", "verify-dhcp-snooping"],
},
{
  "id": "5.7-006", "objective": "5.7", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why did enabling dynamic ARP inspection break connectivity on VLAN 10?",
  "exhibit": {"kind": "config", "content": EX_006},
  "options": opts(
    "DAI checks each ARP against the snooping bindings, and none exist.",
    "DAI needs an ARP access list before it will permit any traffic at all.",
    "DAI must be enabled globally before it can be applied to a VLAN.",
    "DAI operates only on extended-range VLANs, so VLAN 10 is unsupported."),
  "correct": ["A"],
  "explanation": "Dynamic ARP inspection validates ARP on untrusted ports against the bindings that DHCP snooping records, so without snooping running there is no binding table, nothing validates, and every ARP from a desk port is discarded. Enabling ip dhcp snooping for the VLAN is the missing piece. Option B describes ARP ACLs, which handle statically addressed hosts as a supplement rather than a prerequisite. Option C invents a global command. Option D invents a VLAN range restriction.",
  "difficulty": 2,
  "skills": ["dynamic-arp-inspection", "dhcp-snooping", "binding-table-dependency", "troubleshoot-dai"],
},
{
  "id": "5.7-007", "objective": "5.7", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What did SW7 detect on GigabitEthernet0/5?",
  "exhibit": {"kind": "cli_output", "content": EX_007},
  "options": opts(
    "A host requesting an address from an unauthorised DHCP server.",
    "A port carrying more MAC addresses than port security permits.",
    "An ARP reply arriving on a port trusted for DHCP snooping.",
    "An ARP claiming an address the binding table gives elsewhere."),
  "correct": ["D"],
  "explanation": "The message names an invalid ARP request from 00d0.5842.7f22 claiming 10.10.10.99, while the binding table records that MAC holding 10.10.10.55, so the pairing contradicts the recorded lease and DAI discards it. This is the shape of an ARP spoofing attempt. Option A describes what DHCP snooping catches rather than DAI. Option B describes a port security violation, which logs under a different facility. Option C would be permitted, since trusted ports are exempt from inspection.",
  "difficulty": 2,
  "skills": ["dynamic-arp-inspection", "arp-spoofing", "binding-table", "interpret-log-message"],
},
{
  "id": "5.7-008", "objective": "5.7", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which interfaces would discard a DHCP offer arriving on them?",
  "exhibit": {"kind": "cli_output", "content": EX_008},
  "options": opts(
    "Gi0/1 and Gi0/2, because their rate limit is unlimited.",
    "Gi0/9 and Gi0/10, because both are listed as untrusted.",
    "All four, since offers are only accepted from a relay agent.",
    "None, because snooping records offers rather than discarding them."),
  "correct": ["B"],
  "explanation": "The Trusted column decides: an untrusted port drops server-sourced messages, and Gi0/9 and Gi0/10 both read no. Option A names the two trusted uplinks, which accept offers, and reads the rate limit as though it governed trust. Option C introduces a relay agent the exhibit never mentions. Option D describes what happens on a trusted port, where the offer is recorded into the binding table rather than dropped.",
  "difficulty": 1,
  "skills": ["dhcp-snooping", "trusted-ports", "verify-dhcp-snooping", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "5" / "5.7.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "5.7",
    "domain": 5,
    "blueprint_version": "v1.1",
    "scope_note": ("All three features, plus the dependency between two of them: DAI "
                   "validates against the DHCP snooping binding table, so enabling it "
                   "alone drops every ARP on an untrusted port."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
