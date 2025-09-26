"""
WTF (World Transcription Format) Extension for vCon

This module implements the WTF extension as defined in
draft-howe-vcon-wtf-extension-00, providing standardized mechanisms for
representing speech-to-text transcription data from multiple providers.
"""

from .attachment import (
    WTFAttachment,
    Transcript,
    Segment,
    Word,
    Speaker,
    Quality,
    Metadata,
    WTFProvider
)
from .validation import WTFValidator
from .processing import WTFProcessor
from .providers import (
    WhisperAdapter,
    DeepgramAdapter,
    AssemblyAIAdapter,
    ProviderAdapter
)
from .extension import WTFExtension

__all__ = [
    'WTFAttachment',
    'Transcript',
    'Segment',
    'Word',
    'Speaker',
    'Quality',
    'Metadata',
    'WTFProvider',
    'WTFValidator',
    'WTFProcessor',
    'WhisperAdapter',
    'DeepgramAdapter',
    'AssemblyAIAdapter',
    'ProviderAdapter',
    'WTFExtension'
]
