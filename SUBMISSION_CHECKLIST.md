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
- [x] Public GitHub repo: https://github.com/Shanumameyra/briefminion
      (main, pushed 17 Nov 2026).
- [x] Demo video 1–5 min: `demo.mp4` — **80 detik, 1280×720, h264,
      605–620 KB**, recorded 17 Nov 2026 from a live `run_demo.py` session
      (`video/demo.typescript` + `demo.timing`, rendered by
      `video/render_video.py`); frames verified visually. Naskah di
      `video/demo-script.md`. Video jujur: kartu akhir menyatakan demo
      memakai model stub lokal.
- [x] Deadline confirmed: **19 Des 2026 14:59 WIB** (18 Dec 2026 PT,
      per DoraHacks/Eventbrite).

## NOT done — needs Romi (the submitter) before anything is submitted

1. **Real model-backed run.** The demo runs against a deterministic local
   stub model (documented honestly in README). A real run needs either
   Cortensor Portal access (`CORTENSOR_API_KEY`, coordinated via Cortensor
   Discord — Portal is optional for qualification, but the hackathon asks
   to "run your agent with a real model") or any OpenAI-compatible key.
   No account was created and no key was used by the builder. Swap is one
   config edit in `agents.json` (see README); re-run `run_demo.py` after.
2. **Demo video (1–5 min).** ✅ DONE 17 Nov 2026 — `demo.mp4` (80 detik,
   1280×720, h264, ~620 KB), direkam dari sesi `run_demo.py` nyata;
   naskah di `video/demo-script.md`. Video perlu di-upload ke YouTube oleh
   Romi sebelum PR (link YouTube dicantumkan di PR).
3. **GitHub repo + DoraHacks submission.** Repo publik SUDAH ADA:
   https://github.com/Shanumameyra/briefminion (main). Yang belum: PR ke
   repo target Hackathon #5 — **URL-nya MASIH belum diumumkan per cek
   17 Nov 2026 ~13:17 WIB** (halaman DoraHacks + docs Cortensor masih
   "will be added before kickoff"; org GitHub `cortensor` hanya punya 4
   repo: installer, community-projects, salt, desktop-app; org
   `openminion` juga tidak punya repo hackathon-5). Draf deskripsi PR ada
   di `PR-DRAFT.md`. JANGAN submit PR sebelum repo target diumumkan +
   Romi menyetujui.
4. **Confirm the deadline.** ✅ CONFIRMED: 19 Des 2026 14:59 WIB
   (18 Dec 2026 PT).
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
