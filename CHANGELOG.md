# Changelog

## [0.9.0] - 2025-01-26

### 🎉 Major Release: Extension Framework and Privacy Compliance

This release introduces a comprehensive extension framework with two major extensions: the Lawful Basis extension for GDPR-compliant privacy management and the WTF (World Transcription Format) extension for standardized speech-to-text transcription data.

### ✨ Added

#### **Extension Framework**
- **Extension Registry**: Centralized registry for managing vCon extensions
- **Extension Validation**: Comprehensive validation framework for extension data
- **Extension Processing**: Standardized processing and analysis framework
- **Extension Types**: Support for Compatible, Incompatible, and Experimental extensions
- **Extension Management**: Methods for adding, removing, and managing extensions

#### **Lawful Basis Extension (Privacy Compliance)**
- **GDPR Compliance**: Full support for GDPR-compliant consent management
- **Multiple Lawful Basis Types**: consent, contract, legal_obligation, vital_interests, public_task, legitimate_interests
- **Purpose-Specific Permissions**: Granular permission grants with conditions
- **Cryptographic Proof Mechanisms**: Verbal confirmation, signed documents, cryptographic signatures, external systems
- **Temporal Validity**: Expiration dates and status intervals
- **Content Integrity**: Hash validation and canonicalization
- **External Registry Integration**: SCITT (Supply Chain Integrity, Transparency, and Trust) support
- **Permission Checking**: `check_lawful_basis_permission()` method for granular permission validation

#### **WTF Extension (World Transcription Format)**
- **Multi-Provider Support**: Whisper, Deepgram, AssemblyAI
- **Standardized Format**: Hierarchical structure with transcripts, segments, words, and speakers
- **Quality Metrics**: Audio quality assessment and confidence scoring
- **Export Capabilities**: SRT and WebVTT subtitle formats
- **Provider Adapters**: Automatic conversion from provider-specific formats
- **Analysis Tools**: Keyword extraction, confidence analysis, and transcription comparison
- **Speaker Identification**: Support for multiple speakers with timing and confidence data

#### **Vcon Class Extensions**
- **`add_lawful_basis_attachment()`**: Add lawful basis attachments with consent management
- **`add_wtf_transcription_attachment()`**: Add standardized transcription attachments
- **`find_lawful_basis_attachments()`**: Find and filter lawful basis attachments
- **`find_wtf_attachments()`**: Find and filter WTF transcription attachments
- **`check_lawful_basis_permission()`**: Check permissions for specific purposes
- **`validate_extensions()`**: Validate all extensions in a vCon
- **`process_extensions()`**: Process all extensions in a vCon

### 🔄 Changed

#### **Extension Integration**
- **Attachment Properties**: Added `start`, `party`, and `dialog` to allowed attachment properties
- **Extension Registry**: Automatic initialization of default extensions
- **Import Handling**: Graceful handling of extension imports with fallback

### 🧪 Testing

#### **Comprehensive Test Suite**
- **Extension Framework Tests**: Test coverage for extension registry and validation
- **Lawful Basis Tests**: Test suite for privacy compliance functionality
- **WTF Extension Tests**: Test coverage for transcription functionality
- **Integration Tests**: End-to-end testing of extension workflows
- **Provider Adapter Tests**: Testing of multi-provider data conversion
- **Export Functionality Tests**: SRT and WebVTT export testing

### 📄 Documentation

#### **Comprehensive Documentation Updates**
- **README.md**: Added comprehensive quickstart with extension examples
- **API_REFERENCE.md**: Complete extension API documentation (1,751 lines)
- **GUIDE.md**: Comprehensive extension usage guide (765 lines)
- **LLM_GUIDE.md**: AI-assisted development guide with extension patterns (1,817 lines)
- **Extension Examples**: Complete working examples for both extensions

#### **Sample Files**
- **extension_example.py**: Comprehensive extension example (231 lines)
- **example_new_fields.vcon.json**: Clean example showing new fields
- **Cleaned Samples**: Removed 8 deprecated files (~1.4MB cleanup)

### 🔧 Technical Details

