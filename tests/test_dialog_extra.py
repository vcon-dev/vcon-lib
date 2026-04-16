"""Extra tests for dialog utilities to improve coverage."""

import base64
from datetime import datetime, timezone

import pytest

from src.vcon.dialog import Dialog
from src.vcon.party import PartyHistory


class DummyResponse:
    def __init__(self, status_code=200, content=b"data", headers=None, text=""):
        self.status_code = status_code
        self.content = content
        self.headers = headers or {"Content-Type": "text/plain"}
        self.text = text


def test_incomplete_disposition_validation():
    with pytest.raises(ValueError):
        Dialog(type="incomplete", start=datetime.now(timezone.utc), parties=[0])

    with pytest.raises(ValueError):
        Dialog(
            type="incomplete",
            start=datetime.now(timezone.utc),
            parties=[0],
            disposition="invalid",
        )

    dialog = Dialog(
        type="incomplete",
        start=datetime.now(timezone.utc),
        parties=[0],
        disposition="busy",
    )
    assert dialog.disposition == "busy"


def test_video_mediatype_autodetect():
    dialog = Dialog(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],
        filename="clip.mov",
    )
    assert dialog.mediatype == "video/quicktime"

    dialog = Dialog(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],
        filename="clip.unknown",
    )
    assert dialog.mediatype == "video/mp4"


def test_to_dict_party_history_serialization():
    history = [
        PartyHistory(party=0, event="join", time=datetime(2026, 2, 3, 12, 0, tzinfo=timezone.utc)),
        PartyHistory(party=1, event="drop", time="2026-02-03T12:05:00Z"),
    ]
    dialog = Dialog(
        type="text",
        start=datetime.now(timezone.utc),
        parties=[0, 1],
        party_history=history,
    )
    data = dialog.to_dict()
    assert data["party_history"][0]["event"] == "join"
    assert data["party_history"][1]["time"] == "2026-02-03T12:05:00Z"


def test_add_external_data_and_inline_data(monkeypatch):
    def fake_get(url):
        return DummyResponse(content=b"hello", headers={"Content-Type": "text/plain"})

    monkeypatch.setattr("src.vcon.dialog.requests.get", fake_get)

    dialog = Dialog(type="text", start=datetime.now(timezone.utc), parties=[0])
    dialog.add_external_data("https://example.com/file.txt", filename="", mediatype="")

    assert dialog.url
    assert dialog.filename == "file.txt"
    assert dialog.mediatype == "text/plain"
    assert dialog.content_hash

    dialog.add_inline_data("inline", filename="note.txt", mediatype="text/plain")
    assert dialog.body == "inline"
    assert dialog.encoding == "base64url"
    assert dialog.content_hash


def test_is_external_inline_and_hash_checks(monkeypatch):
    dialog = Dialog(type="text", start=datetime.now(timezone.utc), parties=[0])
    assert dialog.is_inline_data()

    dialog.url = "https://example.com"
    assert dialog.is_external_data()

    def fake_get(url):
        return DummyResponse(content=b"content", headers={"Content-Type": "text/plain"})

    monkeypatch.setattr("src.vcon.dialog.requests.get", fake_get)

    dialog.content_hash = base64.urlsafe_b64encode(b"different").decode()
    assert dialog.is_external_data_changed() is True


def test_to_inline_data_success(monkeypatch):
    def fake_get(url):
        return DummyResponse(content=b"payload", headers={"Content-Type": "text/plain"})

    monkeypatch.setattr("src.vcon.dialog.requests.get", fake_get)

    dialog = Dialog(type="text", start=datetime.now(timezone.utc), parties=[0])
    dialog.url = "https://example.com/data"
    dialog.to_inline_data()

    assert dialog.body
    assert dialog.encoding == "base64url"
    assert dialog.mediatype == "text/plain"
    assert not hasattr(dialog, "url")


def test_content_hash_helpers():
    dialog = Dialog(type="text", start=datetime.now(timezone.utc), parties=[0], body="hello")
    calculated = dialog.calculate_content_hash()
    assert dialog.verify_content_hash(calculated)

    with pytest.raises(ValueError):
        Dialog(type="text", start=datetime.now(timezone.utc), parties=[0]).calculate_content_hash()

    assert not dialog.verify_content_hash("wrong")


def test_video_helpers_and_streaming():
    dialog = Dialog(type="video", start=datetime.now(timezone.utc), parties=[0])
    assert dialog.is_video()
    assert dialog.is_video("video/mp4")
    assert not dialog.is_video("text/plain")

    dialog.add_streaming_video_reference("abc", "video/mp4")
    assert dialog.url.startswith("stream://")
    assert dialog.metadata["streaming"]["reference_id"] == "abc"

    assert dialog.get_video_format_from_mediatype("video/mp4") == "mp4"
    assert dialog.get_video_format_from_mediatype("unknown/type") == "unknown"


def test_add_video_with_optimal_storage(monkeypatch):
    dialog = Dialog(type="video", start=datetime.now(timezone.utc), parties=[0])

    with pytest.raises(ValueError):
        dialog.add_video_with_optimal_storage(b"x" * (11 * 1024 * 1024), "big.mp4", size_threshold_mb=10)

    def fake_get(url):
        return DummyResponse(content=b"video", headers={"Content-Type": "video/mp4"})

    monkeypatch.setattr("src.vcon.dialog.requests.get", fake_get)

    dialog.add_video_with_optimal_storage("https://example.com/video.mp4", "video.mp4")
    assert dialog.url.startswith("http")
