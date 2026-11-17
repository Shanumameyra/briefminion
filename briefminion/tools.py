"""BriefMinion tools: the OpenMinion building blocks this agent exercises.

Four tools, all implemented as plain Python functions exposed with
``openminion.tool``:

* ``search_notes``  - READ_ONLY, idempotent (workspace search)
* ``read_note``     - READ_ONLY, idempotent (workspace read, path-guarded)
* ``save_brief``    - WRITE, idempotent (writes ``briefs/<slug>.md``; re-running
  with the same input reproduces the same file)
* ``recall_briefs`` - READ_ONLY, idempotent (long-term memory: briefs saved by
  earlier sessions)

The workspace root is ``briefminion/workspace`` (``notes/`` = knowledge base,
``briefs/`` = generated artifacts). Tools never touch paths outside it.
"""

from __future__ import annotations

import re
from pathlib import Path

from openminion import tool

WORKSPACE_ROOT = Path(__file__).resolve().parent / "workspace"
NOTES_DIR = WORKSPACE_ROOT / "notes"
BRIEFS_DIR = WORKSPACE_ROOT / "briefs"

_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
    "yang", "dan", "atau", "dari", "di", "ke", "tentang", "buat", "buatkan",
    "tolong", "saya", "aku", "apa", "bagaimana", "adalah", "ini", "itu",
    "brief", "ringkasan", "catatan", "mohon", "tidak", "ada",
}


def _tokens(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in _STOPWORDS and len(w) > 1]


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "brief"


def _safe_note_path(path: str) -> Path:
    """Resolve ``path`` inside NOTES_DIR; reject escapes and absolute paths.

    Accepts both ``cortensor.md`` and the search-result form
    ``notes/cortensor.md``.
    """
    cleaned = path.strip()
    if cleaned.startswith("notes/"):
        cleaned = cleaned[len("notes/"):]
    candidate = (NOTES_DIR / cleaned).resolve()
    if not str(candidate).startswith(str(NOTES_DIR.resolve())):
        raise ValueError(f"path di luar notes/: {path!r}")
    if not candidate.is_file():
        raise ValueError(f"catatan tidak ditemukan: {path!r}")
    return candidate


@tool(min_scope="READ_ONLY", idempotent=True)
def search_notes(query: str) -> str:
    """Search the local notes knowledge base for ``query``.

    Returns up to 3 matches as ``path | title | snippet`` lines, or
    ``NO_MATCH`` when nothing matches.
    """
    wanted = _tokens(query)
    if not wanted:
        return "NO_MATCH: query kosong setelah stopword dihapus."
    hits: list[tuple[int, Path, str, str]] = []
    for note in sorted(NOTES_DIR.glob("*.md")):
        text = note.read_text(encoding="utf-8")
        title = next((ln.lstrip("# ").strip() for ln in text.splitlines()
                      if ln.startswith("#")), note.stem)
        words = set(_tokens(text))
        score = sum(1 for tok in wanted if tok in words)
        if score:
            snippet = next((ln.strip() for ln in text.splitlines()
                            if ln.strip() and not ln.startswith("#")), "")[:160]
            hits.append((score, note, title, snippet))
    if not hits:
        return "NO_MATCH: tidak ada catatan yang cocok."
    hits.sort(key=lambda h: (-h[0], h[1].name))
    lines = ["SEARCH_RESULTS:"]
    for _, note, title, snippet in hits[:3]:
        lines.append(f"notes/{note.name} | {title} | {snippet}")
    return "\n".join(lines)


@tool(min_scope="READ_ONLY", idempotent=True)
def read_note(path: str) -> str:
    """Read one note file (``notes/<name>.md``) and return its content."""
    note = _safe_note_path(path)
    content = note.read_text(encoding="utf-8")
    return f"NOTE: {note.name}\n{content[:6000]}"


@tool(idempotent=True)
def save_brief(title: str, markdown: str) -> str:
    """Save a research brief as ``briefs/<slug>.md`` (create or replace).

    Returns the saved path and byte count. The write is confined to the
    workspace ``briefs/`` directory.
    """
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    target = BRIEFS_DIR / f"{_slug(title)}.md"
    header = f"# {title.strip()}\n\n_Disusun oleh BriefMinion (OpenMinion 0.1) dari catatan lokal._\n\n"
    target.write_text(header + markdown.strip() + "\n", encoding="utf-8")
    return f"SAVED: briefs/{target.name} ({target.stat().st_size} byte)"


@tool(min_scope="READ_ONLY", idempotent=True)
def recall_briefs(topic: str) -> str:
    """List briefs saved by earlier sessions that match ``topic``.

    This is the agent's long-term memory: briefs persist on disk across
    sessions, so a later run can recall what an earlier run produced.
    """
    wanted = _tokens(topic)
    if not BRIEFS_DIR.exists():
        return "MEMORY_EMPTY: belum ada brief tersimpan."
    hits: list[str] = []
    for brief in sorted(BRIEFS_DIR.glob("*.md")):
        text = brief.read_text(encoding="utf-8")
        title = next((ln.lstrip("# ").strip() for ln in text.splitlines()
                      if ln.startswith("#")), brief.stem)
        if not wanted or any(tok in text.lower() for tok in wanted):
            first = next((ln.strip() for ln in text.splitlines()
                          if ln.strip() and not ln.startswith(("#", "_"))), "")
            hits.append(f"briefs/{brief.name} | {title} | {first[:120]}")
    if not hits:
        return "MEMORY_EMPTY: tidak ada brief tersimpan untuk topik itu."
    return "PRIOR_BRIEFS:\n" + "\n".join(hits)
