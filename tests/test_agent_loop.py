"""End-to-end test: real OpenMinion Agent loop against the local stub model.

Spins up the stub HTTP server (SSE streaming, OpenAI wire format) and runs
``Agent.run`` through the real OpenMinion 0.1 runtime. Asserts the full
multi-step loop: search -> read -> save -> final reply, plus session memory
on a second run with the same ``session_id``.

Requires ``BRIEF_STUB_API_KEY`` to be set (any dummy value; the stub ignores
auth). Run: ``BRIEF_STUB_API_KEY=stub-local-key .venv/bin/python -m unittest
discover -s tests -v``.
"""

import os
import sys
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from briefminion.agent import run_brief  # noqa: E402
from briefminion.stub_model import serve  # noqa: E402

BRIEFS_DIR = (Path(__file__).resolve().parent.parent
              / "briefminion" / "workspace" / "briefs")


class TestAgentLoop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = serve(port=8765)
        # Fresh ids every run: OpenMinion persists sessions on disk, and a
        # session id created under a different channel can never be reused.
        cls.session_a = f"test-loop-a-{uuid.uuid4().hex[:8]}"
        cls.session_b = f"test-loop-b-{uuid.uuid4().hex[:8]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_full_loop_saves_brief(self):
        target = BRIEFS_DIR / "brief-cortensor-hackathon-5.md"
        if target.exists():
            target.unlink()
        reply = run_brief("Buatkan brief tentang Cortensor",
                          session_id=self.session_a)
        self.assertTrue(target.is_file(), "brief file was not created")
        content = target.read_text(encoding="utf-8")
        self.assertIn("Cortensor Hackathon #5", content)
        self.assertIn("## Fakta kunci", content)
        self.assertIn("brief-cortensor-hackathon-5.md", reply)

    def test_second_run_recalls_prior_brief(self):
        reply = run_brief("Brief apa saja yang sudah dibuat tentang Cortensor?",
                          session_id=self.session_a)
        self.assertIn("brief-cortensor-hackathon-5.md", reply)

    def test_unknown_topic_reports_no_match(self):
        reply = run_brief("Buatkan brief tentang zzzzqqq tidak ada",
                          session_id=self.session_b)
        self.assertIn("Tidak ada catatan", reply)


if __name__ == "__main__":
    unittest.main()
