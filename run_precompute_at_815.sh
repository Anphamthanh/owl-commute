#!/bin/bash
# Waits until Fri Nov 20, 2026, 8:15 AM, then pre-reads the 6:15 to 8:10 AM snapshots. GOOGLE_API_KEY must be in the environment.
cd ~/projects/ksu/hackathon
T=$(date -j -f "%Y-%m-%d %H:%M" "2026-11-20 08:15" +%s); while [ $(date +%s) -lt $T ]; do sleep 30; done
.venv/bin/python precompute_rush.py 20261120-061500 20261120-081000 > precompute.log 2>&1
