#!/usr/bin/env python3
"""Generate bank/4/4.8.json - 'Configure network devices for remote access using SSH'.

Two items on the parts 2.8-004 does not cover: the ordering the key generation
depends on, and what version 2 changes. The vty transport fault already carries
2.8-004 and is not repeated.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

EX_001 = """SW1(config)# crypto key generate rsa modulus 2048
% Please define a domain-name first.

SW1(config)#

The switch has been given the hostname SW1 and a username with a secret.
The vty lines are already set to transport input ssh."""

EX_002 = """! R2 - relevant configuration
!
hostname R2
ip domain-name example.internal
crypto key generate rsa modulus 2048
ip ssh version 1
!
username netadmin privilege 15 secret Wr3nch-Harbour-42
!
line vty 0 4
 login local
 transport input ssh
!

A security review has asked for the version setting to be revisited."""

ITEMS = [
{
  "id": "4.8-001", "objective": "4.8", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which command must be entered before the key can be generated?",
  "exhibit": {"kind": "cli_output", "content": EX_001},
  "options": opts(
    "ip ssh version 2, which selects the key format to generate",
    "ip domain-name followed by the organisation's domain",
    "crypto key zeroize rsa, to clear any partially built key",
    "service password-encryption, so the key is stored protected"),
  "correct": ["B"],
  "explanation": "An RSA key pair is labelled with the device's fully qualified name, so IOS needs both a hostname and a domain name before it can build one, and the error names the missing half directly. Option A selects the protocol version, which is set after a key exists rather than before. Option C erases keys, and there is none to erase. Option D encrypts passwords in the configuration and has no bearing on key generation.",
  "difficulty": 2,
  "skills": ["ssh", "crypto-key-generate", "ip-domain-name", "configure-ssh"],
},
{
  "id": "4.8-002", "objective": "4.8", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What should the version setting be changed to, and why?",
  "exhibit": {"kind": "config", "content": EX_002},
  "options": opts(
    "Change it to 2, which closes known weaknesses in the older protocol.",
    "Leave it at 1, since version 2 requires a key of at least 4096 bits.",
    "Remove the line, so the device negotiates whichever version the client offers.",
    "Change it to 2, which is required before login local will be accepted."),
  "correct": ["A"],
  "explanation": "Version 1 has structural weaknesses that version 2 was written to address, and a device with a 2048-bit key can run version 2 without any other change, so pinning to 2 is the correct outcome of the review. Option B invents a key length requirement. Option C leaves the device willing to fall back to version 1 whenever a client asks, which is the situation being closed. Option D ties the version to local authentication, which works under either.",
  "difficulty": 2,
  "skills": ["ssh", "ssh-version-2", "device-hardening", "configure-ssh"],
},
]
dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "4" / "4.8.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({"objective": "4.8", "domain": 4,
    "blueprint_version": "v1.1",
    "scope_note": "The vty transport fault is left to 2.8-004 rather than repeated.",
    "items": ITEMS}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
