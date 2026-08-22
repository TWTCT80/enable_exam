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
because the page fetches `bank.json`. The app itself is plain HTML/CSS/JS and
deploys to GitHub Pages by publishing the `app/` directory.

## Working on the bank

Items are never hand-edited in `bank/`. Edit the generator for the objective
and re-run it, then validate:

```sh
python3 scripts/gen_3_4.py
python3 scripts/validate.py --batch    # per-item rules only
python3 scripts/validate.py            # + quotas and objective coverage
```

`validate.py` fails on domain-quota drift, uncovered objectives, answer-key
imbalance, the longest-answer tell, near-duplicate stems, exhibitless items
above 15%, short explanations, explanations that skip a distractor, and
malformed `show ip route` exhibits (parent must contain its children, and the
declared subnet/mask counts must match what is printed).

Full mode is expected to fail until the bank is complete; see `PLAN.md` for
the allocation and current state.
