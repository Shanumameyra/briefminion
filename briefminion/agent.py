"""Wire BriefMinion's tools into a real OpenMinion ``Agent``.

The agent is configured through an ``agents.json`` file (OpenMinion's own
config format). Two configs ship with the project:

* ``agents.json``       -- safe default: ``action_policy`` ``auto`` (writes ask
  first). Swap ``providers.openai.base_url`` / ``provider`` to point at a real
  model: Cortensor Portal (``cortensor-portal`` + ``CORTENSOR_API_KEY``) or any
  OpenAI-compatible provider. No code change needed.
* ``agents.demo.json``  -- demo/test config: same agent, but the local stub
  model (``http://127.0.0.1:8765/v1``) and ``action_policy`` ``bypass`` so the
  recorded demo runs unattended. The write tool is confined to
  ``briefminion/workspace/briefs/`` either way.
"""

from __future__ import annotations

import os
from pathlib import Path

# Sandbox workaround (documented in BUILDING_BLOCKS_TESTED.md): httpx 0.28.1
# raises ``InvalidURL: Invalid port: ':1]'`` when NO_PROXY contains bracketed
# IPv6 entries such as ``[::1]`` (present in this VM's environment). The
# OpenMinion OpenAI adapter uses httpx and reads proxy env vars, so a local
# stub at 127.0.0.1 is unreachable until those entries are dropped. Keep the
# unbracketed entries (localhost, 127.0.0.1, ::1) so loopback stays proxyless.
for _var in ("NO_PROXY", "no_proxy"):
    _raw = os.environ.get(_var, "")
    _kept = [h for h in _raw.split(",") if h.strip() and not h.strip().startswith("[")]
    os.environ[_var] = ",".join(_kept)

from openminion import Agent

from .tools import recall_briefs, read_note, save_brief, search_notes

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INSTRUCTIONS = (
    "You are BriefMinion, a research-brief agent. "
    "When the user asks for a brief on a topic: "
    "1) search_notes for the topic, "
    "2) read_note the best match, "
    "3) save_brief with a structured brief (Ringkasan, Fakta kunci, Sumber), "
    "4) reply in Bahasa Indonesia naming the saved file. "
    "If search finds nothing, say so and stop. "
    "If the user asks what was briefed before, use recall_briefs."
)

TOOLS = [search_notes, read_note, save_brief, recall_briefs]


def build_agent(*, config_path: str | Path | None = None,
                session_id: str | None = None) -> Agent:
    """Build the agent. ``config_path`` defaults to the demo config."""
    config = Path(config_path) if config_path else PROJECT_ROOT / "agents.demo.json"
    return Agent(
        instructions=INSTRUCTIONS,
        tools=TOOLS,
        config_path=str(config),
        agent_id="briefer",
        session_id=session_id,
    )


def run_brief(prompt: str, *, config_path: str | Path | None = None,
              session_id: str | None = None) -> str:
    """Run one turn and return the agent's reply text."""
    with build_agent(config_path=config_path, session_id=session_id) as agent:
        result = agent.run(prompt)
        return result.text
