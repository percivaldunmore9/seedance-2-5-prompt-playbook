#!/usr/bin/env python3
"""A/B-test a play: render its before and after prompts on Seedance 2.5 and compare them.

Standard library only (Python 3.9+). ffmpeg is optional and only used by --side-by-side.

    export SEEDANCE_API_KEY=...
    python ab.py list                      # plays and what testing each costs
    python ab.py show 8                    # both request bodies
    python ab.py run 6                     # render before + after at 480p
    python ab.py run 12 --asset marcus=marcus.png --asset vera=vera.png --side-by-side
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLAYBOOK = ROOT / "plays.json"
MODEL = "seedance-2.5"
DEFAULT_BASE_URL = "https://argolink.io/v1"
USER_AGENT = "seedance-2-5-prompt-playbook/1.0"
VERSIONS = ("before", "after")
PLACEHOLDER = re.compile(r"^https://example\.com/([\w-]+)\.\w+$")
MENTION = re.compile(r"@(Image|Video|Audio) ?(\d+)")
FIXED_RATIOS = ("21:9", "16:9", "4:3", "1:1", "3:4", "9:16")
UPLOADS = {
    ".png": ("image", "image/png"), ".jpg": ("image", "image/jpeg"), ".jpeg": ("image", "image/jpeg"),
    ".mp4": ("video", "video/mp4"), ".mov": ("video", "video/quicktime"),
    ".mp3": ("audio", "audio/mpeg"), ".wav": ("audio", "audio/wav"),
}
POLL_EVERY = 12  # the API docs suggest polling every 10-15 seconds


class PlayError(RuntimeError):
    pass


def load(path: Path = PLAYBOOK) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def get_play(book: dict, number: int) -> dict:
    for play in book["plays"]:
        if play["play"] == number:
            return play
    raise PlayError(f"there is no play {number}; plays run from 1 to {len(book['plays'])}")


def mode(body: dict) -> str:
    if body.get("omni_reference_task_type") == "edit":
        return "edit"
    if "start_image" in body or "end_image" in body:
        return "first_last_frames" if "end_image" in body else "first_frame"
    if any(body.get(key) for key in ("reference_images", "reference_videos", "reference_audios")):
        return "reference"
    return "text"


def problems(body: dict) -> list[str]:
    """The documented Seedance 2.5 request rules, checked locally. An empty list means the body passes."""
    issues = []
    prompt = body.get("prompt", "")
    if not prompt.strip():
        issues.append("prompt is required in every mode")
    if len(prompt.encode()) > 40_000:
        issues.append("prompt is longer than 40,000 bytes")
    if body.get("resolution", "720p") not in ("480p", "720p", "1080p"):
        issues.append("resolution must be 480p, 720p or 1080p")
    images, videos, audios = (body.get(key, []) for key in ("reference_images", "reference_videos", "reference_audios"))
    kind = mode(body)
    if kind == "edit":
        if len(videos) != 1:
            issues.append("an edit takes exactly one reference video, the one it edits")
        if images or audios or "start_image" in body or "end_image" in body:
            issues.append("an edit carries only the video it edits")
        issues += [f"an edit keeps its source's {key}; leave it out" for key in ("duration", "aspect_ratio") if key in body]
    else:
        duration = body.get("duration", 5)
        if not isinstance(duration, int) or not 4 <= duration <= 30:
            issues.append("duration must be a whole number of seconds from 4 to 30")
    if kind in ("first_frame", "first_last_frames"):
        if "start_image" not in body:
            issues.append("end_image needs a start_image")
        if body.get("aspect_ratio", "adaptive") != "adaptive":
            issues.append("frame requests take aspect_ratio adaptive (or none) on Seedance 2.5")
        if images or videos or audios:
            issues.append("start_image and end_image cannot be combined with reference lists")
    elif kind in ("text", "reference") and body.get("aspect_ratio", "16:9") not in FIXED_RATIOS:
        issues.append("aspect_ratio must be one of " + ", ".join(FIXED_RATIOS))
    if len(images) > 30 or len(videos) > 10 or len(audios) > 10 or len(images) + len(videos) + len(audios) > 50:
        issues.append("references are limited to 30 images, 10 videos, 10 audio clips and 50 in total")
    available = {"Image": len(images), "Video": len(videos), "Audio": len(audios)}
    for kind_name, number in MENTION.findall(prompt):
        if not 1 <= int(number) <= available[kind_name]:
            issues.append(f"@{kind_name} {number} points past the end of its list")
    return issues


def billed_seconds(play: dict, body: dict) -> int:
    if mode(body) == "edit":
        return 2 * play["source_seconds"]  # the edited video counts as output and as a reference video
    extra = play.get("reference_video_seconds", 0) if body.get("reference_videos") else 0
    return body.get("duration", 5) + extra


def ab_cost(play: dict, prices: dict, resolution: str | None = None) -> float:
    total = 0.0
    for version in VERSIONS:
        body = play[version]
        total += billed_seconds(play, body) * prices[resolution or body["resolution"]]
    return round(total, 4)


def placeholder_names(body: dict) -> list[str]:
    names = []
    for value in iter_urls(body):
        match = PLACEHOLDER.match(value)
        if match and match.group(1) not in names:
            names.append(match.group(1))
    return names


def iter_urls(body: dict):
    for key in ("start_image", "end_image"):
        if key in body:
            yield body[key]["url"]
    for key in ("reference_images", "reference_videos", "reference_audios"):
        for item in body.get(key, []):
            yield item["url"]


def substitute(body: dict, urls: dict) -> dict:
    def swap(value: str) -> str:
        match = PLACEHOLDER.match(value)
        return urls[match.group(1)] if match else value

    body = copy.deepcopy(body)
    for key in ("start_image", "end_image"):
        if key in body:
            body[key] = {"url": swap(body[key]["url"])}
    for key in ("reference_images", "reference_videos", "reference_audios"):
        if key in body:
            body[key] = [{"url": swap(item["url"])} for item in body[key]]
    return body


def prepare(play: dict, resolution: str | None, assets: dict) -> dict:
    """Both request bodies, with the resolution override applied and every placeholder filled."""
    needed = []
    for version in VERSIONS:
        needed += [name for name in placeholder_names(play[version]) if name not in needed]
    missing = [name for name in needed if name not in assets]
    if missing:
        flags = " ".join(f"--asset {name}=FILE" for name in missing)
        raise PlayError(f"play {play['play']} needs your media: {flags}")
    unused = sorted(set(assets) - set(needed))
    if unused:
        raise PlayError(f"play {play['play']} has no asset named {', '.join(unused)}")
    bodies = {}
    for version in VERSIONS:
        body = {"model": MODEL, **substitute(play[version], assets)}
        if resolution:
            body["resolution"] = resolution
        issues = problems(body)
        if issues:
            raise PlayError(f"{version}: " + "; ".join(issues))
        bodies[version] = body
    return bodies


class Api:
    def __init__(self, key: str, base_url: str):
        self.key = key
        self.base_url = base_url.rstrip("/")

    def call(self, method: str, path: str, payload: dict | None = None, binary: bool = False):
        data = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(self.base_url + path, data=data, method=method)
        request.add_header("Authorization", f"Bearer {self.key}")
        request.add_header("User-Agent", USER_AGENT)
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = response.read()
        except urllib.error.HTTPError as error:
            raise PlayError(f"{method} {path}: HTTP {error.code} {error.read().decode(errors='replace')[:400]}") from None
        return raw if binary else json.loads(raw)

    def upload(self, path: Path) -> str:
        if path.suffix.lower() not in UPLOADS:
            raise PlayError(f"{path}: use JPEG, PNG, MP4, MOV, MP3 or WAV")
        kind, content_type = UPLOADS[path.suffix.lower()]
        data = path.read_bytes()
        ticket = self.call("POST", "/media/uploads", {"model": MODEL, "type": kind,
                                                      "content_type": content_type, "size_bytes": len(data)})
        put = urllib.request.Request(ticket["upload_url"], data=data, method="PUT")
        put.add_header("Content-Type", content_type)
        put.add_header("User-Agent", USER_AGENT)
        with urllib.request.urlopen(put, timeout=300):
            pass
        return ticket["media_url"]


def resolve_assets(api: Api | None, given: dict) -> dict:
    urls = {}
    for name, value in given.items():
        if value.startswith("https://"):
            urls[name] = value
        elif api is None:
            urls[name] = value  # dry run: show the path as given
        else:
            path = Path(value)
            if not path.is_file():
                raise PlayError(f"--asset {name}: {value} is neither a file nor an https:// URL")
            print(f"uploading {name} ({path.name})", file=sys.stderr)
            urls[name] = api.upload(path)
    return urls


def render_both(api: Api, bodies: dict, out_dir: Path, number: int, max_wait: float = 3600) -> dict:
    """Submit both versions, poll them together and download whatever finishes."""
    jobs = {version: {"request_id": api.call("POST", "/videos/generations", body)["request_id"], "status": "pending"}
            for version, body in bodies.items()}
    deadline = time.monotonic() + max_wait
    while any(job["status"] == "pending" for job in jobs.values()):
        time.sleep(POLL_EVERY)
        for version, job in jobs.items():
            if job["status"] != "pending":
                continue
            state = api.call("GET", f"/videos/{job['request_id']}")
            job["status"] = state["status"]
            job["progress"] = state.get("progress", 0)
            if state["status"] == "done":
                target = out_dir / f"play-{number:02d}-{version}.mp4"
                target.write_bytes(api.call("GET", f"/videos/{job['request_id']}/content", binary=True))
                job.update(file=str(target), usage=state.get("usage"))
            elif state["status"] in ("failed", "expired"):
                job["error"] = state.get("error")
        print("  " + " · ".join(f"{v} {j['status']} {j.get('progress', 0)}%" for v, j in jobs.items()), file=sys.stderr)
        if time.monotonic() > deadline:
            break
    return jobs


def side_by_side_command(before: str, after: str, out: str, height: int = 480) -> list[str]:
    """ffmpeg command that puts the two clips next to each other at the same height, with the after audio."""
    graph = (f"[0:v]scale=-2:{height},setsar=1[left];[1:v]scale=-2:{height},setsar=1[right];"
             "[left][right]hstack=inputs=2[v]")
    return ["ffmpeg", "-y", "-loglevel", "error", "-i", before, "-i", after, "-filter_complex", graph,
            "-map", "[v]", "-map", "1:a?", "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", out]


def parse_assets(values: list[str] | None) -> dict:
    assets = {}
    for value in values or []:
        name, sep, target = value.partition("=")
        if not sep or not name or not target:
            raise PlayError(f"--asset expects name=FILE_OR_URL, got {value!r}")
        assets[name] = target
    return assets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="A/B-test Seedance 2.5 prompt plays")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="every play with the cost of testing it")
    show = sub.add_parser("show", help="print both request bodies of a play")
    show.add_argument("play", type=int)
    run = sub.add_parser("run", help="render before and after, then download both")
    run.add_argument("play", type=int)
    run.add_argument("--asset", action="append", metavar="NAME=FILE_OR_URL", help="fill a named placeholder")
    run.add_argument("--resolution", choices=["480p", "720p", "1080p"], help="override the 480p draft setting")
    run.add_argument("--out-dir", default="ab-results")
    run.add_argument("--side-by-side", action="store_true", help="also write a comparison clip (needs ffmpeg)")
    run.add_argument("--dry-run", action="store_true", help="print the bodies and the cost, send nothing")
    args = parser.parse_args(argv)

    book = load()
    prices = book["usd_per_second"]
    try:
        if args.command == "list":
            for play in book["plays"]:
                print(f"{play['play']:>2}  ${ab_cost(play, prices):>5.2f}  {mode(play['after']):<17}  {play['title']}")
            return 0
        play = get_play(book, args.play)
        if args.command == "show":
            print(json.dumps({version: {"model": MODEL, **play[version]} for version in VERSIONS},
                             indent=2, ensure_ascii=False))
            return 0

        assets = parse_assets(args.asset)
        cost = ab_cost(play, prices, args.resolution)
        if args.dry_run:
            bodies = prepare(play, args.resolution, resolve_assets(None, assets))
            print(json.dumps(bodies, indent=2, ensure_ascii=False))
            print(f"play {play['play']}: both versions cost ${cost:.2f}", file=sys.stderr)
            return 0
        prepare(play, args.resolution, {name: "https://placeholder.check/" for name in assets})  # fail before uploading
        key = os.environ.get("SEEDANCE_API_KEY")
        if not key:
            raise PlayError("export SEEDANCE_API_KEY first")
        api = Api(key, os.environ.get("SEEDANCE_BASE_URL") or DEFAULT_BASE_URL)
        bodies = prepare(play, args.resolution, resolve_assets(api, assets))
        print(f"play {play['play']}: submitting both versions, about ${cost:.2f} if both finish", file=sys.stderr)
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        jobs = render_both(api, bodies, out_dir, play["play"])
        if args.side_by_side and all(job["status"] == "done" for job in jobs.values()):
            if shutil.which("ffmpeg"):
                compare = str(out_dir / f"play-{play['play']:02d}-compare.mp4")
                subprocess.run(side_by_side_command(jobs["before"]["file"], jobs["after"]["file"], compare), check=True)
                jobs["compare"] = {"file": compare}
            else:
                print("ffmpeg not found; skipped the side-by-side clip", file=sys.stderr)
        print(json.dumps({"play": play["play"], **jobs}, indent=2))
        return 0 if all(job.get("status") == "done" for v, job in jobs.items() if v in VERSIONS) else 1
    except PlayError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
