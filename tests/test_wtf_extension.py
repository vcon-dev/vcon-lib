"""
Tests for WTF Extension

This module contains tests for the WTF (World Transcription Format) extension functionality.
"""

import pytest
import json
from datetime import datetime, timezone
from src.vcon.extensions.wtf import (
    WTFExtension,
    WTFAttachment,
    Transcript,
    Segment,
    Word,
    Speaker,
    Quality,
    Metadata,
    WTFProvider
)
from src.vcon.extensions.wtf.validation import WTFValidator
from src.vcon.extensions.wtf.processing import WTFProcessor


class TestWTFAttachment:
    """Test WTFAttachment class."""
    
    def test_create_wtf_attachment(self):
        """Test creating a WTF attachment."""
        transcript = Transcript(
            text="Hello world",
            language="en",
            duration=2.0,
            confidence=0.95
        )
        
        segments = [
            Segment(
                id=0,
                start=0.0,
                end=2.0,
                text="Hello world",
                confidence=0.95
            )
        ]
        
        metadata = Metadata(
            created_at=datetime.now(timezone.utc).isoformat(),
            processed_at=datetime.now(timezone.utc).isoformat(),
            provider="whisper",
            model="whisper-1"
        )
        
        attachment = WTFAttachment(
            transcript=transcript,
            segments=segments,
            metadata=metadata
        )
        
        assert attachment.transcript.text == "Hello world"
        assert len(attachment.segments) == 1
        assert attachment.metadata.provider == "whisper"
    
    def test_export_to_srt(self):
        """Test SRT export functionality."""
        transcript = Transcript(
            text="Hello world",
            language="en",
            duration=2.0,
            confidence=0.95
        )
        
        segments = [
            Segment(
                id=0,
                start=0.0,
                end=2.0,
                text="Hello world",
                confidence=0.95
            )
        ]
        
        metadata = Metadata(
            created_at=datetime.now(timezone.utc).isoformat(),
            processed_at=datetime.now(timezone.utc).isoformat(),
            provider="whisper",
            model="whisper-1"
        )
        
        attachment = WTFAttachment(
            transcript=transcript,
            segments=segments,
            metadata=metadata
        )
        
        srt_content = attachment.export_to_srt()
        assert "1" in srt_content
        assert "00:00:00,000 --> 00:00:02,000" in srt_content
        assert "Hello world" in srt_content
    
    def test_export_to_vtt(self):
        """Test WebVTT export functionality."""
        transcript = Transcript(
            text="Hello world",
            language="en",
            duration=2.0,
            confidence=0.95
        )
        
        segments = [
            Segment(
                id=0,
                start=0.0,
                end=2.0,
                text="Hello world",
                confidence=0.95
            )
        ]
        
        metadata = Metadata(
            created_at=datetime.now(timezone.utc).isoformat(),
            processed_at=datetime.now(timezone.utc).isoformat(),
            provider="whisper",
            model="whisper-1"
        )
        
        attachment = WTFAttachment(
            transcript=transcript,
            segments=segments,
            metadata=metadata
        )
        
        vtt_content = attachment.export_to_vtt()
        assert "WEBVTT" in vtt_content
        assert "00:00:00.000 --> 00:00:02.000" in vtt_content
        assert "Hello world" in vtt_content
    
    def test_find_low_confidence_segments(self):
        """Test finding low confidence segments."""
        transcript = Transcript(
            text="Hello world",
            language="en",
            duration=2.0,
            confidence=0.95
        )
        
        segments = [
            Segment(
                id=0,
                start=0.0,
                end=1.0,
                text="Hello",
                confidence=0.3  # Low confidence
            ),
            Segment(
                id=1,
                start=1.0,
                end=2.0,
                text="world",
                confidence=0.95  # High confidence
            )
        ]
        
        metadata = Metadata(
            created_at=datetime.now(timezone.utc).isoformat(),
            processed_at=datetime.now(timezone.utc).isoformat(),
            provider="whisper",
            model="whisper-1"
        )
        
        attachment = WTFAttachment(
            transcript=transcript,
            segments=segments,
            metadata=metadata
        )
        
        low_confidence_segments = attachment.find_low_confidence_segments(threshold=0.5)
        assert len(low_confidence_segments) == 1
        assert low_confidence_segments[0].id == 0
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        transcript = Transcript(
            text="Hello world",
            language="en",
            duration=2.0,
            confidence=0.95
        )
        
        segments = [
            Segment(
                id=0,
                start=0.0,
                end=2.0,
                text="Hello world",
                confidence=0.95
            )
        ]
        
        words = [
            Word(
                id=0,
                start=0.0,
                end=1.0,
                text="Hello",
                confidence=0.95
            ),
            Word(
                id=1,
                start=1.0,
                end=2.0,
                text="world",
                confidence=0.95
            )
        ]
        
        metadata = Metadata(
            created_at=datetime.now(timezone.utc).isoformat(),
            processed_at=datetime.now(timezone.utc).isoformat(),
            provider="whisper",
            model="whisper-1"
        )
        
        attachment = WTFAttachment(
            transcript=transcript,
            segments=segments,
            metadata=metadata,
            words=words
        )
        
        keywords = attachment.extract_keywords(min_confidence=0.8)
        assert "hello" in keywords
        assert "world" in keywords
    
    def test_serialization(self):
        """Test serialization and deserialization."""
        transcript = Transcript(
            text="Hello world",
            language="en",
            duration=2.0,
            confidence=0.95
        )
        
        segments = [
            Segment(
                id=0,
                start=0.0,
                end=2.0,
                text="Hello world",
                confidence=0.95
            )
        ]
        
        metadata = Metadata(
            created_at=datetime.now(timezone.utc).isoformat(),
            processed_at=datetime.now(timezone.utc).isoformat(),
            provider="whisper",
            model="whisper-1"
        )
        
        attachment = WTFAttachment(
            transcript=transcript,
            segments=segments,
            metadata=metadata
        )
        
        # Serialize to dict
        attachment_dict = attachment.to_dict()
        
        # Deserialize from dict
        restored_attachment = WTFAttachment.from_dict(attachment_dict)
        
        assert restored_attachment.transcript.text == attachment.transcript.text
        assert len(restored_attachment.segments) == len(attachment.segments)
        assert restored_attachment.metadata.provider == attachment.metadata.provider


