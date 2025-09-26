"""
Processing for WTF Extension

This module implements processing logic for WTF transcription attachments,
including provider integration and analysis capabilities.
"""

from typing import Dict, List, Any, Optional, Union
import logging
from ..base import ExtensionProcessor, ProcessingResult
from .attachment import WTFAttachment, Transcript, Segment, Word, Speaker, Quality

logger = logging.getLogger(__name__)


class WTFProcessor(ExtensionProcessor):
    """Processor for WTF extension."""
    
    def __init__(self):
        self.provider_adapters = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize provider adapters."""
        try:
            from .providers import (
                WhisperAdapter,
                DeepgramAdapter,
                AssemblyAIAdapter
            )
            
            self.provider_adapters = {
                "whisper": WhisperAdapter(),
                "deepgram": DeepgramAdapter(),
                "assemblyai": AssemblyAIAdapter()
            }
            
            logger.info("WTF provider adapters initialized")
        except ImportError as e:
            logger.warning(f"Could not import provider adapters: {str(e)}")
    
    def process(self, vcon_dict: Dict[str, Any]) -> ProcessingResult:
        """Process WTF extension in a vCon."""
        try:
            # Find all WTF transcription attachments
            attachments = vcon_dict.get("attachments", [])
            wtf_attachments = [
                att for att in attachments 
                if att.get("type") == "wtf_transcription"
            ]
            
            if not wtf_attachments:
                return ProcessingResult(
                    True,
                    data={"message": "No WTF transcription attachments found"}
                )
            
            # Process each attachment
            processed_attachments = []
            for i, attachment in enumerate(wtf_attachments):
                try:
                    wtf_obj = WTFAttachment.from_dict(attachment["body"])
                    
                    # Calculate statistics
                    stats = self._calculate_statistics(wtf_obj)
                    
                    processed_attachments.append({
                        "index": i,
                        "provider": wtf_obj.metadata.provider,
                        "model": wtf_obj.metadata.model,
                        "language": wtf_obj.transcript.language,
                        "duration": wtf_obj.transcript.duration,
                        "confidence": wtf_obj.transcript.confidence,
                        "segments_count": len(wtf_obj.segments),
                        "words_count": len(wtf_obj.words),
                        "speakers_count": len(wtf_obj.speakers),
                        "statistics": stats
                    })
                except Exception as e:
                    logger.error(f"Error processing WTF attachment {i}: {str(e)}")
            
            return ProcessingResult(
                True,
                data={
                    "wtf_attachments": processed_attachments,
                    "total_attachments": len(wtf_attachments)
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing WTF extension: {str(e)}")
            return ProcessingResult(
                False,
                errors=[f"Processing error: {str(e)}"]
            )
    
    def can_process(self, extension_name: str) -> bool:
        """Check if this processor can handle the given extension."""
        return extension_name == "wtf_transcription"
    
    def _calculate_statistics(self, wtf_attachment: WTFAttachment) -> Dict[str, Any]:
        """Calculate statistics for a WTF attachment."""
        stats = {
            "total_words": len(wtf_attachment.words),
            "total_segments": len(wtf_attachment.segments),
            "total_speakers": len(wtf_attachment.speakers),
            "average_confidence": 0.0,
            "low_confidence_segments": 0,
            "speaking_time_by_speaker": {}
        }
        
        # Calculate average confidence
        if wtf_attachment.segments:
            total_confidence = sum(segment.confidence for segment in wtf_attachment.segments)
            stats["average_confidence"] = total_confidence / len(wtf_attachment.segments)
        
        # Count low confidence segments
        stats["low_confidence_segments"] = len(
            wtf_attachment.find_low_confidence_segments(threshold=0.5)
        )
        
        # Calculate speaking time by speaker
        stats["speaking_time_by_speaker"] = wtf_attachment.get_speaking_time()
        
        return stats
    
    def convert_from_provider(
        self,
        provider_data: Dict[str, Any],
        provider: str
    ) -> WTFAttachment:
        """Convert provider-specific data to WTF format."""
        adapter = self.provider_adapters.get(provider.lower())
        if not adapter:
            raise ValueError(f"No adapter available for provider: {provider}")
        
        return adapter.convert(provider_data)
    
    def export_transcription(
        self,
        wtf_attachment: WTFAttachment,
        format: str = "srt"
    ) -> str:
        """Export transcription in specified format."""
        if format.lower() == "srt":
            return wtf_attachment.export_to_srt()
        elif format.lower() == "vtt":
            return wtf_attachment.export_to_vtt()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def analyze_transcription(self, wtf_attachment: WTFAttachment) -> Dict[str, Any]:
        """Perform analysis on a WTF transcription."""
        analysis = {
            "keywords": wtf_attachment.extract_keywords(),
            "speaking_time": wtf_attachment.get_speaking_time(),
            "low_confidence_segments": [
                {
                    "id": seg.id,
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text,
                    "confidence": seg.confidence
                }
                for seg in wtf_attachment.find_low_confidence_segments()
            ],
            "quality_metrics": {}
        }
        
        # Add quality metrics if available
        if wtf_attachment.quality:
            analysis["quality_metrics"] = {
                "audio_quality": wtf_attachment.quality.audio_quality,
                "background_noise": wtf_attachment.quality.background_noise,
                "multiple_speakers": wtf_attachment.quality.multiple_speakers,
                "overlapping_speech": wtf_attachment.quality.overlapping_speech,
                "silence_ratio": wtf_attachment.quality.silence_ratio,
                "average_confidence": wtf_attachment.quality.average_confidence,
                "low_confidence_words": wtf_attachment.quality.low_confidence_words
            }
        
        return analysis
    
    def compare_transcriptions(
        self,
        wtf_attachments: List[WTFAttachment]
    ) -> Dict[str, Any]:
        """Compare multiple transcriptions."""
        if len(wtf_attachments) < 2:
            raise ValueError("At least two transcriptions required for comparison")
        
        comparison = {
            "transcription_count": len(wtf_attachments),
            "providers": [att.metadata.provider for att in wtf_attachments],
            "models": [att.metadata.model for att in wtf_attachments],
            "confidence_scores": [att.transcript.confidence for att in wtf_attachments],
            "duration_differences": [],
            "text_differences": []
        }
        
        # Calculate duration differences
        base_duration = wtf_attachments[0].transcript.duration
        for i, att in enumerate(wtf_attachments[1:], 1):
            diff = abs(att.transcript.duration - base_duration)
            comparison["duration_differences"].append({
                "index": i,
                "difference": diff,
                "percentage": (diff / base_duration) * 100 if base_duration > 0 else 0
            })
        
        # Calculate text differences (simplified)
        base_text = wtf_attachments[0].transcript.text.lower()
        for i, att in enumerate(wtf_attachments[1:], 1):
            text = att.transcript.text.lower()
            # Simple word count comparison
            base_words = set(base_text.split())
            text_words = set(text.split())
            common_words = base_words.intersection(text_words)
            total_words = base_words.union(text_words)
            
            similarity = len(common_words) / len(total_words) if total_words else 0
            
            comparison["text_differences"].append({
                "index": i,
                "similarity": similarity,
                "common_words": len(common_words),
                "total_words": len(total_words)
            })
        
        return comparison
