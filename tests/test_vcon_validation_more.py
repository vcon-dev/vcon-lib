"""Additional vCon validation tests."""

from datetime import datetime, timezone

import pytest

from src.vcon.vcon import Vcon


def test_is_valid_errors_for_dialog_and_analysis():
    vcon = Vcon(
        {
            "uuid": "123",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "parties": [{"name": "Alice"}],
            "dialog": [
                {"type": "invalid", "start": "bad", "parties": [2], "mediatype": "text/plain"},
                {"type": "incomplete", "start": datetime.now(timezone.utc).isoformat()},
                {"type": "transfer", "start": datetime.now(timezone.utc).isoformat(), "parties": [0]},
                {"type": "text", "start": datetime.now(timezone.utc).isoformat(), "parties": [0], "mediatype": "bad/type"},
            ],
            "attachments": [
                {"purpose": "tags", "encoding": "bad"},
                {"body": "x", "encoding": "json"},
            ],
            "analysis": [
                {"type": "sentiment", "dialog": 10, "vendor": "acme", "body": {}, "encoding": "json"},
                {"type": "sentiment", "dialog": "bad", "vendor": "acme", "body": {}, "encoding": "json"},
            ],
        }
    )
    vcon.vcon_dict["created_at"] = "invalid-date"

    ok, errors = vcon.is_valid()
    assert not ok
    assert errors


def test_add_analysis_invalid_encoding_and_body():
    vcon = Vcon.build_new()

    with pytest.raises(Exception):
        vcon.add_analysis(type="sentiment", dialog=0, vendor="acme", body={}, encoding="bad")

    with pytest.raises(Exception):
        vcon.add_analysis(type="sentiment", dialog=0, vendor="acme", body="not json", encoding="json")

    with pytest.raises(Exception):
        vcon.add_analysis(type="sentiment", dialog=0, vendor="acme", body="not base64", encoding="base64url")