class TestWTFValidator:
    """Test WTFValidator class."""
    
    def test_validate_attachment(self):
        """Test attachment validation."""
        validator = WTFValidator()
        
        # Valid attachment
        valid_attachment = {
            "purpose": "wtf_transcription",
            "encoding": "json",
            "body": {
                "transcript": {
                    "text": "Hello world",
                    "language": "en",
                    "duration": 2.0,
                    "confidence": 0.95
                },
                "segments": [
                    {
                        "id": 0,
                        "start": 0.0,
                        "end": 2.0,
                        "text": "Hello world",
                        "confidence": 0.95
                    }
                ],
                "metadata": {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "provider": "whisper",
                    "model": "whisper-1"
                }
            }
        }
        
        result = validator.validate_attachment(valid_attachment)
        assert result.is_valid
        
        # Invalid attachment (wrong type)
        invalid_attachment = {
            "type": "invalid_type",
            "encoding": "json",
            "body": {}
        }
        
        result = validator.validate_attachment(invalid_attachment)
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_validate_extension_usage(self):
        """Test extension usage validation."""
        validator = WTFValidator()
        
        vcon_dict = {
            "extensions": ["wtf_transcription"],
            "attachments": [
                {
                    "purpose": "wtf_transcription",
                    "encoding": "json",
                    "body": {
                        "transcript": {
                            "text": "Hello world",
                            "language": "en",
                            "duration": 2.0,
                            "confidence": 0.95
                        },
                        "segments": [
                            {
                                "id": 0,
                                "start": 0.0,
                                "end": 2.0,
                                "text": "Hello world",
                                "confidence": 0.95
                            }
                        ],
                        "metadata": {
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "processed_at": datetime.now(timezone.utc).isoformat(),
                            "provider": "whisper",
                            "model": "whisper-1"
                        }
                    }
                }
            ]
        }
        
        result = validator.validate_extension_usage(vcon_dict)
        assert result.is_valid


class TestWTFProcessor:
    """Test WTFProcessor class."""
    
    def test_process_wtf_extension(self):
        """Test processing WTF extension."""
        processor = WTFProcessor()
        
        vcon_dict = {
            "attachments": [
                {
                    "purpose": "wtf_transcription",
                    "encoding": "json",
                    "body": {
                        "transcript": {
                            "text": "Hello world",
                            "language": "en",
                            "duration": 2.0,
                            "confidence": 0.95
                        },
                        "segments": [
                            {
                                "id": 0,
                                "start": 0.0,
                                "end": 2.0,
                                "text": "Hello world",
                                "confidence": 0.95
                            }
                        ],
                        "metadata": {
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "processed_at": datetime.now(timezone.utc).isoformat(),
                            "provider": "whisper",
                            "model": "whisper-1"
                        }
                    }
                }
            ]
        }
        
        result = processor.process(vcon_dict)
        assert result.success
        assert "wtf_attachments" in result.data
    
    def test_analyze_transcription(self):
        """Test transcription analysis."""
        processor = WTFProcessor()
        
        transcript = Transcript(
            text="Hello world",
            language="en",
            duration=2.0,
            confidence=0.95
        )
        
        segments = [
            Segment(
                id=0,
                start=0.0,
                end=2.0,
                text="Hello world",
                confidence=0.95
            )
        ]
        
        words = [
            Word(
                id=0,
                start=0.0,
                end=1.0,
                text="Hello",
                confidence=0.95
            ),
            Word(
                id=1,
                start=1.0,
                end=2.0,
                text="world",
                confidence=0.95
            )
        ]
        
        metadata = Metadata(
            created_at=datetime.now(timezone.utc).isoformat(),
            processed_at=datetime.now(timezone.utc).isoformat(),
            provider="whisper",
            model="whisper-1"
        )
        
        attachment = WTFAttachment(
            transcript=transcript,
            segments=segments,
            metadata=metadata,
            words=words
        )
        
        analysis = processor.analyze_transcription(attachment)
        assert "keywords" in analysis
        assert "speaking_time" in analysis
        assert "low_confidence_segments" in analysis


