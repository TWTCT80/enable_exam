# Bank allocation plan (300 items = 3 x 100-item exam)

Ratios held at every size, per the domain quota table.

| Domain | Name | Weight | /100 | /300 |
|---|---|---|---|---|
| 1 | Network Fundamentals | 20% | 20 | 60 |
| 2 | Network Access | 20% | 20 | 60 |
| 3 | IP Connectivity | 25% | 25 | 75 |
| 4 | IP Services | 10% | 10 | 30 |
| 5 | Security Fundamentals | 15% | 15 | 45 |
| 6 | Automation and Programmability | 10% | 10 | 30 |

`configure and verify` objectives get a larger share and a harder difficulty
mix, per spec. Marked (C&V) below.

## Domain 3 - 75 items

| Objective | Verb | Planned | Done |
|---|---|---|---|
| 3.1 Interpret routing table components | interpret | 13 | 13 |
| 3.2 Forwarding decision by default | determine | 15 | 15 |
| 3.3 IPv4/IPv6 static routing (C&V) | configure and verify | 18 | 18 |
| 3.4 Single-area OSPFv2 (C&V) | configure and verify | 20 | 20 |
| 3.5 First hop redundancy protocols | describe | 9 | 9 |

**Domain 3 is complete at 75/75.** No top-ups outstanding.

## Open decisions (resolved)

- **6.4 (AI/ML in network operations) is authored.** It is a genuine v1.1
  objective in Cisco's published blueprint. The spec's "no v2.0 AI content"
  rule is read as excluding v2.0's separate five-domain AI/network-ops
  domain, not v1.1's 6.4. Confirmed by the user.
- **3.1 vs 3.2 scope line.** 3.1 = reading the table. 3.2 = simulating a
  packet. 3.1-007 (recursive next-hop resolution) stays in 3.1 as a
  deliberate boundary case. Confirmed by the user.

## Domain 1 - 60 items  **COMPLETE**

| Objective | Verb | Planned | Done |
|---|---|---|---|
| 1.1 Role and function of network components | explain | 4 | 4 |
| 1.2 Network topology architectures | describe | 4 | 4 |
| 1.3 Physical interface and cabling types | compare | 4 | 4 |
| 1.4 Interface and cable issues | identify | 5 | 5 |
| 1.5 TCP compared to UDP | compare | 4 | 4 |
| 1.6 IPv4 addressing and subnetting (C&V) | configure and verify | 9 | 9 |
| 1.7 Private IPv4 addressing | describe | 3 | 3 |
| 1.8 IPv6 addressing and prefix (C&V) | configure and verify | 7 | 7 |
| 1.9 IPv6 address types | describe | 4 | 4 |
| 1.10 Verify IP parameters for client OS | verify | 4 | 4 |
| 1.11 Wireless principles | describe | 4 | 4 |
| 1.12 Virtualization fundamentals | explain | 3 | 3 |
| 1.13 Switching concepts | describe | 5 | 5 |

## Item types

`single` and `multi` only. `draganddrop` was removed from the schema: the
runner has no keyboard-navigable implementation of it, and a drag interaction
that fails on a keyboard is worse than not offering one. Matching content is
expressed as multi-answer items instead.

## Domain 2 - 60 items  **COMPLETE**

| Objective | Verb | Planned | Done |
|---|---|---|---|
| 2.1 VLANs spanning multiple switches (C&V) | configure and verify | 10 | 10 |
| 2.2 Interswitch connectivity (C&V) | configure and verify | 9 | 9 |
| 2.3 Layer 2 discovery protocols (C&V) | configure and verify | 5 | 5 |
| 2.4 EtherChannel / LACP (C&V) | configure and verify | 8 | 8 |
| 2.5 Rapid PVST+ | interpret | 10 | 10 |
| 2.6 Cisco wireless architectures and AP modes | describe | 5 | 5 |
| 2.7 WLAN physical infrastructure connections | describe | 4 | 4 |
| 2.8 Network device management access | describe | 5 | 5 |
| 2.9 Wireless LAN GUI configuration | interpret | 4 | 4 |

## Domain 5 - 45 items  **COMPLETE**

| Objective | Verb | Planned | Done |
|---|---|---|---|
| 5.1 Key security concepts | define | 4 | 4 |
| 5.2 Security program elements | describe | 3 | 3 |
| 5.3 Device access control, local passwords (C&V) | configure and verify | 5 | 5 |
| 5.4 Password policy elements | describe | 3 | 3 |
| 5.5 IPsec remote access and site-to-site VPNs | describe | 4 | 4 |
| 5.6 Access control lists (C&V) | configure and verify | 9 | 9 |
| 5.7 Layer 2 security features (C&V) | configure and verify | 8 | 8 |
| 5.8 AAA concepts | compare | 3 | 3 |
| 5.9 Wireless security protocols | describe | 3 | 3 |
| 5.10 WLAN with WPA2 PSK in the GUI (C&V) | configure and verify | 3 | 3 |

