# Open Source Software Disclosure Schedule
## vCon Library

**Document Version:** 1.0
**Date:** October 30, 2025
**Project:** vCon Library v0.9.0
**Project License:** MIT License
**Copyright:** (c) 2024 StrolidInc

---

## 1. Executive Summary

This document provides a comprehensive disclosure of all open source software (OSS) components used in the vCon Library project. The vCon Library is a Python implementation of the vCon (Virtual Conversation) specification, licensed under the MIT License.

All dependencies used in this project are compatible with the MIT License and are suitable for commercial and non-commercial use.

---

## 2. Primary Application

### vCon Library
- **Version:** 0.9.0
- **License:** MIT License
- **Copyright:** (c) 2024 StrolidInc
- **Description:** Complete vCon 0.3.0 specification implementation for managing virtual conversations
- **Repository:** https://github.com/StrolidInc/vcon-lib (assumed)

---

## 3. Production Dependencies

These dependencies are required for runtime operation of the vCon Library.

### 3.1 Core Dependencies

#### authlib
- **Version:** ^1.6.4
- **License:** BSD-3-Clause
- **Copyright:** Authlib Contributors
- **Description:** The ultimate Python library for building OAuth and OpenID Connect servers and clients
- **Homepage:** https://authlib.org/
- **Purpose:** OAuth and authentication functionality
- **License Compatibility:** ✅ Compatible with MIT

#### uuid6
- **Version:** ^2024.7.10
- **License:** MIT License
- **Copyright:** uuid6 Contributors
- **Description:** New time-based UUID formats suited for database keys
- **Homepage:** https://github.com/oittaa/uuid6-python
- **Purpose:** Generate time-based UUIDs for vCon identifiers
- **License Compatibility:** ✅ Compatible with MIT

#### requests
- **Version:** ^2.32.3
- **License:** Apache License 2.0
- **Copyright:** Kenneth Reitz and contributors
- **Description:** HTTP library for Python
- **Homepage:** https://requests.readthedocs.io/
- **Purpose:** HTTP requests for loading vCons from URLs
- **License Compatibility:** ✅ Compatible with MIT

#### pydash
- **Version:** ^8.0.3
- **License:** MIT License
- **Copyright:** Derrick Gilland
- **Description:** Python utility library for functional programming
- **Homepage:** https://pydash.readthedocs.io/
- **Purpose:** Utility functions for data manipulation
- **License Compatibility:** ✅ Compatible with MIT

#### python-dateutil
- **Version:** ^2.9.0.post0
- **License:** Apache License 2.0 / BSD-3-Clause (dual-licensed)
- **Copyright:** Gustavo Niemeyer and contributors
- **Description:** Extensions to the standard Python datetime module
- **Homepage:** https://dateutil.readthedocs.io/
- **Purpose:** Date and time parsing for vCon timestamps
- **License Compatibility:** ✅ Compatible with MIT

#### mutagen
- **Version:** ^1.47.0
- **License:** GNU GPL v2 or later
- **Copyright:** Michael Urman, Joe Wreschnig, and contributors
- **Description:** Read and write audio tags for many formats
- **Homepage:** https://mutagen.readthedocs.io/
- **Purpose:** Audio metadata extraction for dialog media
- **License Compatibility:** ⚠️ **GPL - Attention Required** - Consider implications for distribution
- **Note:** GPL is a strong copyleft license. While it can be used in MIT projects, derivative works may need to comply with GPL terms

#### ffmpeg
- **Version:** ^1.4
- **License:** MIT License
- **Copyright:** ffmpeg-python contributors
- **Description:** Python bindings for FFmpeg
- **Homepage:** https://github.com/jiashaokun/ffmpeg
- **Purpose:** Media processing capabilities
- **License Compatibility:** ✅ Compatible with MIT
- **Note:** Requires FFmpeg binary (LGPL/GPL) to be installed separately

#### logger
- **Version:** ^1.4
- **License:** MIT License
- **Copyright:** logger contributors
- **Description:** Python logging helper
- **Homepage:** https://github.com/jiashaokun/logger
- **Purpose:** Logging functionality
- **License Compatibility:** ✅ Compatible with MIT

