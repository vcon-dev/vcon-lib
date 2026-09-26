"""Validate library output against the vCon working group's JSON schema.

The schema is vendored at tests/schema/vcon_json_schema.json (see
tests/schema/SOURCE.md for provenance) and matches the appendix schema of
draft-ietf-vcon-vcon-core-04. This test builds a vCon using only the
library's public helpers -- add_tag, add_lawful_basis_attachment,
add_dialog (with and without inline audio), and add_attachment -- and
checks that the resulting dict validates with no post-processing.
"""

import json
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")

from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog, b64url_encode

SCHEMA_PATH = Path(__file__).parent / "schema" / "vcon_json_schema.json"


def _load_schema():
    return json.loads(SCHEMA_PATH.read_text())


def test_vcon_built_with_public_helpers_validates_against_wg_schema():
    schema = _load_schema()

    vcon = Vcon.build_new()
    vcon.add_party(Party(name="Alice", role="caller"))
    vcon.add_party(Party(name="Bob", role="agent"))

    # Dialog without inline audio (plain text).
    text_dialog = Dialog(
        type="text",
        start=vcon.created_at,
        parties=[0, 1],
        body="Hello, how can I help?",
        encoding="none",
        mediatype="text/plain",
    )
    vcon.add_dialog(text_dialog)

    # Dialog with inline audio, base64url-encoded per -04 (unpadded).
    audio_bytes = b"RIFF\x00\x00\x00\x00WAVEfmt fake audio payload"
    audio_dialog = Dialog(
        type="recording",
        start=vcon.created_at,
        parties=[0, 1],
        body=b64url_encode(audio_bytes),
        encoding="base64url",
        mediatype="audio/x-wav",
    )
    vcon.add_dialog(audio_dialog)

    vcon.add_tag("category", "support")
    vcon.add_tag("priority", "high")

    vcon.add_lawful_basis_attachment(
        lawful_basis="consent",
        expiration="2030-01-01T00:00:00Z",
        purpose_grants=[
            {"purpose": "recording", "granted": True, "granted_at": vcon.created_at}
        ],
        party_index=0,
        dialog_index=1,
    )

    vcon.add_attachment(
        purpose="notes",
        body={"summary": "Customer called about billing."},
        encoding="json",
        party=1,
        dialog=0,
    )

    vcon_dict = vcon.to_dict()

    # No post-processing: validate exactly what the library produced.
    jsonschema.validate(instance=vcon_dict, schema=schema)

    # Also confirm the library's own validator is happy with the same
    # output, and that content is what we expect.
    is_valid, errors = vcon.is_valid()
    assert is_valid, errors
    assert vcon.get_tag("category") == "support"
    assert vcon.get_tag("priority") == "high"


def test_legacy_string_tags_body_still_validates_after_add_tag():
    """A vCon with a legacy (pre-0.10.0) JSON-string tags body should, once
    add_tag() normalizes it back to a list, validate against the schema."""
    schema = _load_schema()

    vcon = Vcon.build_new()
    vcon.add_party(Party(name="Alice"))

    # Simulate a vCon written under -02 conventions / by an older release:
    # the tags attachment body is a JSON-encoded string, not a list.
    vcon.vcon_dict["attachments"].append(
        {
            "purpose": "tags",
            "body": json.dumps(["existing:tag"]),
            "encoding": "json",
            "mediatype": "application/json",
            "start": vcon.created_at,
            "party": 0,
            "dialog": 0,
        }
    )

    assert vcon.get_tag("existing") == "tag"

    vcon.add_tag("new", "value")

    tags_attachment = vcon.find_attachment_by_purpose("tags")
    assert tags_attachment["body"] == ["existing:tag", "new:value"]
    assert vcon.get_tag("existing") == "tag"
    assert vcon.get_tag("new") == "value"

    jsonschema.validate(instance=vcon.to_dict(), schema=schema)
