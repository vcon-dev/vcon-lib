"""Tests for vcon.body.decode_body and its use across reader call sites.

draft-ietf-vcon-vcon-core-04 section 2.3.2 makes a "json"-encoded body the
JSON value itself, not a json.dumps string. These tests confirm readers
accept both that shape and the legacy JSON-string shape written under -02
conventions (and by this library prior to 0.10.0).
"""

import json

import pytest

from vcon import Vcon
from vcon.body import decode_body


def test_decode_body_passthrough_for_already_decoded_value():
    assert decode_body({"body": ["a", "b"], "encoding": "json"}) == ["a", "b"]
    assert decode_body({"body": {"k": "v"}, "encoding": "json"}) == {"k": "v"}


def test_decode_body_parses_legacy_json_string():
    entry = {"body": json.dumps(["a", "b"]), "encoding": "json"}
    assert decode_body(entry) == ["a", "b"]


def test_decode_body_parses_string_with_no_encoding_set():
    entry = {"body": json.dumps({"k": "v"})}
    assert decode_body(entry) == {"k": "v"}


def test_decode_body_leaves_base64url_and_none_bodies_as_strings():
    assert decode_body({"body": "abcXYZ", "encoding": "base64url"}) == "abcXYZ"
    assert decode_body({"body": "plain text", "encoding": "none"}) == "plain text"


def test_decode_body_leaves_unparseable_string_unchanged():
    entry = {"body": "not json", "encoding": "json"}
    assert decode_body(entry) == "not json"


def test_decode_body_handles_missing_or_empty_entry():
    assert decode_body(None) is None
    assert decode_body({}) is None
    assert decode_body({"encoding": "json"}) is None


def test_vcon_decoded_body_delegates_to_module_function():
    entry = {"body": json.dumps([1, 2, 3]), "encoding": "json"}
    assert Vcon.decoded_body(entry) == [1, 2, 3]


def test_get_tag_reads_legacy_string_tags_body_without_add_tag():
    """get_tag() must work even on a raw legacy vCon it never wrote itself."""
    vcon = Vcon.build_new()
    vcon.vcon_dict["attachments"].append(
        {
            "purpose": "tags",
            "body": json.dumps(["category:legacy"]),
            "encoding": "json",
            "party": 0,
            "dialog": 0,
        }
    )
    assert vcon.get_tag("category") == "legacy"
    assert vcon.get_tag("missing") is None


def test_lawful_basis_validator_accepts_legacy_string_body():
    from vcon.extensions.lawful_basis.validation import LawfulBasisValidator

    body = {
        "lawful_basis": "consent",
        "expiration": "2030-01-01T00:00:00+00:00",
        "purpose_grants": [
            {"purpose": "recording", "granted": True, "granted_at": "2025-01-01T00:00:00+00:00"}
        ],
    }
    attachment = {
        "purpose": "lawful_basis",
        "encoding": "json",
        "body": json.dumps(body),
    }
    result = LawfulBasisValidator().validate_attachment(attachment)
    assert result.is_valid, result.errors


def test_wtf_validator_accepts_legacy_string_body():
    from vcon.extensions.wtf.validation import WTFValidator

    body = {
        "transcript": {"text": "hello", "language": "en", "duration": 1.0, "confidence": 0.9},
        "segments": [{"id": 0, "start": 0.0, "end": 1.0, "text": "hello", "confidence": 0.9}],
        "metadata": {
            "created_at": "2025-01-01T00:00:00Z",
            "processed_at": "2025-01-01T00:00:01Z",
            "provider": "whisper",
            "model": "whisper-1",
        },
    }
    attachment = {
        "purpose": "wtf_transcription",
        "encoding": "json",
        "body": json.dumps(body),
    }
    result = WTFValidator().validate_attachment(attachment)
    assert result.is_valid, result.errors