#### pypdf
- **Version:** ^6.0.0
- **License:** BSD-3-Clause
- **Copyright:** pypdf contributors
- **Description:** Pure-python PDF library for splitting, merging, cropping, and transforming PDFs
- **Homepage:** https://pypdf.readthedocs.io/
- **Purpose:** PDF attachment handling
- **License Compatibility:** ✅ Compatible with MIT

#### pillow
- **Version:** ^11.3.0
- **License:** HPND (Historical Permission Notice and Disclaimer)
- **Copyright:** Jeffrey A. Clark (Alex) and contributors
- **Description:** Python Imaging Library (Fork)
- **Homepage:** https://python-pillow.org/
- **Purpose:** Image processing for visual attachments
- **License Compatibility:** ✅ Compatible with MIT

### 3.2 Sub-Dependencies (Production)

These are transitive dependencies required by the core dependencies:

#### certifi
- **Version:** 2025.8.3
- **License:** MPL-2.0 (Mozilla Public License 2.0)
- **Description:** Python package for Mozilla's CA Bundle
- **Purpose:** SSL certificate verification
- **License Compatibility:** ✅ Compatible with MIT

#### cffi
- **Version:** 2.0.0
- **License:** MIT License
- **Description:** Foreign Function Interface for Python calling C code
- **Purpose:** C bindings for cryptography
- **License Compatibility:** ✅ Compatible with MIT

#### charset-normalizer
- **Version:** 3.3.2
- **License:** MIT License
- **Description:** Universal charset detector
- **Purpose:** Character encoding detection
- **License Compatibility:** ✅ Compatible with MIT

#### cryptography
- **Version:** 46.0.1
- **License:** Apache License 2.0 / BSD-3-Clause (dual-licensed)
- **Description:** Cryptographic recipes and primitives
- **Purpose:** Digital signatures and encryption
- **License Compatibility:** ✅ Compatible with MIT

#### idna
- **Version:** 3.8
- **License:** BSD-3-Clause
- **Description:** Internationalized Domain Names in Applications (IDNA)
- **Purpose:** Domain name encoding
- **License Compatibility:** ✅ Compatible with MIT

#### pycparser
- **Version:** 2.22
- **License:** BSD-3-Clause
- **Description:** C parser in Python
- **Purpose:** Used by cffi
- **License Compatibility:** ✅ Compatible with MIT

#### six
- **Version:** 1.16.0
- **License:** MIT License
- **Description:** Python 2 and 3 compatibility utilities
- **Purpose:** Python version compatibility
- **License Compatibility:** ✅ Compatible with MIT

#### typing-extensions
- **Version:** 4.12.2
- **License:** Python Software Foundation License
- **Description:** Backported type hints for Python
- **Purpose:** Type annotations compatibility
- **License Compatibility:** ✅ Compatible with MIT

#### urllib3
- **Version:** 2.5.0
- **License:** MIT License
- **Description:** HTTP library with connection pooling
- **Purpose:** HTTP connections for requests
- **License Compatibility:** ✅ Compatible with MIT

---

## 4. Development Dependencies

These dependencies are only used during development, testing, and documentation generation. They are not required for runtime operation and are not distributed with the library.

### 4.1 Testing Dependencies

#### pytest
- **Version:** ^8.3.4
- **License:** MIT License
- **Description:** Simple powerful testing framework
- **Purpose:** Unit testing
- **License Compatibility:** ✅ Compatible with MIT

#### pytest-cov
- **Version:** ^5.0.0
- **License:** MIT License
- **Description:** Pytest plugin for measuring code coverage
- **Purpose:** Code coverage analysis
- **License Compatibility:** ✅ Compatible with MIT

#### pytest-mock
- **Version:** ^3.14.0
- **License:** MIT License
- **Description:** Thin wrapper around mock for easier use with pytest
- **Purpose:** Mocking in unit tests
- **License Compatibility:** ✅ Compatible with MIT