#### **Extension Architecture**
- **Base Classes**: `ExtensionType`, `ExtensionValidator`, `ExtensionProcessor`
- **Registry System**: Centralized `ExtensionRegistry` with automatic initialization
- **Validation Framework**: Comprehensive validation with error and warning reporting
- **Processing Framework**: Standardized processing with result reporting

#### **Lawful Basis Implementation**
- **Data Structures**: `LawfulBasisAttachment`, `PurposeGrant`, `ContentHash`, `ProofMechanism`
- **Validation**: Comprehensive validation of consent data and temporal validity
- **Processing**: Permission checking and consent verification
- **Compliance**: GDPR, CCPA, and HIPAA compliance support

#### **WTF Implementation**
- **Data Structures**: `WTFAttachment`, `Transcript`, `Segment`, `Word`, `Speaker`, `Quality`
- **Provider Adapters**: `WhisperAdapter`, `DeepgramAdapter`, `AssemblyAIAdapter`
- **Export Formats**: SRT and WebVTT subtitle generation
- **Analysis Tools**: Keyword extraction, confidence analysis, speaking time calculation

### 🚀 Performance

#### **Optimizations**
- **Lazy Loading**: Extensions loaded only when needed
- **Efficient Validation**: Optimized validation algorithms
- **Memory Management**: Efficient handling of large transcription data
- **Export Performance**: Fast SRT and WebVTT generation

### 🔒 Security

#### **Privacy and Security**
- **Content Integrity**: Hash validation and canonicalization
- **Cryptographic Proofs**: Support for digital signatures and proof mechanisms
- **Temporal Validation**: Expiration date checking and status validation
- **Permission Granularity**: Fine-grained permission checking

### 📊 Statistics

#### **Code Metrics**
- **New Files**: 20+ new extension-related files
- **Lines of Code**: 2,000+ lines of new extension functionality
- **Test Coverage**: Test coverage for extension features
- **Documentation**: 4,000+ lines of comprehensive documentation

#### **Feature Coverage**
- **2 Major Extensions**: Lawful Basis and WTF
- **3 Provider Adapters**: Multi-provider transcription support
- **2 Export Formats**: SRT and WebVTT
- **6+ Validation Types**: Comprehensive extension validation
- **15+ New Methods**: Extension-specific functionality

## [0.8.0] - 2025-01-26

### 🎉 Major Release: Version Management Simplification

This release aligns with the upcoming vCon draft specification by removing mandatory version management and enforcement, making the version field optional while maintaining full backward compatibility.

### ✨ Added

#### **Flexible Versioning**
- **Optional Version Field**: The `vcon` field is now optional in vCon objects
- **Version Preservation**: Existing vCons with version fields continue to work unchanged
- **Simplified Creation**: New vCons can be created without version fields

### 🔄 Changed

#### **Version Management Simplification**
- **Removed `strict_version` Parameter**: Eliminated from all Vcon methods (`__init__`, `build_from_json`, `build_new`, `load`, `load_from_file`, `load_from_url`)
- **No Automatic Version Assignment**: vCon objects no longer automatically get a version field
- **No Version Migration**: Removed automatic migration from older versions
- **Updated Validation**: The `is_valid()` method no longer requires the version field

#### **Method Signatures Updated**
- `Vcon(vcon_dict=None, property_handling="default")` - removed `strict_version` parameter
- `build_from_json(json_str, property_handling="default")` - removed `strict_version` parameter
- `build_new(created_at=None, property_handling="default")` - removed `strict_version` parameter
- `load(source, property_handling="default")` - removed `strict_version` parameter
- `load_from_file(file_path, property_handling="default")` - removed `strict_version` parameter
- `load_from_url(url, property_handling="default")` - removed `strict_version` parameter

### 🧪 Testing

#### **Updated Test Suite**
- **Replaced Version Migration Tests**: Updated tests to cover optional version field behavior
- **New Test Cases**: Added comprehensive tests for versionless vCon creation and preservation
- **Backward Compatibility Tests**: Ensured existing vCons with version fields continue to work

### 📄 Documentation

#### **Updated Documentation**
- **README.md**: Updated to reflect version field being optional
- **API_REFERENCE.md**: Removed `strict_version` parameter from all method signatures
- **GUIDE.md**: Updated examples to show versionless vCon creation
- **MIGRATION_GUIDE.md**: Added migration steps for version management changes

