"""Regression tests for the 1.0.5 fixes."""

import copy
import json
from pathlib import Path

import pytest

from vcon import Vcon, Session, compute_content_hash
from vcon.party import Party
from vcon.validation import content_hash_problems

T = "2026-01-01T00:00:00Z"
EXAMPLES = Path(__file__).parent / "schema" / "examples"
GRANT = {"purpose": "recording", "granted": True, "granted_at": T}


def _with_basis(body):
    v = Vcon.build_new()
    v.add_party(Party(name="Alice"))
    v.add_session(Session(start=T, parties=[0]))
    v.add_extension("lawful_basis")
    v.vcon_dict["attachments"].append({
        "purpose": "lawful_basis", "start": T, "party": 0, "session": [0],
        "encoding": "json", "mediatype": "application/json", "body": body,
    })
    return v


@pytest.mark.parametrize("body,expected", [
    ({"lawful_basis": "consent", "expiration": "2099-01-01", "purpose_grants": [GRANT]}, None),
    ({"lawful_basis": "consent", "expiration": 5, "purpose_grants": [GRANT]}, "Invalid expiration timestamp format"),
    ({"lawful_basis": "consent", "expiration": None, "purpose_grants": ["x"]},
     "Purpose grant 0: Missing required field in purpose grant: purpose"),
    ({"lawful_basis": ["consent"], "expiration": None, "purpose_grants": [GRANT]}, "Unsupported lawful basis"),
    ({"lawful_basis": "consent", "expiration": None,
      "purpose_grants": [dict(GRANT, granted_at=1)]}, "Invalid granted_at timestamp format"),
    ({"lawful_basis": "consent", "expiration": None, "purpose_grants": [GRANT],
      "proof_mechanisms": [{"proof_type": ["x"], "timestamp": None, "proof_data": {}}]},
     "Invalid timestamp format in proof mechanism"),
    ({"lawful_basis": "consent", "expiration": None, "purpose_grants": [GRANT],
      "content_hash": "sha-256:abc", "registry": 7}, "Missing required field in content_hash"),
])
def test_malformed_lawful_basis_bodies_are_reported_not_raised(body, expected):
    ok, errors = _with_basis(body).is_valid()
    if expected is None:
        assert ok, errors
    else:
        assert not ok and any(expected in e for e in errors), errors


def test_content_hash_with_trailing_newline_is_rejected():
    h = compute_content_hash(b"x")
    assert content_hash_problems(h) == []
    assert content_hash_problems(h + "\n")


def test_created_at_offset_of_24_hours_is_invalid():
    v = Vcon({"vcon": "0.5.0", "uuid": "01928e10-193e-8231-b9a2-279e0d16bc46",
              "created_at": "2026-01-01T00:00:00+24:00"})
    ok, errors = v.is_valid()
    assert not ok and any("offset must be a timedelta" in e for e in errors)


@pytest.mark.parametrize("name", ["B6-signed", "B7-encrypted"])
def test_jws_and_jwe_containers_are_kept_and_validated(name):
    raw = json.loads((EXAMPLES / f"{name}.json").read_text())
    v = Vcon(copy.deepcopy(raw))
    assert v.to_dict() == raw  # nothing added (no uuid, created_at or arrays)
    assert v.is_valid() == (True, [])


def test_signed_payload_is_validated():
    raw = json.loads((EXAMPLES / "B6-signed.json").read_text())
    raw["payload"] = "not base64url json"
    assert not Vcon(raw).is_valid()[0]
    raw = json.loads((EXAMPLES / "B6-signed.json").read_text())
    raw["signatures"] = []
    assert any("signatures" in e for e in Vcon(raw).is_valid()[1])


def test_encrypted_vcon_warns_that_content_is_unchecked():
    raw = json.loads((EXAMPLES / "B7-encrypted.json").read_text())
    assert any("cannot be validated" in w for w in Vcon(raw).get_validation_warnings())
