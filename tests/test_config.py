"""Unit tests for config.py — FR-06, NFR-05."""

import pytest
from config import Config


# ── defaults ──────────────────────────────────────────────────────────────────

def test_default_init():
    cfg = Config()
    assert cfg.port == 5000
    assert cfg.model_path == "tiny"
    assert cfg.no_voice is False


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


def test_valid_no_voice_true():
    cfg = Config(no_voice=True)
    assert cfg.no_voice is True


def test_valid_custom_model_path():
    cfg = Config(model_path="base")
    assert cfg.model_path == "base"


def test_valid_all_overrides():
    cfg = Config(port=9000, model_path="small", no_voice=True)
    assert cfg.port == 9000
    assert cfg.model_path == "small"
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


# ── model_path validation ─────────────────────────────────────────────────────

@pytest.mark.parametrize("size", [
    "tiny", "tiny.en", "base", "base.en",
    "small", "small.en", "medium", "medium.en",
    "large-v1", "large-v2", "large-v3",
])
def test_valid_model_sizes(size):
    cfg = Config(model_path=size)
    assert cfg.model_path == size


def test_invalid_model_size_raises():
    with pytest.raises(ValueError, match="faster-whisper"):
        Config(model_path="vosk-model-en-us-0.22")


def test_invalid_model_size_garbage():
    with pytest.raises(ValueError, match="faster-whisper"):
        Config(model_path="huge")


# ── property helpers ──────────────────────────────────────────────────────────

def test_server_url_default_port():
    cfg = Config()
    assert cfg.server_url == "http://0.0.0.0:5000"


def test_server_url_custom_port():
    cfg = Config(port=8888)
    assert cfg.server_url == "http://0.0.0.0:8888"


