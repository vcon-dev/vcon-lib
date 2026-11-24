"""Guard the ffmpeg dependency.

The PyPI package `ffmpeg` (1.4) is not ffmpeg-python. It installs an empty
`ffmpeg/__init__.py`, and when both are installed it empties the real one, so
`ffmpeg.probe` disappears. Releases 0.6.0 to 1.0.3 declared `ffmpeg = "^1.4"`
where ffmpeg-python was meant, and a conserver image built with both lost
`ffmpeg.probe`. Every real recording then failed transcription.
"""
import re
from importlib import metadata

import pytest


def _requirement_names(dist_name):
    names = []
    for req in metadata.requires(dist_name) or []:
        match = re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", req)
        names.append(re.sub(r"[-_.]+", "-", match.group(0)).lower())
    return names


def test_vcon_does_not_require_the_empty_ffmpeg_package():
    assert "ffmpeg" not in _requirement_names("vcon")


def test_import_ffmpeg_has_probe():
    ffmpeg = pytest.importorskip("ffmpeg")
    assert hasattr(ffmpeg, "probe"), "the installed `ffmpeg` module is not ffmpeg-python"