#### **Updated Sample Files**
- **Removed Version Fields**: All sample vCon JSON files updated to demonstrate versionless vCons
- **Backward Compatibility**: Existing vCons with version fields continue to work

### 🔧 Technical Details

#### **Implementation Changes**
- **Removed Version Logic**: Eliminated version checking, migration, and enforcement code
- **Simplified Initialization**: Streamlined vCon object creation process
- **Preserved Functionality**: All other features remain unchanged

#### **Backward Compatibility**
- **Existing vCons**: Continue to work without any changes
- **Version Fields**: Preserved when present, not added when absent
- **API Compatibility**: All other methods and properties remain unchanged

### 🎯 Benefits

1. **Enhanced Flexibility**: vCon objects can now exist without mandatory versioning
2. **Simplified Implementation**: Reduced complexity in version management
3. **Better Privacy Support**: Enables creation of redacted versions without version conflicts
4. **Multiple Version Support**: Allows different versions of the same vCon to coexist
5. **Specification Compliance**: Aligns with upcoming vCon draft specification

---

## [0.7.0] - 2025-07-19

### 🎉 Major Release: Complete vCon 0.3.0 Specification Compliance

This release implements full compliance with the IETF vCon 0.3.0 specification, adding comprehensive support for all new fields, validation, and features while maintaining complete backward compatibility.

### ✨ Added

#### **vCon Object Level Features**
- **Extensions Support**: 
  - `extensions` field for declaring extension capabilities
  - `must_support` field for specifying required extensions
  - Helper methods: `add_extension()`, `remove_extension()`, `get_extensions()`
  - Helper methods: `add_must_support()`, `remove_must_support()`, `get_must_support()`
  - Automatic duplicate prevention and validation

#### **Enhanced Party Object Support**
- **New Contact Methods**:
  - `sip` field for SIP URI contact information
  - `did` field for Decentralized Identifier (blockchain-based identity)
  - `jCard` field for vCard format contact information (RFC 7095)
  - `timezone` field for party timezone information
- **Civic Address Support**: Complete GEOPRIV specification compliance
  - All administrative areas (a1-a6)
  - Street and building information (sts, hno, hns, prd, flr)
  - Location and identification fields (country, pc, nam, lmk, loc, pod)

#### **Enhanced Dialog Object Support**
- **Session Management**:
  - `session_id` field for session tracking
  - `content_hash` field for content integrity verification (replaces alg/signature)
  - `application` field for application identification
  - `message_id` field for email/text dialog identification
- **Content Integrity**:
  - `calculate_content_hash()` method with SHA-256 support
  - `verify_content_hash()` method for integrity verification
  - Automatic content hash calculation for external files

#### **Party History Event Tracking**
- **New PartyHistory Class**: Complete implementation of party history events
  - Support for all 6 specification event types: `join`, `drop`, `hold`, `unhold`, `mute`, `unmute`
  - Event validation with `VALID_EVENTS` list
  - ISO 8601 time serialization for all events
  - Proper error handling for invalid events

#### **Enhanced Media Type Support**
- **Specification-Compliant Media Types**:
  - Added `audio/x-mp3` and `audio/x-mp4` (specification required)
  - Enhanced video format support (MP4, WebM, AVI, MKV, MOV, FLV, 3GP)
  - Complete audio format coverage (WAV, MP3, MP4, OGG, WebM, AAC)
  - Image and document support (JPEG, TIFF, PDF)

#### **Disposition Values for Incomplete Dialogs**
- **Complete Disposition Support**: All 6 specification values implemented
  - `no-answer`: Call attempted but no answer
  - `congestion`: System load prevented completion
  - `failed`: Call/connection failed
  - `busy`: Party was busy
  - `hung-up`: Party hung up before conversation
  - `voicemail-no-message`: Voicemail answered but no message left
- **Validation**: Automatic validation for incomplete dialog types

#### **Transfer Dialog Enhancements**
- **Updated Field Names**: Consistent underscore naming convention
  - `transfer-target` → `transfer_target`
  - `target-dialog` → `target_dialog`
