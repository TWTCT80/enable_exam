# CCNA 200-301 practice exam

**[Take the exam →](https://twtct80.github.io/ccna_tester/)**

300 original practice questions for the Cisco CCNA 200-301 **v1.1** blueprint,
plus a static exam runner that works the way the real exam does: a 120-minute
clock that does not pause, and a confirmed answer that is final.

No account, no tracking, nothing to install. Once the page has loaded it needs
no network, so an attempt survives a tunnel.

---

## What makes these questions different

**Every single item has an exhibit.** All 300 require reading real device output,
a configuration, a topology or a payload, or doing arithmetic. None of them ask
what a default administrative distance is or which port a protocol uses. Facts
belong in flashcards; these are meant to make you work.

**The faults are the kind that hide.** A good share of the bank is scenarios
where every interface is up and the configuration reads as though it should
work: a native VLAN mismatch that logs a warning and keeps trunking, an access
list permit sitting below the deny that shadows it, `ip nat inside` never
applied, a NAT pool with no `overload` keyword that serves the first six users
of the morning.

**Every wrong answer is a real mistake.** Distractors are drawn from things a
candidate could actually believe — a subnet boundary off by one block, the right
answer for a neighbouring protocol, a command with the right keywords in the
wrong order — and each explanation names the misconception it targets rather
than just restating the right answer.

**Nothing is copied.** Every item is written from scratch against Cisco's
published exam topics. None reproduces or paraphrases real exam content.

**A right answer you guessed is worth reviewing too.** Any item can be marked
unsure while you answer it (<kbd>U</kbd>). It changes nothing about scoring and
you still cannot go back — it only means the review afterwards explains that
item as fully as one you got wrong. Everything else stays one click away under
*Every item in this attempt*.

### Coverage

| Domain | Weight | Items |
|---|---|---|
| 1.0 Network Fundamentals | 20% | 60 |
| 2.0 Network Access | 20% | 60 |
| 3.0 IP Connectivity | 25% | 75 |
| 4.0 IP Services | 10% | 30 |
| 5.0 Security Fundamentals | 15% | 45 |
| 6.0 Automation and Programmability | 10% | 30 |

All 53 objectives are covered. An attempt samples at those weights, so a
100-question exam gives you 20/20/25/10/15/10 exactly, drawn fresh each time.

### Also here

`app/lab-tasks.md` — one Packet Tracer task per *configure and verify*
objective. Simulations cannot be reproduced honestly in a web app, so the runner
does not pretend to; each task says what to build, what must be true when you
are done, the command that proves it, and a fault to introduce on purpose.

---

## A note before you share the link

The site is public and the whole question bank is sent to your browser, so
anyone with the URL can read all 300 answers. That is inherent to a static app
rather than a flaw — but it means this works as study material, not as a test
you could set for someone else.

---

## Running it locally

```sh
python3 -m http.server -d app 8000     # then open http://localhost:8000
```

It has to be served over HTTP; opening `index.html` from disk will not work,
because the page fetches `bank.json`.

The app is plain HTML, CSS and JavaScript. No build step, no framework, no
dependencies. It targets a laptop screen and is deliberately not adapted for
phones — see `PLAN.md` for that decision and the measurements behind it.

---

## For anyone wanting to work on the bank

<details>
<summary>Layout, generators and the quality gate</summary>

```
blueprint/objectives.json   53 objectives, from Cisco's published PDF
bank/<domain>/<obj>.json    the item bank, one file per objective
scripts/gen_<obj>.py        one generator per objective - the source of truth
scripts/iosfmt.py           shared IOS output renderers, columns verified
scripts/validate.py         the quality gate
scripts/stats.py            coverage and difficulty report
scripts/build_bank.py       bank/ -> app/bank.json
```

Items are never hand-edited under `bank/`. Edit the generator for the objective,
re-run it, then check:

```sh
python3 scripts/gen_3_4.py
python3 scripts/lencheck.py bank/3/3.4.json   # longest-answer tell, per item
python3 scripts/validate.py --batch           # per-item rules only
python3 scripts/validate.py                   # + quotas and coverage
python3 scripts/stats.py                      # coverage and difficulty report
```

`validate.py` fails on domain-quota drift, uncovered objectives, answer-key
imbalance, the longest-answer tell, near-duplicate stems, exhibitless items
above 15%, short explanations, explanations that skip a distractor, and
malformed `show ip route` exhibits — the parent banner must contain its
children, and the declared subnet and mask counts must match what is printed.
That last check has caught several exhibits that looked fine by eye.

Several generators assert their own arithmetic before writing: subnet and
broadcast boundaries, EUI-64 derivation, wildcard masks, HSRP virtual MACs and
JSON validity are all computed with the standard library rather than typed out,
so a miscalculated value cannot reach a candidate.

`.github/workflows/pages.yml` rebuilds `bank.json` from source on every push and
runs the validator first, so a bank failing its own checks cannot reach the
site.

</details>

---

Written against the v1.1 blueprint, which retires **2027-02-02**. v2.0 adds a
troubleshooting level and an AI/network-operations domain; none of that is here.
