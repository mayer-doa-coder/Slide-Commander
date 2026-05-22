"""Unit tests for config.py — FR-06, NFR-05."""

import pytest
from config import Config


# ── defaults ──────────────────────────────────────────────────────────────────

def test_default_init():
    cfg = Config()
    assert cfg.port == 5000
    assert cfg.model_path == "vosk-model-en-us-0.22"
    assert cfg.pin is None
    assert cfg.no_voice is False


def test_default_pin_disabled():
    cfg = Config()
    assert cfg.pin_enabled is False


# ── valid overrides ───────────────────────────────────────────────────────────

def test_valid_port_override():
    cfg = Config(port=8080)
    assert cfg.port == 8080


def test_valid_port_boundary_low():
    cfg = Config(port=1024)
    assert cfg.port == 1024


def test_valid_port_boundary_high():
    cfg = Config(port=65535)
    assert cfg.port == 65535


def test_valid_pin():
    cfg = Config(pin="1234")
    assert cfg.pin == "1234"
    assert cfg.pin_enabled is True


def test_valid_pin_leading_zeros():
    cfg = Config(pin="0042")
    assert cfg.pin == "0042"


def test_valid_pin_all_zeros():
    cfg = Config(pin="0000")
    assert cfg.pin == "0000"


def test_valid_pin_all_nines():
    cfg = Config(pin="9999")
    assert cfg.pin == "9999"


def test_valid_no_voice_true():
    cfg = Config(no_voice=True)
    assert cfg.no_voice is True


def test_valid_custom_model_path():
    cfg = Config(model_path="vosk-model-small-en-us-0.15")
    assert cfg.model_path == "vosk-model-small-en-us-0.15"


def test_valid_all_overrides():
    cfg = Config(port=9000, model_path="vosk-model-small-en-us-0.15", pin="5678", no_voice=True)
    assert cfg.port == 9000
    assert cfg.model_path == "vosk-model-small-en-us-0.15"
    assert cfg.pin == "5678"
    assert cfg.no_voice is True


# ── port validation errors ────────────────────────────────────────────────────

def test_port_too_high():
    with pytest.raises(ValueError, match="65535"):
        Config(port=99999)


def test_port_too_low():
    with pytest.raises(ValueError, match="1024"):
        Config(port=80)


def test_port_zero():
    with pytest.raises(ValueError):
        Config(port=0)


def test_port_negative():
    with pytest.raises(ValueError):
        Config(port=-1)


def test_port_boundary_just_below_min():
    with pytest.raises(ValueError):
        Config(port=1023)


def test_port_boundary_just_above_max():
    with pytest.raises(ValueError):
        Config(port=65536)


def test_port_as_string_raises():
    with pytest.raises(ValueError, match="integer"):
        Config(port="5000")  # type: ignore[arg-type]


def test_port_as_float_raises():
    with pytest.raises(ValueError, match="integer"):
        Config(port=5000.0)  # type: ignore[arg-type]


def test_port_as_bool_raises():
    # bool is a subclass of int in Python; we explicitly reject it
    with pytest.raises(ValueError, match="integer"):
        Config(port=True)  # type: ignore[arg-type]


# ── pin validation errors ─────────────────────────────────────────────────────

def test_pin_too_short():
    with pytest.raises(ValueError, match="4 decimal digits"):
        Config(pin="123")


def test_pin_too_long():
    with pytest.raises(ValueError, match="4 decimal digits"):
        Config(pin="12345")


def test_pin_with_letters():
    with pytest.raises(ValueError, match="4 decimal digits"):
        Config(pin="12A4")


def test_pin_empty_string():
    with pytest.raises(ValueError, match="4 decimal digits"):
        Config(pin="")


def test_pin_spaces():
    with pytest.raises(ValueError, match="4 decimal digits"):
        Config(pin="12 4")


def test_pin_as_integer_raises():
    with pytest.raises(ValueError, match="string"):
        Config(pin=1234)  # type: ignore[arg-type]


def test_pin_special_chars():
    with pytest.raises(ValueError, match="4 decimal digits"):
        Config(pin="12#4")


# ── property helpers ──────────────────────────────────────────────────────────

def test_server_url_default_port():
    cfg = Config()
    assert cfg.server_url == "http://0.0.0.0:5000"


def test_server_url_custom_port():
    cfg = Config(port=8888)
    assert cfg.server_url == "http://0.0.0.0:8888"


def test_pin_enabled_false_when_none():
    assert Config().pin_enabled is False


def test_pin_enabled_true_when_set():
    assert Config(pin="0000").pin_enabled is True
