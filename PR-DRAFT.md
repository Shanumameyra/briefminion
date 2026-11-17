# PR description draft — BriefMinion (Cortensor Hackathon #5)

> DRAFT — do NOT submit until the dedicated Hackathon #5 repository URL is
> announced by Cortensor/DoraHacks (still "will be added" as of 17 Nov 2026)
> and Romi approves the submission.

## BriefMinion — a research-brief agent on OpenMinion 0.1

**Repo:** https://github.com/Shanumameyra/briefminion
**Demo video (1–5 min):** `demo.mp4` in the repo (80 s) — also to be uploaded
to YouTube by the submitter before filing the PR.
**Author:** Romi Prayoga (@Shanumameyra), solo, Indonesia.

## What it does

One useful, repeatable workflow: turn a topic into a sourced research
brief, in Bahasa Indonesia.

1. `search_notes` — search a local Markdown knowledge base for the topic.
2. `read_note` — read the best-matching note (path-guarded to `notes/`).
3. `save_brief` — save a structured brief (`Ringkasan`, `Fakta kunci`,
   `Sumber`) to `briefs/<slug>.md`.
4. `recall_briefs` — list briefs saved by earlier sessions (long-term
   memory on disk; sessions are durable OpenMinion sessions).

Demo: `Buatkan brief tentang Cortensor` → brief saved; then in the same
session `Brief apa saja yang sudah dibuat?` → the agent recalls it.

## How to run

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
BRIEF_STUB_API_KEY=stub-local-key .venv/bin/python run_demo.py
BRIEF_STUB_API_KEY=stub-local-key .venv/bin/python -m unittest discover -s tests -v
```

Tests: **23/23 OK** (verified 17 Nov 2026).

## OpenMinion building blocks tested

See `BUILDING_BLOCKS_TESTED.md`: `Agent` loop, `@tool` with `min_scope` /
`idempotent`, action policy, durable sessions, provider config override,
SSE streaming tool calls, tool-result envelope parsing — plus 7
reproducible findings with root causes and workarounds. Product feedback
in `WHAT_WE_LEARNED.md`.

## Model — stated honestly

The recorded demo runs against a deterministic local stub model
(`briefminion/stub_model.py`, an OpenAI-compatible chat-completions
server), because no provider credential was available to the builder.
Everything else is the real OpenMinion 0.1.22 SDK. Swapping in a real
model is one config edit in `agents.json` (Cortensor Portal via
`CORTENSOR_API_KEY`, or any OpenAI-compatible provider) — no code change.
A real-model run will replace the demo recording before submission if
Portal access is granted.

## Checklist (per DoraHacks submission checklist)

- [x] Public source repo + README with setup/run instructions
- [x] Short explanation of the OpenMinion SDK workflow
- [x] One working example + 1–5 min demo video (`demo.mp4`, 80 s)
- [x] Building Blocks Tested note
- [x] What We Learned note
- [ ] Real-model run (needs Cortensor Portal access / OpenAI-compatible key)
- [ ] PR filed to the dedicated Hackathon #5 repository (URL not announced yet)
