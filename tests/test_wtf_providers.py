"""Tests for WTF provider adapters."""

import pytest

from src.vcon.extensions.wtf.providers import (
    ProviderAdapter,
    WhisperAdapter,
    DeepgramAdapter,
    AssemblyAIAdapter,
)


class DummyAdapter(ProviderAdapter):
    def convert(self, provider_data):
        return provider_data


def test_normalize_confidence_and_timestamp():
    adapter = DummyAdapter()

    assert adapter._normalize_confidence(-1, "whisper") == 0.0
    assert adapter._normalize_confidence(0, "whisper") == 0.5
    assert adapter._normalize_confidence(0.8, "deepgram") == 0.8
    assert adapter._normalize_confidence("bad", "other") == 0.0

    assert adapter._normalize_timestamp(1.25) == 1.25
    assert adapter._normalize_timestamp("2.5") == 2.5
    assert adapter._normalize_timestamp("bad") == 0.0


def test_whisper_adapter_convert():
    adapter = WhisperAdapter()
    data = {
        "text": "Hello world",
        "language": "en",
        "model": "whisper-1",
        "segments": [
            {
                "start": 0,
                "end": 1.2,
                "text": "Hello world",
                "avg_logprob": -0.2,
                "words": [
                    {"start": 0, "end": 0.5, "word": "Hello", "probability": -0.1},
                    {"start": 0.6, "end": 1.2, "word": "world", "probability": -0.2},
                ],
            }
        ],
        "temperature": 0.1,
    }

    attachment = adapter.convert(data)

    assert attachment.transcript.text == "Hello world"
    assert attachment.transcript.language == "en"
    assert attachment.transcript.duration == 1.2
    assert attachment.segments[0].words == [0, 1]
    assert attachment.metadata.provider == "whisper"
    assert "whisper" in attachment.extensions


def test_deepgram_adapter_convert():
    adapter = DeepgramAdapter()
    data = {
        "results": {
            "channels": [
                {
                    "alternatives": [
                        {
                            "transcript": "Hi there.",
                            "confidence": 0.9,
                            "words": [
                                {"start": 0.0, "end": 0.2, "word": "Hi", "confidence": 0.8},
                                {"start": 0.3, "end": 0.6, "word": "there.", "confidence": 0.7},
                            ],
                        }
                    ]
                }
            ]
        },
        "metadata": {"duration": 1.0, "language": "en"},
    }

    attachment = adapter.convert(data)

    assert attachment.transcript.text == "Hi there."
    assert attachment.segments
    assert attachment.words
    assert attachment.metadata.provider == "deepgram"
    assert "deepgram" in attachment.extensions


def test_deepgram_adapter_missing_channels():
    adapter = DeepgramAdapter()

    with pytest.raises(ValueError):
        adapter.convert({"results": {"channels": []}})


def test_assemblyai_adapter_convert():
    adapter = AssemblyAIAdapter()
    data = {
        "text": "Hello there",
        "confidence": 0.9,
        "audio_duration": 2.0,
        "language_code": "en",
        "words": [
            {"start": 0, "end": 500, "text": "Hello", "confidence": 0.8},
            {"start": 600, "end": 1100, "text": "there", "confidence": 0.7},
        ],
        "utterances": [
            {
                "speaker": "A",
                "words": [
                    {"start": 0, "text": "Hello"},
                    {"start": 600, "text": "there"},
                ],
            }
        ],
    }

    attachment = adapter.convert(data)

    assert attachment.transcript.language == "en"
    assert attachment.transcript.duration == 2.0
    assert attachment.segments
    assert attachment.metadata.provider == "assemblyai"
    assert "assemblyai" in attachment.extensions
