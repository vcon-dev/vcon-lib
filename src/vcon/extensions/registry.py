"""
Extension registry for managing vCon extensions.

This module provides a centralized registry for managing vCon extensions,
including registration, validation, and processing capabilities.
"""

from typing import Dict, List, Optional, Any
import logging
from .base import ExtensionInfo, ExtensionType, ValidationResult, ProcessingResult

logger = logging.getLogger(__name__)


class ExtensionRegistry:
    """Central registry for managing vCon extensions."""
    
    def __init__(self):
        self._extensions: Dict[str, ExtensionInfo] = {}
        self._initialized = False
    
    def register_extension(self, extension_info: ExtensionInfo) -> None:
        """Register a new extension."""
        if extension_info.name in self._extensions:
            logger.warning(f"Extension {extension_info.name} is already registered, overwriting")
        
        self._extensions[extension_info.name] = extension_info
        logger.info(f"Registered extension: {extension_info.name} v{extension_info.version}")
    
    def get_extension(self, name: str) -> Optional[ExtensionInfo]:
        """Get extension information by name."""
        return self._extensions.get(name)
    
    def list_extensions(self) -> List[str]:
        """List all registered extension names."""
        return list(self._extensions.keys())
    
    def initialize_default_extensions(self) -> None:
        """Initialize default extensions."""
        try:
            from .lawful_basis import LawfulBasisExtension
            from .wtf import WTFExtension
            
            # Register lawful basis extension
            lawful_basis_ext = LawfulBasisExtension()
            self.register_extension(lawful_basis_ext.get_extension_info())
            
            # Register WTF extension
            wtf_ext = WTFExtension()
            self.register_extension(wtf_ext.get_extension_info())
            
            logger.info("Default extensions initialized")
            
        except ImportError as e:
            logger.warning(f"Could not initialize default extensions: {str(e)}")
    
    def is_extension_registered(self, name: str) -> bool:
        """Check if an extension is registered."""
        return name in self._extensions
    
    def validate_extension(self, name: str, vcon_dict: Dict[str, Any]) -> ValidationResult:
        """Validate an extension in a vCon."""
        extension = self.get_extension(name)
        if not extension:
            return ValidationResult(False, [f"Extension {name} is not registered"])
        
        if not extension.validator:
            return ValidationResult(True, warnings=[f"No validator for extension {name}"])
        
        try:
            return extension.validator.validate_extension_usage(vcon_dict)
        except Exception as e:
            logger.error(f"Error validating extension {name}: {str(e)}")
            return ValidationResult(False, [f"Validation error for {name}: {str(e)}"])
    
    def validate_attachment(self, attachment: Dict[str, Any]) -> ValidationResult:
        """Validate an extension attachment."""
        attachment_type = attachment.get("type")
        if not attachment_type:
            return ValidationResult(False, ["Attachment missing type field"])
        
        # Find extension that handles this attachment type
        for extension in self._extensions.values():
            if attachment_type in extension.attachment_types:
                if extension.validator:
                    try:
                        return extension.validator.validate_attachment(attachment)
                    except Exception as e:
                        logger.error(f"Error validating attachment {attachment_type}: {str(e)}")
                        return ValidationResult(False, [f"Validation error for {attachment_type}: {str(e)}"])
                else:
                    return ValidationResult(True, warnings=[f"No validator for attachment type {attachment_type}"])
        
        # If no extension handles this attachment type, it's not an extension attachment
        return ValidationResult(True)
    
    def process_extensions(self, vcon_dict: Dict[str, Any]) -> Dict[str, ProcessingResult]:
        """Process all extensions in a vCon."""
        results = {}
        extensions = vcon_dict.get("extensions", [])
        
        for extension_name in extensions:
            extension = self.get_extension(extension_name)
            if not extension:
                results[extension_name] = ProcessingResult(
                    False, 
                    errors=[f"Extension {extension_name} is not registered"]
                )
                continue
            
            if not extension.processor:
                results[extension_name] = ProcessingResult(
                    True,
                    data={"message": f"No processor for extension {extension_name}"}
                )
                continue
            
            try:
                result = extension.processor.process(vcon_dict)
                results[extension_name] = result
            except Exception as e:
                logger.error(f"Error processing extension {extension_name}: {str(e)}")
                results[extension_name] = ProcessingResult(
                    False,
                    errors=[f"Processing error for {extension_name}: {str(e)}"]
                )
        
        return results
    
    def get_required_extensions(self, vcon_dict: Dict[str, Any]) -> List[str]:
        """Get list of extensions that must be supported."""
        must_support = vcon_dict.get("must_support", [])
        required = []
        
        for extension_name in must_support:
            extension = self.get_extension(extension_name)
            if extension and extension.type == ExtensionType.INCOMPATIBLE:
                required.append(extension_name)
        
        return required
    
    def check_compatibility(self, vcon_dict: Dict[str, Any]) -> ValidationResult:
        """Check if all required extensions are supported."""
        required = self.get_required_extensions(vcon_dict)
        missing = []
        
        for extension_name in required:
            if not self.is_extension_registered(extension_name):
                missing.append(extension_name)
        
        if missing:
            return ValidationResult(
                False,
                [f"Missing required extensions: {', '.join(missing)}"]
            )
        
        return ValidationResult(True)
    
    def initialize_default_extensions(self):
        """Initialize default extensions."""
        if self._initialized:
            return
        
        # Import and register default extensions
        try:
            from .lawful_basis import LawfulBasisExtension
            from .wtf import WTFExtension
            
            # Register lawful basis extension
            lawful_basis = LawfulBasisExtension()
            self.register_extension(lawful_basis.get_extension_info())
            
            # Register WTF extension
            wtf = WTFExtension()
            self.register_extension(wtf.get_extension_info())
            
            self._initialized = True
            logger.info("Default extensions initialized")
            
        except ImportError as e:
            logger.warning(f"Could not import default extensions: {str(e)}")


# Global registry instance
_global_registry = ExtensionRegistry()


def get_extension_registry() -> ExtensionRegistry:
    """Get the global extension registry."""
    if not _global_registry._initialized:
        _global_registry.initialize_default_extensions()
    return _global_registry


def register_extension(extension_info: ExtensionInfo) -> None:
    """Register an extension with the global registry."""
    _global_registry.register_extension(extension_info)


def validate_extension(name: str, vcon_dict: Dict[str, Any]) -> ValidationResult:
    """Validate an extension using the global registry."""
    return _global_registry.validate_extension(name, vcon_dict)


def validate_attachment(attachment: Dict[str, Any]) -> ValidationResult:
    """Validate an attachment using the global registry."""
    return _global_registry.validate_attachment(attachment)
