"""Tests for vCon signing and verification."""

import pytest

from src.vcon.vcon import Vcon


def test_sign_and_verify_round_trip():
    vcon = Vcon.build_new()
    private_key, public_key = Vcon.generate_key_pair()

    vcon.sign(private_key)
    assert vcon.verify(public_key)


def test_verify_requires_signature():
    vcon = Vcon.build_new()
    _, public_key = Vcon.generate_key_pair()

    with pytest.raises(ValueError):
        vcon.verify(public_key)


def test_verify_bad_signature_returns_false():
    vcon = Vcon.build_new()
    private_key, public_key = Vcon.generate_key_pair()
    vcon.sign(private_key)

    # Tamper with signature
    vcon.vcon_dict["signatures"][0]["signature"] = "bad"
    assert vcon.verify(public_key) is False
