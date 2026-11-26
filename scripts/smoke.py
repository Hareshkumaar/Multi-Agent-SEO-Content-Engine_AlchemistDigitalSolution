"""Run one article against a running server and print each progress event.
Usage: python scripts/smoke.py http://localhost:8000 "best laptops for students under 100000 PKR" """
import json
import sys

import httpx

base, topic = sys.argv[1].rstrip("/"), sys.argv[2]
with httpx.stream("POST", f"{base}/api/generate", timeout=300,
                  json={"topic": topic, "audience": "University students", "tone": "friendly, practical"}) as r:
    for line in r.iter_lines():
        if line.startswith("data: "):
            print(json.loads(line[6:]))
