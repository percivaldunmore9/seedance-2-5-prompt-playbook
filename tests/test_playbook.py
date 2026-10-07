"""Offline tests for the playbook: request rules, README sync, and ab.py against a fake API."""
import io
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import ab  # noqa: E402

BOOK = ab.load()
PLAYS = BOOK["plays"]
PRICES = BOOK["usd_per_second"]
README = (ROOT / "README.md").read_text(encoding="utf-8")


def test_twenty_plays_in_order():
    assert [play["play"] for play in PLAYS] == list(range(1, 21))


@pytest.mark.parametrize("play", PLAYS, ids=[f"play{play['play']}" for play in PLAYS])
def test_both_versions_pass_the_request_rules(play):
    for version in ab.VERSIONS:
        assert ab.problems({"model": ab.MODEL, **play[version]}) == [], version


@pytest.mark.parametrize("play", PLAYS, ids=[f"play{play['play']}" for play in PLAYS])
def test_a_pair_differs_only_in_the_prompt_and_reference_order(play):
    before, after = play["before"], play["after"]
    assert before["prompt"] != after["prompt"]
    assert ab.mode(before) == ab.mode(after)
    for key in ("duration", "resolution", "aspect_ratio", "omni_reference_task_type"):
        assert before.get(key) == after.get(key), key
    assert sorted(ab.iter_urls(before)) == sorted(ab.iter_urls(after))
    assert play["changes"] and play["symptom"]


def test_readme_shows_every_prompt_and_cost():
    for play in PLAYS:
        assert play["before"]["prompt"] in README
        assert play["after"]["prompt"] in README
        assert f"`python ab.py run {play['play']}`" in README
        assert f"${ab.ab_cost(play, PRICES):.2f} for both versions" in README


@pytest.mark.parametrize("body, expected", [
    ({"prompt": "x", "start_image": {"url": "https://a/b.png"}, "aspect_ratio": "16:9"}, "adaptive"),
    ({"prompt": "x", "start_image": {"url": "https://a/b.png"}, "reference_images": [{"url": "https://a/c.png"}]},
     "cannot be combined"),
    ({"prompt": "x", "end_image": {"url": "https://a/b.png"}}, "needs a start_image"),
    ({"prompt": "x", "omni_reference_task_type": "edit", "duration": 5, "reference_videos": [{"url": "https://a/v.mp4"}]},
     "keeps its source's duration"),
    ({"prompt": "x", "omni_reference_task_type": "edit", "reference_videos": [{"url": "https://a/v.mp4"}],
      "reference_images": [{"url": "https://a/c.png"}]}, "only the video it edits"),
    ({"prompt": "@Image 3 waves", "reference_images": [{"url": "https://a/1.png"}, {"url": "https://a/2.png"}]},
     "@Image 3 points past the end"),
    ({"prompt": "x", "reference_images": [{"url": f"https://a/{n}.png"} for n in range(31)]}, "limited to 30 images"),
    ({"prompt": "x", "duration": 3}, "from 4 to 30"),
    ({"prompt": "x", "aspect_ratio": "adaptive"}, "aspect_ratio must be one of"),
    ({"prompt": "  "}, "prompt is required"),
])
def test_documented_rejections_are_caught_locally(body, expected):
    assert any(expected in issue for issue in ab.problems(body)), ab.problems(body)


def test_costs_follow_the_billing_rules():
    by_number = {play["play"]: play for play in PLAYS}
    assert ab.ab_cost(by_number[1], PRICES) == pytest.approx(2 * 6 * 0.0874)
    assert ab.ab_cost(by_number[13], PRICES) == pytest.approx(2 * (6 + 5) * 0.0874)   # reference video seconds
    assert ab.ab_cost(by_number[14], PRICES) == pytest.approx(2 * (2 * 6) * 0.0874)   # an edit bills its source twice
    assert ab.ab_cost(by_number[11], PRICES, "720p") == pytest.approx(2 * 8 * 0.196)  # images and audio are free


def test_named_assets_are_required_and_checked():
    play12 = ab.get_play(BOOK, 12)
    with pytest.raises(ab.PlayError, match="--asset marcus=FILE --asset vera=FILE|--asset vera=FILE --asset marcus=FILE"):
        ab.prepare(play12, None, {})
    with pytest.raises(ab.PlayError, match="no asset named dog"):
        ab.prepare(play12, None, {"marcus": "https://x/m.png", "vera": "https://x/v.png", "dog": "https://x/d.png"})
    bodies = ab.prepare(play12, "720p", {"marcus": "https://x/m.png", "vera": "https://x/v.png"})
    assert bodies["before"]["reference_images"] == [{"url": "https://x/v.png"}, {"url": "https://x/m.png"}]
    assert bodies["after"]["reference_images"] == [{"url": "https://x/m.png"}, {"url": "https://x/v.png"}]
    assert bodies["after"]["resolution"] == "720p" and bodies["after"]["model"] == "seedance-2.5"