#### coverage
- **Version:** 7.6.1
- **License:** Apache License 2.0
- **Description:** Code coverage measurement
- **Purpose:** Coverage reporting
- **License Compatibility:** ✅ Compatible with MIT

### 4.2 Documentation Dependencies

#### sphinx
- **Version:** <7.0.0
- **License:** BSD-2-Clause
- **Description:** Python documentation generator
- **Purpose:** API documentation generation
- **License Compatibility:** ✅ Compatible with MIT

#### sphinx-rtd-theme
- **Version:** ^3.0.2
- **License:** MIT License
- **Description:** Read the Docs theme for Sphinx
- **Purpose:** Documentation styling
- **License Compatibility:** ✅ Compatible with MIT

#### docutils
- **Version:** 0.19
- **License:** Public Domain / BSD-2-Clause / Python Software Foundation License
- **Description:** Python Documentation Utilities
- **Purpose:** Documentation processing
- **License Compatibility:** ✅ Compatible with MIT

### 4.3 Code Quality Dependencies

#### flake8
- **Version:** ^7.1.2
- **License:** MIT License
- **Description:** Modular source code checker
- **Purpose:** Code style enforcement
- **License Compatibility:** ✅ Compatible with MIT

### 4.4 Documentation Sub-Dependencies

#### alabaster
- **Version:** 0.7.13
- **License:** BSD-3-Clause
- **Purpose:** Sphinx theme

#### babel
- **Version:** 2.16.0
- **License:** BSD-3-Clause
- **Purpose:** Internationalization utilities

#### colorama
- **Version:** 0.4.6
- **License:** BSD-3-Clause
- **Purpose:** Cross-platform colored terminal text

#### imagesize
- **Version:** 1.4.1
- **License:** MIT License
- **Purpose:** Image size detection

#### iniconfig
- **Version:** 2.0.0
- **License:** MIT License
- **Purpose:** INI config parsing

#### jinja2
- **Version:** 3.1.6
- **License:** BSD-3-Clause
- **Purpose:** Template engine for Sphinx

#### markupsafe
- **Version:** 2.1.5
- **License:** BSD-3-Clause
- **Purpose:** Safe string handling for Jinja2

#### mccabe
- **Version:** 0.7.0
- **License:** MIT License
- **Purpose:** Code complexity checker

#### packaging
- **Version:** 24.1
- **License:** Apache License 2.0 / BSD-2-Clause
- **Purpose:** Core utilities for Python packages

#### pluggy
- **Version:** 1.5.0
- **License:** MIT License
- **Purpose:** Plugin system for pytest

#### pycodestyle
- **Version:** 2.12.1
- **License:** MIT License
- **Purpose:** Python style guide checker

#### pyflakes
- **Version:** 3.2.0
- **License:** MIT License
- **Purpose:** Passive Python syntax checker

#### pygments
- **Version:** 2.19.1
- **License:** BSD-2-Clause
- **Purpose:** Syntax highlighting

#### snowballstemmer
- **Version:** 2.2.0
- **License:** BSD-3-Clause
- **Purpose:** Stemming algorithms for search

#### sphinxcontrib-applehelp
- **Version:** 1.0.4
- **License:** BSD-2-Clause
- **Purpose:** Apple Help output for Sphinx

#### sphinxcontrib-devhelp
- **Version:** 1.0.2
- **License:** BSD-2-Clause
- **Purpose:** DevHelp output for Sphinx

#### sphinxcontrib-htmlhelp
- **Version:** 2.0.1
- **License:** BSD-2-Clause
- **Purpose:** HTML Help output for Sphinx

#### sphinxcontrib-jquery
- **Version:** 4.1
- **License:** 0BSD (BSD Zero Clause)
- **Purpose:** jQuery for Sphinx

#### sphinxcontrib-jsmath
- **Version:** 1.0.1
- **License:** BSD-2-Clause
- **Purpose:** JavaScript math rendering

#### sphinxcontrib-qthelp
- **Version:** 1.0.3
- **License:** BSD-2-Clause
- **Purpose:** Qt Help output for Sphinx

