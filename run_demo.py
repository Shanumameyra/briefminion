"""Recorded demo: start the local stub model, run BriefMinion twice.

Run 1 (fresh session): "Buatkan brief tentang Cortensor" -> the agent must
search notes, read the Cortensor note, save a brief, and reply in Bahasa
Indonesia naming the saved file.

Run 2 (same session_id): "Brief apa saja yang sudah dibuat?" -> the agent
recalls prior briefs, proving durable sessions + long-term memory.

Usage:
    BRIEF_STUB_API_KEY=stub-local-key .venv/bin/python run_demo.py
"""

from __future__ import annotations

import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from briefminion.agent import run_brief  # noqa: E402
from briefminion.stub_model import serve  # noqa: E402


def _wait_for_stub(port: int, tries: int = 25) -> None:
    for _ in range(tries):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/v1/models", timeout=2) as resp:
                if resp.status == 200:
                    return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("stub model tidak merespons")


def main() -> int:
    server = serve(port=8765)
    _wait_for_stub(8765)
    print("== stub model jalan di http://127.0.0.1:8765/v1 (brief-stub-1)")
    try:
        print("\n== Run 1 (session demo-1): Buatkan brief tentang Cortensor")
        reply1 = run_brief("Buatkan brief tentang Cortensor",
                           session_id="demo-1")
        print(f"   Agen: {reply1}")
        print("\n== Run 2 (session demo-1 lagi): Brief apa saja yang sudah dibuat?")
        reply2 = run_brief("Brief apa saja yang sudah dibuat tentang Cortensor?",
                           session_id="demo-1")
        print(f"   Agen: {reply2}")
    finally:
        server.shutdown()
    print("\n== demo selesai")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
