#!/usr/bin/env python3
"""Generate bank/2/2.8.json - 'Describe network device management access'.

Telnet, SSH, HTTP/HTTPS, console, TACACS+/RADIUS and cloud-managed access.

No port numbers are tested anywhere: the spec bans that recall, so TACACS+ and
RADIUS are separated by what they actually do differently rather than by which
transport and port each uses.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import packet_capture, capture_row, opts  # noqa: E402

# --- exhibits -------------------------------------------------------------

EX_001 = packet_capture([
    capture_row(14, "2.104881", "10.20.5.44", "10.20.5.1", "TELNET", 69,
                "Telnet Data ..."),
    capture_row(19, "2.140552", "10.20.5.1", "10.20.5.44", "TELNET", 84,
                "Telnet Data ..."),
    capture_row(31, "6.882140", "10.20.5.44", "10.20.5.1", "TELNET", 71,
                "Telnet Data ..."),
], "Capture taken on the management segment") + """

Reassembled payload from frames 14 to 31:

    User Access Verification

    Username: netadmin
    Password: Wr3nch-Harbour-42
    SW1>"""

EX_002 = """An access control server is being chosen for the network team.

    Requirement
    ---------------------------------------------------------------
    Junior staff may log in to switches but run only show commands
    Senior staff get full privileges on the same devices
    Every command a user types must be recorded centrally
    The entire exchange with the server must be encrypted, not just
    the password field"""

EX_003 = """A distribution switch has become unreachable. Its uplinks are down,
its management VLAN interface does not answer, and no routing protocol
adjacency to it remains. The switch itself is powered on and its status
lights are normal.

An engineer is standing in the room with the switch and a laptop."""

EX_004 = """! SW4 - relevant configuration
!
hostname SW4
ip domain-name example.internal
crypto key generate rsa modulus 2048
!
username netadmin privilege 15 secret Wr3nch-Harbour-42
!
line vty 0 4
 login local
 transport input telnet
!

Attempts to reach SW4 over SSH are refused, while Telnet connects and
prompts for credentials normally."""

EX_005 = """! SW5 - relevant configuration
!
ip http server
no ip http secure-server
!
line con 0
 password 7 08701E1D5D4C53
 login
!
line vty 0 15
 transport input ssh
 login local
!"""


ITEMS = [
{
  "id": "2.8-001", "objective": "2.8", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does this capture demonstrate about the management protocol in use?",
  "exhibit": {"kind": "cli_output", "content": EX_001},
  "options": opts(
    "The session was encrypted, and the analyser has decrypted it using a stored key.",
    "The password shown is a hash, so the capture reveals nothing an attacker could reuse.",
    "The capture was taken on the device itself, which is why the payload is readable.",
    "Credentials crossed the network in clear text, readable by anyone capturing."),
  "correct": ["D"],
  "explanation": "Telnet carries its payload with no encryption at all, so reassembling the frames yields the username and password exactly as typed, which is why SSH replaced it for device management. Option A credits an encryption the protocol never applied. Option B hopes the value is a hash, but the reassembled stream shows the characters the operator entered. Option C suggests the capture point explains the readability, when a capture anywhere along the path would show the same thing.",
  "difficulty": 1,
  "skills": ["management-access", "telnet", "ssh", "cleartext-credentials"],
},
{
  "id": "2.8-002", "objective": "2.8", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which access control protocol fits these requirements, and why?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "RADIUS, because it combines authentication with authorisation in one exchange.",
    "TACACS+, which separates authorisation and logs each command.",
    "RADIUS, because it is an open standard and therefore records more detail.",
    "Either one, since both handle per-command authorisation in the same way."),
  "correct": ["B"],
  "explanation": "Two requirements decide this: different privilege levels for different staff on the same device, and a record of every command typed, which needs authorisation and accounting handled separately from authentication. TACACS+ does that and encrypts the whole payload rather than the password alone. Option A names the very property that makes RADIUS unsuitable here, since combining the two leaves no room for per-command control. Option C substitutes openness for capability. Option D denies a difference that is the heart of the comparison.",
  "difficulty": 2,
  "skills": ["management-access", "tacacs-plus", "radius", "aaa-comparison"],
},
{
  "id": "2.8-003", "objective": "2.8", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which access method lets the engineer reach the switch now?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "SSH to the management VLAN interface, once a laptop is on the same subnet.",
    "HTTPS to the device's web interface from the laptop over a patch lead.",
    "The console port, using a cable directly from the laptop to the switch.",
    "Telnet from the laptop, since Telnet needs no working routing protocol."),
  "correct": ["C"],
  "explanation": "Console access is out of band: it needs no address, no VLAN and nothing on the network to be working, which is exactly why it remains available when everything else on the device has failed. Options A, B and D all depend on the switch being reachable over the network, and the exhibit states the uplinks are down and the management interface does not answer. Option D also assumes Telnet somehow bypasses that, when it needs IP reachability just as SSH does.",
  "difficulty": 2,
  "skills": ["management-access", "console-access", "out-of-band", "troubleshoot-access"],
},
{
  "id": "2.8-004", "objective": "2.8", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why are SSH connections refused when the keys have been generated?",
  "exhibit": {"kind": "config", "content": EX_004},
  "options": opts(
    "The vty lines accept Telnet only, so SSH is never offered on them.",
    "The RSA key is too short, and SSH requires a modulus above 2048 bits.",
    "The username needs privilege level 15 removed before SSH will accept it.",
    "A domain name must be set after the key is generated, not before."),
  "correct": ["A"],
  "explanation": "Generating a key makes SSH possible but does not enable it: the vty lines decide what they will listen for, and transport input telnet excludes SSH entirely. Changing that line to transport input ssh is the fix, and doing so also stops the clear-text option. Option B invents a length requirement, and 2048 exceeds the 768-bit minimum comfortably. Option C confuses privilege level, which governs what an account may do after logging in. Option D reverses the correct order, since the domain name must exist before the key can be generated at all.",
  "difficulty": 3,
  "skills": ["management-access", "ssh", "transport-input", "troubleshoot-access"],
},
{
  "id": "2.8-005", "objective": "2.8", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which weakness in SW5's management configuration remains?",
  "exhibit": {"kind": "config", "content": EX_005},
  "options": opts(
    "The vty lines still permit Telnet alongside SSH, exposing credentials.",
    "The console line has no password set, so anyone in the room gains access.",
    "Local login is configured on vty, which bypasses any central authentication.",
    "The web interface is served over plain HTTP rather than being secured."),
  "correct": ["D"],
  "explanation": "The vty lines are already restricted to SSH and the console does carry a password, but ip http server is on while ip http secure-server is off, so the web interface answers over unencrypted HTTP and anything sent to it, credentials included, crosses in clear. Option A is contradicted by transport input ssh. Option B is contradicted by the password line under line con 0, even though it is stored with the weak type 7 reversible encoding. Option C describes a design choice rather than the exposure the HTTP line creates.",
  "difficulty": 2,
  "skills": ["management-access", "http-vs-https", "verify-management-config", "device-hardening"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "2" / "2.8.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "2.8",
    "domain": 2,
    "blueprint_version": "v1.1",
    "scope_note": ("No port-number recall: TACACS+ and RADIUS are separated by what "
                   "they do differently, not by transport and port."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
