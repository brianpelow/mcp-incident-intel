"""Tests for ServerConfig."""

from mcpincident.core.config import ServerConfig


def test_config_defaults() -> None:
    config = ServerConfig()
    assert config.industry == "fintech"
    assert config.runbook_dir == "runbooks"
    assert config.timeout_seconds == 30
    assert config.push is False if hasattr(config, "push") else True


def test_config_has_pagerduty_false() -> None:
    config = ServerConfig(pagerduty_token="")
    assert config.has_pagerduty is False


def test_config_has_pagerduty_true() -> None:
    config = ServerConfig(pagerduty_token="test-token")
    assert config.has_pagerduty is True


def test_config_has_dynatrace_false() -> None:
    config = ServerConfig(dynatrace_url="", dynatrace_token="")
    assert config.has_dynatrace is False


def test_config_has_dynatrace_true() -> None:
    config = ServerConfig(
        dynatrace_url="https://test.live.dynatrace.com",
        dynatrace_token="test-token",
    )
    assert config.has_dynatrace is True