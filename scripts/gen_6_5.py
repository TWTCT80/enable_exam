#!/usr/bin/env python3
"""Generate bank/6/6.5.json - 'Describe characteristics of REST-based APIs'.

All four areas the objective names: authentication types (004), CRUD (001),
HTTP verbs (003, 006) and data encoding (005). Status codes appear as evidence
to reason from rather than as values to recall.

003 is the one that matters in practice: PUT replaces a resource, so fields
omitted from the body are removed, and the request that looks like a small edit
quietly deletes the rest of the configuration.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from iosfmt import http_exchange, opts  # noqa: E402

BEARER = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJuZXRhZG1pbiJ9"
YANG = "application/yang-data+json"

EX_001 = """A controller exposes its interface configuration at

    /restconf/data/ietf-interfaces:interfaces          the collection
    /restconf/data/ietf-interfaces:interfaces/interface=Loopback0
                                                       one member

Loopback0 already exists. A new Loopback10 is to be added, and the
existing members must be left exactly as they are."""

EX_002 = http_exchange(
    "GET /restconf/data/ietf-interfaces:interfaces HTTP/1.1",
    [("Host", "10.9.9.1"), ("Authorization", BEARER), ("Accept", YANG)],
    response="HTTP/1.1 401 Unauthorized",
    response_headers=[("WWW-Authenticate", 'Bearer realm="restconf"')],
) + """

The path is correct and the same path returned data yesterday from the
same client."""

EX_003 = http_exchange(
    "PUT /restconf/data/ietf-interfaces:interfaces/interface=Loopback0 HTTP/1.1",
    [("Host", "10.9.9.1"), ("Authorization", BEARER), ("Content-Type", YANG)],
    body=json.dumps({"ietf-interfaces:interface": {"name": "Loopback0",
                                                   "enabled": False}}, indent=2),
    response="HTTP/1.1 204 No Content",
) + """

