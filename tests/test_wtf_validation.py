"""Tests for WTF validation logic."""

from datetime import datetime, timezone

from src.vcon.extensions.wtf.validation import WTFValidator


def _minimal_body():
    return {
        "transcript": {
            "text": "Hello",
            "language": "en",
            "duration": 1.0,
            "confidence": 0.9,
        },
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 1.0,
                "text": "Hello",
                "confidence": 0.9,
            }
        ],
        "metadata": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "provider": "whisper",
            "model": "whisper-1",
        },
    }


def test_validate_attachment_success():
    validator = WTFValidator()
    attachment = {
        "purpose": "wtf_transcription",
        "encoding": "json",
        "body": _minimal_body(),
    }

    result = validator.validate_attachment(attachment)
    assert result.is_valid


def test_validate_attachment_wrong_purpose():
    validator = WTFValidator()
    attachment = {"purpose": "wrong", "encoding": "json", "body": {}}

    result = validator.validate_attachment(attachment)
    assert not result.is_valid


def test_validate_extension_usage_warning_and_error():
    validator = WTFValidator()
    attachment = {
        "purpose": "wtf_transcription",
        "encoding": "json",
        "body": {"segments": []},
    }

    result = validator.validate_extension_usage({"attachments": [attachment]})
    assert not result.is_valid
    assert result.warnings


def test_validate_quality_errors():
    validator = WTFValidator()
    body = _minimal_body()
    body["quality"] = {
        "audio_quality": "invalid",
        "background_noise": 2,
        "multiple_speakers": "yes",
        "overlapping_speech": "no",
        "silence_ratio": -0.1,
        "average_confidence": 2,
        "low_confidence_words": -1,
        "processing_warnings": "warn",
    }

    attachment = {
        "purpose": "wtf_transcription",
        "encoding": "json",
        "body": body,
    }

    result = validator.validate_attachment(attachment)
    assert not result.is_valid
    assert result.errors
