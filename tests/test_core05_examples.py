"""Appendix B examples of core-05 load and validate; library output validates against Appendix C."""

import base64
import copy
import json
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")

from vcon import Vcon, Dialog, Session, Event
from vcon.party import Party

SCHEMA_DIR = Path(__file__).parent / "schema"
SCHEMA = json.loads((SCHEMA_DIR / "vcon_json_schema.json").read_text())
EXAMPLES = sorted((SCHEMA_DIR / "examples").glob("B*.json"))
UNSIGNED = [p for p in EXAMPLES if p.name[:2] in {"B1", "B2", "B3", "B4", "B5", "B8", "B9"}]


def _validator():
    return jsonschema.Draft7Validator(SCHEMA, format_checker=jsonschema.FormatChecker())


def test_all_nine_appendix_b_examples_are_present():
    assert [p.name[:2] for p in EXAMPLES] == ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9"]


@pytest.mark.parametrize("path", UNSIGNED, ids=lambda p: p.name[:2])
def test_unsigned_example_validates_against_appendix_c(path):
    data = json.loads(path.read_text())
    _validator().validate(data)


@pytest.mark.parametrize("path", UNSIGNED, ids=lambda p: p.name[:2])
def test_unsigned_example_loads_and_passes_is_valid(path):
    data = json.loads(path.read_text())
    vcon = Vcon.load(str(path))
    assert vcon.migration_report is None  # already 0.5.0
    assert vcon.vcon == "0.5.0"
    valid, errors = vcon.is_valid()
    assert valid, errors
    # Loading does not change the example's content.
    assert vcon.to_dict()["sessions"] == data["sessions"]
    assert vcon.to_dict().get("events") == data.get("events")
    assert vcon.to_dict()["dialog"] == data["dialog"]


def test_signed_example_b6_payload_loads_and_validates():
    envelope = json.loads((SCHEMA_DIR / "examples" / "B6-signed.json").read_text())
    protected = json.loads(base64.urlsafe_b64decode(envelope["signatures"][0]["protected"] + "=="))
    assert protected == {"alg": "RS256"}
    raw = envelope["payload"]
    payload = json.loads(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)))
    _validator().validate(payload)
    vcon = Vcon(payload)
    assert vcon.is_valid()[0]


def test_encrypted_example_b7_is_a_jwe_not_a_vcon():
    envelope = json.loads((SCHEMA_DIR / "examples" / "B7-encrypted.json").read_text())
    assert {"protected", "iv", "ciphertext", "tag", "recipients", "unprotected"} <= set(envelope)
    assert json.loads(base64.urlsafe_b64decode(envelope["protected"] + "=="))["alg"] == "RSA-OAEP"


def test_b1_events_use_bare_integer_sessions():
    vcon = Vcon.load(str(SCHEMA_DIR / "examples" / "B1-two-party-call-inline-recording.json"))
    assert [e["type"] for e in vcon.events] == ["join", "join", "drop", "drop"]
    assert all(e["sessions"] == 0 and "dialog" not in e for e in vcon.events)


def test_b8_and_b9_use_the_renamed_parameters():
    b8 = Vcon.load(str(SCHEMA_DIR / "examples" / "B8-redacted.json"))
    b9 = Vcon.load(str(SCHEMA_DIR / "examples" / "B9-amended-signed.json"))
    assert b8.redacted_from["uuid"] and b9.amended_from["uuid"]


def test_library_built_vcon_with_every_object_kind_validates():
    vcon = Vcon.build_new()
    vcon.add_party(Party(name="Alice", tel="+12025550101"))
    vcon.add_party(Party(name="Bob", tel="+12025550102"))
    vcon.add_party(Party(name="Carol", tel="+12025550103"))
    vcon.add_session(Session(start="2026-01-01T00:00:00Z", duration=60, parties=[0, 1]))
    s1 = vcon.add_session(Session(start="2026-01-01T00:00:10Z", duration=30, parties=[1, 2]))
    s2 = vcon.add_session(Session(start="2026-01-01T00:00:45Z", parties=[0, 2]))
    vcon.vcon_dict["sessions"][0]["sessions"] = [{"session": 1, "type": "child", "description": "consult"}]
    vcon.add_dialog(
        Dialog(type="recording", start="2026-01-01T00:00:00Z", duration=60, parties=[[0], [1]],
               mediatype="audio/wav", url="https://example.com/a.wav", content_hash="sha512-abc"),
        session=0,
    )
    vcon.add_dialog(Dialog(type="text", start="2026-01-01T00:00:10Z", parties=[1], body="hello", mediatype="text/plain", encoding="none"), session=1)
    vcon.add_incomplete_dialog(start="2026-01-01T00:00:45Z", disposition="busy", parties=[0], session=2)
    vcon.add_dialog(Dialog.placeholder())
    T = "2026-01-01T00:00:00Z"
    for e in (
        Event(type="join", time=T, sessions=0, party=0),
        Event(type="keydown", time=T, sessions=[0, 1], party=1, button="#"),
        Event(type="consultation-start", time=T, sessions=0, party=1, transferee=0, transfer_target=2, consultation=1),
        Event(type="consultative-transfer", time=T, sessions=0, party=1, transferee=0, transfer_target=2, consultation=1, target_session=2),
        Event(type="blind-transfer", time=T, sessions=0, party=1, transferee=0, transfer_target=2, target_session=2),
        Event(type="transfer-abandoned", time=T, sessions=0, party=1, transferee=0),
        Event(type="channel-contributors", time=T, dialog=0, channel=1, contributors=[1, 2]),
        Event(type="channel-contributors", time=T, dialog=0, channel=0, contributors=None),
    ):
        vcon.add_event(e)
    vcon.add_tag("k", "v")
    vcon.add_lawful_basis_attachment(
        lawful_basis="consent", expiration="2030-01-01T00:00:00Z",
        purpose_grants=[{"purpose": "recording", "granted": True, "granted_at": T}],
    )
    vcon.add_analysis(type="summary", vendor="v", body="s", dialog=0, sessions=[0], attachment=0)
    vcon.add_wtf_transcription_analysis(
        transcript={"text": "hi", "language": "en", "duration": 1.0, "confidence": 0.9},
        segments=[{"id": 0, "start": 0.0, "end": 1.0, "text": "hi", "confidence": 0.9}],
        metadata={"created_at": T, "processed_at": T, "provider": "p", "model": "m"},
        dialog_index=0,
    )
    out = vcon.to_dict()
    _validator().validate(out)
    assert vcon.is_valid() == (True, [])
    assert out["vcon"] == "0.5.0"
    assert out["dialog"][3] == {}
    assert s1 == 1 and s2 == 2


def test_empty_build_new_validates_against_appendix_c():
    _validator().validate(Vcon.build_new().to_dict())
