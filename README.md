# CCNA 200-301 v1.1 practice exam

A versioned item bank and a static exam runner, written against Cisco's
published 200-301 **v1.1** exam topics (retires 2027-02-02). All items are
original and written to the objectives; none reproduce real exam content.

## Layout

```
blueprint/objectives.json   53 objectives, fetched from Cisco's official PDF
bank/<domain>/<obj>.json    the item bank, one file per objective
scripts/iosfmt.py           shared IOS output renderers (verified columns)
scripts/gen_<obj>.py        one generator per objective - the source of truth
scripts/validate.py         quality gate
scripts/build_bank.py       bank/ -> app/bank.json
app/                        static runner, no build step, no framework
```

## Running the app

```sh
python3 scripts/build_bank.py --allow-partial   # regenerate app/bank.json
python3 -m http.server -d app 8000              # then open http://localhost:8000
```

It must be served over HTTP; opening `index.html` from disk will not work,
because the page fetches `bank.json`. Once loaded the app needs no network at
all, so an attempt survives losing connectivity.

## Deploying to GitHub Pages

`.github/workflows/pages.yml` publishes the `app/` directory on every push to
`main` or `master`. It validates the bank and rebuilds `bank.json` from source
first, so the deployed site can never drift from the item bank, and a bank that
fails its own checks cannot reach the site.

In the repository, set **Settings > Pages > Source** to **GitHub Actions**.

Note that a Pages site is publicly readable, and `bank.json` is served to the
browser in full - so anyone with the URL can read all 300 answers. That is
inherent to a static app rather than a flaw, but it is worth knowing before
sharing the link.

## Working on the bank

Items are never hand-edited in `bank/`. Edit the generator for the objective
and re-run it, then validate:

```sh
python3 scripts/gen_3_4.py
python3 scripts/lencheck.py bank/3/3.4.json   # longest-answer tell, per item
python3 scripts/validate.py --batch           # per-item rules only
python3 scripts/validate.py                   # + quotas and objective coverage
python3 scripts/stats.py                      # coverage and difficulty report
```

`lencheck.py` is worth running while drafting rather than after: it reports the
same longest-answer measure `validate.py` enforces, but per item, so an option
that needs shortening is obvious before the batch is committed.

`validate.py` fails on domain-quota drift, uncovered objectives, answer-key
imbalance, the longest-answer tell, near-duplicate stems, exhibitless items
above 15%, short explanations, explanations that skip a distractor, and
malformed `show ip route` exhibits (parent must contain its children, and the
declared subnet/mask counts must match what is printed).

`app/lab-tasks.md` is generated too, by `scripts/gen_lab_tasks.py`, which reads
the blueprint and refuses to build unless its task list matches the 15
configure-and-verify objectives exactly.
