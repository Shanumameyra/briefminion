# What We Learned — feedback for Cortensor / OpenMinion

Actionable product feedback from building BriefMinion for Cortensor
Hackathon #5 (OpenMinion 0.1.22, 17 Nov 2026). Ordered by impact on a new
builder's first hour.

1. **Make the Python quickstart work with zero config.** Today
   `Agent(tools=[...])` + `agent.run(...)` fails with `inbound authenticity
   denied (reason=invalid_channel)` unless the agent profile sets
   `default_channel` to a trusted channel. The error never names the
   setting. Either default the API channel to `console`, or make the error
   say: "set `agents.<id>.default_channel`". This is the single biggest
   first-hour papercut.
2. **Let a session change channel, or let me delete one.** A session id
   created under a bad/empty channel is permanently poisoned
   (`belongs to channel '', not 'console'`). A `session forget <id>` CLI
   command (or a documented DB path) would save a lot of confusion.
3. **Document the tool-result envelope.** The model sees
   `{"status": "success", "outputs": {"data": ...}}`, not the raw return
   value. Anyone parsing tool output on the model side (or writing a
   custom provider) needs this in the runtime-surfaces docs, with an
   example payload.
4. **Document the internal turns.** The freshness classifier and the
   `CURRENT TASK` / `Continue the active task` scaffolding are invisible
   until you log requests. A one-page "what the runtime sends your model"
   note — including that internal turns may offer different tools —
   would prevent a class of "my model gets confused" bugs.
5. **Tool-call id uniqueness should be enforced with a clear error.**
   A reused tool-call id aborts the turn with `session event idempotency
   conflict` and no mention of the id. Say which id collided, or
   auto-namespace ids per turn.
6. **Portal needs a no-key smoke path for hackathon builders.** The
   catalog marks `cortensor-portal` experimental (slow/unstable, no
   retries), and there is no documented way to get trial access without
   joining Discord and coordinating. A self-serve trial key — even heavily
   rate-limited — would let builders do the "real model-backed run" the
   hackathon asks for. As it stands, builders without access must fake the
   model role (as this project does, transparently) or bring their own
   paid key.
7. **The Cortensor docs' timeline is TBD everywhere.** The Hackathon #5
   docs page lists kickoff, deadline, evaluation and the submission-repo
   URL all as TBD (last updated 7 Oct 2026), while Eventbrite/DoraHacks
   list 16 Oct – 19 Dec 2026. Builders need one canonical deadline and
   the submission PR repository URL before kickoff, not after.
8. **Small things that worked well and should be kept:** the
   `providers.<name>.base_url` override (the cleanest swap seam in the
   SDK), `@tool` deriving schemas from plain functions, and
   `setup --list-providers` as a discoverable catalog. The
   `tool_call_strategy: hybrid` fallback (JSON tool calls in text) is a
   sensible robustness net for weaker models.