#### sphinxcontrib-serializinghtml
- **Version:** 1.1.5
- **License:** BSD-2-Clause
- **Purpose:** Serialized HTML output for Sphinx

---

## 5. License Compatibility Analysis

### 5.1 Compatible Licenses

The following licenses are fully compatible with the MIT License used by vCon Library:

- **MIT License** - Permissive, allows commercial use
- **BSD-2-Clause, BSD-3-Clause** - Permissive, attribution required
- **Apache License 2.0** - Permissive, patent grant included
- **HPND** - Permissive, historical permission notice
- **0BSD** - Public domain equivalent
- **Python Software Foundation License** - Permissive
- **MPL-2.0** - Weak copyleft, file-level (when used as library)

### 5.2 Licenses Requiring Attention

#### GNU GPL v2 or later (mutagen)
- **Status:** ⚠️ **Requires Careful Consideration**
- **Component:** mutagen (audio metadata library)
- **Impact:** GPL is a strong copyleft license
- **Implications:**
  - Using GPL code in MIT project is permitted
  - If mutagen code is modified or if vCon Library is distributed as a combined work with mutagen, GPL terms may apply
  - End users who receive vCon Library with mutagen must have access to source code
  - Consider using alternative libraries (e.g., tinytag, eyed3) if GPL compatibility is a concern
- **Recommendation:**
  - Document GPL dependency clearly
  - Ensure compliance if distributing binary packages
  - Consider making mutagen an optional dependency
  - Provide source code access for GPL compliance

---

## 6. Distribution Considerations

### 6.1 Source Distribution
When distributing vCon Library as source code:
- Include this OSS Disclosure document
- Include LICENSE.txt (MIT License)
- Include all dependency licenses (automatically handled by pip/poetry)
- Ensure GPL compliance for mutagen (source code availability)

### 6.2 Binary Distribution
When distributing compiled/bundled versions:
- Include all license notices
- Provide source code access for GPL components (mutagen)
- Include this OSS Disclosure document
- Consider legal review for GPL implications

### 6.3 Commercial Use
The MIT License and most dependencies allow commercial use. However:
- GPL components (mutagen) may require source code disclosure
- Consult with legal counsel for commercial distributions
- Consider optional dependencies to avoid GPL

---

## 7. Compliance Recommendations

### 7.1 Required Actions
1. ✅ Include this OSS Disclosure in documentation
2. ✅ Maintain LICENSE.txt file
3. ⚠️ Review GPL implications for mutagen
4. ✅ Include license notices in distributions
5. ✅ Document all dependencies in requirements.txt/pyproject.toml

### 7.2 Optional Actions
1. Consider making mutagen optional to avoid GPL
2. Add license scanning to CI/CD pipeline
3. Regularly update this disclosure with dependency changes
4. Monitor for security vulnerabilities in dependencies
5. Review new dependencies before adding

### 7.3 For End Users
If you use vCon Library:
- Review your own license compatibility requirements
- Be aware of GPL dependency (mutagen)
- Ensure your distribution model complies with all licenses
- Consult legal counsel for commercial use

---

## 8. License Texts

Full license texts for all dependencies are available in the following locations:

- **Python Package Metadata:** `/path/to/site-packages/<package>/LICENSE` or `COPYING`
- **PyPI:** Each package page on https://pypi.org/
- **GitHub:** Most projects have LICENSE files in their repositories

### Key License URLs

- **MIT License:** https://opensource.org/licenses/MIT
- **BSD Licenses:** https://opensource.org/licenses/BSD-3-Clause
- **Apache 2.0:** https://opensource.org/licenses/Apache-2.0
- **GPL v2:** https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
- **MPL 2.0:** https://www.mozilla.org/en-US/MPL/2.0/

---

## 9. Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-30 | Initial OSS Disclosure Schedule | Generated for vCon Library v0.9.0 |

---

## 10. Contact Information

For questions regarding open source licenses in vCon Library:

