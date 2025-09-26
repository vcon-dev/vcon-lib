"""
vCon Extensions Module

This module provides the framework for implementing vCon extensions,
including the Lawful Basis and WTF (World Transcription Format) extensions.
"""

from .base import ExtensionType, ExtensionValidator, ExtensionProcessor
from .registry import ExtensionRegistry, get_extension_registry

# Import extension implementations
from .lawful_basis import LawfulBasisExtension
from .wtf import WTFExtension

# Initialize the global registry
_global_registry = None

def get_extension_registry() -> ExtensionRegistry:
    """Get the global extension registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ExtensionRegistry()
        _global_registry.initialize_default_extensions()
    return _global_registry

__all__ = [
    'ExtensionType',
    'ExtensionValidator', 
    'ExtensionProcessor',
    'ExtensionRegistry',
    'get_extension_registry',
    'LawfulBasisExtension',
    'WTFExtension'
]
