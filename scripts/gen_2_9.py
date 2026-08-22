#!/usr/bin/env python3
"""Generate bank/2/2.9.json - 'Interpret the wireless LAN GUI configuration'.

The objective's four named areas: WLAN creation (001), security settings (002),
QoS profiles (003) and advanced settings (004).

This objective has no CLI transcript behind it, so rather than draw a fake web
page in ASCII - which would invent a layout and train candidates to read a
screen that does not exist - the exhibits transcribe the field and value pairs
a candidate actually reads, grouped by the tab they sit on. Same reasoning as
the decision to avoid the summary form of show cdp neighbors in 2.3.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import wlc_page, opts  # noqa: E402

# --- exhibits -------------------------------------------------------------

EX_001 = wlc_page("WLC GUI  -  WLANs > Edit > CORP-WIFI", [
    ("General", [
        ("Profile Name", "CORP-WIFI"),
        ("SSID", "CORP-WIFI"),
        ("Status", "Disabled"),
        ("Radio Policy", "All"),
        ("Interface/Interface Group", "vlan10-corp"),
        ("Broadcast SSID", "Enabled"),
    ]),
    ("Security > Layer 2", [
        ("Layer 2 Security", "WPA+WPA2"),
        ("WPA2 Policy", "Enabled"),
        ("WPA2 Encryption", "AES"),
        ("Authentication Key Mgmt", "PSK"),
    ]),
]) + """

The access points are joined and healthy, VLAN 10 is reachable, and the
pre-shared key has been distributed. No client can see or join CORP-WIFI."""

EX_002 = wlc_page("WLC GUI  -  WLANs > Edit > GUEST-WIFI", [
    ("General", [
        ("Profile Name", "GUEST-WIFI"),
        ("SSID", "GUEST-WIFI"),
        ("Status", "Enabled"),
        ("Interface/Interface Group", "vlan90-guest"),
    ]),
    ("Security > Layer 2", [
        ("Layer 2 Security", "None"),
    ]),
    ("Security > Layer 3", [
        ("Layer 3 Security", "Web Policy"),
        ("Web Policy", "Authentication"),
    ]),
])

EX_003 = wlc_page("WLC GUI  -  WLANs > Edit > VOICE-WIFI", [
    ("General", [
        ("Profile Name", "VOICE-WIFI"),
        ("SSID", "VOICE-WIFI"),
        ("Status", "Enabled"),
        ("Interface/Interface Group", "vlan20-voice"),
    ]),
    ("QoS", [
        ("Quality of Service (QoS)", "Silver (best effort)"),
        ("Application Visibility", "Disabled"),
        ("WMM Policy", "Allowed"),
    ]),
]) + """

