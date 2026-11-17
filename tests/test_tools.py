"""Unit tests for BriefMinion tools (no model, no network)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from briefminion.tools import read_note, recall_briefs, save_brief, search_notes


def _unwrap(fn, *args, **kwargs):
    """Call an @tool function: unwrap to the plain callable when needed."""
    target = getattr(fn, "func", None) or getattr(fn, "__wrapped__", None) or fn
    return target(*args, **kwargs)


class TestTools(unittest.TestCase):
    def test_search_finds_cortensor(self):
        out = _unwrap(search_notes, "Cortensor hackathon hadiah")
        self.assertIn("SEARCH_RESULTS:", out)
        self.assertIn("notes/cortensor.md", out)

    def test_search_no_match(self):
        out = _unwrap(search_notes, "zzzzqqq tidak ada")
        self.assertTrue(out.startswith("NO_MATCH"))

    def test_read_note(self):
        out = _unwrap(read_note, "cortensor.md")
        self.assertIn("Hackathon #5", out)
        self.assertIn("$1.150", out)

    def test_read_note_accepts_search_result_path(self):
        out = _unwrap(read_note, "notes/cortensor.md")
        self.assertIn("Hackathon #5", out)

    def test_read_note_rejects_escape(self):
        with self.assertRaises(Exception):
            _unwrap(read_note, "../tools.py")

    def test_save_and_recall_roundtrip(self):
        out = _unwrap(save_brief, "Brief Uji Cortensor",
                      "## Ringkasan\nIsi uji.")
        self.assertIn("SAVED: briefs/brief-uji-cortensor.md", out)
        saved = Path(__file__).resolve().parent.parent / \
            "briefminion" / "workspace" / "briefs" / "brief-uji-cortensor.md"
        try:
            self.assertTrue(saved.is_file())
            self.assertIn("Brief Uji Cortensor", saved.read_text(encoding="utf-8"))
            recalled = _unwrap(recall_briefs, "Cortensor")
            self.assertIn("brief-uji-cortensor.md", recalled)
        finally:
            saved.unlink(missing_ok=True)

    def test_recall_empty_topic(self):
        out = _unwrap(recall_briefs, "zzzzqqq tidak ada")
        self.assertIn("MEMORY_EMPTY", out)


if __name__ == "__main__":
    unittest.main()
