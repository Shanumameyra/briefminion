# Building Blocks Tested — BriefMinion (OpenMinion 0.1.22)

Cortensor Hackathon #5 requires this note: what OpenMinion building blocks
the project used, what worked, and what did not. Tested 17 Nov 2026 on
Python 3.12, `openminion==0.1.22` (PyPI), Linux VM.

## Blocks used

| Block | How it was used | Verdict |
|---|---|---|
| `Agent` (Python API, `openminion.api`) | Multi-step loop: search → read → save → reply; `session_id` reuse across runs | Works, with the caveats below |
| `@tool` (`min_scope`, `idempotent`) | 4 tools: 3 `READ_ONLY`, 1 write confined to `briefs/` | Works |
| Action policy | `agents.json` default `auto` (writes ask first); `agents.demo.json` `bypass` for the unattended demo | Works |
| Durable sessions | Same `session_id` across two `run_brief` calls; state in project-local `.openminion/state/openminion.db` | Works |
| Provider config override | `providers.openai.base_url` → local stub `http://127.0.0.1:8765/v1` in `agents.json` | Works |
| Native tool calls over SSE | Stub streams `tool_calls` deltas; adapter reconstructs them | Works |
| `openminion setup --list-providers` | Enumerated providers incl. `cortensor-portal` (experimental) and `ollama` (no key) | Works |
| Memory | Long-term memory via on-disk briefs + `recall_briefs`; session history via durable sessions | Works (see note) |

## What worked

- The documented quickstart shape (`Agent(tools=[...])`, `agent.run(prompt)`)
  drives a real multi-turn tool loop once configured; 23/23 tests pass,
  including 3 end-to-end tests through the real runtime.
- Tool schemas are derived from the `@tool` functions with no extra schema
  code; `min_scope="READ_ONLY"` tools run without confirmation under the
  default policy.
- The `providers.<name>.base_url` override in `agents.json` is the one clean
  seam for pointing the runtime at any OpenAI-compatible endpoint — this is
  what makes the stub-model swap possible with zero code change.
- Sessions are genuinely durable: a second run with the same `session_id`
  sees the earlier run's work (verified via `recall_briefs` returning the
  brief saved by the first run).

## What broke (reproducible)

1. **Programmatic `Agent.run` is denied out of the box: `inbound
   authenticity denied (reason=invalid_channel, mode=warn)`.**
   Root cause: the gateway requires the turn's `channel` to be a trusted
   channel; the API path takes it from `agents.<id>.default_channel`,
   whose default is the empty string, and the default trusted list is only
   `["console"]`. The documented quickstart (no config file, no channel)
   therefore fails. Fix: set `"default_channel": "console"` in the agent
   profile. This is arguably a docs/config bug: the quickstart should work
   with no config, or the error should name the missing setting.
2. **Stale sessions are channel-pinned forever.** A `session_id` created
   while the channel was `""` can never be reused after the fix:
   `ValueError: Session '…' belongs to channel '', not 'console'`. There is
   no documented way to migrate or drop a single session; the workaround is
   a fresh session id (or deleting the state DB). Worth a `session forget`
   command.
3. **httpx 0.28.1 chokes on bracketed IPv6 `NO_PROXY` entries.**
   With `NO_PROXY` containing `[::1]` (common in sandboxed VMs), any httpx
   request — including to `127.0.0.1` — raises `InvalidURL: Invalid port:
   ':1]'` before connecting. OpenMinion's OpenAI adapter uses httpx and
   inherits process proxy env, so the failure surfaces as a provider error.
   Workaround in `briefminion/agent.py`: drop bracketed entries from
   `NO_PROXY`/`no_proxy` at import time.
4. **Tool-call ids must be unique per call.** Reusing one static id
   (`call_stub_1`) for every turn aborts the run with `session event
   idempotency conflict`. The runtime never says which id collided; found by
   reading the session-store code. Fix: fresh `uuid` per call.
5. **Tool results arrive JSON-enveloped.** The model does not see the raw
   tool return value; it sees
   `{"status": "success", "summary": …, "outputs": {"data": "<real text>"}}`
   with literal `\n` escapes. Any model-side parsing that expects the raw
   text (markers, line starts) silently fails. The stub unwraps
   `outputs.data` first. This envelope is undocumented in the quickstart.
6. **The runtime injects its own turns.** Each user turn is preceded by
   internal model calls (a freshness-routing classifier with only a
   `submit_output` tool, plus `CURRENT TASK` / `Continue the active task`
   scaffold messages). A model backend must tolerate turns whose tool list
   does not contain the agent's tools, and must not mistake scaffold text
   for the user's prompt. The stub gates tool calls on the offered tool
   list and skips scaffold user messages.
7. **Cortensor Portal is marked experimental in the provider catalog**
   ("can be slow or unstable and requests do not automatically retry").
   Not tested here: no Portal access/credentials were available, and the
   `cortensor-router` (direct) path expects a local router on
   `127.0.0.1:8080`, which was not running.

## Not tested

- A real model-backed run (no Portal access, no API key, ~750 MB free RAM —
  a local LLM is not viable in this VM). The stub is a deterministic
  stand-in; the swap is one config edit, documented in `README.md`.
- The `cortensor-portal` and `cortensor-router` providers, MCP/A2A
  surfaces, skills, and the interactive CLI/Focus room.
- Multi-agent delegation/handoffs (not needed for this workflow).

## Environment

- `openminion==0.1.22`, Python 3.12.3, Linux x86_64.
- Reproduce: `BRIEF_STUB_API_KEY=stub-local-key .venv/bin/python -m unittest
  discover -s tests -v` → 23 tests, all passing (17 Nov 2026).