class TestWTFExtension:
    """Test WTFExtension class."""
    
    def test_get_extension_info(self):
        """Test getting extension information."""
        extension = WTFExtension()
        info = extension.get_extension_info()
        
        assert info.name == "wtf_transcription"
        assert info.version == "1.0"
        assert "wtf_transcription" in info.attachment_types
    
    def test_create_wtf_attachment(self):
        """Test creating WTF attachment."""
        extension = WTFExtension()
        
        transcript = {
            "text": "Hello world",
            "language": "en",
            "duration": 2.0,
            "confidence": 0.95
        }
        
        segments = [
            {
                "id": 0,
                "start": 0.0,
                "end": 2.0,
                "text": "Hello world",
                "confidence": 0.95
            }
        ]
        
        metadata = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "provider": "whisper",
            "model": "whisper-1"
        }
        
        attachment = extension.create_wtf_attachment(
            transcript=transcript,
            segments=segments,
            metadata=metadata
        )
        
        assert attachment["purpose"] == "wtf_transcription"
        assert attachment["encoding"] == "json"
        assert "body" in attachment
        assert attachment["body"]["transcript"]["text"] == "Hello world"
    
    def test_validate_wtf_attachment(self):
        """Test validating WTF attachment."""
        extension = WTFExtension()
        
        valid_attachment = {
            "purpose": "wtf_transcription",
            "encoding": "json",
            "body": {
                "transcript": {
                    "text": "Hello world",
                    "language": "en",
                    "duration": 2.0,
                    "confidence": 0.95
                },
                "segments": [
                    {
                        "id": 0,
                        "start": 0.0,
                        "end": 2.0,
                        "text": "Hello world",
                        "confidence": 0.95
                    }
                ],
                "metadata": {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "provider": "whisper",
                    "model": "whisper-1"
                }
            }
        }
        
        assert extension.validate_wtf_attachment(valid_attachment)
    
    def test_export_transcription(self):
        """Test exporting transcription."""
        extension = WTFExtension()
        
        attachment = {
            "purpose": "wtf_transcription",
            "encoding": "json",
            "body": {
                "transcript": {
                    "text": "Hello world",
                    "language": "en",
                    "duration": 2.0,
                    "confidence": 0.95
                },
                "segments": [
                    {
                        "id": 0,
                        "start": 0.0,
                        "end": 2.0,
                        "text": "Hello world",
                        "confidence": 0.95
                    }
                ],
                "metadata": {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "provider": "whisper",
                    "model": "whisper-1"
                }
            }
        }
        
        srt_content = extension.export_transcription(attachment, "srt")
        assert "1" in srt_content
        assert "Hello world" in srt_content

        vtt_content = extension.export_transcription(attachment, "vtt")
        assert "WEBVTT" in vtt_content
        assert "Hello world" in vtt_content


class TestWTFTranscriptionAnalysis:
    """Tests for the add_wtf_transcription_analysis() Vcon helper."""

    def _payload(self):
        return {
            "transcript": {
                "text": "Hello world",
                "language": "en",
                "duration": 2.0,
                "confidence": 0.95,
            },
            "segments": [{
                "id": 0,
                "start": 0.0,
                "end": 2.0,
                "text": "Hello world",
                "confidence": 0.95,
            }],
            "metadata": {
                "created_at": "2026-05-10T00:00:00Z",
                "processed_at": "2026-05-10T00:00:01Z",
                "provider": "whisper",
                "model": "whisper-1",
            },
        }

    def test_add_wtf_transcription_analysis_basic(self):
        from vcon import Vcon

        vcon = Vcon.build_new()
        vcon.add_wtf_transcription_analysis(**self._payload(), dialog_index=0)

        assert len(vcon.vcon_dict["analysis"]) == 1
        assert vcon.vcon_dict["attachments"] == []

        entry = vcon.vcon_dict["analysis"][0]
        assert entry["type"] == "transcription"
        assert entry["vendor"] == "whisper"
        assert entry["product"] == "whisper-1"
        assert entry["encoding"] == "json"
        assert entry["schema"] == Vcon.WTF_SCHEMA_URL
        assert entry["dialog"] == [0]

        body = json.loads(entry["body"])
        assert body["transcript"]["text"] == "Hello world"

    def test_add_wtf_transcription_analysis_registers_extension(self):
        from vcon import Vcon

        vcon = Vcon.build_new()
        vcon.add_wtf_transcription_analysis(**self._payload())
        assert "wtf_transcription" in vcon.get_extensions()

    def test_attachment_helper_unchanged_regression(self):
        """Sanity: the existing _attachment helper still writes to attachments[]."""
        from vcon import Vcon

        vcon = Vcon.build_new()
        vcon.add_wtf_transcription_attachment(**self._payload(), dialog_index=0)
        assert len(vcon.vcon_dict["attachments"]) == 1
        assert vcon.vcon_dict["analysis"] == []
        assert vcon.vcon_dict["attachments"][0]["purpose"] == "wtf_transcription"
