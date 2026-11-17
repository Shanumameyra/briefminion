"""Deterministic local stand-in for an OpenAI-compatible chat model.

Why this exists (stated plainly, see README): a real model-backed run needs
a provider credential the builder does not have -- Cortensor Portal access
(``CORTENSOR_API_KEY``) or any OpenAI-compatible key. This VM also has ~750 MB
RAM free, so a local LLM is not viable. The stub therefore plays the *model*
role with fixed, inspectable routing rules, while everything else -- the
OpenMinion runtime, the agent loop, tool execution, policy, sessions and
memory -- is the real OpenMinion 0.1 SDK.

The stub speaks the exact wire format OpenMinion's OpenAI adapter expects:

* ``POST /v1/chat/completions`` with ``stream: true``  -> SSE chunks
  (``data: {...}`` lines, then ``data: [DONE]``), tool-call deltas included.
* ``POST /v1/chat/completions`` with ``stream: false`` -> one JSON object.
* ``GET  /v1/models`` -> model list (some clients probe it).

Routing rules (stateless; the full history is re-read on every turn):

1. no ``search_notes`` call yet          -> call ``search_notes`` (whole prompt)
2. search returned NO_MATCH              -> final text: no notes found
3. search ok, no ``read_note`` yet       -> call ``read_note`` (first hit)
4. read ok, no ``save_brief`` yet        -> call ``save_brief`` (brief built
   deterministically from the note that was just read)
5. save ok                               -> final text summarising the brief

Tool results are recognised by their markers: ``SEARCH_RESULTS:`` /
``NO_MATCH``, ``NOTE:``, ``SAVED:``. If the conversation already contains a
``recall_briefs`` result (``PRIOR_BRIEFS:`` / ``MEMORY_EMPTY``) the router
still proceeds with the search -> read -> save flow.
"""

from __future__ import annotations

import json
import os
import re
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL_NAME = "brief-stub-1"

# Opt-in diagnostics: set BRIEF_STUB_LOG=/tmp/stub-log.jsonl to record every
# request's messages (helps debug how a runtime shapes tool results).

_SEARCH_RE = re.compile(r"^SEARCH_RESULTS:", re.M)
_NO_MATCH_RE = re.compile(r"^NO_MATCH", re.M)
_NOTE_RE = re.compile(r"^NOTE:\s*(\S+)", re.M)
_SAVED_RE = re.compile(r"^SAVED:\s*(\S+)", re.M)
_PRIOR_RE = re.compile(r"^PRIOR_BRIEFS:\n(.*)", re.M | re.S)
_MEMORY_EMPTY_RE = re.compile(r"^MEMORY_EMPTY", re.M)
_RECALL_RE = re.compile(r"sudah dibuat|apa saja|recall|ingat|sebelumnya|riwayat", re.I)


def _unwrap_tool_content(raw: str) -> str:
    """Unwrap OpenMinion's tool-result envelope.

    The runtime returns tool output as a JSON string like
    ``{"status": "success", "summary": ..., "outputs": {"data": "<real text>"}}``.
    Without unwrapping, markers such as ``SEARCH_RESULTS:`` sit inside one
    JSON line with literal ``\\n`` escapes and no regex matches. Falls back
    to the raw string when it is not such an envelope.
    """
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw
    if isinstance(parsed, dict):
        outputs = parsed.get("outputs")
        if isinstance(outputs, dict) and isinstance(outputs.get("data"), str):
            return outputs["data"]
        if isinstance(parsed.get("data"), str):
            return parsed["data"]
    return raw


def _tool_names(messages: list[dict]) -> list[str]:
    names: list[str] = []
    for msg in messages:
        for call in msg.get("tool_calls") or []:
            fn = call.get("function") or {}
            if fn.get("name"):
                names.append(fn["name"])
    return names


def _tool_texts(messages: list[dict]) -> str:
    return "\n".join(
        _unwrap_tool_content(str(m.get("content") or ""))
        for m in messages
        if m.get("role") == "tool"
    )


def _last_user_text(messages: list[dict]) -> str:
    """The user's original request.

    The runtime injects scaffold user messages (``Continue the active task
    ...``, ``CURRENT TASK ...`` JSON wrappers); the original prompt is the
    first user message that is neither.
    """
    for msg in messages:
        if msg.get("role") != "user":
            continue
        content = msg.get("content")
        text = ""
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            text = " ".join(
                str(p.get("text") or "") for p in content
                if isinstance(p, dict)
            )
        stripped = text.strip()
        if stripped and not stripped.startswith("Continue the active task") \
                and not stripped.startswith("CURRENT TASK"):
            return stripped
    return ""


