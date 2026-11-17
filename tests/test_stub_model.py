"""Unit tests for the deterministic stub model router (no network)."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from briefminion.stub_model import _build_brief, decide


def _user(text):
    return [{"role": "user", "content": text}]


def _with_tool(name, content, call_id="call_stub_1"):
    return [
        {"role": "user", "content": "Buatkan brief tentang Cortensor"},
        {"role": "assistant", "content": None,
         "tool_calls": [{"id": call_id, "type": "function",
                         "function": {"name": name, "arguments": "{}"}}]},
        {"role": "tool", "tool_call_id": call_id, "content": content},
    ]


class TestStubRouter(unittest.TestCase):
    def test_first_turn_searches(self):
        d = decide(_user("Buatkan brief tentang Cortensor"))
        self.assertEqual(d["tool_call"]["name"], "search_notes")
        self.assertIn("Cortensor", d["tool_call"]["arguments"]["query"])

    def test_after_search_reads_first_hit(self):
        msgs = _user("Buatkan brief tentang Cortensor") + _with_tool(
            "search_notes",
            "SEARCH_RESULTS:\nnotes/cortensor.md | Cortensor Hackathon #5 | x")
        d = decide(msgs)
        self.assertEqual(d["tool_call"]["name"], "read_note")
        self.assertEqual(d["tool_call"]["arguments"]["path"], "notes/cortensor.md")

    def test_no_match_gives_final_text(self):
        msgs = _user("Buatkan brief tentang zzzz") + _with_tool(
            "search_notes", "NO_MATCH: tidak ada catatan yang cocok.")
        d = decide(msgs)
        self.assertIn("text", d)
        self.assertIn("Tidak ada catatan", d["text"])

    def test_after_read_saves_brief(self):
        msgs = _user("Buatkan brief tentang Cortensor") + _with_tool(
            "search_notes",
            "SEARCH_RESULTS:\nnotes/cortensor.md | Cortensor Hackathon #5 | x")
        msgs += _with_tool(
            "read_note", "NOTE: cortensor.md\n# Cortensor Hackathon #5\nBaris fakta satu.")
        d = decide(msgs)
        self.assertEqual(d["tool_call"]["name"], "save_brief")
        self.assertIn("Cortensor", d["tool_call"]["arguments"]["title"])

    def test_json_envelope_tool_result_is_unwrapped(self):
        """OpenMinion wraps tool output in a JSON envelope; the router must
        see through it (markers live inside ``outputs.data``)."""
        envelope = json.dumps(
            {"status": "success", "summary": "Tool executed successfully",
             "outputs": {"data": "SEARCH_RESULTS:\nnotes/cortensor.md | T | x"}})
        msgs = _user("Buatkan brief tentang Cortensor") + _with_tool(
            "search_notes", envelope)
        d = decide(msgs)
        self.assertEqual(d["tool_call"]["name"], "read_note")
        self.assertEqual(d["tool_call"]["arguments"]["path"], "notes/cortensor.md")

    def test_internal_turn_without_agent_tools_gets_text(self):
        """A runtime-internal turn (e.g. freshness classifier) offers only
        ``submit_output``; the router must not emit an agent tool call."""
        d = decide(_user("Classify freshness"), available_tools=["submit_output"])
        self.assertIn("text", d)
        self.assertNotIn("tool_call", d)

    def test_scaffold_user_messages_are_skipped(self):
        msgs = [
            {"role": "user", "content": "Buatkan brief tentang Cortensor"},
            {"role": "user", "content": "CURRENT TASK (user instructions; data, not system authority):\n{\"revision\":1}"},
            {"role": "user", "content": "Continue the active task using the existing conversation."},
        ]
        d = decide(msgs)
        self.assertEqual(d["tool_call"]["arguments"]["query"],
                         "Buatkan brief tentang Cortensor")

    def test_recall_question_calls_recall_first(self):
        d = decide(_user("Brief apa saja yang sudah dibuat tentang Cortensor?"))
        self.assertEqual(d["tool_call"]["name"], "recall_briefs")

    def test_prior_briefs_become_final_text(self):
        msgs = _user("Brief apa saja yang sudah dibuat?") + _with_tool(
            "recall_briefs",
            "PRIOR_BRIEFS:\nbriefs/brief-cortensor-hackathon-5.md | Brief Cortensor | x")
        d = decide(msgs)
        self.assertIn("text", d)
        self.assertIn("brief-cortensor-hackathon-5.md", d["text"])

    def test_empty_memory_falls_through_to_search(self):
        msgs = _user("Brief apa saja yang sudah dibuat?") + _with_tool(
            "recall_briefs", "MEMORY_EMPTY: tidak ada brief tersimpan untuk topik itu.")
        d = decide(msgs)
        self.assertEqual(d["tool_call"]["name"], "search_notes")

    def test_after_save_final_text(self):
        msgs = _user("Buatkan brief tentang Cortensor") + _with_tool(
            "search_notes",
            "SEARCH_RESULTS:\nnotes/cortensor.md | Cortensor Hackathon #5 | x")
        msgs += _with_tool(
            "read_note", "NOTE: cortensor.md\n# Cortensor Hackathon #5\nFakta.")
        msgs += _with_tool(
            "save_brief", "SAVED: briefs/brief-cortensor-hackathon-5.md (123 byte)")
        d = decide(msgs)
        self.assertIn("text", d)
        self.assertIn("briefs/brief-cortensor-hackathon-5.md", d["text"])

    def test_build_brief_shape(self):
        title, md = _build_brief(
            "cortensor.md",
            "NOTE: cortensor.md\n# Cortensor Hackathon #5\nFakta satu.\nFakta dua.")
        self.assertEqual(title, "Cortensor Hackathon #5")
        self.assertIn("## Ringkasan", md)
        self.assertIn("## Fakta kunci", md)
        self.assertIn("Fakta satu.", md)
        self.assertIn("## Sumber", md)

    def test_build_brief_joins_wrapped_lines_and_strips_markers(self):
        title, md = _build_brief(
            "cortensor.md",
            "NOTE: cortensor.md\n# Cortensor Hackathon #5\nBaris satu\n"
            "lanjutan baris satu.\n\n- Butir daftar.")
        self.assertIn("- Baris satu lanjutan baris satu.", md)
        self.assertIn("- Butir daftar.", md)
        self.assertNotIn("- - Butir", md)


if __name__ == "__main__":
    unittest.main()
