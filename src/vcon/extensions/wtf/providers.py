"""
Provider Adapters for WTF Extension

This module implements adapters for converting provider-specific transcription
data to the standardized WTF format.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone
from .attachment import (
    WTFAttachment,
    Transcript,
    Segment,
    Word,
    Speaker,
    Quality,
    Metadata
)

logger = logging.getLogger(__name__)


class ProviderAdapter(ABC):
    """Base class for provider adapters."""
    
    @abstractmethod
    def convert(self, provider_data: Dict[str, Any]) -> WTFAttachment:
        """Convert provider-specific data to WTF format."""
        pass
    
    def _normalize_confidence(self, confidence: Any, provider: str) -> float:
        """Normalize confidence scores to [0.0, 1.0] range."""
        if isinstance(confidence, (int, float)):
            if provider == "whisper":
                # Whisper uses log probabilities, convert to confidence
                return max(0.0, min(1.0, (confidence + 1.0) / 2.0))
            elif provider in ["deepgram", "assemblyai"]:
                # These providers typically use 0-1 range already
                return max(0.0, min(1.0, float(confidence)))
            else:
                # Default normalization
                return max(0.0, min(1.0, float(confidence)))
        
        return 0.0
    
    def _normalize_timestamp(self, timestamp: Any) -> float:
        """Normalize timestamps to seconds."""
        if isinstance(timestamp, (int, float)):
            return float(timestamp)
        elif isinstance(timestamp, str):
            # Try to parse as seconds
            try:
                return float(timestamp)
            except ValueError:
                logger.warning(f"Could not parse timestamp: {timestamp}")
                return 0.0
        
        return 0.0


class WhisperAdapter(ProviderAdapter):
    """Adapter for OpenAI Whisper transcription data."""
    
    def convert(self, whisper_data: Dict[str, Any]) -> WTFAttachment:
        """Convert Whisper data to WTF format."""
        try:
            # Extract transcript information
            text = whisper_data.get("text", "")
            language = whisper_data.get("language", "en")
            
            # Calculate duration from segments
            segments_data = whisper_data.get("segments", [])
            duration = 0.0
            if segments_data:
                last_segment = segments_data[-1]
                duration = self._normalize_timestamp(last_segment.get("end", 0))
            
            # Calculate average confidence
            confidence = 0.0
            if segments_data:
                confidences = [
                    self._normalize_confidence(seg.get("avg_logprob", -1), "whisper")
                    for seg in segments_data
                ]
                confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            transcript = Transcript(
                text=text,
                language=language,
                duration=duration,
                confidence=confidence
            )
            
            # Convert segments
            segments = []
            words = []
            word_id = 0
            
            for i, seg_data in enumerate(segments_data):
                segment = Segment(
                    id=i,
                    start=self._normalize_timestamp(seg_data.get("start", 0)),
                    end=self._normalize_timestamp(seg_data.get("end", 0)),
                    text=seg_data.get("text", "").strip(),
                    confidence=self._normalize_confidence(seg_data.get("avg_logprob", -1), "whisper")
                )
                segments.append(segment)
                
                # Convert words if available
                seg_words = seg_data.get("words", [])
                for word_data in seg_words:
                    word = Word(
                        id=word_id,
                        start=self._normalize_timestamp(word_data.get("start", 0)),
                        end=self._normalize_timestamp(word_data.get("end", 0)),
                        text=word_data.get("word", ""),
                        confidence=self._normalize_confidence(word_data.get("probability", 0), "whisper")
                    )
                    words.append(word)
                    word_id += 1
                
                # Add word references to segment
                segment.words = list(range(len(words) - len(seg_words), len(words)))
            
            # Create metadata
            metadata = Metadata(
                created_at=datetime.now(timezone.utc).isoformat(),
                processed_at=datetime.now(timezone.utc).isoformat(),
                provider="whisper",
                model=whisper_data.get("model", "whisper-1"),
                processing_time=whisper_data.get("processing_time"),
                options=whisper_data.get("options", {})
            )
            
            # Create extensions with Whisper-specific data
            extensions = {
                "whisper": {
                    "temperature": whisper_data.get("temperature"),
                    "compression_ratio": whisper_data.get("compression_ratio"),
                    "avg_logprob": whisper_data.get("avg_logprob"),
                    "no_speech_prob": whisper_data.get("no_speech_prob")
                }
            }
            
            return WTFAttachment(
                transcript=transcript,
                segments=segments,
                metadata=metadata,
                words=words,
                extensions=extensions
            )
            
        except Exception as e:
            logger.error(f"Error converting Whisper data: {str(e)}")
            raise


class DeepgramAdapter(ProviderAdapter):
    """Adapter for Deepgram transcription data."""
    
    def convert(self, deepgram_data: Dict[str, Any]) -> WTFAttachment:
        """Convert Deepgram data to WTF format."""
        try:
            # Extract transcript information
            results = deepgram_data.get("results", {})
            channels = results.get("channels", [])
            
            if not channels:
                raise ValueError("No channels found in Deepgram data")
            
            channel = channels[0]
            alternatives = channel.get("alternatives", [])
            
            if not alternatives:
                raise ValueError("No alternatives found in Deepgram data")
            
            alternative = alternatives[0]
            text = alternative.get("transcript", "")
            confidence = alternative.get("confidence", 0.0)
            
            # Get metadata
            metadata_info = deepgram_data.get("metadata", {})
            duration = metadata_info.get("duration", 0.0)
            
            transcript = Transcript(
                text=text,
                language=metadata_info.get("language", "en"),
                duration=duration,
                confidence=self._normalize_confidence(confidence, "deepgram")
            )
            
            # Convert words
            words = []
            word_id = 0
            
            for word_data in alternative.get("words", []):
                word = Word(
                    id=word_id,
                    start=self._normalize_timestamp(word_data.get("start", 0)),
                    end=self._normalize_timestamp(word_data.get("end", 0)),
                    text=word_data.get("word", ""),
                    confidence=self._normalize_confidence(word_data.get("confidence", 0), "deepgram"),
                    speaker=word_data.get("speaker")
                )
                words.append(word)
                word_id += 1
            
            # Convert segments (create from words)
            segments = []
            current_segment_words = []
            current_segment_text = ""
            segment_id = 0
            
            for word in words:
                current_segment_words.append(word.id)
                current_segment_text += word.text + " "
                
                # Create segment at sentence boundaries or every 10 words
                if (word.text.endswith(('.', '!', '?')) or 
                    len(current_segment_words) >= 10):
                    
                    segment = Segment(
                        id=segment_id,
                        start=words[current_segment_words[0]].start,
                        end=words[current_segment_words[-1]].end,
                        text=current_segment_text.strip(),
                        confidence=sum(w.confidence for w in words[current_segment_words[0]:current_segment_words[-1]+1]) / len(current_segment_words),
                        words=current_segment_words.copy()
                    )
                    segments.append(segment)
                    segment_id += 1
                    
                    current_segment_words = []
                    current_segment_text = ""
            
            # Add remaining words as final segment
            if current_segment_words:
                segment = Segment(
                    id=segment_id,
                    start=words[current_segment_words[0]].start,
                    end=words[current_segment_words[-1]].end,
                    text=current_segment_text.strip(),
                    confidence=sum(w.confidence for w in words[current_segment_words[0]:current_segment_words[-1]+1]) / len(current_segment_words),
                    words=current_segment_words
                )
                segments.append(segment)
            
            # Create metadata
            metadata = Metadata(
                created_at=datetime.now(timezone.utc).isoformat(),
                processed_at=datetime.now(timezone.utc).isoformat(),
                provider="deepgram",
                model=metadata_info.get("model_name", "nova-2"),
                processing_time=metadata_info.get("processing_time"),
                audio={
                    "duration": duration,
                    "sample_rate": metadata_info.get("sample_rate"),
                    "channels": metadata_info.get("channels"),
                    "format": metadata_info.get("format")
                },
                options=deepgram_data.get("options", {})
            )
            
            # Create extensions with Deepgram-specific data
            extensions = {
                "deepgram": {
                    "utterances": results.get("utterances", []),
                    "paragraphs": results.get("paragraphs", []),
                    "search_terms": results.get("search_terms", [])
                }
            }
            
            return WTFAttachment(
                transcript=transcript,
                segments=segments,
                metadata=metadata,
                words=words,
                extensions=extensions
            )
            
        except Exception as e:
            logger.error(f"Error converting Deepgram data: {str(e)}")
            raise


class AssemblyAIAdapter(ProviderAdapter):
    """Adapter for AssemblyAI transcription data."""
    
    def convert(self, assemblyai_data: Dict[str, Any]) -> WTFAttachment:
        """Convert AssemblyAI data to WTF format."""
        try:
            # Extract transcript information
            text = assemblyai_data.get("text", "")
            confidence = assemblyai_data.get("confidence", 0.0)
            audio_duration = assemblyai_data.get("audio_duration", 0.0)
            language_code = assemblyai_data.get("language_code", "en")
            
            transcript = Transcript(
                text=text,
                language=language_code,
                duration=audio_duration,
                confidence=self._normalize_confidence(confidence, "assemblyai")
            )
            
            # Convert words
            words = []
            word_id = 0
            
            for word_data in assemblyai_data.get("words", []):
                word = Word(
                    id=word_id,
                    start=self._normalize_timestamp(word_data.get("start", 0)) / 1000,  # Convert ms to seconds
                    end=self._normalize_timestamp(word_data.get("end", 0)) / 1000,
                    text=word_data.get("text", ""),
                    confidence=self._normalize_confidence(word_data.get("confidence", 0), "assemblyai"),
                    speaker=word_data.get("speaker")
                )
                words.append(word)
                word_id += 1
            
            # Convert utterances to segments
            segments = []
            segment_id = 0
            
            for utterance in assemblyai_data.get("utterances", []):
                utterance_words = utterance.get("words", [])
                if not utterance_words:
                    continue
                
                # Find word indices for this utterance
                word_indices = []
                utterance_text = ""
                
                for word_data in utterance_words:
                    # Find corresponding word in words list
                    for i, word in enumerate(words):
                        if (abs(word.start - word_data.get("start", 0) / 1000) < 0.01 and
                            word.text == word_data.get("text", "")):
                            word_indices.append(i)
                            utterance_text += word.text + " "
                            break
                
                if word_indices:
                    segment = Segment(
                        id=segment_id,
                        start=words[word_indices[0]].start,
                        end=words[word_indices[-1]].end,
                        text=utterance_text.strip(),
                        confidence=sum(words[i].confidence for i in word_indices) / len(word_indices),
                        speaker=utterance.get("speaker"),
                        words=word_indices
                    )
                    segments.append(segment)
                    segment_id += 1
            
            # Create metadata
            metadata = Metadata(
                created_at=datetime.now(timezone.utc).isoformat(),
                processed_at=datetime.now(timezone.utc).isoformat(),
                provider="assemblyai",
                model=assemblyai_data.get("model", "best"),
                processing_time=assemblyai_data.get("processing_time"),
                audio={
                    "duration": audio_duration,
                    "sample_rate": assemblyai_data.get("sample_rate"),
                    "channels": assemblyai_data.get("channels")
                },
                options=assemblyai_data.get("options", {})
            )
            
            # Create extensions with AssemblyAI-specific data
            extensions = {
                "assemblyai": {
                    "sentiment_analysis": assemblyai_data.get("sentiment_analysis_results"),
                    "entity_detection": assemblyai_data.get("entities"),
                    "topic_detection": assemblyai_data.get("topics"),
                    "auto_highlights": assemblyai_data.get("auto_highlights_result")
                }
            }
            
            return WTFAttachment(
                transcript=transcript,
                segments=segments,
                metadata=metadata,
                words=words,
                extensions=extensions
            )
            
        except Exception as e:
            logger.error(f"Error converting AssemblyAI data: {str(e)}")
            raise
