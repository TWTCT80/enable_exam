#!/usr/bin/env python3
"""Generate bank/4/4.9.json - 'Describe the capabilities and functions of
TFTP/FTP in the network'.

Separated by what each can and cannot do: TFTP is small and unauthenticated
over UDP, FTP authenticates and runs over TCP.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import opts  # noqa: E402

EX_001 = """An IOS image is to be copied onto twelve routers across a WAN.

    Requirement
    ---------------------------------------------------------------
    Only named accounts may retrieve the image from the server
    A partial transfer over a lossy circuit must be detectable
    The server already refuses anonymous connections"""

EX_002 = """R2# copy tftp: flash:
Address or name of remote host []? 10.9.9.60
Source filename []? c2900-universalk9-mz.SPA.157-3.M4b.bin
Destination filename [c2900-universalk9-mz.SPA.157-3.M4b.bin]?
Accessing tftp://10.9.9.60/c2900-universalk9-mz.SPA.157-3.M4b.bin...

At no point was a username or password requested."""

ITEMS = [
{
  "id": "4.9-001", "objective": "4.9", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which transfer method meets these requirements?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "TFTP, which is lighter and therefore better suited to a WAN circuit.",
    "Either, because both prompt for credentials before transferring.",
    "TFTP, provided the server is configured to demand a username.",
    "FTP, since it authenticates the user and runs over a connection."),
  "correct": ["D"],
  "explanation": "FTP asks for a username and password before the transfer and runs over TCP, so the session is acknowledged and an incomplete transfer is apparent, which covers all three requirements. Option A picks the lighter protocol but TFTP has no concept of an account, so a server refusing anonymous access will refuse it. Option B credits TFTP with credentials it does not support. Option C expects a TFTP server to demand a username, which the protocol gives it no way to do.",
  "difficulty": 2,
  "skills": ["ftp", "tftp", "file-transfer", "authentication"],
},
{
  "id": "4.9-002", "objective": "4.9", "domain": 4, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does the absence of any credential prompt tell you?",
  "exhibit": {"kind": "cli_output", "content": EX_002},
  "options": opts(
    "The router cached credentials from an earlier transfer to the same server.",
    "The server has been left misconfigured and should have demanded a login.",
    "TFTP carries no authentication, so anyone reaching the server may fetch the file.",
    "The prompt appears only once the transfer has finished and is verified."),
  "correct": ["C"],
  "explanation": "TFTP has no mechanism for a username or password at all, so the transfer begins as soon as the filename is supplied and any device that can reach the server may retrieve or replace files there. Option A invents credential caching for a protocol with no credentials. Option B blames the server, when the omission is inherent to the protocol rather than a configuration choice. Option D postpones a prompt that never comes.",
  "difficulty": 1,
  "skills": ["tftp", "ftp", "file-transfer", "no-authentication"],
},
]
dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "4" / "4.9.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({"objective": "4.9", "domain": 4,
    "blueprint_version": "v1.1",
    "scope_note": "Separated by capability rather than by port number.",
    "items": ITEMS}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
