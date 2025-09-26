"""
WTF Extension Implementation

This module provides the main extension class that integrates all WTF
functionality with the vCon extension framework.
"""

from typing import Dict, Any, List, Optional
import logging
from ..base import ExtensionInfo, ExtensionType
from .validation import WTFValidator
from .processing import WTFProcessor
from .attachment import WTFAttachment

logger = logging.getLogger(__name__)


class WTFExtension:
    """Main class for the WTF extension."""
    
    def __init__(self):
        self.validator = WTFValidator()
        self.processor = WTFProcessor()
    
    def get_extension_info(self) -> ExtensionInfo:
        """Get extension information."""
        return ExtensionInfo(
            name="wtf_transcription",
            extension_type=ExtensionType.COMPATIBLE,
            version="1.0",
            description="World Transcription Format for standardized speech-to-text representation with multi-provider support",
            attachment_types=["wtf_transcription"],
            validator=self.validator,
            processor=self.processor
        )
    
    def create_wtf_attachment(
        self,
        transcript: Dict[str, Any],
        segments: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Create a WTF transcription attachment dictionary."""
        from .attachment import (
            WTFAttachment, Transcript, Segment, Metadata, Word, Speaker, Quality
        )
        
        # Create transcript object
        transcript_obj = Transcript.from_dict(transcript)
        
        # Create segment objects
        segment_objs = [Segment.from_dict(seg) for seg in segments]
        
        # Create metadata object
        metadata_obj = Metadata.from_dict(metadata)
        
        # Create optional objects
        words = kwargs.get("words", [])
        if words:
            word_objs = [Word.from_dict(word) for word in words]
        else:
            word_objs = []
        
        speakers = kwargs.get("speakers", {})
        if speakers:
            from .attachment import Speaker
            speaker_objs = {
                str(speaker_id): Speaker.from_dict(speaker_data)
                for speaker_id, speaker_data in speakers.items()
            }
        else:
            speaker_objs = {}
        
        quality = kwargs.get("quality")
        if quality:
            quality_obj = Quality.from_dict(quality)
        else:
            quality_obj = None
        
        # Create attachment object
        attachment = WTFAttachment(
            transcript=transcript_obj,
            segments=segment_objs,
            metadata=metadata_obj,
            words=word_objs,
            speakers=speaker_objs,
            quality=quality_obj,
            alternatives=kwargs.get("alternatives", []),
            enrichments=kwargs.get("enrichments", {}),
            extensions=kwargs.get("extensions", {}),
            streaming=kwargs.get("streaming", {})
        )
        
        # Return as attachment dictionary
        return {
            "type": "wtf_transcription",
            "encoding": "json",
            "body": attachment.to_dict()
        }
    
    def convert_from_provider(
        self,
        provider_data: Dict[str, Any],
        provider: str
    ) -> Dict[str, Any]:
        """Convert provider-specific data to WTF attachment."""
        wtf_attachment = self.processor.convert_from_provider(provider_data, provider)
        
        return {
            "type": "wtf_transcription",
            "encoding": "json",
            "body": wtf_attachment.to_dict()
        }
    
    def validate_wtf_attachment(self, attachment: Dict[str, Any]) -> bool:
        """Validate a WTF transcription attachment."""
        result = self.validator.validate_attachment(attachment)
        return result.is_valid
    
    def export_transcription(
        self,
        attachment: Dict[str, Any],
        format: str = "srt"
    ) -> str:
        """Export transcription in specified format."""
        wtf_attachment = WTFAttachment.from_dict(attachment["body"])
        return self.processor.export_transcription(wtf_attachment, format)
    
    def analyze_transcription(self, attachment: Dict[str, Any]) -> Dict[str, Any]:
        """Perform analysis on a WTF transcription."""
        wtf_attachment = WTFAttachment.from_dict(attachment["body"])
        return self.processor.analyze_transcription(wtf_attachment)
    
    def compare_transcriptions(self, attachments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple transcriptions."""
        wtf_attachments = [
            WTFAttachment.from_dict(att["body"]) for att in attachments
        ]
        return self.processor.compare_transcriptions(wtf_attachments)
