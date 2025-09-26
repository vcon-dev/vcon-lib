"""
Lawful Basis Extension for vCon

This module implements the lawful basis extension as defined in
draft-howe-vcon-lawful-basis-00, providing standardized mechanisms for
recording, verifying, and managing lawful bases for processing conversation data.
"""

from .attachment import (
    LawfulBasisAttachment,
    PurposeGrant,
    ContentHash,
    ProofMechanism,
    RegistryInfo,
    LawfulBasisType,
    ProofType,
    HashAlgorithm,
    CanonicalizationMethod
)
from .validation import LawfulBasisValidator
from .processing import LawfulBasisProcessor
from .registry import SCITTRegistryClient
from .extension import LawfulBasisExtension

__all__ = [
    'LawfulBasisAttachment',
    'PurposeGrant',
    'ContentHash',
    'ProofMechanism',
    'RegistryInfo',
    'LawfulBasisType',
    'ProofType',
    'HashAlgorithm',
    'CanonicalizationMethod',
    'LawfulBasisValidator',
    'LawfulBasisProcessor',
    'SCITTRegistryClient',
    'LawfulBasisExtension'
]
