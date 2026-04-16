"""Tests for vCon property handling modes."""

from datetime import datetime, timezone

import pytest

from src.vcon.vcon import Vcon, PROPERTY_HANDLING_META, PROPERTY_HANDLING_STRICT
from src.vcon.party import Party
from src.vcon.dialog import Dialog


def test_property_handling_meta_moves_custom_fields():
    vcon = Vcon(
        {
            "uuid": "123",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "custom": "value",
            "parties": [{"name": "Alice", "custom_party": "yes"}],
            "dialog": [{"type": "text", "start": datetime.now(timezone.utc).isoformat(), "parties": [0], "custom_dialog": 1, "mediatype": "text/plain"}],
            "attachments": [{"purpose": "tags", "body": [], "encoding": "json", "custom_attachment": True}],
            "analysis": [{"type": "sentiment", "dialog": 0, "vendor": "acme", "body": {}, "encoding": "json", "custom_analysis": 1}],
        },
        property_handling=PROPERTY_HANDLING_META,
    )

    assert vcon.vcon_dict["meta"]["custom"] == "value"
    assert vcon.vcon_dict["parties"][0]["meta"]["custom_party"] == "yes"
    assert vcon.vcon_dict["dialog"][0]["meta"]["custom_dialog"] == 1
    assert vcon.vcon_dict["attachments"][0]["meta"]["custom_attachment"] is True
    assert vcon.vcon_dict["analysis"][0]["meta"]["custom_analysis"] == 1


def test_property_handling_strict_drops_custom_fields():
    vcon = Vcon(
        {
            "uuid": "123",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "custom": "value",
        },
        property_handling=PROPERTY_HANDLING_STRICT,
    )

    assert "custom" not in vcon.vcon_dict


def test_add_party_dialog_processed():
    vcon = Vcon.build_new(property_handling=PROPERTY_HANDLING_STRICT)
    party = Party(name="Alice", custom_party="yes")
    vcon.add_party(party)
    assert "custom_party" not in vcon.parties[0]

    dialog = Dialog(type="text", start=datetime.now(timezone.utc), parties=[0], mediatype="text/plain", custom_dialog=1)
    vcon.add_dialog(dialog)
    assert "custom_dialog" not in vcon.dialog[0]