- **Project Repository:** https://github.com/StrolidInc/vcon-lib (assumed)
- **Maintainer:** Thomas McCarthy-Howe <ghostofbasho@gmail.com>
- **License:** MIT License

---

## 11. Appendix A: Quick Reference Table

| Package | Version | License | Type | GPL Compatible | Notes |
|---------|---------|---------|------|----------------|-------|
| authlib | 1.6.4 | BSD-3-Clause | Production | Yes | OAuth library |
| uuid6 | 2024.7.10 | MIT | Production | Yes | UUID generation |
| requests | 2.32.5 | Apache-2.0 | Production | Yes | HTTP client |
| pydash | 8.0.3 | MIT | Production | Yes | Utilities |
| python-dateutil | 2.9.0 | Apache-2.0/BSD | Production | Yes | Date parsing |
| mutagen | 1.47.0 | **GPL v2+** | Production | **GPL** | ⚠️ Audio metadata |
| ffmpeg | 1.4 | MIT | Production | Yes | Media processing |
| logger | 1.4 | MIT | Production | Yes | Logging |
| pypdf | 6.1.0 | BSD-3-Clause | Production | Yes | PDF handling |
| pillow | 11.3.0 | HPND | Production | Yes | Image processing |
| pytest | 8.3.4 | MIT | Development | Yes | Testing |
| pytest-cov | 5.0.0 | MIT | Development | Yes | Coverage |
| pytest-mock | 3.14.0 | MIT | Development | Yes | Mocking |
| sphinx | 6.2.1 | BSD-2-Clause | Development | Yes | Documentation |
| sphinx-rtd-theme | 3.0.2 | MIT | Development | Yes | Docs theme |
| flake8 | 7.1.2 | MIT | Development | Yes | Linting |

---

## 12. Appendix B: Dependency Graph

```
vCon Library (MIT)
├── Production Dependencies
│   ├── authlib (BSD-3-Clause)
│   │   └── cryptography (Apache-2.0/BSD)
│   │       └── cffi (MIT)
│   │           └── pycparser (BSD-3-Clause)
│   ├── uuid6 (MIT)
│   ├── requests (Apache-2.0)
│   │   ├── certifi (MPL-2.0)
│   │   ├── charset-normalizer (MIT)
│   │   ├── idna (BSD-3-Clause)
│   │   └── urllib3 (MIT)
│   ├── pydash (MIT)
│   │   └── typing-extensions (PSF)
│   ├── python-dateutil (Apache-2.0/BSD)
│   │   └── six (MIT)
│   ├── mutagen (GPL v2+) ⚠️
│   ├── ffmpeg (MIT)
│   ├── logger (MIT)
│   ├── pypdf (BSD-3-Clause)
│   └── pillow (HPND)
└── Development Dependencies
    ├── pytest (MIT)
    │   ├── colorama (BSD-3-Clause)
    │   ├── iniconfig (MIT)
    │   ├── packaging (Apache-2.0/BSD)
    │   └── pluggy (MIT)
    ├── pytest-cov (MIT)
    │   └── coverage (Apache-2.0)
    ├── pytest-mock (MIT)
    ├── sphinx (BSD-2-Clause)
    │   ├── alabaster (BSD-3-Clause)
    │   ├── babel (BSD-3-Clause)
    │   ├── docutils (Public Domain/BSD)
    │   ├── imagesize (MIT)
    │   ├── jinja2 (BSD-3-Clause)
    │   ├── pygments (BSD-2-Clause)
    │   └── [sphinxcontrib-* packages] (BSD-2-Clause)
    ├── sphinx-rtd-theme (MIT)
    │   └── sphinxcontrib-jquery (0BSD)
    └── flake8 (MIT)
        ├── mccabe (MIT)
        ├── pycodestyle (MIT)
        └── pyflakes (MIT)
```

---

**End of Open Source Software Disclosure Schedule**

---

**Disclaimer:** This disclosure schedule is provided for informational purposes. It is the responsibility of users and distributors to ensure compliance with all applicable licenses. Consult with legal counsel for specific compliance questions.
