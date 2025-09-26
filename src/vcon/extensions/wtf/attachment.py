"""
WTF Attachment Classes

This module implements the core data structures for WTF (World Transcription Format)
attachments as defined in the draft specification.
"""

from enum import Enum
from typing import List, Dict, Optional, Union, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class WTFProvider(Enum):
    """Supported transcription providers."""
    WHISPER = "whisper"
    DEEPGRAM = "deepgram"
    ASSEMBLYAI = "assemblyai"
    GOOGLE = "google"
    AMAZON = "amazon"
    AZURE = "azure"
    REV_AI = "rev.ai"
    SPEECHMATICS = "speechmatics"
    WAV2VEC2 = "wav2vec2"
    PARAKEET = "parakeet"


class Transcript:
    """Represents the high-level transcript information."""
    
    def __init__(
        self,
        text: str,
        language: str,
        duration: float,
        confidence: float
    ):
        self.text = text
        self.language = language
        self.duration = duration
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "text": self.text,
            "language": self.language,
            "duration": self.duration,
            "confidence": self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transcript':
        """Create from dictionary representation."""
        return cls(
            text=data["text"],
            language=data["language"],
            duration=data["duration"],
            confidence=data["confidence"]
        )


class Word:
    """Represents a single word in the transcription."""
    
    def __init__(
        self,
        id: int,
        start: float,
        end: float,
        text: str,
        confidence: float,
        speaker: Optional[Union[int, str]] = None,
        is_punctuation: Optional[bool] = None
    ):
        self.id = id
        self.start = start
        self.end = end
        self.text = text
        self.confidence = confidence
        self.speaker = speaker
        self.is_punctuation = is_punctuation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "confidence": self.confidence
        }
        
        if self.speaker is not None:
            result["speaker"] = self.speaker
        if self.is_punctuation is not None:
            result["is_punctuation"] = self.is_punctuation
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Word':
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            start=data["start"],
            end=data["end"],
            text=data["text"],
            confidence=data["confidence"],
            speaker=data.get("speaker"),
            is_punctuation=data.get("is_punctuation")
        )


class Segment:
    """Represents a logical chunk of transcribed content."""
    
    def __init__(
        self,
        id: int,
        start: float,
        end: float,
        text: str,
        confidence: float,
        speaker: Optional[Union[int, str]] = None,
        words: Optional[List[int]] = None
    ):
        self.id = id
        self.start = start
        self.end = end
        self.text = text
        self.confidence = confidence
        self.speaker = speaker
        self.words = words or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "confidence": self.confidence
        }
        
        if self.speaker is not None:
            result["speaker"] = self.speaker
        if self.words:
            result["words"] = self.words
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Segment':
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            start=data["start"],
            end=data["end"],
            text=data["text"],
            confidence=data["confidence"],
            speaker=data.get("speaker"),
            words=data.get("words")
        )


class Speaker:
    """Represents speaker information for diarization."""
    
    def __init__(
        self,
        id: Union[int, str],
        label: str,
        segments: List[int],
        total_time: float,
        confidence: float
    ):
        self.id = id
        self.label = label
        self.segments = segments
        self.total_time = total_time
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "label": self.label,
            "segments": self.segments,
            "total_time": self.total_time,
            "confidence": self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Speaker':
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            label=data["label"],
            segments=data["segments"],
            total_time=data["total_time"],
            confidence=data["confidence"]
        )


class Quality:
    """Represents quality metrics for the transcription."""
    
    def __init__(
        self,
        audio_quality: str,
        background_noise: float,
        multiple_speakers: bool,
        overlapping_speech: bool,
        silence_ratio: float,
        average_confidence: float,
        low_confidence_words: int,
        processing_warnings: List[str]
    ):
        self.audio_quality = audio_quality
        self.background_noise = background_noise
        self.multiple_speakers = multiple_speakers
        self.overlapping_speech = overlapping_speech
        self.silence_ratio = silence_ratio
        self.average_confidence = average_confidence
        self.low_confidence_words = low_confidence_words
        self.processing_warnings = processing_warnings
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "audio_quality": self.audio_quality,
            "background_noise": self.background_noise,
            "multiple_speakers": self.multiple_speakers,
            "overlapping_speech": self.overlapping_speech,
            "silence_ratio": self.silence_ratio,
            "average_confidence": self.average_confidence,
            "low_confidence_words": self.low_confidence_words,
            "processing_warnings": self.processing_warnings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Quality':
        """Create from dictionary representation."""
        return cls(
            audio_quality=data["audio_quality"],
            background_noise=data["background_noise"],
            multiple_speakers=data["multiple_speakers"],
            overlapping_speech=data["overlapping_speech"],
            silence_ratio=data["silence_ratio"],
            average_confidence=data["average_confidence"],
            low_confidence_words=data["low_confidence_words"],
            processing_warnings=data["processing_warnings"]
        )