Before the request, Loopback0 carried a name, a description, an IPv4
address and an enabled flag. Afterwards only the name and the enabled
flag remain."""

EX_004 = """An automation host will call a controller's API several thousand
times an hour.

    Requirement
    ---------------------------------------------------------------
    The long-lived credential must not travel on every single request
    Access must lapse on its own after a period without renewal
    A leaked value must be revocable without changing the account
    Nothing may be placed in the request URL, which is logged upstream"""

EX_005 = http_exchange(
    "GET /restconf/data/ietf-interfaces:interfaces HTTP/1.1",
    [("Host", "10.9.9.1"), ("Authorization", BEARER),
     ("Accept", "application/yang-data+json")],
)

EX_006 = http_exchange(
    "DELETE /restconf/data/ietf-interfaces:interfaces/interface=Loopback99 HTTP/1.1",
    [("Host", "10.9.9.1"), ("Authorization", BEARER)],
    response="HTTP/1.1 204 No Content",
)

ITEMS = [
{
  "id": "6.5-001", "objective": "6.5", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which request creates Loopback10 without disturbing the existing members?",
  "exhibit": {"kind": "topology", "content": EX_001},
  "options": opts(
    "PUT to the collection, carrying the full set of interfaces as it should end up.",
    "GET the collection, edit the returned body by hand, and send it back.",
    "POST to the collection, which adds a member alongside the existing ones.",
    "PATCH the individual member path for Loopback10, which does not yet exist."),
  "correct": ["C"],
  "explanation": "Create maps onto POST against the collection, and the server places the new member inside it without the client needing to know or resend what is already there. Option A would work only if the body listed every existing interface too, and anything omitted would be removed. Option B describes that same replacement carried out manually, with a race against any other change in between. Option D patches a resource that does not exist yet, so there is nothing to modify.",
  "difficulty": 2,
  "skills": ["rest-api", "crud", "http-verbs", "post"],
},
{
  "id": "6.5-002", "objective": "6.5", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What does this response indicate?",
  "exhibit": {"kind": "cli_output", "content": EX_002},
  "options": opts(
    "The token is missing, expired or no longer accepted.",
    "The path requested does not exist on this controller.",
    "The controller understood the request and refuses to carry it out.",
    "The body of the request was malformed and could not be parsed."),
  "correct": ["A"],
  "explanation": "A 401 concerns who is asking rather than what was asked, and the WWW-Authenticate header inviting a bearer credential confirms it; since the same path worked yesterday, an expired token is the likeliest cause. Option B describes a 404, which the working path rules out. Option C describes a 403, where the caller is known but not permitted. Option D describes a 400, and this request carries no body at all.",
  "difficulty": 2,
  "skills": ["rest-api", "status-codes", "authentication-types", "troubleshoot-api"],
},
{
  "id": "6.5-003", "objective": "6.5", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Why did the description and the address disappear from Loopback0?",
  "exhibit": {"kind": "cli_output", "content": EX_003},
  "options": opts(
    "The controller rejected the request and rolled the resource back to defaults.",
    "PATCH was needed, since only PATCH can remove a field explicitly.",
    "The Content-Type header did not match the encoding the body actually used.",
    "PUT replaces the whole resource, so fields left out of the body are removed."),
  "correct": ["D"],
  "explanation": "PUT states what the resource should be in its entirety, so the controller made it match the body exactly and the fields absent from that body ceased to exist; PATCH is the verb for changing part of a resource and leaving the rest alone. The 204 confirms the request succeeded, which is what makes this destructive rather than an error. Option A is contradicted by that success. Option B reverses which verb removes fields. Option C blames a header that matches the body correctly.",
  "difficulty": 3,
  "skills": ["rest-api", "http-verbs", "put-vs-patch", "crud"],
},
{
  "id": "6.5-004", "objective": "6.5", "domain": 6, "type": "multi", "select_count": 2,
  "stem": "Refer to the exhibit. Which two approaches fail the stated requirements? (Choose two.)",
  "exhibit": {"kind": "topology", "content": EX_004},
  "options": opts(
    "A bearer token presented in a header until it expires",
    "Basic authentication, sending the account credential on every request",
    "An API key appended to the request URL as a query parameter",
    "A token that can be revoked without changing the underlying account",
    "A credential exchanged once at the start and then held by the client"),
  "correct": ["B", "C"],
  "explanation": "Basic authentication puts the long-lived account credential on every one of several thousand requests an hour, which the first line forbids, and an API key in the URL lands in the logs upstream, which the fourth line forbids by name. Option A meets all four. Option D describes the revocation the third line asks for. Option E describes obtaining a token once, which is the behaviour the first line is written around.",
  "difficulty": 2,
  "skills": ["rest-api", "authentication-types", "bearer-token", "api-security"],
},
{
  "id": "6.5-005", "objective": "6.5", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. What is the Accept header telling the controller?",
  "exhibit": {"kind": "cli_output", "content": EX_005},
  "options": opts(
    "That the controller must store its configuration in JSON form.",
    "That the body being sent with this request is encoded as JSON.",
    "That the client wants the response encoded as JSON.",
    "That only controllers able to parse JSON may answer this request."),
  "correct": ["C"],
  "explanation": "Accept describes what the client is willing to receive, so the controller returns JSON rather than XML; the companion header Content-Type describes what the client is sending, and confusing the two is the usual slip. Option B states the Content-Type meaning, and this request has no body in any case. Option A treats a transport encoding as a storage format. Option D reads it as a capability filter rather than a preference for this exchange.",
  "difficulty": 2,
  "skills": ["rest-api", "data-encoding", "accept-header", "content-type"],
},
{
  "id": "6.5-006", "objective": "6.5", "domain": 6, "type": "single", "select_count": 1,
  "stem": "Refer to the exhibit. Which CRUD operation has this request performed?",
  "exhibit": {"kind": "cli_output", "content": EX_006},
  "options": opts(
    "Delete, removing Loopback99 from the controller.",
    "Read, retrieving the current state of Loopback99.",
    "Update, changing one field on Loopback99.",
    "Create, adding Loopback99 to the collection."),
  "correct": ["A"],
  "explanation": "The verb is DELETE against a single member path, and the 204 reports success with nothing left to return, which is the ordinary response to a removal. Option B maps to GET, which would return a body describing the resource. Option C maps to PUT or PATCH, both of which carry a body saying what to change. Option D maps to POST against the collection rather than DELETE against a member.",
  "difficulty": 1,
  "skills": ["rest-api", "crud", "http-verbs", "status-codes"],
},
]

dest = pathlib.Path(__file__).resolve().parent.parent / "bank" / "6" / "6.5.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({
    "objective": "6.5", "domain": 6, "blueprint_version": "v1.1",
    "scope_note": ("Status codes are evidence to reason from, not values to recall. "
                   "003 covers PUT replacing a resource wholesale."),
    "items": ITEMS,
}, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {dest} ({len(ITEMS)} items)")
