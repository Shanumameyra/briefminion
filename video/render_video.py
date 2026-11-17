#!/usr/bin/env python3
"""Render the recorded BriefMinion terminal session into demo.mp4.

Method (honest): the session was recorded live with `script` (see
video/demo.typescript + demo.timing) — real output of run_demo.py, the
saved brief, and the 23-test suite. This script replays that recording as
terminal frames (DejaVu Sans Mono on a dark background) at a readable
pace, with title / tools / end cards. No output text is invented.
"""
import os, re, shutil, subprocess, sys, textwrap

BASE = os.path.dirname(os.path.abspath(__file__))  # video/
ROOT = os.path.dirname(BASE)
W, H, FPS = 1280, 720, 10
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BG = (13, 17, 23)
FG = (230, 237, 243)
DIM = (139, 148, 158)
BLUE = (88, 166, 255)
GREEN = (126, 231, 135)
AMBER = (210, 153, 34)

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

mono = ImageFont.truetype(FONT_MONO, 19)
mono_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 19)
sans = ImageFont.truetype(FONT_SANS, 24)
sans_b = ImageFont.truetype(FONT_SANS_B, 40)
sans_sm = ImageFont.truetype(FONT_SANS, 20)


def strip_ansi(b: bytes) -> str:
    s = b.decode("utf-8", "replace")
    s = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", s)
    s = re.sub(r"\x1b\][^\x07]*\x07", "", s)
    s = s.replace("\x07", "").replace("\x00", "")
    return s


def load_lines() -> list[str]:
    raw = open(os.path.join(BASE, "demo.typescript"), "rb").read()
    text = strip_ansi(raw)
    # `script` may emit \r\n; normalise, drop its header/footer if present.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for ln in text.split("\n"):
        if ln.startswith("Script started") or ln.startswith("Script done"):
            continue
        lines.append(ln.rstrip())
    # Drop trailing blank lines, keep one trailing blank.
    while len(lines) > 1 and lines[-1] == "" and lines[-2] == "":
        lines.pop()
    return lines


def wrap(lines: list[str], width: int = 98) -> list[str]:
    out: list[str] = []
    for ln in lines:
        if len(ln) <= width:
            out.append(ln)
        else:
            out.extend(textwrap.wrap(ln, width=width, break_long_words=False,
                                     break_on_hyphens=False) or [""])
    return out


def draw_terminal(draw, vis_lines):
    y = 28
    for ln in vis_lines:
        if ln.startswith("==") or ln.startswith("==="):
            f, c = mono_b, BLUE
        elif "Agen:" in ln or ln.startswith("   Agen"):
            f, c = mono, GREEN
        elif ln.startswith("OK") or ln == ".......................":
            f, c = mono_b, GREEN
        elif ln.startswith("# ") or ln.startswith("## "):
            f, c = mono_b, AMBER
        else:
            f, c = mono, FG
        draw.text((40, y), ln, font=f, fill=c)
        y += 25


def card(title, lines, accent=BLUE):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 8], fill=accent)
    d.text((80, 200), title, font=sans_b, fill=FG)
    y = 290
    for ln in lines:
        d.text((80, y), ln, font=sans, fill=DIM)
        y += 40
    d.text((80, 620), "BriefMinion  ·  Cortensor Hackathon #5  ·  DoraHacks",
           font=sans_sm, fill=DIM)
    return img


def term_frame(vis_lines):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 8], fill=BLUE)
    d.text((40, 660), "BriefMinion — live terminal recording (run_demo.py, 17 Nov 2026)",
           font=sans_sm, fill=DIM)
    draw_terminal(d, vis_lines)
    return img


def main():
    frames_dir = os.path.join(BASE, "frames")
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir)

    lines = wrap(load_lines())
    # Scene plan (seconds): title 7, tools 6, terminal replay, end 8.
    scenes = []
    scenes.append(("card", card("BriefMinion", [
        "A research-brief agent built on the OpenMinion 0.1 Python SDK.",
        "Ask in Bahasa Indonesia — it searches notes, reads, saves a brief,",
        "and recalls earlier briefs in the same durable session.",
    ]), 7))
    scenes.append(("card", card("What it does — 4 tools", [
        "search_notes  — search the local Markdown knowledge base",
        "read_note     — read the best-matching note (path-guarded)",
        "save_brief    — save a structured brief to briefs/<slug>.md",
        "recall_briefs — list briefs from earlier sessions",
    ]), 6))

    # Terminal replay: reveal lines one by one (0.85 s per line),
    # with readability holds after key sections.
    vis: list[str] = []
    max_lines = 24
    hold_after = {
        "== demo selesai": 5,
        "=== Tes: 23 tes unit ===": 2,
        "OK": 5,
        "=== Demo selesai": 4,
    }
    replay = []
    for ln in lines:
        vis = (vis + [ln])[-max_lines:]
        dur = 0.85
        for key, h in hold_after.items():
            if ln.startswith(key):
                dur += h
        replay.append((list(vis), dur))
    scenes.append(("replay", replay, 0))

    scenes.append(("card", card("Result — verified 17 Nov 2026", [
        "Brief saved: briefs/brief-cortensor-hackathon-5.md",
        "Recall works across runs in the same session (demo-1).",
        "Tests: 23/23 OK  ·  Repo: github.com/Shanumameyra/briefminion",
        "Model note: demo runs on a deterministic local stub —",
        "swap to a real model = one config edit in agents.json.",
    ], accent=GREEN), 8))

    # Emit frames at FPS, caching identical screens.
    cache: dict[str, str] = {}
    idx = 0
    total_s = 0.0
    for kind, payload, dur in scenes:
        if kind == "card":
            key = f"card-{id(payload)}"
            path = os.path.join(frames_dir, f"u{len(cache)}.png")
            payload.save(path)
            cache[key] = path
            n = int(dur * FPS)
            for _ in range(n):
                shutil.copy(cache[key], os.path.join(frames_dir, f"{idx:04d}.png"))
                idx += 1
            total_s += dur
        else:
            for vis_lines, d in payload:
                img = term_frame(vis_lines)
                # cheap dedupe: hash of visible text
                h = hash(tuple(vis_lines))
                if h not in cache:
                    p = os.path.join(frames_dir, f"u{len(cache)}.png")
                    img.save(p)
                    cache[h] = p
                n = max(1, int(round(d * FPS)))
                for _ in range(n):
                    shutil.copy(cache[h], os.path.join(frames_dir, f"{idx:04d}.png"))
                    idx += 1
                total_s += d
    print(f"frames={idx} unique={len(cache)} est_duration={total_s:.1f}s")

    out = os.path.join(ROOT, "demo.mp4")
    cmd = ["ffmpeg", "-y", "-framerate", str(FPS), "-i",
           os.path.join(frames_dir, "%04d.png"),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           out]
    subprocess.run(cmd, check=True, capture_output=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