## Domain 4 - 30 items  **COMPLETE**

| Objective | Verb | Planned | Done |
|---|---|---|---|
| 4.1 Inside source NAT, static and pools (C&V) | configure and verify | 6 | 6 |
| 4.2 NTP client and server mode (C&V) | configure and verify | 4 | 4 |
| 4.3 Role of DHCP and DNS | explain | 3 | 3 |
| 4.4 Function of SNMP | explain | 3 | 3 |
| 4.5 Syslog facilities and severity levels | describe | 4 | 4 |
| 4.6 DHCP client and relay (C&V) | configure and verify | 4 | 4 |
| 4.7 Per-hop behaviour for QoS | explain | 2 | 2 |
| 4.8 Remote access using SSH | configure | 2 | 2 |
| 4.9 TFTP/FTP capabilities | describe | 2 | 2 |

## Domain 6 - 30 items  **COMPLETE**

| Objective | Verb | Planned | Done |
|---|---|---|---|
| 6.1 How automation impacts network management | explain | 4 | 4 |
| 6.2 Traditional vs controller-based networking | compare | 4 | 4 |
| 6.3 Controller-based, software defined architecture | describe | 5 | 5 |
| 6.4 AI and machine learning in network operations | explain | 3 | 3 |
| 6.5 REST-based API characteristics | describe | 6 | 6 |
| 6.6 Ansible and Terraform | recognize | 4 | 4 |
| 6.7 JSON-encoded data | recognize | 4 | 4 |

---

## Bank complete: 300 items

All six domains at quota, all 53 objectives covered, `validate.py` green
in full mode. `build_bank.py` no longer needs `--allow-partial`, and the
runner offers the full 100-question, 120-minute exam.

Still outstanding: `scripts/stats.py` and `app/lab-tasks.md`.

## The unsure marker

A correct answer got no explanation, so a lucky guess taught nothing. The
runner now takes a per-item **unsure** flag (checkbox next to Confirm,
<kbd>U</kbd> on the keyboard), and the results screen has three tiers:
missed items, correct-but-marked-unsure, and a collapsed section holding
every item in the attempt for anything you meant to mark and did not.

Decisions behind it:

- **Binary, not a confidence scale.** A second judgement per item under a
  running clock costs more than the granularity is worth.
- **It is an annotation, not navigation.** "No back, no skip" still holds.
  The header comment in `app.js` records it as the one departure from
  mirroring the real delivery.
- **Scoring is untouched.** Flagged-and-correct is correct; the headline
  percent does not move. The score card carries a subline, `n marked unsure`.
- **It lives in the report.** With no localStorage, `run.report` is the only
  thing that outlives the tab, so the flag is in the JSON (`score.marked_unsure`,
  `unsure_correct[]`, and `unsure` on each missed item) and in the Markdown.
- The checkbox sits outside `#q-options` deliberately: `picked()` and the
  keyboard handler enumerate the inputs in that container, and a stray
  checkbox among them would count as an answer.

## Option lettering in review

The explanations name letters — 296 of 300 say things like "Option C is ruled
out because…" — and those letters are the bank's own `option.id`. The attempt
shuffles display order per item and letters the options A–E by *position*, so
on a review card the explanation was pointing at the wrong rows. Every card
was affected: in a 25-item sample, 24 had an exam order differing from the
bank's.

Review cards now list options in bank order with the `id` shown as the key,
so "Option C" is the third row, always. The exam screen still shuffles —
fixed positions would be learnable across attempts, and the review card's
`correct` / `you` marks carry what actually happened during the run. A note
above the missed items says so, since the letters there deliberately do not
match the ones that were on screen.

## Deliberate non-goal: mobile

The runner targets a laptop screen, which is what the spec asked for
("readable on a laptop screen at 100% zoom"). It was never designed or
tested for a phone, and the user decided against adapting it.

The measurement behind that decision, should it be revisited:

| Exhibit width | Items |
|---|---|
| median | 70 characters |
| over 60 characters | 263 of 300 (88%) |
| widest | 128 characters (1.5-002) |

A phone in portrait fits roughly 48 monospace characters at the current
size, so 88% of exhibits would need sideways scrolling - and the CLI
output is the whole point of the bank. Making it work would mean
auto-fitting the exhibit font to the viewport with a readable floor, and
adding opportunistic resume so an evicted background tab does not cost a
90-minute attempt. Neither is built.

The app is fully offline once loaded: bank.json is fetched at start and
nothing else needs the network.
