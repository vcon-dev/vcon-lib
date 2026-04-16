"""Tests for extension registry utilities."""

from typing import Dict, Any

from src.vcon.extensions.base import (
    ExtensionInfo,
    ExtensionType,
    ExtensionValidator,
    ExtensionProcessor,
    ValidationResult,
    ProcessingResult,
)
from src.vcon.extensions.registry import ExtensionRegistry


class DummyValidator(ExtensionValidator):
    def __init__(self, should_raise: bool = False):
        self.should_raise = should_raise

    def validate_attachment(self, attachment: Dict[str, Any]) -> ValidationResult:
        if self.should_raise:
            raise ValueError("boom")
        if attachment.get("purpose") == "dummy_attachment":
            return ValidationResult(True)
        return ValidationResult(False, ["invalid attachment"])

    def validate_extension_usage(self, vcon_dict: Dict[str, Any]) -> ValidationResult:
        if self.should_raise:
            raise RuntimeError("bad usage")
        return ValidationResult(True)


class DummyProcessor(ExtensionProcessor):
    def __init__(self, should_raise: bool = False):
        self.should_raise = should_raise

    def process(self, vcon_dict: Dict[str, Any]) -> ProcessingResult:
        if self.should_raise:
            raise RuntimeError("process failed")
        return ProcessingResult(True, data={"processed": True})

    def can_process(self, extension_name: str) -> bool:
        return extension_name == "dummy"


def _make_info(name: str, validator=None, processor=None, attachment_types=None, ext_type=ExtensionType.COMPATIBLE):
    return ExtensionInfo(
        name=name,
        extension_type=ext_type,
        version="1.0.0",
        description="test",
        attachment_types=attachment_types or [],
        validator=validator,
        processor=processor,
    )


def test_register_and_list_extensions():
    registry = ExtensionRegistry()
    info = _make_info("dummy")

    registry.register_extension(info)
    assert registry.get_extension("dummy") == info
    assert registry.list_extensions() == ["dummy"]
    assert registry.is_extension_registered("dummy")


def test_validate_extension_not_registered():
    registry = ExtensionRegistry()
    result = registry.validate_extension("missing", {})
    assert not result.is_valid
    assert "not registered" in result.errors[0]


def test_validate_extension_without_validator():
    registry = ExtensionRegistry()
    registry.register_extension(_make_info("dummy"))

    result = registry.validate_extension("dummy", {})
    assert result.is_valid
    assert result.warnings


def test_validate_extension_with_validator():
    registry = ExtensionRegistry()
    registry.register_extension(_make_info("dummy", validator=DummyValidator()))

    result = registry.validate_extension("dummy", {"extensions": ["dummy"]})
    assert result.is_valid


def test_validate_extension_validator_exception():
    registry = ExtensionRegistry()
    registry.register_extension(_make_info("dummy", validator=DummyValidator(should_raise=True)))

    result = registry.validate_extension("dummy", {})
    assert not result.is_valid
    assert "Validation error" in result.errors[0]


def test_validate_attachment_missing_purpose():
    registry = ExtensionRegistry()
    result = registry.validate_attachment({"body": {}})
    assert not result.is_valid
    assert "purpose" in result.errors[0]


def test_validate_attachment_without_validator():
    registry = ExtensionRegistry()
    registry.register_extension(
        _make_info("dummy", attachment_types=["dummy_attachment"])
    )

    result = registry.validate_attachment({"purpose": "dummy_attachment", "body": {}})
    assert result.is_valid
    assert result.warnings


def test_validate_attachment_with_validator():
    registry = ExtensionRegistry()
    registry.register_extension(
        _make_info("dummy", validator=DummyValidator(), attachment_types=["dummy_attachment"])
    )

    result = registry.validate_attachment({"purpose": "dummy_attachment", "body": {}})
    assert result.is_valid


def test_process_extensions_paths():
    registry = ExtensionRegistry()
    registry.register_extension(_make_info("dummy"))
    registry.register_extension(
        _make_info("processable", processor=DummyProcessor())
    )
    registry.register_extension(
        _make_info("broken", processor=DummyProcessor(should_raise=True))
    )

    results = registry.process_extensions({"extensions": ["missing", "dummy", "processable", "broken"]})

    assert not results["missing"].success
    assert results["dummy"].success
    assert results["processable"].success
    assert not results["broken"].success


def test_required_extensions_and_compatibility():
    registry = ExtensionRegistry()
    registry.register_extension(_make_info("required", ext_type=ExtensionType.INCOMPATIBLE))

    vcon_dict = {"critical": ["required", "missing"]}

    required = registry.get_required_extensions(vcon_dict)
    assert required == ["required"]

    result = registry.check_compatibility(vcon_dict)
    assert result.is_valid
