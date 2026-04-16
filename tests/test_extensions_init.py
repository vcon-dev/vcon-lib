"""Tests for extensions package init helpers."""

from src.vcon.extensions import get_extension_registry


def test_get_extension_registry_initializes_defaults():
    registry = get_extension_registry()
    extensions = registry.list_extensions()
    assert "lawful_basis" in extensions
    assert "wtf_transcription" in extensions
