"""Tests for extension base classes."""

from datetime import datetime, timezone

from src.vcon.extensions.base import (
    ExtensionAttachment,
    ExtensionInfo,
    ExtensionType,
    ProcessingResult,
    ValidationResult,
)


def test_validation_result_bool_and_errors():
    result = ValidationResult(True)
    assert result

    result.add_warning("be careful")
    assert result
    assert result.warnings == ["be careful"]

    result.add_error("bad")
    assert not result
    assert result.errors == ["bad"]


def test_processing_result_add_error():
    result = ProcessingResult(True, data={"ok": True})
    assert result.success

    result.add_error("failed")
    assert not result.success
    assert result.errors == ["failed"]


def test_extension_info_to_dict():
    info = ExtensionInfo(
        name="example",
        extension_type=ExtensionType.COMPATIBLE,
        version="1.2.3",
        description="Example extension",
        attachment_types=["example_attachment"],
    )

    assert info.to_dict() == {
        "name": "example",
        "type": "compatible",
        "version": "1.2.3",
        "description": "Example extension",
        "attachment_types": ["example_attachment"],
    }


def test_extension_attachment_round_trip():
    start = datetime(2026, 2, 3, 12, 30, tzinfo=timezone.utc)
    attachment = ExtensionAttachment(
        attachment_purpose="example",
        body={"value": 123},
        start=start,
        party=1,
        dialog=2,
        encoding="json",
        meta={"note": "ok"},
    )

    attachment_dict = attachment.to_dict()
    assert attachment_dict["start"] == start.isoformat()
    assert attachment_dict["party"] == 1
    assert attachment_dict["dialog"] == 2
    assert attachment_dict["meta"] == {"note": "ok"}

    restored = ExtensionAttachment.from_dict(attachment_dict)
    assert restored.purpose == "example"
    assert restored.body == {"value": 123}
    assert restored.start == start.isoformat()
    assert restored.party == 1
    assert restored.dialog == 2
    assert restored.encoding == "json"
    assert restored.meta == {"note": "ok"}
