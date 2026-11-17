#!/bin/bash
# Driver for the recorded BriefMinion demo (run under `script` for timing).
cd "$(dirname "$0")/.." || exit 1
export BRIEF_STUB_API_KEY=stub-local-key
echo "=== BriefMinion — demo agen research-brief (OpenMinion 0.1.22) ==="
echo
.venv/bin/python run_demo.py
echo
echo "=== Hasil: brief yang tersimpan di briefs/ ==="
cat briefminion/workspace/briefs/brief-cortensor-hackathon-5.md
echo
echo "=== Tes: 23 tes unit ==="
.venv/bin/python -m unittest discover -s tests 2>&1 | tail -5
echo
echo "=== Demo selesai — repo: github.com/Shanumameyra/briefminion ==="