class Metadata:
    """Represents processing and source metadata."""
    
    def __init__(
        self,
        created_at: str,
        processed_at: str,
        provider: str,
        model: str,
        processing_time: Optional[float] = None,
        audio: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ):
        self.created_at = created_at
        self.processed_at = processed_at
        self.provider = provider
        self.model = model
        self.processing_time = processing_time
        self.audio = audio or {}
        self.options = options or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "created_at": self.created_at,
            "processed_at": self.processed_at,
            "provider": self.provider,
            "model": self.model
        }
        
        if self.processing_time is not None:
            result["processing_time"] = self.processing_time
        if self.audio:
            result["audio"] = self.audio
        if self.options:
            result["options"] = self.options
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Metadata':
        """Create from dictionary representation."""
        return cls(
            created_at=data["created_at"],
            processed_at=data["processed_at"],
            provider=data["provider"],
            model=data["model"],
            processing_time=data.get("processing_time"),
            audio=data.get("audio"),
            options=data.get("options")
        )


class WTFAttachment:
    """
    Represents a WTF transcription attachment.
    
    This class handles the creation, validation, and processing of WTF
    transcription attachments according to the draft specification.
    """
    
    def __init__(
        self,
        transcript: Transcript,
        segments: List[Segment],
        metadata: Metadata,
        words: Optional[List[Word]] = None,
        speakers: Optional[Dict[str, Speaker]] = None,
        alternatives: Optional[List[Dict[str, Any]]] = None,
        enrichments: Optional[Dict[str, Any]] = None,
        extensions: Optional[Dict[str, Any]] = None,
        quality: Optional[Quality] = None,
        streaming: Optional[Dict[str, Any]] = None
    ):
        self.transcript = transcript
        self.segments = segments
        self.metadata = metadata
        self.words = words or []
        self.speakers = speakers or {}
        self.alternatives = alternatives or []
        self.enrichments = enrichments or {}
        self.extensions = extensions or {}
        self.quality = quality
        self.streaming = streaming or {}
    
    def get_speaking_time(self) -> Dict[str, float]:
        """Calculate speaking time for each speaker."""
        speaking_times = {}
        
        for speaker_id, speaker in self.speakers.items():
            speaking_times[speaker_id] = speaker.total_time
        
        return speaking_times
    
    def find_low_confidence_segments(self, threshold: float = 0.5) -> List[Segment]:
        """Find segments with confidence below threshold."""
        return [segment for segment in self.segments if segment.confidence < threshold]
    
    def extract_keywords(self, min_confidence: float = 0.8) -> List[str]:
        """Extract keywords from high-confidence words."""
        keywords = []
        for word in self.words:
            if word.confidence >= min_confidence and not word.is_punctuation:
                keywords.append(word.text.lower())
        return list(set(keywords))  # Remove duplicates
    
    def export_to_srt(self) -> str:
        """Export transcription to SRT subtitle format."""
        srt_content = []
        
        for i, segment in enumerate(self.segments, 1):
            # Convert timestamps to SRT format (HH:MM:SS,mmm)
            start_time = self._format_srt_timestamp(segment.start)
            end_time = self._format_srt_timestamp(segment.end)
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(segment.text)
            srt_content.append("")  # Empty line between segments
        
        return "\n".join(srt_content)
    
    def export_to_vtt(self) -> str:
        """Export transcription to WebVTT format."""
        vtt_content = ["WEBVTT", ""]
        
        for segment in self.segments:
            start_time = self._format_vtt_timestamp(segment.start)
            end_time = self._format_vtt_timestamp(segment.end)
            
            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(segment.text)
            vtt_content.append("")
        
        return "\n".join(vtt_content)
    
    def _format_srt_timestamp(self, seconds: float) -> str:
        """Format timestamp for SRT format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _format_vtt_timestamp(self, seconds: float) -> str:
        """Format timestamp for WebVTT format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "transcript": self.transcript.to_dict(),
            "segments": [segment.to_dict() for segment in self.segments],
            "metadata": self.metadata.to_dict()
        }
        
        if self.words:
            result["words"] = [word.to_dict() for word in self.words]
        if self.speakers:
            result["speakers"] = {
                str(speaker_id): speaker.to_dict() 
                for speaker_id, speaker in self.speakers.items()
            }
        if self.alternatives:
            result["alternatives"] = self.alternatives
        if self.enrichments:
            result["enrichments"] = self.enrichments
        if self.extensions:
            result["extensions"] = self.extensions
        if self.quality:
            result["quality"] = self.quality.to_dict()
        if self.streaming:
            result["streaming"] = self.streaming
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WTFAttachment':
        """Create from dictionary representation."""
        # Parse speakers
        speakers = {}
        if "speakers" in data:
            for speaker_id, speaker_data in data["speakers"].items():
                speakers[speaker_id] = Speaker.from_dict(speaker_data)
        
        return cls(
            transcript=Transcript.from_dict(data["transcript"]),
            segments=[Segment.from_dict(s) for s in data["segments"]],
            metadata=Metadata.from_dict(data["metadata"]),
            words=[Word.from_dict(w) for w in data.get("words", [])],
            speakers=speakers,
            alternatives=data.get("alternatives"),
            enrichments=data.get("enrichments"),
            extensions=data.get("extensions"),
            quality=Quality.from_dict(data["quality"]) if data.get("quality") else None,
            streaming=data.get("streaming")
        )
