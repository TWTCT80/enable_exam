#!/usr/bin/env python3
"""Generate bank/5/5.5.json - 'Describe IPsec remote access and site-to-site VPNs'.

Both VPN types the objective names, plus what IPsec actually provides. 003 is
the one worth having: GRE encapsulates and does not encrypt, so a tunnel that
looks like a private link carries readable payload until IPsec is added.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import packet_capture, capture_row, opts  # noqa: E402

EX_001 = """A manufacturer is joining its two sites over the internet.

    Requirement
    ---------------------------------------------------------------
    Both sites have a permanent circuit and a router at the edge
    The link must be up continuously, not raised per session
    Hosts must reach the far site with no software installed on them
    Users must not authenticate individually for the site link"""

EX_002 = """Traffic between two offices currently crosses the internet inside a
GRE tunnel between the edge routers.

    Requirement now added
    ---------------------------------------------------------------
    Anyone capturing the traffic in transit must not be able to read it
    Any alteration made in transit must be detectable at the far end
    Each router must be able to confirm which peer it is talking to"""

EX_003 = packet_capture([
    capture_row(41, "8.220114", "203.0.113.7", "198.51.100.9", "GRE", 154,
                "Encapsulated IP"),
    capture_row(42, "8.220780", "203.0.113.7", "198.51.100.9", "GRE", 622,
                "Encapsulated IP"),
], "Capture taken at an internet exchange, between the two edge routers") + """

Reassembled from the encapsulated payload of frames 41 and 42:

    POST /hr/salary-review HTTP/1.1
    Host: intranet.example.internal
    Authorization: Basic bmV0YWRtaW46V3IzbmNo

The tunnel between the two offices was built with GRE and nothing else."""

EX_004 = """        home worker                              head office
       +-----------+                              +-----------+
       |  laptop   |======= internet =============|  FW-EDGE  |
       | VPN client|                              +-----+-----+
       +-----------+                                    |
                                                   office LAN

The laptop raises the tunnel when the user signs in with their own
credentials, and drops it when they sign out. No tunnel exists while the
laptop is switched off."""

ITEMS = [
{
  "id": "5.5-001", "objective": "5.5", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which VPN arrangement fits these requirements?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "A remote access VPN, with client software installed on every host.",
    "A remote access VPN reached through a browser-based portal per user.",
    "A site-to-site VPN between the two edge routers.",
    "Neither; IPsec cannot join two sites without a private circuit."),
  "correct": ["C"],
  "explanation": "A permanent link that hosts use without knowing it exists, raised between two gateways rather than per user, is the definition of a site-to-site VPN: the routers carry the tunnel and every host behind them benefits. Options A and B both authenticate individual users and need something on the endpoint, which the requirement rules out twice over. Option D is wrong because carrying private traffic across the public internet is exactly what IPsec was designed for.",
  "difficulty": 2,
  "skills": ["ipsec", "site-to-site-vpn", "remote-access-vpn", "design-to-requirements"],
},
{
  "id": "5.5-002", "objective": "5.5", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which statement describes what adding IPsec provides against these three requirements?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "Only confidentiality; detecting any alteration needs a separate mechanism.",
    "Only integrity; the payload itself stays readable while in transit.",
    "Neither of those; IPsec confirms the peer and does nothing further.",
    "All three: payload encrypted, alteration detectable, peers authenticated."),
  "correct": ["D"],
  "explanation": "IPsec covers all three requirements together, encrypting the payload so a capture is unreadable, carrying an integrity check so tampering is detected, and authenticating each peer before the tunnel is established. Options A and B each claim one property and deny the other, when the protocol suite provides both. Option C reduces IPsec to peer authentication alone, which is the part that happens first rather than the whole of it.",
  "difficulty": 2,
  "skills": ["ipsec", "confidentiality", "integrity", "peer-authentication"],
},
{
  "id": "5.5-003", "objective": "5.5", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why is this content readable to anyone capturing between the two offices?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts(
    "GRE encrypts the header but leaves the encapsulated payload in clear.",
    "GRE encapsulates traffic without encrypting it, so IPsec must be added.",
    "The tunnel's MTU is too small for encryption to be applied to each packet.",
    "GRE encryption is present but switched off by default and must be enabled."),
  "correct": ["B"],
  "explanation": "GRE is a tunnelling protocol: it wraps one protocol inside another so the traffic can traverse a path it otherwise could not, and it offers no confidentiality whatsoever, which is why the credentials are legible in the capture. Pairing it with IPsec is the usual answer. Option A credits GRE with encrypting something, which it never does. Option C ties encryption to MTU, which affects fragmentation rather than protection. Option D invents an encryption feature GRE does not possess.",
  "difficulty": 3,
  "skills": ["ipsec", "gre", "encapsulation-vs-encryption", "read-packet-capture"],
},
{
  "id": "5.5-004", "objective": "5.5", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which VPN type is shown here?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts("Remote access", "Site-to-site", "GRE without IPsec", "No VPN at all"),
  "correct": ["A"],
  "explanation": "The tunnel is raised by an individual signing in, terminates on their own laptop and disappears when they sign out, which is what distinguishes remote access from a permanent gateway-to-gateway link. Option B would run between two routers and stay up regardless of who is working. Option C names an encapsulation rather than a VPN type, and nothing in the drawing indicates GRE. Option D is contradicted by the client and the tunnel both being shown.",
  "difficulty": 1,
  "skills": ["ipsec", "remote-access-vpn", "site-to-site-vpn", "read-topology"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "5" / "5.5.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "5.5", "domain": 5, "blueprint_version": "v1.1",
    "scope_note": "GRE encapsulates; IPsec protects. 003 shows the difference in a capture.",
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
