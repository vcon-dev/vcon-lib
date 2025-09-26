"""
Validation for WTF Extension

This module implements validation logic for WTF transcription attachments
according to the draft specification.
"""

from typing import Dict, List, Any, Optional
import logging
from ..base import ExtensionValidator, ValidationResult
from .attachment import WTFAttachment, WTFProvider

logger = logging.getLogger(__name__)


class WTFValidator(ExtensionValidator):
    """Validator for WTF extension."""
    
    def __init__(self):
        self.supported_providers = {provider.value for provider in WTFProvider}
        self.valid_audio_qualities = ["high", "medium", "low"]
    
    def validate_attachment(self, attachment: Dict[str, Any]) -> ValidationResult:
        """Validate a WTF transcription attachment."""
        result = ValidationResult(True)
        
        # Check attachment type
        if attachment.get("type") != "wtf_transcription":
            result.add_error("Invalid attachment type for WTF extension")
            return result
        
        # Check encoding
        if attachment.get("encoding") != "json":
            result.add_error("WTF transcription attachment must use 'json' encoding")
        
        # Validate body structure
        body = attachment.get("body")
        if not isinstance(body, dict):
            result.add_error("WTF transcription attachment body must be a dictionary")
            return result
        
        # Validate required fields
        body_result = self._validate_wtf_body(body)
        if not body_result.is_valid:
            result.errors.extend(body_result.errors)
            result.warnings.extend(body_result.warnings)
            result.is_valid = False
        
        return result
    
    def validate_extension_usage(self, vcon_dict: Dict[str, Any]) -> ValidationResult:
        """Validate WTF extension usage in a vCon."""
        result = ValidationResult(True)
        
        # Check if extension is declared
        extensions = vcon_dict.get("extensions", [])
        if "wtf_transcription" not in extensions:
            result.add_warning("WTF transcription extension not declared in extensions array")
        
        # Validate all WTF transcription attachments
        attachments = vcon_dict.get("attachments", [])
        wtf_attachments = [
            att for att in attachments 
            if att.get("type") == "wtf_transcription"
        ]
        
        for i, attachment in enumerate(wtf_attachments):
            att_result = self.validate_attachment(attachment)
            if not att_result.is_valid:
                result.add_error(f"WTF transcription attachment {i}: {', '.join(att_result.errors)}")
                result.is_valid = False
            result.warnings.extend([f"Attachment {i}: {w}" for w in att_result.warnings])
        
        return result
    
    def _validate_wtf_body(self, body: Dict[str, Any]) -> ValidationResult:
        """Validate the body of a WTF transcription attachment."""
        result = ValidationResult(True)
        
        # Validate required fields
        required_fields = ["transcript", "segments", "metadata"]
        for field in required_fields:
            if field not in body:
                result.add_error(f"Missing required field: {field}")
        
        # Validate transcript
        if "transcript" in body:
            transcript_result = self._validate_transcript(body["transcript"])
            if not transcript_result.is_valid:
                result.add_error(f"Transcript validation failed: {', '.join(transcript_result.errors)}")
                result.is_valid = False
        
        # Validate segments
        if "segments" in body:
            segments_result = self._validate_segments(body["segments"])
            if not segments_result.is_valid:
                result.add_error(f"Segments validation failed: {', '.join(segments_result.errors)}")
                result.is_valid = False
        
        # Validate metadata
        if "metadata" in body:
            metadata_result = self._validate_metadata(body["metadata"])
            if not metadata_result.is_valid:
                result.add_error(f"Metadata validation failed: {', '.join(metadata_result.errors)}")
                result.is_valid = False
        
        # Validate optional fields
        if "words" in body:
            words_result = self._validate_words(body["words"])
            if not words_result.is_valid:
                result.add_error(f"Words validation failed: {', '.join(words_result.errors)}")
                result.is_valid = False
        
        if "speakers" in body:
            speakers_result = self._validate_speakers(body["speakers"])
            if not speakers_result.is_valid:
                result.add_error(f"Speakers validation failed: {', '.join(speakers_result.errors)}")
                result.is_valid = False
        
        if "quality" in body:
            quality_result = self._validate_quality(body["quality"])
            if not quality_result.is_valid:
                result.add_error(f"Quality validation failed: {', '.join(quality_result.errors)}")
                result.is_valid = False
        
        return result
    
    def _validate_transcript(self, transcript: Dict[str, Any]) -> ValidationResult:
        """Validate transcript object."""
        result = ValidationResult(True)
        
        required_fields = ["text", "language", "duration", "confidence"]
        for field in required_fields:
            if field not in transcript:
                result.add_error(f"Missing required field in transcript: {field}")
        
        # Validate text
        if "text" in transcript:
            if not isinstance(transcript["text"], str):
                result.add_error("Transcript text must be a string")
        
        # Validate language (BCP-47 format)
        if "language" in transcript:
            language = transcript["language"]
            if not isinstance(language, str) or len(language) < 2:
                result.add_error("Invalid language code format")
        
        # Validate duration
        if "duration" in transcript:
            duration = transcript["duration"]
            if not isinstance(duration, (int, float)) or duration < 0:
                result.add_error("Duration must be a non-negative number")
        
        # Validate confidence
        if "confidence" in transcript:
            confidence = transcript["confidence"]
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                result.add_error("Confidence must be a number between 0.0 and 1.0")
        
        return result
    
    def _validate_segments(self, segments: List[Dict[str, Any]]) -> ValidationResult:
        """Validate segments array."""
        result = ValidationResult(True)
        
        if not isinstance(segments, list):
            result.add_error("Segments must be a list")
            return result
        
        if not segments:
            result.add_error("At least one segment is required")
            return result
        
        # Validate each segment
        for i, segment in enumerate(segments):
            segment_result = self._validate_segment(segment)
            if not segment_result.is_valid:
                result.add_error(f"Segment {i}: {', '.join(segment_result.errors)}")
                result.is_valid = False
        
        return result
    
    def _validate_segment(self, segment: Dict[str, Any]) -> ValidationResult:
        """Validate a single segment."""
        result = ValidationResult(True)
        
        required_fields = ["id", "start", "end", "text", "confidence"]
        for field in required_fields:
            if field not in segment:
                result.add_error(f"Missing required field in segment: {field}")
        
        # Validate id
        if "id" in segment:
            if not isinstance(segment["id"], int):
                result.add_error("Segment id must be an integer")
        
        # Validate timestamps
        if "start" in segment and "end" in segment:
            start = segment["start"]
            end = segment["end"]
            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
                result.add_error("Segment start and end must be numbers")
            elif start >= end:
                result.add_error("Segment start must be less than end")
        
        # Validate text
        if "text" in segment:
            if not isinstance(segment["text"], str):
                result.add_error("Segment text must be a string")
        
        # Validate confidence
        if "confidence" in segment:
            confidence = segment["confidence"]
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                result.add_error("Segment confidence must be a number between 0.0 and 1.0")
        
        return result
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> ValidationResult:
        """Validate metadata object."""
        result = ValidationResult(True)
        
        required_fields = ["created_at", "processed_at", "provider", "model"]
        for field in required_fields:
            if field not in metadata:
                result.add_error(f"Missing required field in metadata: {field}")
        
        # Validate timestamps
        for field in ["created_at", "processed_at"]:
            if field in metadata:
                try:
                    from datetime import datetime
                    datetime.fromisoformat(metadata[field].replace('Z', '+00:00'))
                except ValueError:
                    result.add_error(f"Invalid timestamp format in {field}")
        
        # Validate provider
        if "provider" in metadata:
            provider = metadata["provider"]
            if provider not in self.supported_providers:
                result.add_warning(f"Unknown provider: {provider}")
        
        # Validate model
        if "model" in metadata:
            if not isinstance(metadata["model"], str):
                result.add_error("Model must be a string")
        
        return result
    
    def _validate_words(self, words: List[Dict[str, Any]]) -> ValidationResult:
        """Validate words array."""
        result = ValidationResult(True)
        
        if not isinstance(words, list):
            result.add_error("Words must be a list")
            return result
        
        # Validate each word
        for i, word in enumerate(words):
            word_result = self._validate_word(word)
            if not word_result.is_valid:
                result.add_error(f"Word {i}: {', '.join(word_result.errors)}")
                result.is_valid = False
        
        return result
    
    def _validate_word(self, word: Dict[str, Any]) -> ValidationResult:
        """Validate a single word."""
        result = ValidationResult(True)
        
        required_fields = ["id", "start", "end", "text", "confidence"]
        for field in required_fields:
            if field not in word:
                result.add_error(f"Missing required field in word: {field}")
        
        # Validate id
        if "id" in word:
            if not isinstance(word["id"], int):
                result.add_error("Word id must be an integer")
        
        # Validate timestamps
        if "start" in word and "end" in word:
            start = word["start"]
            end = word["end"]
            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
                result.add_error("Word start and end must be numbers")
            elif start >= end:
                result.add_error("Word start must be less than end")
        
        # Validate text
        if "text" in word:
            if not isinstance(word["text"], str):
                result.add_error("Word text must be a string")
        
        # Validate confidence
        if "confidence" in word:
            confidence = word["confidence"]
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                result.add_error("Word confidence must be a number between 0.0 and 1.0")
        
        return result
    
    def _validate_speakers(self, speakers: Dict[str, Any]) -> ValidationResult:
        """Validate speakers object."""
        result = ValidationResult(True)
        
        if not isinstance(speakers, dict):
            result.add_error("Speakers must be a dictionary")
            return result
        
        # Validate each speaker
        for speaker_id, speaker_data in speakers.items():
            speaker_result = self._validate_speaker(speaker_data)
            if not speaker_result.is_valid:
                result.add_error(f"Speaker {speaker_id}: {', '.join(speaker_result.errors)}")
                result.is_valid = False
        
        return result
    
    def _validate_speaker(self, speaker: Dict[str, Any]) -> ValidationResult:
        """Validate a single speaker."""
        result = ValidationResult(True)
        
        required_fields = ["id", "label", "segments", "total_time", "confidence"]
        for field in required_fields:
            if field not in speaker:
                result.add_error(f"Missing required field in speaker: {field}")
        
        # Validate segments
        if "segments" in speaker:
            if not isinstance(speaker["segments"], list):
                result.add_error("Speaker segments must be a list")
        
        # Validate total_time
        if "total_time" in speaker:
            total_time = speaker["total_time"]
            if not isinstance(total_time, (int, float)) or total_time < 0:
                result.add_error("Speaker total_time must be a non-negative number")
        
        # Validate confidence
        if "confidence" in speaker:
            confidence = speaker["confidence"]
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                result.add_error("Speaker confidence must be a number between 0.0 and 1.0")
        
        return result
    
    def _validate_quality(self, quality: Dict[str, Any]) -> ValidationResult:
        """Validate quality object."""
        result = ValidationResult(True)
        
        required_fields = [
            "audio_quality", "background_noise", "multiple_speakers",
            "overlapping_speech", "silence_ratio", "average_confidence",
            "low_confidence_words", "processing_warnings"
        ]
        
        for field in required_fields:
            if field not in quality:
                result.add_error(f"Missing required field in quality: {field}")
        
        # Validate audio_quality
        if "audio_quality" in quality:
            audio_quality = quality["audio_quality"]
            if audio_quality not in self.valid_audio_qualities:
                result.add_error(f"Invalid audio_quality: {audio_quality}")
        
        # Validate background_noise
        if "background_noise" in quality:
            noise = quality["background_noise"]
            if not isinstance(noise, (int, float)) or not (0.0 <= noise <= 1.0):
                result.add_error("Background noise must be a number between 0.0 and 1.0")
        
        # Validate boolean fields
        for field in ["multiple_speakers", "overlapping_speech"]:
            if field in quality:
                if not isinstance(quality[field], bool):
                    result.add_error(f"{field} must be a boolean")
        
        # Validate silence_ratio
        if "silence_ratio" in quality:
            ratio = quality["silence_ratio"]
            if not isinstance(ratio, (int, float)) or not (0.0 <= ratio <= 1.0):
                result.add_error("Silence ratio must be a number between 0.0 and 1.0")
        
        # Validate average_confidence
        if "average_confidence" in quality:
            confidence = quality["average_confidence"]
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                result.add_error("Average confidence must be a number between 0.0 and 1.0")
        
        # Validate low_confidence_words
        if "low_confidence_words" in quality:
            count = quality["low_confidence_words"]
            if not isinstance(count, int) or count < 0:
                result.add_error("Low confidence words count must be a non-negative integer")
        
        # Validate processing_warnings
        if "processing_warnings" in quality:
            warnings = quality["processing_warnings"]
            if not isinstance(warnings, list):
                result.add_error("Processing warnings must be a list")
            elif not all(isinstance(w, str) for w in warnings):
                result.add_error("All processing warnings must be strings")
        
        return result
    
    def validate_wtf_attachment(self, attachment: WTFAttachment) -> ValidationResult:
        """Validate a WTFAttachment object."""
        result = ValidationResult(True)
        
        # Validate transcript
        if not attachment.transcript.text:
            result.add_error("Transcript text cannot be empty")
        
        if attachment.transcript.duration <= 0:
            result.add_error("Transcript duration must be positive")
        
        if not (0.0 <= attachment.transcript.confidence <= 1.0):
            result.add_error("Transcript confidence must be between 0.0 and 1.0")
        
        # Validate segments
        if not attachment.segments:
            result.add_error("At least one segment is required")
        
        # Check segment consistency
        for i, segment in enumerate(attachment.segments):
            if segment.start >= segment.end:
                result.add_error(f"Segment {i}: start time must be less than end time")
            
            if not (0.0 <= segment.confidence <= 1.0):
                result.add_error(f"Segment {i}: confidence must be between 0.0 and 1.0")
        
        # Validate words if present
        if attachment.words:
            for i, word in enumerate(attachment.words):
                if word.start >= word.end:
                    result.add_error(f"Word {i}: start time must be less than end time")
                
                if not (0.0 <= word.confidence <= 1.0):
                    result.add_error(f"Word {i}: confidence must be between 0.0 and 1.0")
        
        return result
