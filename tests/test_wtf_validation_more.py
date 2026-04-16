"""Additional tests for WTF validation helpers."""

from datetime import datetime, timezone

import pytest

from src.vcon.extensions.wtf.validation import WTFValidator
from src.vcon.extensions.wtf.attachment import (
    WTFAttachment,
    Transcript,
    Segment,
    Metadata,
    Word,
)


def test_validate_words_and_speakers_errors():
    validator = WTFValidator()
    body = {
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
        "words": [
            {"id": "bad", "start": 1, "end": 0, "text": 1, "confidence": 2}
        ],
        "speakers": {
            "A": {"id": "A", "label": "A", "segments": "bad", "total_time": -1, "confidence": 2}
        },
    }

    result = validator.validate_attachment({"purpose": "wtf_transcription", "encoding": "json", "body": body})
    assert not result.is_valid


def test_validate_wtf_attachment_object():
    validator = WTFValidator()
    attachment = WTFAttachment(
        transcript=Transcript(text="Hi", language="en", duration=1.0, confidence=0.8),
        segments=[Segment(id=0, start=0.0, end=1.0, text="Hi", confidence=0.8)],
        metadata=Metadata(
            created_at=datetime.now(timezone.utc).isoformat(),
            processed_at=datetime.now(timezone.utc).isoformat(),
            provider="whisper",
            model="whisper-1",
        ),
        words=[Word(id=0, start=0.0, end=1.0, text="Hi", confidence=0.8)],
    )

    result = validator.validate_wtf_attachment(attachment)
    assert result.is_valid

    attachment.transcript.duration = 0
    result = validator.validate_wtf_attachment(attachment)
    assert not result.is_valid