Handsets on this WLAN report choppy audio whenever the office data
network is busy. Wired QoS is already trusting and prioritising the
voice VLAN correctly end to end."""

EX_004 = wlc_page("WLC GUI  -  WLANs > Edit > CORP-WIFI", [
    ("Advanced", [
        ("Enable Session Timeout", "1800 seconds"),
        ("Client Exclusion", "Enabled, 60 seconds"),
        ("Maximum Allowed Clients", "0"),
        ("Aironet IE", "Enabled"),
        ("P2P Blocking Action", "Disabled"),
        ("Client Load Balancing", "Disabled"),
    ]),
])


ITEMS = [
{
  "id": "2.9-001", "objective": "2.9", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why can no client see or join this WLAN?",
  "exhibit": {"kind": "config", "content": EX_001},
  "options": opts(
    "Broadcast SSID is enabled, which hides the network from ordinary clients.",
    "The WLAN's Status is Disabled, so it is never advertised.",
    "The Radio Policy of All prevents the WLAN binding to any single band.",
    "WPA2 with PSK cannot be used together with an interface group."),
  "correct": ["B"],
  "explanation": "A WLAN is only pushed to the access points once its Status is Enabled, so with it disabled the SSID is never advertised no matter how complete the rest of the configuration is. Option A reverses the meaning of Broadcast SSID, which when enabled makes the network visible rather than hiding it. Option C misreads Radio Policy, where All means both bands carry the WLAN rather than none. Option D invents a conflict; WPA2 with a pre-shared key on a mapped interface is an ordinary combination.",
  "difficulty": 1,
  "skills": ["wlan-gui", "wlan-creation", "wlan-status", "troubleshoot-wlan"],
},
{
  "id": "2.9-002", "objective": "2.9", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What will a guest experience when joining this WLAN, and how is their traffic protected over the air?",
  "exhibit": {"kind": "config", "content": EX_002},
  "options": opts(
    "They join without a key and are redirected to a login page; the air link is unencrypted.",
    "They are prompted for a pre-shared key, after which their traffic is encrypted with AES.",
    "They join without a key and their traffic is encrypted once web authentication succeeds.",
    "They cannot join at all, because a WLAN requires some Layer 2 security to be set."),
  "correct": ["A"],
  "explanation": "Layer 2 Security reads None, so association needs no key and nothing encrypts the radio link; the Layer 3 Web Policy then intercepts the browser and demands credentials before granting access. Option B describes a pre-shared key the configuration does not set. Option C is the most tempting error: web authentication controls who passes traffic but never turns on link-layer encryption, so guest traffic stays readable over the air. Option D is contradicted by this being a working and common guest arrangement.",
  "difficulty": 3,
  "skills": ["wlan-gui", "security-settings", "web-authentication", "wireless-encryption"],
},
{
  "id": "2.9-003", "objective": "2.9", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which change on the controller addresses the reported audio problem?",
  "exhibit": {"kind": "config", "content": EX_003},
  "options": opts(
    "Disable the WMM Policy, so voice frames are no longer queued behind data.",
    "Enable Application Visibility so the controller can identify the voice stream.",
    "Set Quality of Service on this WLAN to Platinum, the profile intended for voice.",
    "Move the WLAN to the data interface so it shares the wired queue already trusted."),
  "correct": ["C"],
  "explanation": "The wired path is already prioritising voice, so the gap is over the air: this WLAN sits on Silver, the best-effort profile, and voice needs Platinum, which is the profile the controller reserves for it. Option A removes the very mechanism that gives voice frames preferential radio access. Option B adds visibility and reporting without changing how frames are queued. Option D moves voice onto the data network, which would undo the separation that makes the wired prioritisation work.",
  "difficulty": 2,
  "skills": ["wlan-gui", "qos-profiles", "platinum-profile", "voice-over-wireless"],
},
{
  "id": "2.9-004", "objective": "2.9", "domain": 2, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does the Maximum Allowed Clients value of 0 mean for this WLAN?",
  "exhibit": {"kind": "config", "content": EX_004},
  "options": opts(
    "No limit is applied; clients are capped by hardware alone.",
    "The WLAN is closed to clients until an administrator raises the figure.",
    "Clients are admitted one at a time as earlier sessions time out.",
    "The value is ignored while Client Exclusion remains enabled."),
  "correct": ["A"],
  "explanation": "On this page zero is the value meaning unlimited rather than none, so the WLAN accepts clients up to whatever the access points and controller can carry. Option B reads zero literally, which would silently take a working WLAN out of service and is the reason the convention is worth knowing. Option C invents a queueing behaviour tied to the session timeout above it. Option D links the field to Client Exclusion, which governs how long a misbehaving client is locked out rather than how many may join.",
  "difficulty": 2,
  "skills": ["wlan-gui", "advanced-settings", "client-limits", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "2" / "2.9.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "2.9",
    "domain": 2,
    "blueprint_version": "v1.1",
    "scope_note": ("Exhibits transcribe the field/value pairs a candidate reads on the "
                   "controller, grouped by tab, rather than drawing an invented web "
                   "page in ASCII."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
