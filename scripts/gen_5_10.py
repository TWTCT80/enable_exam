#!/usr/bin/env python3
"""Generate bank/5/5.10.json - 'Configure and verify WLAN within the GUI using
WPA2 PSK'.

Configure-and-verify against the controller GUI, using the same field/value
transcription as 2.9 rather than an invented web page.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import wlc_page, opts  # noqa: E402

EX_001 = """A new WLAN called BRANCH-STAFF is being created on the controller.

    Requirement
    ---------------------------------------------------------------
    Clients join with a passphrase, not an individual account
    Data must be protected with AES rather than TKIP
    No RADIUS server is available at this site
    The WLAN maps to the existing vlan30-staff interface"""

EX_002 = wlc_page("WLC GUI  -  WLANs > Edit > BRANCH-STAFF", [
    ("General", [
        ("Profile Name", "BRANCH-STAFF"),
        ("SSID", "BRANCH-STAFF"),
        ("Status", "Enabled"),
        ("Interface/Interface Group", "vlan30-staff"),
    ]),
    ("Security > Layer 2", [
        ("Layer 2 Security", "WPA+WPA2"),
        ("WPA2 Policy", "Enabled"),
        ("WPA2 Encryption", "AES"),
        ("Authentication Key Mgmt", "802.1X"),
        ("PSK Format", "not configured"),
    ]),
]) + """

No RADIUS server is configured on this controller. Clients see the SSID
and attempt to join, but every association fails."""

EX_003 = wlc_page("WLC GUI  -  WLANs > Edit > BRANCH-STAFF", [
    ("Security > Layer 2", [
        ("Layer 2 Security", "WPA+WPA2"),
        ("WPA Policy", "Disabled"),
        ("WPA2 Policy", "Enabled"),
        ("WPA2 Encryption", "AES"),
        ("Authentication Key Mgmt", "PSK"),
        ("PSK Format", "ASCII"),
    ]),
])

ITEMS = [
{
  "id": "5.10-001", "objective": "5.10", "domain": 5, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Which two settings on the Layer 2 security tab meet the requirement? (Choose two.)",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "Authentication Key Mgmt set to 802.1X",
    "WPA2 Encryption set to AES",
    "Layer 2 Security set to None",
    "Authentication Key Mgmt set to PSK",
    "WPA2 Encryption set to TKIP"),
  "correct": ["B", "D"],
  "explanation": "A passphrase rather than individual accounts means the key management is PSK, and protecting data with AES means the WPA2 encryption is AES, so those two together satisfy the requirement without any RADIUS server. Option A selects 802.1X, which needs the RADIUS server the site does not have. Option C removes security altogether. Option E selects TKIP, the older cipher the requirement rules out by name.",
  "difficulty": 2,
  "skills": ["wlan-gui", "wpa2-psk", "configure-wlan", "security-settings"],
},
{
  "id": "5.10-002", "objective": "5.10", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why does every association attempt fail?",
  "exhibit": {"kind": "config", "content": EX_002},
  "options": opts(
    "The WLAN Status is Enabled before the security settings were completed.",
    "AES cannot be selected while the WLAN maps to a tagged VLAN interface.",
    "Key management is 802.1X, which needs a RADIUS server that is absent.",
    "The interface vlan30-staff has to be created after the WLAN, not before."),
  "correct": ["C"],
  "explanation": "802.1X hands authentication to a RADIUS server, and none is configured, so the exchange never completes and every client is refused even though the SSID is advertised correctly; switching key management to PSK and setting a passphrase resolves it. Option A treats enabling the WLAN as premature, but a WLAN must be enabled to be advertised at all. Option B invents a conflict between AES and a mapped interface. Option D invents an ordering requirement for the interface.",
  "difficulty": 2,
  "skills": ["wlan-gui", "wpa2-psk", "802-1x", "troubleshoot-wlan"],
},
{
  "id": "5.10-003", "objective": "5.10", "domain": 5, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What do these settings confirm about how clients join this WLAN?",
  "exhibit": {"kind": "config", "content": EX_003},
  "options": opts(
    "They authenticate individually against a RADIUS server using AES.",
    "They supply a shared passphrase, and their data is protected with AES.",
    "They join without any credential, since only the format has been set.",
    "They supply a passphrase, but the older WPA cipher protects their data."),
  "correct": ["B"],
  "explanation": "Authentication Key Mgmt reads PSK, so every client presents the same passphrase, and WPA2 Encryption reads AES with the WPA policy disabled, so the newer cipher protects the traffic. Option A describes 802.1X, which these settings do not select. Option C ignores the PSK setting, and the ASCII format line describes how the passphrase is entered rather than replacing it. Option D is contradicted by WPA Policy reading Disabled, which leaves only WPA2 with AES in use.",
  "difficulty": 1,
  "skills": ["wlan-gui", "wpa2-psk", "verify-wlan", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "5" / "5.10.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "5.10", "domain": 5, "blueprint_version": "v1.1",
    "scope_note": "GUI transcribed as field/value pairs, as in 2.9.",
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
