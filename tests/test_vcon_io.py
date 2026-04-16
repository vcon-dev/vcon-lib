"""Tests for vCon I/O helpers."""

import json
from datetime import datetime, timezone

import pytest

from src.vcon.vcon import Vcon


class DummyResponse:
    def __init__(self, text="{}", status_code=200, raise_error=False):
        self.text = text
        self.status_code = status_code
        self._raise_error = raise_error

    def raise_for_status(self):
        if self._raise_error or self.status_code >= 400:
            raise Exception("bad status")


def test_validate_json_and_file(tmp_path):
    valid = Vcon.build_new()
    json_str = valid.to_json()
    ok, errors = Vcon.validate_json(json_str)
    assert ok
    assert not errors

    ok, errors = Vcon.validate_json("not json")
    assert not ok
    assert errors

    path = tmp_path / "vcon.json"
    path.write_text(json_str)
    ok, errors = Vcon.validate_file(str(path))
    assert ok

    ok, errors = Vcon.validate_file(str(tmp_path / "missing.json"))
    assert not ok
    assert "File not found" in errors[0]


def test_load_from_file_and_url(monkeypatch, tmp_path):
    vcon = Vcon.build_new()
    path = tmp_path / "vcon.json"
    path.write_text(vcon.to_json())

    loaded = Vcon.load_from_file(str(path))
    assert loaded.uuid == vcon.uuid

    def fake_get(url):
        return DummyResponse(text=vcon.to_json())

    monkeypatch.setattr("src.vcon.vcon.requests.get", fake_get)
    loaded = Vcon.load_from_url("https://example.com/vcon.json")
    assert loaded.uuid == vcon.uuid


def test_save_to_file(tmp_path):
    vcon = Vcon.build_new()
    path = tmp_path / "out.json"
    vcon.save_to_file(str(path))
    assert json.loads(path.read_text())["uuid"] == vcon.uuid


def test_post_to_url(monkeypatch):
    vcon = Vcon.build_new()

    class PostResponse:
        def __init__(self):
            self.status_code = 200
        def raise_for_status(self):
            return None

    def fake_post(url, data=None, headers=None):
        assert headers["Content-Type"] == "application/json"
        assert json.loads(data)["uuid"] == vcon.uuid
        return PostResponse()

    monkeypatch.setattr("src.vcon.vcon.requests.post", fake_post)
    response = vcon.post_to_url("https://example.com/vcon")
    assert response.status_code == 200
