# Submission Checklist — Cortensor Hackathon #5

## Done (in this repo, verified 17 Nov 2026)

- [x] Working agent on OpenMinion 0.1.22: `BriefMinion` — research-brief
      workflow (search → read → save → recall) via the Python `Agent` API.
- [x] Public-ready repo layout: README, requirements, 23 passing tests
      (`BRIEF_STUB_API_KEY=stub-local-key .venv/bin/python -m unittest
      discover -s tests -v` → OK), recorded demo (`run_demo.py`,
      transcript in `demo-transcript.txt`).
- [x] `BUILDING_BLOCKS_TESTED.md` — blocks used, what worked, 7
      reproducible findings with root causes and workarounds.
- [x] `WHAT_WE_LEARNED.md` — actionable product feedback.
- [x] Example output: `briefminion/workspace/briefs/brief-cortensor-hackathon-5.md`.
- [x] All code and notes are original work; no copied code. Apache-2.0.

## NOT done — needs Romi (the submitter) before anything is submitted

1. **Real model-backed run.** The demo runs against a deterministic local
   stub model (documented honestly in README). A real run needs either
   Cortensor Portal access (`CORTENSOR_API_KEY`, coordinated via Cortensor
   Discord — Portal is optional for qualification, but the hackathon asks
   to "run your agent with a real model") or any OpenAI-compatible key.
   No account was created and no key was used by the builder. Swap is one
   config edit in `agents.json` (see README); re-run `run_demo.py` after.
2. **Demo video (1–5 min).** Required by the submission checklist. Not
   recorded — needs a screen recording of `run_demo.py` (or a run against
   the real model). The transcript in `demo-transcript.txt` is the script.
3. **GitHub repo + DoraHacks submission.** Needs Romi's GitHub account:
   fork/clone the official repo is NOT required, but the project must be
   public on GitHub, and submission is a PR linking it to the dedicated
   Hackathon #5 repository (URL "to be added before kickoff" per Cortensor
   docs — verify it exists on the DoraHacks page first). Builder did NOT
   create any account or submit anything.
4. **Confirm the deadline.** Cortensor's docs list the submission deadline
   as TBD; Eventbrite lists 19 Dec 2026. Confirm on
   https://dorahacks.io/hackathon/2418/detail before submitting.
5. **Prize payout (if placed).** $1,150 total in $COR (50% liquid, 50%
   one-month staking lock); 1st $500. Cortensor may require identity /
   eligibility checks for prize distribution; a winning team designates
   one payout recipient (wallet address). Awards are discretionary — no
   placement is guaranteed. Identity verification, W-8BEN, and bank/wallet
   details are Romi's step, not the builder's.

## Prize / eligibility notes (verified 17 Nov 2026)

- Open and Indonesia-eligible as far as public rules show: no
  Indonesia-specific exclusion in the Cortensor docs, DoraHacks terms, or
  hackathon pages (DoraHacks terms: void where prohibited by law; minors
  need a guardian). Final payout eligibility is the organizer's call.
- No entry fee; no paid keys/APIs/deposits were used to build this.