class Reply(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def fake_api(monkeypatch, outcomes):
    """outcomes maps 'before'/'after' to the list of statuses that job reports."""
    calls, submitted = [], []
    ids = {}

    def urlopen(request, timeout=None):
        url = request.full_url
        calls.append((request.get_method(), url))
        agent = {key.lower(): value for key, value in request.header_items()}.get("user-agent")
        assert agent == "seedance-2-5-prompt-playbook/1.0", f"{url} sent no explicit User-Agent"
        if url.endswith("/media/uploads"):
            name = len([c for c in calls if c[1].endswith("/media/uploads")])
            return Reply(json.dumps({"upload_url": f"https://bucket.test/{name}",
                                     "media_url": f"https://media.test/{name}"}).encode())
        if url.startswith("https://bucket.test/"):
            return Reply(b"")
        if url.endswith("/videos/generations"):
            body = json.loads(request.data)
            version = "before" if not submitted else "after"
            submitted.append(body)
            ids[f"job-{version}"] = version
            return Reply(json.dumps({"request_id": f"job-{version}"}).encode())
        job_id = url.rsplit("/videos/", 1)[1].split("/")[0]
        if url.endswith("/content"):
            return Reply(f"MP4-{ids[job_id]}".encode())
        return Reply(json.dumps(outcomes[ids[job_id]].pop(0)).encode())

    monkeypatch.setattr(ab.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(ab.time, "sleep", lambda seconds: None)
    monkeypatch.setenv("SEEDANCE_API_KEY", "k")
    monkeypatch.delenv("SEEDANCE_BASE_URL", raising=False)
    return calls, submitted


def test_run_uploads_each_asset_once_and_renders_both(monkeypatch, tmp_path):
    for name in ("marcus", "vera"):
        (tmp_path / f"{name}.png").write_bytes(b"png")
    calls, submitted = fake_api(monkeypatch, {
        "before": [{"status": "pending", "progress": 50}, {"status": "done", "usage": {"billed_seconds": 8}}],
        "after": [{"status": "done", "usage": {"billed_seconds": 8}}],
    })
    code = ab.main(["run", "12", "--asset", f"marcus={tmp_path / 'marcus.png'}",
                    "--asset", f"vera={tmp_path / 'vera.png'}", "--out-dir", str(tmp_path / "out")])
    assert code == 0
    assert sum(1 for method, url in calls if url.endswith("/media/uploads")) == 2
    assert calls[0][1] == "https://argolink.io/v1/media/uploads"
    marcus, vera = "https://media.test/1", "https://media.test/2"
    assert submitted[0]["reference_images"] == [{"url": vera}, {"url": marcus}]
    assert submitted[1]["reference_images"] == [{"url": marcus}, {"url": vera}]
    assert (tmp_path / "out" / "play-12-before.mp4").read_bytes() == b"MP4-before"
    assert (tmp_path / "out" / "play-12-after.mp4").read_bytes() == b"MP4-after"


def test_a_failed_version_is_reported_and_the_other_kept(monkeypatch, tmp_path, capsys):
    fake_api(monkeypatch, {
        "before": [{"status": "done", "usage": {"billed_seconds": 5}}],
        "after": [{"status": "failed", "error": {"code": "content_policy_violation", "retryable": False}}],
    })
    assert ab.main(["run", "5", "--out-dir", str(tmp_path)]) == 1
    summary = json.loads(capsys.readouterr().out)
    assert summary["after"]["error"]["code"] == "content_policy_violation"
    assert (tmp_path / "play-05-before.mp4").exists()
    assert not (tmp_path / "play-05-after.mp4").exists()


def test_missing_assets_stop_before_any_request(monkeypatch, capsys):
    def urlopen(request, timeout=None):
        raise AssertionError("no request expected")

    monkeypatch.setattr(ab.urllib.request, "urlopen", urlopen)
    monkeypatch.setenv("SEEDANCE_API_KEY", "k")
    assert ab.main(["run", "16"]) == 1
    assert "--asset lake=FILE" in capsys.readouterr().err


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
def test_side_by_side_command_stacks_two_clips(tmp_path):
    for name, size in (("a.mp4", "854x480"), ("b.mp4", "480x854")):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"testsrc=size={size}:rate=24:duration=1",
                        "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-shortest",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(tmp_path / name)], check=True)
    out = tmp_path / "compare.mp4"
    subprocess.run(ab.side_by_side_command(str(tmp_path / "a.mp4"), str(tmp_path / "b.mp4"), str(out)), check=True)
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "json", str(out)], capture_output=True, text=True, check=True)
    stream = json.loads(probe.stdout)["streams"][0]
    assert stream["height"] == 480 and stream["width"] == 854 + 270