def _first_search_hit(tool_text: str) -> str | None:
    for line in tool_text.splitlines():
        if line.startswith("notes/"):
            return line.split("|")[0].strip()
    return None


def _build_brief(note_name: str, tool_text: str) -> tuple[str, str]:
    """Build (title, markdown body) from the NOTE tool result.

    Facts are taken as paragraphs (blank-line separated, hard wraps joined),
    so wrapped source lines do not become separate bullets and source list
    markers (``- ``) are not doubled.
    """
    match = _NOTE_RE.search(tool_text)
    body = tool_text[match.end():].strip() if match else tool_text
    lines = [ln.rstrip() for ln in body.splitlines()]
    title = next((ln.lstrip("# ").strip() for ln in lines if ln.startswith("#")),
                 note_name.replace(".md", "").replace("-", " ").title())
    paragraphs: list[str] = []
    current: list[str] = []
    for ln in lines:
        if ln.startswith("#"):
            continue
        if not ln.strip():
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        if ln[0] in " \t" and (current or paragraphs):
            # Indented continuation line: belongs to the paragraph above it.
            target = current if current else [paragraphs.pop()]
            target.append(ln.strip())
            if not current:
                paragraphs.append(" ".join(target))
            continue
        stripped = ln.strip()
        if stripped.startswith(("- ", "* ")):
            # A list item is its own fact; don't merge it into the
            # surrounding paragraph.
            if current:
                paragraphs.append(" ".join(current))
                current = []
            paragraphs.append(stripped[2:].strip())
        else:
            current.append(stripped)
    if current:
        paragraphs.append(" ".join(current))
    facts = [p[:280] + ("…" if len(p) > 280 else "") for p in paragraphs if p][:5]
    md = ["## Ringkasan",
          f"Topik: **{title}**. Brief ini dirangkum dari catatan lokal "
          f"`notes/{note_name}`.",
          "",
          "## Fakta kunci"]
    for fact in facts:
        md.append(f"- {fact}")
    md += ["", "## Sumber", f"- `notes/{note_name}` (catatan lokal, terverifikasi 17 Nov 2026)",
           "", "## Yang masih perlu dicek",
           "- Syarat payout akhir (identitas / KYC / W-8BEN / rekening) ada di tangan penyelenggara; bukan bagian dari brief ini."]
    return title, "\n".join(md)


def decide(messages: list[dict], available_tools: list[str] | None = None) -> dict:
    """Return either ``{"tool_call": {"name": ..., "arguments": {...}}}``
    or ``{"text": ...}`` for the next assistant turn.

    ``available_tools`` is the request's tool list. The runtime also sends
    internal turns (e.g. a freshness classifier) whose only tool is
    ``submit_output``; for those we must NOT emit one of our agent tools --
    a plain text reply is the safe fallback and the runtime tolerates it.
    """
    tool_text = _tool_texts(messages)
    made = _tool_names(messages)
    user_text = _last_user_text(messages).strip()
    offered = set(available_tools or [])

    def _call(name: str, args: dict) -> dict:
        if offered and name not in offered:
            return {"text": "Lanjutkan tugas dengan hasil tool yang sudah ada."}
        # Every tool call needs a fresh id: the runtime treats a repeated
        # tool-call id as a duplicate session event ("session event
        # idempotency conflict") and aborts the turn.
        return {"tool_call": {"id": f"call_stub_{uuid.uuid4().hex[:12]}",
                              "name": name, "arguments": args}}

    # Memory first: a "what was already briefed?" question is answered from
    # the on-disk briefs (long-term memory), not by rebuilding the brief.
    if _RECALL_RE.search(user_text) and "recall_briefs" not in made:
        return _call("recall_briefs", {"topic": user_text})
    prior = _PRIOR_RE.search(tool_text)
    if prior:
        return {"text": ("Brief yang sudah dibuat sebelumnya:\n"
                         f"{prior.group(1).strip()}\n"
                         "Itu arsip dari sesi-sesi sebelumnya; minta topik baru "
                         "kalau mau brief lain.")}
    if "search_notes" not in made:
        return _call("search_notes", {"query": user_text or "cortensor"})
    if _NO_MATCH_RE.search(tool_text):
        return {"text": ("Tidak ada catatan lokal yang cocok dengan topik itu, "
                         "jadi saya tidak bisa menyusun brief. Coba topik lain "
                         "yang ada di catatan: Cortensor, Reactive Omni, atau Terminal 3.")}
    if "read_note" not in made:
        hit = _first_search_hit(tool_text)
        if not hit:
            return {"text": "Hasil pencarian tidak memuat path catatan yang bisa dibaca."}
        return _call("read_note", {"path": hit})
    if "save_brief" not in made:
        note_match = _NOTE_RE.search(tool_text)
        note_name = note_match.group(1) if note_match else "notes.md"
        title, md = _build_brief(note_name, tool_text)
        return _call("save_brief",
                     {"title": f"Brief {title}", "markdown": md})
    saved = _SAVED_RE.search(tool_text)
    path = saved.group(1) if saved else "briefs/"
    return {"text": (f"Selesai. Brief tersimpan di `{path}` — disusun dari catatan "
                     f"lokal lewat pencarian, pembacaan, dan penyimpanan sebagai "
                     f"satu alur agen.")}


