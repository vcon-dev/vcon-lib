"""
vCon Extensions Module

This module provides the framework for implementing vCon extensions,
including the Lawful Basis and WTF (World Transcription Format) extensions.
"""

from .base import ExtensionType, ExtensionValidator, ExtensionProcessor
from .registry import ExtensionRegistry

# Import extension implementations
from .lawful_basis import LawfulBasisExtension
from .wtf import WTFExtension

__all__ = [
    'ExtensionType',
    'ExtensionValidator', 
    'ExtensionProcessor',
    'ExtensionRegistry',
    'LawfulBasisExtension',
    'WTFExtension'
]
