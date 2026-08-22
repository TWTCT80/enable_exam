#!/usr/bin/env python3
"""Generate bank/1/1.11.json - 'Describe wireless principles'.

All four sub-topics: nonoverlapping channels (001), RF signal quality (002),
SSID and how it differs from BSSID (003), and encryption as it appears in a
scan (004). Each item reads a survey or scan result rather than defining a term.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402


def _selftest():
    """2.4 GHz channels are 22 MHz wide on 5 MHz centres, so channels must be
    at least five apart to avoid overlapping. That is why 1, 6 and 11 are the
    only three that fit."""
    def overlaps(a, b):
        return abs(a - b) < 5
    for a, b in ((1, 6), (6, 11), (1, 11)):
        assert not overlaps(a, b), (a, b)
    assert overlaps(3, 1) and overlaps(3, 6)      # item 001 turns on this
    assert not overlaps(3, 11)


_selftest()

# --- exhibits -------------------------------------------------------------

EX_001 = """Site survey of the 2.4 GHz band on one floor

    AP        Channel    Neighbouring cells overlap this AP's coverage
    ------    -------    --------------------------------------------
    AP-A            1    AP-B, AP-D
    AP-B            6    AP-A, AP-C, AP-D
    AP-C           11    AP-B
    AP-D            3    AP-A, AP-B

Users nearest AP-D report slow throughput and frequent stalls, and the
three other cells were stable before AP-D was installed."""

EX_002 = """Client-side survey taken from one desk

    AP        Channel    Signal (RSSI)    Noise floor    SNR
    ------    -------    -------------    -----------    ----
    AP-1            1        -62 dBm        -92 dBm      30 dB
    AP-2            6        -57 dBm        -61 dBm       4 dB
    AP-3           11        -71 dBm        -94 dBm      23 dB

All three advertise the same SSID and the client may associate with any
of them."""

EX_003 = """Wireless scan taken by a laptop in the lobby

    SSID          BSSID                Channel    Security
    ----------    -----------------    -------    ------------
    CORP-WIFI     00:1a:2b:3c:4d:50          1    WPA2-Enterprise
    CORP-WIFI     00:1a:2b:3c:4d:70          6    WPA2-Enterprise
    CORP-WIFI     00:1a:2b:3c:4d:90         11    WPA2-Enterprise
    GUEST-WIFI    00:1a:2b:3c:4d:51          1    Open"""

EX_004 = """Wireless scan taken in a shared office building

    SSID          Channel    Security          Signal
    ----------    -------    --------------    --------
    OFFICE-A            1    WPA2-Personal     -48 dBm
    OFFICE-B            6    WPA3-Personal     -55 dBm
    HOTSPOT-C          11    Open              -61 dBm
    LEGACY-D            1    WEP               -67 dBm"""


ITEMS = [
{
  "id": "1.11-001", "objective": "1.11", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why did installing AP-D degrade performance across this floor?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "AP-D is too close to AP-C, and both are serving the edge of the same coverage area.",
    "AP-D uses a channel already carried by AP-A, so the two cells are duplicating traffic.",
    "AP-D is transmitting at a higher power than the other three access points.",
    "AP-D sits on channel 3, which overlaps both channel 1 and channel 6."),
  "correct": ["D"],
  "explanation": "In the 2.4 GHz band each channel is far wider than the spacing between channel numbers, so only channels five or more apart avoid overlapping, which is why 1, 6 and 11 are the standard plan. Channel 3 sits two away from 1 and three away from 6, so AP-D interferes with AP-A and AP-B at once, matching the overlap column exactly. Option A points at AP-C on channel 11, which is eight away from AP-D and does not overlap it. Option B treats channel 3 and channel 1 as the same channel. Option C invents a power difference the survey never records.",
  "difficulty": 3,
  "skills": ["nonoverlapping-channels", "rf-interference", "2-4ghz-channel-plan", "wireless-principles"],
},
{
  "id": "1.11-002", "objective": "1.11", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which access point should this client associate with for the most reliable connection?",
  "exhibit": {"kind": "topology", "content": EX_002},
  "options": opts(
    "AP-1, because it combines a strong signal with a quiet noise floor.",
    "AP-2, because it shows the strongest received signal of the three.",
    "AP-3, because channel 11 is furthest from the other two cells.",
    "Any of the three, because all advertise the same SSID and are equivalent."),
  "correct": ["A"],
  "explanation": "What matters is how far the signal rises above the noise, not its absolute strength, and AP-1's 30 dB signal-to-noise ratio is the widest margin available. Option B picks the strongest raw RSSI, but AP-2 sits in a noise floor of -61 dBm, leaving only 4 dB of usable margin, which is the trap this item is built around. Option C picks on channel separation, which affects neighbouring cells rather than this client's own link quality, and AP-3's 23 dB is still below AP-1's. Option D treats a shared SSID as meaning the radio conditions are identical.",
  "difficulty": 2,
  "skills": ["rf", "signal-to-noise-ratio", "rssi", "wireless-principles"],
},
{
  "id": "1.11-003", "objective": "1.11", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Three entries share the name CORP-WIFI while showing different BSSID values. What does that indicate?",
  "exhibit": {"kind": "topology", "content": EX_003},
  "options": opts(
    "Three separate wireless networks have each been given the same name by mistake.",
    "One wireless network served by three access points, each with its own radio ID.",
    "One access point is advertising the same network three times to spread its load.",
    "The laptop has recorded the same access point once for each channel it scanned."),
  "correct": ["B"],
  "explanation": "The SSID names the wireless network a user selects, while the BSSID identifies the individual radio serving it, so three BSSIDs under one SSID means three access points cooperating to cover an area, which their placement on channels 1, 6 and 11 confirms. Option A treats a shared SSID as a naming error, when sharing it is exactly what lets a client roam. Option C would require one radio to hold three BSSIDs on three channels at once. Option D assumes the scan duplicated a single AP, but a single radio reports one BSSID per network.",
  "difficulty": 2,
  "skills": ["ssid", "bssid", "wireless-principles", "roaming"],
},
{
  "id": "1.11-004", "objective": "1.11", "domain": 1, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which network in this scan offers the strongest protection for traffic sent across it?",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts("OFFICE-A", "LEGACY-D", "OFFICE-B", "HOTSPOT-C"),
  "correct": ["C"],
  "explanation": "The Security column ranks these plainly: OFFICE-B advertises WPA3, the newest of the personal modes and the strongest shown. Option A advertises WPA2, which remains sound but has been superseded by WPA3. Option B advertises WEP, which is long broken and offers protection in name only. Option D is Open, so its traffic carries no link-layer encryption at all, and its stronger signal is irrelevant to the question of protection.",
  "difficulty": 1,
  "skills": ["wireless-encryption", "wpa3", "wireless-principles", "read-correct-row"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "1" / "1.11.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "1.11",
    "domain": 1,
    "blueprint_version": "v1.1",
    "scope_note": ("Channel overlap arithmetic is asserted in _selftest(). Encryption "
                   "appears here only as it is read from a scan; the protocols "
                   "themselves belong to 5.9."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items, channel-overlap self-test passed)")
