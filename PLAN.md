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
