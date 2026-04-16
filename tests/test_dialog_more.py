"""Additional dialog tests to cover utility methods."""

import base64
from datetime import datetime, timezone

import pytest

from src.vcon.dialog import Dialog


def test_is_audio_image_pdf_and_frame_rate():
    dialog = Dialog(type="text", start=datetime.now(timezone.utc), parties=[0], mediatype="audio/mp3")
    assert dialog.is_audio()
    assert not dialog.is_image()

    dialog.mediatype = "image/jpeg"
    assert dialog.is_image()
    assert not dialog.is_pdf()

    dialog.mediatype = "application/pdf"
    assert dialog.is_pdf()

    assert dialog._calculate_frame_rate("30000/1001") == pytest.approx(29.970, rel=1e-3)
    assert dialog._calculate_frame_rate("0/0") == 0
    assert dialog._calculate_frame_rate("bad") == 0


def test_add_video_data_external_non_url_error():
    dialog = Dialog(type="video", start=datetime.now(timezone.utc), parties=[0])
    with pytest.raises(ValueError):
        dialog.add_video_data("not-a-url", filename="clip.mp4", mediatype="video/mp4", inline=False)


def test_add_image_data_invalid_type(monkeypatch, tmp_path):
    image_path = tmp_path / "image.bin"
    image_path.write_bytes(b"data")

    def fake_guess_type(path):
        return ("image/unknown", None)

    monkeypatch.setattr("mimetypes.guess_type", fake_guess_type)

    dialog = Dialog(type="text", start=datetime.now(timezone.utc), parties=[0])
    with pytest.raises(ValueError):
        dialog.add_image_data(str(image_path))


def test_add_image_data_basic(monkeypatch, tmp_path):
    image_path = tmp_path / "image.jpg"
    image_path.write_bytes(b"jpgdata")

    def fake_guess_type(path):
        return ("image/jpeg", None)

    monkeypatch.setattr("mimetypes.guess_type", fake_guess_type)

    dialog = Dialog(type="text", start=datetime.now(timezone.utc), parties=[0])
    dialog.add_image_data(str(image_path))

    assert dialog.encoding == "base64url"
    assert dialog.mediatype == "image/jpeg"
    assert dialog.filename == "image.jpg"
    assert dialog.content_hash
    assert base64.urlsafe_b64decode(dialog.body.encode()) == b"jpgdata"
