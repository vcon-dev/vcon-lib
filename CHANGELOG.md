# Changelog

## [Unreleased] - 2025-07-19

### Added
- **New Required Fields Support**: Added support for the latest IETF vCon specification requirements
  - **vCon Object Level**: 
    - `extensions` field for declaring extension capabilities
    - `must_support` field for specifying required extensions
    - Helper methods: `add_extension()`, `remove_extension()`, `get_extensions()`, `add_must_support()`, `remove_must_support()`, `get_must_support()`
  - **Party Object**: 
    - `sip` field for SIP URI contact information
    - `did` field for Decentralized Identifier support
    - `jCard` field for vCard format contact information
    - `timezone` field for party timezone information
  - **Dialog Object**: 
    - `session_id` field for session tracking
    - `content_hash` field for content integrity verification (replaces alg/signature)
    - Helper methods: `set_session_id()`, `get_session_id()`, `set_content_hash()`, `get_content_hash()`, `calculate_content_hash()`, `verify_content_hash()`
- **Comprehensive Testing**: Added extensive test coverage for all new fields and functionality
- **Documentation**: Updated README, usage guide, and created dedicated documentation for new required fields
- **Example**: Created `samples/example_new_fields.py` demonstrating all new functionality
- **Backward Compatibility**: All new fields are optional and maintain full backward compatibility

### Changed
- Updated `_ALLOWED_VCON_PROPERTIES`, `_ALLOWED_PARTY_PROPERTIES`, and `_ALLOWED_DIALOG_PROPERTIES` to include new fields
- Enhanced property handling to properly process new fields in different modes (default, strict, meta)

### Technical Details
- New fields are properly serialized to JSON when they have values
- Content hash calculation uses SHA-256 algorithm by default
- Extension management prevents duplicate entries
- All existing functionality continues to work unchanged

---

## [Previous Version]

- Updated the `__init__` methods in `Dialog` and `Party` classes to accept additional keyword arguments (`**kwargs`) for flexibility.
- Simplified attribute assignment by using `locals()` to set non-None values.
- Enhanced the `to_dict` method in `Dialog` to return all non-None attributes.
- Improved readability and consistency in the code structure.
- Added docstrings for better documentation of methods and parameters.