def _completion_payload(model: str, decision: dict) -> dict:
    if "tool_call" in decision:
        tc = decision["tool_call"]
        message = {"role": "assistant", "content": None,
                   "tool_calls": [{"id": tc["id"], "type": "function",
                                   "function": {"name": tc["name"],
                                                "arguments": json.dumps(tc["arguments"], ensure_ascii=False)}}]}
        finish = "tool_calls"
    else:
        message = {"role": "assistant", "content": decision["text"]}
        finish = "stop"
    return {"id": "chatcmpl-stub", "object": "chat.completion",
            "created": 0, "model": model,
            "choices": [{"index": 0, "message": message, "finish_reason": finish}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}


def _sse_chunks(model: str, decision: dict) -> list[str]:
    """SSE chunks for one streamed completion (OpenAI shape)."""
    base = {"id": "chatcmpl-stub", "object": "chat.completion.chunk",
            "created": 0, "model": model}
    chunks: list[dict] = []
    if "tool_call" in decision:
        tc = decision["tool_call"]
        args = json.dumps(tc["arguments"], ensure_ascii=False)
        chunks.append({**base, "choices": [{"index": 0, "delta": {
            "role": "assistant", "content": None,
            "tool_calls": [{"index": 0, "id": tc["id"], "type": "function",
                            "function": {"name": tc["name"], "arguments": ""}}]},
            "finish_reason": None}]})
        chunks.append({**base, "choices": [{"index": 0, "delta": {
            "tool_calls": [{"index": 0,
                            "function": {"arguments": args}}]},
            "finish_reason": None}]})
        chunks.append({**base, "choices": [{"index": 0, "delta": {},
                                            "finish_reason": "tool_calls"}]})
    else:
        chunks.append({**base, "choices": [{"index": 0, "delta": {
            "role": "assistant", "content": decision["text"]},
            "finish_reason": None}]})
        chunks.append({**base, "choices": [{"index": 0, "delta": {},
                                            "finish_reason": "stop"}]})
    return [f"data: {json.dumps(c, ensure_ascii=False)}\n\n" for c in chunks]


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):  # keep test output clean
        pass

    def _send_json(self, payload: dict, status: int = 200) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):  # noqa: N802
        if self.path.rstrip("/") in ("/v1/models", "/models"):
            self._send_json({"object": "list",
                             "data": [{"id": MODEL_NAME, "object": "model",
                                       "created": 0, "owned_by": "briefminion"}]})
        else:
            self._send_json({"error": "not found"}, status=404)

    def do_POST(self):  # noqa: N802
        if self.path.rstrip("/") != "/v1/chat/completions":
            self._send_json({"error": "not found"}, status=404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send_json({"error": "invalid json"}, status=400)
            return
        log_path = os.environ.get("BRIEF_STUB_LOG")
        offered = [t.get("function", {}).get("name")
                   for t in payload.get("tools") or []]
        if log_path:
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"messages": payload.get("messages"),
                                     "tools": offered},
                                    ensure_ascii=False) + "\n")
        decision = decide(payload.get("messages") or [],
                          available_tools=offered)
        if payload.get("stream"):
            body = "".join(_sse_chunks(payload.get("model") or MODEL_NAME, decision))
            body += "data: [DONE]\n\n"
            raw = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        else:
            self._send_json(_completion_payload(payload.get("model") or MODEL_NAME, decision))


def serve(host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
