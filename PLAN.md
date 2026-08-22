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
