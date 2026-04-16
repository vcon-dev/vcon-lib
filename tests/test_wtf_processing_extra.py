"""Extra tests for WTF processing."""

from datetime import datetime, timezone
import types
import pytest

from src.vcon.extensions.wtf.processing import WTFProcessor
from src.vcon.extensions.wtf.attachment import (
    WTFAttachment,
    Transcript,
    Segment,
    Metadata,
    Word,
    Speaker,
    Quality,
)


def _make_attachment():
    return WTFAttachment(
        transcript=Transcript(text="Hello world", language="en", duration=2.0, confidence=0.8),
        segments=[
            Segment(id=0, start=0.0, end=1.0, text="Hello", confidence=0.9),
            Segment(id=1, start=1.0, end=2.0, text="world", confidence=0.4),
        ],
        metadata=Metadata(
            created_at=datetime.now(timezone.utc).isoformat(),
            processed_at=datetime.now(timezone.utc).isoformat(),
            provider="whisper",
            model="whisper-1",
        ),
        words=[
            Word(id=0, start=0.0, end=0.5, text="Hello", confidence=0.9),
            Word(id=1, start=0.6, end=1.0, text="world", confidence=0.4),
        ],
        speakers={
            "A": Speaker(id="A", label="A", segments=[0, 1], total_time=2.0, confidence=0.8)
        },
        quality=Quality(
            audio_quality="high",
            background_noise=0.1,
            multiple_speakers=False,
            overlapping_speech=False,
            silence_ratio=0.2,
            average_confidence=0.7,
            low_confidence_words=1,
            processing_warnings=[],
        ),
    )


def test_analyze_transcription_and_compare():
    processor = WTFProcessor()
    attachment = _make_attachment()

    analysis = processor.analyze_transcription(attachment)
    assert "keywords" in analysis
    assert "quality_metrics" in analysis
    assert analysis["quality_metrics"]["audio_quality"] == "high"

    comparison = processor.compare_transcriptions([attachment, attachment])
    assert comparison["transcription_count"] == 2
    assert comparison["duration_differences"][0]["difference"] == 0

    with pytest.raises(ValueError):
        processor.compare_transcriptions([attachment])


def test_convert_from_provider_and_export():
    processor = WTFProcessor()

    class DummyAdapter:
        def convert(self, data):
            return _make_attachment()

    processor.provider_adapters["dummy"] = DummyAdapter()

    attachment = processor.convert_from_provider({}, "dummy")
    assert attachment.transcript.text == "Hello world"

    assert processor.export_transcription(attachment, "srt").startswith("1")
    assert "WEBVTT" in processor.export_transcription(attachment, "vtt")

    with pytest.raises(ValueError):
        processor.export_transcription(attachment, "unknown")

    with pytest.raises(ValueError):
        processor.convert_from_provider({}, "missing")


def test_process_paths_for_missing_and_errors():
    processor = WTFProcessor()
    result = processor.process({"attachments": []})
    assert result.success

    attachment = _make_attachment().to_dict()
    vcon_dict = {
        "attachments": [
            {"purpose": "wtf_transcription", "encoding": "json", "body": attachment},
            {"purpose": "wtf_transcription", "encoding": "json", "body": {}},
        ]
    }

    result = processor.process(vcon_dict)
    assert result.success
    assert result.data["total_attachments"] == 2


def test_initialize_providers_import_error(monkeypatch):
    original_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.endswith(".providers") or name == "src.vcon.extensions.wtf.providers":
            raise ImportError("boom")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    processor = WTFProcessor()
    processor._initialize_providers()
    assert processor.provider_adapters
