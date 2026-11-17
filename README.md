# BriefMinion — a research-brief agent on OpenMinion 0.1

Cortensor Hackathon #5 entry (DoraHacks, 16 Oct – 19 Dec 2026).
Build a small, working agent with the OpenMinion 0.1 Python SDK, show it
running, and report what worked, what broke, and what should improve.

## What it does

One useful, repeatable workflow: turn a topic into a sourced research brief.

1. `search_notes` — search a local Markdown knowledge base for the topic.
2. `read_note` — read the best-matching note (path-guarded to `notes/`).
3. `save_brief` — save a structured brief (`Ringkasan`, `Fakta kunci`,
   `Sumber`) to `briefs/<slug>.md`.
4. `recall_briefs` — list briefs saved by earlier sessions (long-term
   memory on disk; sessions themselves are durable OpenMinion sessions).

Ask in Bahasa Indonesia, e.g. `Buatkan brief tentang Cortensor`, then
`Brief apa saja yang sudah dibuat?` in the same session.

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
BRIEF_STUB_API_KEY=stub-local-key .venv/bin/python run_demo.py
```

`run_demo.py` starts the local model (below), runs the agent twice in one
session (build a brief, then recall it), and prints the replies. Tests:

```bash
BRIEF_STUB_API_KEY=stub-local-key .venv/bin/python -m unittest discover -s tests -v
```

## The model question, stated honestly

A real model-backed run needs a provider credential this build does not
have: Cortensor Portal access (`CORTENSOR_API_KEY`) or any OpenAI-compatible
key. The VM this was built on also has ~750 MB RAM free, so a local LLM is
not viable. So the *model* role is played by `briefminion/stub_model.py`:
a deterministic, OpenAI-compatible chat-completions server (SSE streaming
included) with fixed, inspectable routing rules. Everything else is the
real OpenMinion 0.1.22 SDK: the `Agent` loop, `@tool` execution, action
policy, durable sessions, and the tool-result envelope.

Swap in a real model with zero code change — edit `agents.json`:

```json
{"agents": {"briefer": {"provider": "cortensor-portal",
                        "model": "oss-20b",
                        "default_channel": "console"}},
 "providers": {"cortensor-portal": {"api_key_env": "CORTENSOR_API_KEY"}}}
```

or any `openai`-compatible provider via `providers.<name>.base_url`.
Portal access is optional for qualification and is coordinated through the
Cortensor Discord; that step belongs to the submitter (see
`SUBMISSION_CHECKLIST.md`).

## Layout

| Path | What it is |
|---|---|
| `briefminion/tools.py` | The 4 `@tool` functions + workspace guards |
| `briefminion/agent.py` | `Agent` wiring, instructions, config selection |
| `briefminion/stub_model.py` | Deterministic local OpenAI-compatible model |
| `briefminion/workspace/notes/` | Knowledge base (3 notes, verified 17 Nov 2026) |
| `briefminion/workspace/briefs/` | Generated briefs (demo output) |
| `run_demo.py` | Recorded demo (see `demo-transcript.txt`) |
| `tests/` | 23 tests: tools, stub router, full agent loop |
| `BUILDING_BLOCKS_TESTED.md` | Required note: blocks used, what worked/broke |
| `WHAT_WE_LEARNED.md` | Product feedback for Cortensor/OpenMinion |
| `SUBMISSION_CHECKLIST.md` | What is done vs. what needs the submitter |

## OpenMinion building blocks exercised

Agent (`openminion.api.Agent`), `@tool` with `min_scope`/`idempotent`,
action policy (ask-first default, bypass only in the demo config), durable
sessions (`session_id` reuse), provider config override
(`providers.openai.base_url`), SSE streaming tool calls, tool-result
envelope parsing. Details in `BUILDING_BLOCKS_TESTED.md`.

## License

Apache-2.0 (same as OpenMinion). All code and notes in this repo are
original work written for this hackathon.