- **Enhanced Transfer Support**: Complete transfer operation tracking

#### **Comprehensive Documentation**
- **Updated Class Documentation**: Complete docstrings for all classes
  - Vcon class with vCon 0.3.0 feature documentation
  - Party class with new contact method documentation
  - Dialog class with session and content hash documentation
  - CivicAddress class with GEOPRIV compliance documentation
  - PartyHistory class with event tracking documentation
- **Enhanced README**: Comprehensive usage examples and feature documentation
- **API Documentation**: Complete API reference with examples

### 🔧 Changed

#### **Property Handling**
- **Updated Allowed Properties**: All new fields added to property lists
  - `_ALLOWED_VCON_PROPERTIES`: Added extensions, must_support
  - `_ALLOWED_PARTY_PROPERTIES`: Added sip, did, jCard, timezone
  - `_ALLOWED_DIALOG_PROPERTIES`: Added session_id, content_hash, application, message_id
- **Enhanced Property Processing**: Improved handling in all modes (default, strict, meta)

#### **Validation Enhancements**
- **Comprehensive Validation**: Enhanced validation for all new fields
  - Party history event validation
  - Disposition value validation for incomplete dialogs
  - Media type validation with specification compliance
  - Civic address field validation
- **Backward Compatibility**: All validation maintains backward compatibility

#### **Serialization Improvements**
- **ISO 8601 Compliance**: All datetime fields properly serialized
- **Content Hash Integration**: Automatic content hash calculation and verification
- **Extension Management**: Proper serialization of extensions and must_support fields

### 🧪 Testing

#### **Comprehensive Test Coverage**
- **149 Tests Passing**: Complete test suite with 7 skipped (advanced features)
- **New Feature Tests**: Extensive testing for all new vCon 0.3.0 features
  - Party history event validation tests
  - Disposition value validation tests
  - Media type validation tests
  - Extension management tests
  - Content hash calculation tests
- **Backward Compatibility Tests**: Verification that existing functionality works unchanged
- **Validation Tests**: Comprehensive validation testing for all new fields

### 📚 Documentation

#### **Complete Documentation Update**
- **Class Documentation**: Updated all class docstrings with vCon 0.3.0 features
- **README Enhancement**: Comprehensive usage examples and feature documentation
- **API Reference**: Complete API documentation with examples
- **Workplan Documentation**: Complete implementation tracking in IETF-123-WORKPLAN.md

### 🔄 Migration Support

#### **Version Migration**
- **Automatic Migration**: Seamless migration from older vCon versions
- **Strict Mode Support**: Optional strict version checking
- **Backward Compatibility**: Full compatibility with existing vCon files

### 🔑 Security

#### **Enhanced Security Features**
- **Content Integrity**: SHA-256 content hashing for external files
- **Digital Signatures**: JWS support for vCon signing
- **Validation**: Comprehensive validation for all security-related fields

### 📄 Sample Files

#### **Updated Sample Files**
- **Version 0.3.0 Compliance**: All sample files updated to vCon 0.3.0
- **New Field Examples**: Sample files demonstrating new features
- **Backward Compatibility**: Existing sample files continue to work

### 🔧 Technical Details

#### **Implementation Quality**
- **149 Tests Passing**: Comprehensive test coverage
- **Zero Breaking Changes**: Complete backward compatibility
- **Specification Compliance**: Full vCon 0.3.0 specification implementation
- **Performance**: Optimized implementation with minimal overhead
- **Error Handling**: Comprehensive error handling and validation

#### **Code Quality**
- **Type Hints**: Complete type annotation coverage
- **Documentation**: Comprehensive docstrings and comments
- **Linting**: Clean code with minimal linting issues
- **Modularity**: Well-structured, maintainable code

---

## [0.6.0] - Previous Version

- Updated the `__init__` methods in `Dialog` and `Party` classes to accept additional keyword arguments (`**kwargs`) for flexibility.
- Simplified attribute assignment by using `locals()` to set non-None values.
- Enhanced the `to_dict` method in `Dialog` to return all non-None attributes.
- Improved readability and consistency in the code structure.
- Added docstrings for better documentation of methods and parameters.
