"""Minimal Argolink example for seedance-2.5; no request is made on import."""
from __future__ import annotations
import os
import requests

BASE = "https://api.argolink.io"
MODEL = "seedance-2.5"

def request():
    key = os.environ["ARGOLINK_API_KEY"]
    body = {"model": MODEL, "prompt": "a concise cinematic establishing shot", "duration": 5}
    response = requests.post(BASE + "/v1/videos/generations", headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, json=body, timeout=60)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    print(request())
